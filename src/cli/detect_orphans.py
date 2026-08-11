"""Orphan detection: flag seed domains not seen in relationship scanning.

Compares the full seed domain inventory against the relationship scan data
to identify domains that are:
- ACTIVE: found as targets in recent relationship scans
- ORPHAN: in seeds but never linked from any scanned government site
- STALE: previously active but no longer appearing in relationships

This data feeds back into the scanner to:
1. Prioritize active hub domains for scanning
2. Surface orphan domains for manual review
3. Detect domain death/redirect
"""

from __future__ import annotations

import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

from src.lib import relationship_shards
from src.lib.country_utils import iter_seed_toon_files


PRIORITIZATION_PATH = Path("docs/data/gov-domain-prioritization.json")
ORPHAN_REPORT_PATH = Path("docs/data/orphan-domains-report.json")
RELATIONSHIP_SHARD_DIR = Path("docs/data/relationships")
LEGACY_RELATIONSHIP_JSONL = Path("docs/data/relationships.jsonl")


def load_seed_domains(toon_dir: Path) -> dict[str, set[str]]:
    """Load all seed domains from TOON files, keyed by country name."""
    seed_by_country: dict[str, set[str]] = defaultdict(set)
    for toon_file in iter_seed_toon_files(toon_dir):
        with toon_file.open(encoding="utf-8") as f:
            data = json.load(f)
        country = data.get("country", toon_file.stem)
        for d in data.get("domains", []):
            cdn = d.get("canonical_domain")
            if cdn:
                seed_by_country[country].add(cdn.lower())
            for p in d.get("pages", []):
                host = urlparse(p.get("url", "")).hostname
                if host:
                    parts = host.split(".")
                    if len(parts) >= 2:
                        seed_by_country[country].add(
                            ".".join(parts[-2:]).lower()
                        )
    return seed_by_country


def load_swh_domains(swh_path: Path) -> dict[str, set[str]]:
    """Load Software Heritage domain inventory."""
    if not swh_path.exists():
        return {}
    with swh_path.open(encoding="utf-8") as f:
        data = json.load(f)
    result: dict[str, set[str]] = defaultdict(set)
    for name, info in data.get("countries", {}).items():
        for domain in info.get("domains", []):
            result[name].add(domain.lower())
    return result


def load_relationship_targets(
    shard_dir: Path,
) -> dict[str, set[str]]:
    """Load all government target domains from the relationship dataset.

    Args:
        shard_dir: Directory holding the sharded relationship dataset.  A
            checkout that predates the split falls back to the single-file
            dataset automatically.

    Returns:
        Mapping of target_domain -> set of source_domains linking to it.
    """
    tgt_sources: dict[str, set[str]] = defaultdict(set)
    for row in relationship_shards.iter_rows(
        shard_dir, legacy_path=LEGACY_RELATIONSHIP_JSONL
    ):
        if row.get("target_category") != "known_government":
            continue
        tgt_sources[row["target_domain"]].add(row["source_domain"])
    return tgt_sources


def detect_orphans(
    toon_dir: Path = Path("data/toon-seeds/countries"),
    swh_path: Path = Path("data/imports/swh_gov_domains_import.json"),
    shard_dir: Path = RELATIONSHIP_SHARD_DIR,
    domain_to_country: dict[str, str] | None = None,
) -> dict:
    """Run orphan detection and return report.

    Args:
        toon_dir: Directory containing TOON seed files.
        swh_path: Path to Software Heritage import JSON.
        shard_dir: Directory holding the sharded relationship dataset.
        domain_to_country: Mapping of source domain -> country name.

    Returns:
        Report dict with per-country orphan analysis.
    """
    seeds = load_seed_domains(toon_dir)
    swh = load_swh_domains(swh_path)

    # Merge SWH into seeds
    for name, domains in swh.items():
        seeds[name].update(domains)

    tgt_sources = load_relationship_targets(shard_dir)

    # Build reverse mapping if not provided
    if domain_to_country is None:
        d2c_path = Path("/tmp/domain_to_country.json")
        if d2c_path.exists():
            with d2c_path.open() as f:
                domain_to_country = json.load(f)
        else:
            domain_to_country = {}

    report: dict[str, dict] = {}
    for country_name in sorted(seeds.keys()):
        country_seeds = seeds[country_name]

        # Find targets linked from this country's scanned domains
        scanned = {
            d for d, c in domain_to_country.items() if c == country_name
        }

        active: set[str] = set()
        for tgt, sources in tgt_sources.items():
            if any(s in scanned for s in sources):
                active.add(tgt)

        orphans = country_seeds - active - scanned

        # Categorize orphans
        subdomains = set()
        staging = set()
        likely_dead = set()
        other_orphans = set()

        for domain in orphans:
            parts = domain.split(".")
            if len(parts) > 3:
                subdomains.add(domain)
            elif any(
                kw in domain
                for kw in ["test", "staging", "dev", "demo", "old", "backup"]
            ):
                staging.add(domain)
            elif len(parts) == 2 and parts[1] in {
                "gov", "gouv", "gob", "gv",
            }:
                likely_dead.add(domain)
            else:
                other_orphans.add(domain)

        report[country_name] = {
            "seed_count": len(country_seeds),
            "active_count": len(active),
            "orphan_count": len(orphans),
            "active_rate": round(len(active) / max(len(country_seeds), 1) * 100, 1),
            "active_domains": sorted(active)[:20],
            "orphan_breakdown": {
                "subdomains": len(subdomains),
                "staging_test": len(staging),
                "likely_dead": len(likely_dead),
                "other": len(other_orphans),
            },
            "orphan_sample": sorted(other_orphans)[:10],
            "staging_sample": sorted(staging)[:5],
        }

    return report


def write_report(report: dict, output_path: Path = ORPHAN_REPORT_PATH) -> None:
    """Write orphan detection report to JSON."""
    output = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "description": (
            "Orphan domain detection report. Compares seed domain inventory "
            "against relationship scan data to find domains not linked from "
            "any scanned government site."
        ),
        "countries": report,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)


def main() -> None:
    """Run orphan detection and print summary."""
    report = detect_orphans()
    write_report(report)

    total_seeds = sum(c["seed_count"] for c in report.values())
    total_active = sum(c["active_count"] for c in report.values())
    total_orphans = sum(c["orphan_count"] for c in report.values())

    print(f"Orphan detection complete: {ORPHAN_REPORT_PATH}")
    print(f"  Total seed domains: {total_seeds}")
    print(f"  Active (linked):    {total_active} ({total_active*100//max(total_seeds,1)}%)")
    print(f"  Orphans:            {total_orphans}")

    print("\nPer-country breakdown:")
    for country in sorted(report.keys()):
        c = report[country]
        if c["orphan_count"] > 0:
            print(
                f"  {country:30s}  seeds={c['seed_count']:5d}  "
                f"active={c['active_count']:4d} ({c['active_rate']:4.1f}%)  "
                f"orphans={c['orphan_count']:5d}"
            )


if __name__ == "__main__":
    main()
