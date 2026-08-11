"""Relationship scanner job with progressive scanning and incremental merge.

Scans government web pages for external relationships (links, scripts, etc.)
and merges results into a persistent JSONL file plus per-country summary
files optimised for browser consumption.
"""

from __future__ import annotations

import json
import sqlite3
import time
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from src.lib import relationship_shards
from src.lib.country_utils import country_filename_to_code, iter_seed_toon_files
from src.lib.gov_domain_registry import GovernmentDomainRegistry
from src.lib.settings import Settings
from src.services.multi_scanner import MultiScanner, MultiScanResult
from src.storage.schema import initialize_schema

_GOV_REGISTRY = GovernmentDomainRegistry()

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Sharded dataset directory.  Replaces the single relationships.jsonl file,
# which grew to within a few kilobytes of GitHub's 100 MiB per-file limit.
RELATIONSHIP_SHARD_DIR = Path("docs/data/relationships")

# Pre-sharding location, still read once when a checkout has no shards yet.
LEGACY_RELATIONSHIP_JSONL = Path("docs/data/relationships.jsonl")
SUMMARIES_DIR = Path("docs/data/summaries")
PRIORITIZATION_PATH = Path("docs/data/gov-domain-prioritization.json")
MAX_FAILURES_BEFORE_BACKOFF = 3
BACKOFF_BASE_DAYS = 1
BACKOFF_MAX_DAYS = 28
DEFAULT_SCAN_WINDOW_DAYS = 28


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class AggregatedRelationship:
    """A deduplicated relationship edge with merge metadata."""

    source_domain: str
    target_domain: str
    target_hostname: str
    relationship_type: str
    target_category: str
    source_pages: set[str]
    observations: int
    page_regions: set[str]
    first_seen: str
    last_seen: str

    def to_dict(self) -> dict:
        """Serialise this edge for the published JSONL dataset.

        ``source_pages`` stays an integer for consumers that already read it as
        one, and ``source_page_urls`` carries the URLs it counts.  Publishing
        both is what makes the count independently verifiable, and it is what
        lets the next scan cycle resume the tally instead of restarting it --
        the scanner only visits a slice of the corpus per run, so an edge's
        page set has to survive a round-trip through this file.
        """
        return {
            "source_domain": self.source_domain,
            "target_domain": self.target_domain,
            "target_hostname": self.target_hostname,
            "relationship_type": self.relationship_type,
            "target_category": self.target_category,
            "source_pages": len(self.source_pages),
            "source_page_urls": sorted(self.source_pages),
            "observations": self.observations,
            "page_regions": sorted(self.page_regions),
            "first_seen": self.first_seen,
            "last_seen": self.last_seen,
        }


@dataclass
class UrlEligibility:
    """Priority and eligibility metadata for a single URL."""

    url: str
    country_code: str
    source_domain: str
    priority: int  # lower = higher priority
    last_attempted: str | None
    failure_count: int


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _rel_key(edge: Any) -> tuple[str, str, str, str]:
    """Deterministic identity key for a relationship edge."""
    return (
        edge.source_domain,
        edge.target_domain,
        edge.target_hostname,
        edge.relationship_type,
    )


def _backoff_days(failure_count: int) -> int:
    """Exponential backoff capped at BACKOFF_MAX_DAYS."""
    if failure_count <= 0:
        return 0
    return min(BACKOFF_BASE_DAYS * (2 ** (failure_count - 1)), BACKOFF_MAX_DAYS)


def _registered_domain_from_url(url: str) -> str:
    """The registrable domain for a URL's host (e.g. "mjusticia.gob.es"),
    falling back to the raw hostname for hosts entirely under a multi-label
    public suffix (e.g. bare "gob.es" itself, per the Public Suffix List --
    tldextract's registered_domain is empty for those)."""
    from urllib.parse import urlparse

    from tldextract import extract as tld_extract

    hostname = urlparse(url).hostname or ""
    if not hostname:
        return ""
    return tld_extract(url).registered_domain or hostname


def _derive_country_from_tld(url: str) -> str:
    """Country code for a URL's host, looked up against the government domain
    registry (built from the TOON seed files) rather than a hardcoded TLD
    table. Falls back to "UNKNOWN" for a host that isn't a known government
    domain -- previously this also silently mis-mapped any country outside a
    fixed 30-entry TLD list (e.g. Canada) to "UNKNOWN" even when the domain
    was a correctly-seeded government domain, since the table was never kept
    in sync with the TOON seed set."""
    registered_domain = _registered_domain_from_url(url)
    if not registered_domain:
        return "UNKNOWN"
    return _GOV_REGISTRY.country_for_domain(registered_domain) or "UNKNOWN"


# ---------------------------------------------------------------------------
# Core job class
# ---------------------------------------------------------------------------

class RelationshipScannerJob:
    """Progressive relationship scanner with metadata-driven eligibility."""

    def __init__(self, settings: Settings):
        self.settings = settings
        self.scanner = MultiScanner(
            timeout_seconds=settings.crawl_timeout_seconds,
            run_accessibility=False,
            run_social_media=False,
            run_tech=False,
            run_third_party_js=False,
            run_relationships=True,
        )
        self.db_path = initialize_schema(settings.metadata_db_url)

    # ------------------------------------------------------------------
    # TOON helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _load_toon_file(toon_path: Path) -> dict:
        with toon_path.open("r", encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    def _extract_urls_from_toon(toon_data: dict) -> list[str]:
        urls: list[str] = []
        for domain_entry in toon_data.get("domains", []):
            for page in domain_entry.get("pages", []):
                url = page.get("url")
                if url:
                    urls.append(url)
        return urls

    @staticmethod
    def _toon_page_count(toon_path: Path) -> int:
        try:
            toon_data = RelationshipScannerJob._load_toon_file(toon_path)
        except (OSError, json.JSONDecodeError):
            return 0
        declared = toon_data.get("page_count")
        if isinstance(declared, int):
            return max(declared, 0)
        return len(RelationshipScannerJob._extract_urls_from_toon(toon_data))

    # ------------------------------------------------------------------
    # Metadata helpers (SQLite)
    # ------------------------------------------------------------------

    def _load_hub_tiers(self) -> dict[str, int]:
        """Load domain prioritization tiers from network analysis.

        Returns mapping of domain -> tier score (0=critical, 1=high,
        2=medium, 3=low/unknown).  Hub domains are scanned first
        because they link to the most other government sites.
        """
        if not PRIORITIZATION_PATH.exists():
            return {}
        try:
            with PRIORITIZATION_PATH.open(encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, json.JSONDecodeError):
            return {}

        tiers: dict[str, int] = {}
        for country_data in data.get("countries", {}).values():
            for tier_name, tier_score in [
                ("critical", 0), ("high", 1), ("medium", 2),
            ]:
                for domain in country_data.get("scan_priority", {}).get(
                    tier_name, []
                ):
                    if domain not in tiers or tier_score < tiers[domain]:
                        tiers[domain] = tier_score
        return tiers

    def _get_eligible_urls(
        self,
        country_code: str,
        all_urls: list[str],
        skip_recently_scanned_days: int = 0,
    ) -> list[UrlEligibility]:
        """Return URLs sorted by priority: never-scanned → failed → oldest.

        Priority order (lower number = scan first):
          0 — never scanned
          1 — last scan failed (sorted by oldest attempt)
          2 — last scan succeeded, but stale (sorted by oldest success)
          3 — recently scanned successfully (skip these)
        """
        # Deduplicate while preserving order for deterministic results
        seen: set[str] = set()
        unique_urls: list[str] = []
        for u in all_urls:
            if u not in seen:
                seen.add(u)
                unique_urls.append(u)
        all_urls = unique_urls

        conn = sqlite3.connect(self.db_path)
        try:
            rows = conn.execute(
                """
                SELECT url, country_code, source_domain,
                       last_attempted_at, last_successful_at,
                       status, failure_count
                FROM relationship_scan_state
                WHERE url IN ({placeholders})
                """.format(placeholders=",".join("?" * len(all_urls))),
                all_urls,
            ).fetchall()
        finally:
            conn.close()

        state_map: dict[str, dict] = {}
        for row in rows:
            state_map[row[0]] = {
                "country_code": row[1],
                "source_domain": row[2],
                "last_attempted": row[3],
                "last_successful": row[4],
                "status": row[5],
                "failure_count": row[6],
            }

        cutoff = None
        if skip_recently_scanned_days > 0:
            cutoff = (
                datetime.now(timezone.utc) - timedelta(days=skip_recently_scanned_days)
            ).isoformat()

        eligible: list[UrlEligibility] = []
        for url in all_urls:
            state = state_map.get(url)

            if state is None:
                # Never scanned — highest priority
                eligible.append(UrlEligibility(
                    url=url,
                    country_code=country_code,
                    source_domain=_registered_domain_from_url(url),
                    priority=0,
                    last_attempted=None,
                    failure_count=0,
                ))
                continue

            last_attempted = state["last_attempted"]
            last_successful = state["last_successful"]
            failure_count = state["failure_count"]

            # Check backoff: if last attempt was recent enough, skip
            if last_attempted and failure_count > 0:
                backoff_days = _backoff_days(failure_count)
                backoff_cutoff = (
                    datetime.fromisoformat(last_attempted) + timedelta(days=backoff_days)
                )
                if datetime.now(timezone.utc) < backoff_cutoff:
                    continue  # Still in backoff window

            # Recently scanned successfully — skip
            if cutoff and last_successful and last_successful >= cutoff:
                continue  # priority=3, skip

            if failure_count > 0:
                priority = 1  # Failed URLs second
            elif last_successful:
                priority = 2  # Stale successful URLs third
            else:
                priority = 0  # Never successfully scanned

            eligible.append(UrlEligibility(
                url=url,
                country_code=country_code,
                source_domain=state.get("source_domain", ""),
                priority=priority,
                last_attempted=last_attempted,
                failure_count=failure_count,
            ))

        eligible.sort(key=lambda e: (e.priority, e.last_attempted or "", e.url))
        return eligible

    def _sort_by_hub_tier(
        self,
        eligible: list[UrlEligibility],
    ) -> list[UrlEligibility]:
        """Re-sort eligible URLs to boost hub domains.

        Hub domains (from network centrality analysis) are scanned first
        because they link to the most other government sites, revealing
        more of the network per scan.
        """
        hub_tiers = self._load_hub_tiers()
        if not hub_tiers:
            return eligible

        def sort_key(e: UrlEligibility) -> tuple[int, str, str]:
            domain = e.url.split("//")[-1].split("/")[0].split(":")[0]
            # Extract registered domain (last 2 parts)
            parts = domain.split(".")
            reg_domain = ".".join(parts[-2:]) if len(parts) >= 2 else domain
            tier = hub_tiers.get(reg_domain, 3)  # 3 = unknown/low
            return (e.priority, tier, e.last_attempted or "", e.url)

        return sorted(eligible, key=sort_key)

    def _update_scan_state(
        self,
        url: str,
        country_code: str,
        source_domain: str,
        scan_id: str,
        success: bool,
        scan_duration_ms: int,
    ) -> None:
        """Upsert per-URL scan state after a scan attempt."""
        now = datetime.now(timezone.utc).isoformat()
        conn = sqlite3.connect(self.db_path)
        try:
            existing = conn.execute(
                "SELECT failure_count FROM relationship_scan_state WHERE url = ?",
                (url,),
            ).fetchone()

            if existing is None:
                new_failures = 0 if success else 1
                conn.execute(
                    """
                    INSERT INTO relationship_scan_state
                    (url, country_code, source_domain, last_attempted_at,
                     last_successful_at, status, failure_count,
                     scan_duration_ms, last_scan_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        url, country_code, source_domain, now,
                        now if success else None,
                        "completed" if success else "failed",
                        new_failures, scan_duration_ms, scan_id,
                    ),
                )
            else:
                prev_failures = existing[0]
                new_failures = 0 if success else prev_failures + 1
                conn.execute(
                    """
                    UPDATE relationship_scan_state
                    SET last_attempted_at = ?,
                        last_successful_at = CASE WHEN ? THEN ? ELSE last_successful_at END,
                        status = ?,
                        failure_count = ?,
                        scan_duration_ms = ?,
                        last_scan_id = ?
                    WHERE url = ?
                    """,
                    (
                        now, success, now,
                        "completed" if success else "failed",
                        new_failures, scan_duration_ms, scan_id, url,
                    ),
                )
            conn.commit()
        finally:
            conn.close()

    def _save_scan_result(
        self,
        url: str,
        country_code: str,
        scan_id: str,
        source_domain: str,
        source_url: str,
        relationships_found: int,
        scan_duration_ms: int,
        is_reachable: bool,
        error_message: str | None,
        status_code: int | None,
    ) -> None:
        """Append a scan result row for history."""
        now = datetime.now(timezone.utc).isoformat()
        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute(
                """
                INSERT OR IGNORE INTO relationship_scan_results
                (url, country_code, scan_id, status_code, error_message,
                 is_reachable, source_domain, source_url, relationships_found,
                 scan_duration_ms, scanned_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    url, country_code, scan_id, status_code, error_message,
                    1 if is_reachable else 0, source_domain, source_url,
                    relationships_found, scan_duration_ms, now,
                ),
            )
            conn.commit()
        finally:
            conn.close()

    # ------------------------------------------------------------------
    # Country ordering (fairness)
    # ------------------------------------------------------------------

    def _get_last_scan_time_per_country(self) -> dict[str, str]:
        """Return most recent scan time per country for fairness ordering."""
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.execute(
                """
                SELECT country_code, MAX(last_successful_at)
                FROM relationship_scan_state
                GROUP BY country_code
                """
            )
            return {row[0]: row[1] for row in cursor.fetchall() if row[1]}
        finally:
            conn.close()

    def _build_balanced_country_order(
        self, toon_files: list[Path],
    ) -> list[Path]:
        """Interleave small, medium, and large countries for fairness."""
        if len(toon_files) <= 1:
            return list(toon_files)

        last_scans = self._get_last_scan_time_per_country()
        entries: list[tuple[Path, int, str | None]] = [
            (
                p,
                self._toon_page_count(p),
                last_scans.get(country_filename_to_code(p.stem)),
            )
            for p in toon_files
        ]

        counts = sorted(c for _, c, _ in entries)
        lo = counts[len(counts) // 3]
        hi = counts[(len(counts) * 2) // 3]

        buckets: dict[str, list[tuple[Path, int, str | None]]] = {
            "small": [], "medium": [], "large": [],
        }
        for entry in entries:
            bucket = "small" if entry[1] <= lo else "large" if entry[1] > hi else "medium"
            buckets[bucket].append(entry)

        for items in buckets.values():
            items.sort(key=lambda x: (0 if not x[2] else 1, x[2] or "", x[0].stem))

        balanced: list[Path] = []
        while any(buckets.values()):
            for key in ("small", "medium", "large"):
                if buckets[key]:
                    balanced.append(buckets[key].pop(0)[0])
        return balanced

    # ------------------------------------------------------------------
    # JSONL merge
    # ------------------------------------------------------------------

    def _load_existing_relationships(
        self, shard_dir: Path,
    ) -> dict[tuple[str, str, str, str], AggregatedRelationship]:
        """Load existing relationships from the shard directory for merging.

        Args:
            shard_dir: Directory holding the sharded dataset.  When it contains
                no shards the pre-sharding single-file dataset is read instead,
                so a checkout that predates the split still merges rather than
                starting from an empty set.

        Returns:
            Relationship map keyed by (source, target, hostname, type).
        """
        existing: dict[tuple[str, str, str, str], AggregatedRelationship] = {}

        for row in relationship_shards.iter_rows(
            shard_dir, legacy_path=LEGACY_RELATIONSHIP_JSONL
        ):
            key = (
                row["source_domain"],
                row["target_domain"],
                row["target_hostname"],
                row["relationship_type"],
            )
            existing[key] = AggregatedRelationship(
                source_domain=row["source_domain"],
                target_domain=row["target_domain"],
                target_hostname=row["target_hostname"],
                relationship_type=row["relationship_type"],
                target_category=row.get("target_category", "unknown_external"),
                # Rows written before source_page_urls existed carry only a
                # count, which cannot be merged into; they restart their tally
                # the first time the scanner revisits one of their pages.
                source_pages=set(row.get("source_page_urls", [])),
                observations=row.get("observations", 1),
                page_regions=set(row.get("page_regions", [])),
                first_seen=row.get("first_seen", ""),
                last_seen=row.get("last_seen", ""),
            )
        return existing

    def _merge_new_relationships(
        self,
        existing: dict[tuple[str, str, str, str], AggregatedRelationship],
        new_edges: list[tuple[Any, str]],
    ) -> dict[tuple[str, str, str, str], AggregatedRelationship]:
        """Merge new edges into the existing relationship map.

        Args:
            existing: Current relationship map (loaded from JSONL).
            new_edges: List of (RelationshipEdge, source_url) tuples from
                       the current scan batch.

        Returns:
            Updated relationship map.
        """
        now = datetime.now(timezone.utc).isoformat()

        for edge, source_url in new_edges:
            key = _rel_key(edge)
            if key in existing:
                agg = existing[key]
                agg.source_pages.add(source_url)
                agg.observations += 1
                agg.page_regions.add(edge.page_region)
                if now < agg.first_seen:
                    agg.first_seen = now
                if now > agg.last_seen:
                    agg.last_seen = now
            else:
                existing[key] = AggregatedRelationship(
                    source_domain=edge.source_domain,
                    target_domain=edge.target_domain,
                    target_hostname=edge.target_hostname,
                    relationship_type=edge.relationship_type,
                    target_category=edge.target_category,
                    source_pages={source_url},
                    observations=1,
                    page_regions={edge.page_region},
                    first_seen=now,
                    last_seen=now,
                )
        return existing

    def _write_jsonl(
        self,
        relationships: dict[tuple[str, str, str, str], AggregatedRelationship],
        shard_dir: Path,
    ) -> None:
        """Write the full relationship map out as a sharded dataset.

        The dataset is committed to the repository so GitHub Pages can serve it,
        which puts it under GitHub's 100 MiB per-file ceiling.  Splitting it
        across per-TLD shards keeps every file well clear of that limit as the
        dataset grows.  See :mod:`src.lib.relationship_shards`.

        Args:
            relationships: Relationship map to publish.
            shard_dir: Destination directory for the shards.
        """
        index = relationship_shards.write_rows(
            (agg.to_dict() for agg in relationships.values()), shard_dir
        )

        # The single-file dataset this replaced would otherwise linger in a
        # working copy and keep being served alongside the shards.
        if LEGACY_RELATIONSHIP_JSONL.is_file():
            LEGACY_RELATIONSHIP_JSONL.unlink()

        largest = max((entry["bytes"] for entry in index["shards"]), default=0)
        print(
            f"Wrote {index['total_rows']} relationships across "
            f"{len(index['shards'])} shard(s); largest {largest / 1048576:.1f} MiB"
        )

    # ------------------------------------------------------------------
    # Summary generation (browser-optimised)
    # ------------------------------------------------------------------

    def _build_country_summary(
        self,
        country_code: str,
        relationships: dict[tuple[str, str, str, str], AggregatedRelationship],
    ) -> dict:
        """Build a pre-aggregated summary for one country."""
        country_rels = {
            k: v for k, v in relationships.items()
            if v.source_domain.endswith(
                _tld_for_country(country_code)
            )
        }

        # Top source domains by relationship count
        src_counts: dict[str, int] = defaultdict(int)
        for agg in country_rels.values():
            src_counts[agg.source_domain] += agg.observations
        top_sources = sorted(src_counts.items(), key=lambda x: -x[1])[:50]

        # Top target domains
        tgt_counts: dict[str, int] = defaultdict(int)
        for agg in country_rels.values():
            tgt_counts[agg.target_domain] += agg.observations
        top_targets = sorted(tgt_counts.items(), key=lambda x: -x[1])[:50]

        # Type breakdown
        type_counts: dict[str, int] = defaultdict(int)
        for agg in country_rels.values():
            type_counts[agg.relationship_type] += 1

        return {
            "country_code": country_code,
            "total_relationships": len(country_rels),
            "total_source_domains": len(src_counts),
            "top_source_domains": [
                {"domain": d, "count": c} for d, c in top_sources
            ],
            "top_target_domains": [
                {"domain": d, "count": c} for d, c in top_targets
            ],
            "relationship_types": dict(type_counts),
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

    def _write_summaries(
        self,
        relationships: dict[tuple[str, str, str, str], AggregatedRelationship],
        countries: list[str],
    ) -> None:
        """Write per-country summary files and index."""
        SUMMARIES_DIR.mkdir(parents=True, exist_ok=True)

        index: dict[str, dict] = {}
        for cc in countries:
            summary = self._build_country_summary(cc, relationships)
            out = SUMMARIES_DIR / f"{cc.lower()}.json"
            with out.open("w", encoding="utf-8") as f:
                json.dump(summary, f, ensure_ascii=False, indent=2)
            index[cc] = {
                "total_relationships": summary["total_relationships"],
                "total_source_domains": summary["total_source_domains"],
                "file": f"{cc.lower()}.json",
            }

        with (SUMMARIES_DIR / "index.json").open("w", encoding="utf-8") as f:
            json.dump(index, f, ensure_ascii=False, indent=2)

    # ------------------------------------------------------------------
    # Coverage report
    # ------------------------------------------------------------------

    def _build_coverage_report(
        self,
        countries: list[str],
        toon_dir: Path,
    ) -> dict:
        """Build a coverage report for all countries."""
        report: dict[str, dict] = {}
        conn = sqlite3.connect(self.db_path)
        try:
            for cc in countries:
                toon_file = toon_dir / f"{country_filename_to_code(cc).lower()}.toon"
                if not toon_file.exists():
                    report[cc] = {"error": "TOON file not found"}
                    continue

                toon_data = self._load_toon_file(toon_file)
                all_urls = self._extract_urls_from_toon(toon_data)

                rows = conn.execute(
                    """
                    SELECT url, status, last_successful_at, failure_count
                    FROM relationship_scan_state
                    WHERE url IN ({ph})
                    """.format(ph=",".join("?" * len(all_urls))),
                    all_urls,
                ).fetchall()

                state_map = {r[0]: r for r in rows}
                attempted = 0
                successful = 0
                failed = 0
                skipped = 0
                never_scanned = 0
                stale = 0

                cutoff_28d = (
                    datetime.now(timezone.utc) - timedelta(days=DEFAULT_SCAN_WINDOW_DAYS)
                ).isoformat()

                for url in all_urls:
                    state = state_map.get(url)
                    if state is None:
                        never_scanned += 1
                        continue
                    attempted += 1
                    if state[1] == "completed":
                        successful += 1
                        if state[2] and state[2] < cutoff_28d:
                            stale += 1
                    elif state[1] == "failed":
                        failed += 1
                    else:
                        skipped += 1

                report[cc] = {
                    "total_urls": len(all_urls),
                    "attempted": attempted,
                    "successful": successful,
                    "failed": failed,
                    "skipped": skipped,
                    "never_scanned": never_scanned,
                    "stale_28d": stale,
                }
        finally:
            conn.close()
        return report

    # ------------------------------------------------------------------
    # Single-country scan
    # ------------------------------------------------------------------

    async def scan_country(
        self,
        country_code: str,
        toon_path: Path,
        rate_limit_per_second: float = 2.0,
        max_runtime_seconds: float | None = None,
        start_time: float | None = None,
        skip_recently_scanned_days: int = 0,
    ) -> dict[str, Any]:
        """Scan a country's URLs progressively and merge results."""
        scan_id = (
            f"rels-{country_code}-"
            f"{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}-"
            f"{uuid4().hex[:8]}"
        )

        print(f"Starting relationship scan {scan_id} for {country_code}")

        toon_data = self._load_toon_file(toon_path)
        all_urls = self._extract_urls_from_toon(toon_data)

        # Deterministic URL ordering (no set())
        all_urls_deduped = sorted(set(all_urls))
        print(f"Found {len(all_urls_deduped)} unique URLs to scan")

        # Get eligible URLs and boost hub domains
        eligible = self._get_eligible_urls(
            country_code, all_urls_deduped, skip_recently_scanned_days,
        )
        eligible = self._sort_by_hub_tier(eligible)
        urls = [e.url for e in eligible]
        print(
            f"Eligible URLs: {len(urls)} "
            f"(skipped {len(all_urls_deduped) - len(urls)} recently scanned or in backoff)"
        )

        if not urls:
            print("Nothing to scan for this country")
            return {
                "scan_id": scan_id,
                "country_code": country_code,
                "total_urls": len(all_urls_deduped),
                "urls_scanned": 0,
                "urls_skipped": len(all_urls_deduped),
                "is_complete": True,
                "relationships_extracted": 0,
                "unique_edges": 0,
            }

        _start = start_time if start_time is not None else time.monotonic()

        # Load existing relationships for incremental merge
        existing = self._load_existing_relationships(RELATIONSHIP_SHARD_DIR)
        new_edges: list[tuple[Any, str]] = []
        scanned_urls: list[str] = []

        def _on_result(result: MultiScanResult) -> None:
            scan_start = time.monotonic()
            success = result.is_reachable and result.relationships is not None
            rel_count = 0
            error_msg = result.error_message
            status_code = None

            if result.relationships and result.relationships.relationships:
                rel_count = len(result.relationships.relationships)
                for edge in result.relationships.relationships:
                    new_edges.append((edge, result.url))

            # Update metadata
            self._update_scan_state(
                url=result.url,
                country_code=country_code,
                source_domain=_registered_domain_from_url(result.url),
                scan_id=scan_id,
                success=success,
                scan_duration_ms=int((time.monotonic() - scan_start) * 1000),
            )

            # Save individual scan result
            self._save_scan_result(
                url=result.url,
                country_code=country_code,
                scan_id=scan_id,
                source_domain=_registered_domain_from_url(result.url),
                source_url=result.url,
                relationships_found=rel_count,
                scan_duration_ms=int((time.monotonic() - scan_start) * 1000),
                is_reachable=result.is_reachable,
                error_message=error_msg,
                status_code=status_code,
            )

            scanned_urls.append(result.url)

        scan_results = await self.scanner.scan_urls_batch(
            urls,
            rate_limit_per_second=rate_limit_per_second,
            max_runtime_seconds=max_runtime_seconds,
            start_time=_start,
            on_result=_on_result,
        )

        # Merge and write
        merged = self._merge_new_relationships(existing, new_edges)
        self._write_jsonl(merged, RELATIONSHIP_SHARD_DIR)

        scanned_count = len(scan_results)
        is_complete = scanned_count == len(urls)

        print(f"Scanned {scanned_count}/{len(urls)} URLs, "
              f"found {len(new_edges)} new relationship observations")
        print(f"Total relationships after merge: {len(merged)}")

        return {
            "scan_id": scan_id,
            "country_code": country_code,
            "total_urls": len(all_urls_deduped),
            "urls_scanned": scanned_count,
            "urls_skipped": len(all_urls_deduped) - scanned_count,
            "is_complete": is_complete,
            "relationships_extracted": len(new_edges),
            "unique_edges": len(merged),
        }

    # ------------------------------------------------------------------
    # All-countries scan
    # ------------------------------------------------------------------

    async def scan_all_countries(
        self,
        toon_seeds_dir: Path,
        rate_limit_per_second: float = 2.0,
        max_runtime_seconds: float | None = None,
        skip_recently_scanned_days: int = 0,
    ) -> list[dict[str, Any]]:
        """Scan all countries progressively with fairness ordering."""
        all_stats: list[dict[str, Any]] = []

        toon_files = self._build_balanced_country_order(
            iter_seed_toon_files(toon_seeds_dir)
        )
        countries = [country_filename_to_code(p.stem) for p in toon_files]
        print(f"Found {len(toon_files)} TOON files to process")

        start_time = time.monotonic()
        _country_buffer = 5 * 60  # 5 min safety margin

        for toon_path in toon_files:
            country_code = country_filename_to_code(toon_path.stem)

            if max_runtime_seconds is not None:
                elapsed = time.monotonic() - start_time
                remaining = max_runtime_seconds - elapsed
                if remaining < _country_buffer:
                    print(
                        f"Time budget near limit "
                        f"({elapsed / 60:.1f}m elapsed, "
                        f"{remaining / 60:.1f}m remaining) "
                        f"— stopping before {country_code}"
                    )
                    break

            try:
                stats = await self.scan_country(
                    country_code,
                    toon_path,
                    rate_limit_per_second=rate_limit_per_second,
                    max_runtime_seconds=max_runtime_seconds,
                    start_time=start_time,
                    skip_recently_scanned_days=skip_recently_scanned_days,
                )
                all_stats.append(stats)
            except Exception as exc:
                print(f"Error scanning {country_code}: {exc}")
                all_stats.append({"country_code": country_code, "error": str(exc)})

        # Write summaries and coverage report
        if all_stats:
            successful_countries = [
                s["country_code"] for s in all_stats if "error" not in s
            ]
            if successful_countries:
                existing = self._load_existing_relationships(RELATIONSHIP_SHARD_DIR)
                self._write_summaries(existing, successful_countries)

            coverage = self._build_coverage_report(countries, toon_seeds_dir)
            coverage_path = Path("docs/data/coverage_report.json")
            coverage_path.parent.mkdir(parents=True, exist_ok=True)
            with coverage_path.open("w", encoding="utf-8") as f:
                json.dump(coverage, f, ensure_ascii=False, indent=2)
            print(f"Coverage report written to {coverage_path}")

        return all_stats


# ---------------------------------------------------------------------------
# Country TLD helper (for summary filtering)
# ---------------------------------------------------------------------------

_TLD_MAP: dict[str, str] = {
    "ICELAND": ".is",
    "FRANCE": ".fr",
    "GERMANY": ".de",
    "UNITED_KINGDOM": ".uk",
    "IRELAND": ".ie",
    "SPAIN": ".es",
    "PORTUGAL": ".pt",
    "ITALY": ".it",
    "NETHERLANDS": ".nl",
    "BELGIUM": ".be",
    "AUSTRIA": ".at",
    "SWITZERLAND": ".ch",
    "NORWAY": ".no",
    "SWEDEN": ".se",
    "FINLAND": ".fi",
    "DENMARK": ".dk",
    "POLAND": ".pl",
    "CZECHIA": ".cz",
    "SLOVAKIA": ".sk",
    "HUNGARY": ".hu",
    "ROMANIA": ".ro",
    "BULGARIA": ".bg",
    "CROATIA": ".hr",
    "SLOVENIA": ".si",
    "ESTONIA": ".ee",
    "LATVIA": ".lv",
    "LITHUANIA": ".lt",
    "CYPRUS": ".cy",
    "MALTA": ".mt",
    "LUXEMBOURG": ".lu",
    "GREECE": ".gr",
    "EU_INSTITUTIONS": ".eu",
}


def _tld_for_country(country_code: str) -> str:
    return _TLD_MAP.get(country_code, "")
