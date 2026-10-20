"""CLI tool to generate the user-preferences + design-systems stats page.

Queries the metadata database for user-preference scan signals (EN 301 549
clause 9.7 evidence: ``prefers-color-scheme``, ``prefers-reduced-motion``,
``prefers-contrast``, ``prefers-reduced-transparency``, ``forced-colors``,
the ``color-scheme`` property, ``forced-color-adjust: none`` override risk)
and design-system adoption, then:

- updates ``docs/user-preferences.md`` between
  ``<!-- USER_PREFERENCES_STATS_START -->`` and
  ``<!-- USER_PREFERENCES_STATS_END -->`` markers,
- writes ``docs/user-preferences-data.json`` with a ``by_url`` array,
- writes ``docs/user-preferences-data.csv`` (UTF-8 BOM, one row per URL).

Every aggregate in the Markdown page and the JSON ``summary`` is computed
from the merged per-URL records that also populate ``by_url``, so a reader
can independently recompute the published counts by grouping the ``by_url``
rows (AGENTS.md, "Independent Verification").  The JSON/CSV files are
workflow artifacts rather than committed files.

**Interpretation limit:** these are signals of effort, not conformance
verdicts.  Clause 9.7 is a "do not block or override" rule; absence of a
media query is not a failure, and presence of one is not a pass.
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import sqlite3
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

from src.cli._report_common import count_toon_seed_urls
from src.lib.country_utils import country_code_to_display_name
from src.lib.design_system_registry import DesignSystemRegistry
from src.lib.settings import load_settings
from src.services.preference_scanner import PREFERENCE_FEATURES

# ---------------------------------------------------------------------------
# HTML comment markers
# ---------------------------------------------------------------------------

_STATS_MARKER_START = "<!-- USER_PREFERENCES_STATS_START -->"
_STATS_MARKER_END = "<!-- USER_PREFERENCES_STATS_END -->"

# Table label for each detected feature, in report order.
_FEATURE_LABELS: list[tuple[str, str]] = [
    ("prefers-color-scheme", "Dark/light colour scheme (`prefers-color-scheme`)"),
    ("color-scheme", "Declared colour scheme (`color-scheme`)"),
    ("prefers-reduced-motion", "Reduced motion (`prefers-reduced-motion`)"),
    ("prefers-contrast", "Increased contrast (`prefers-contrast`)"),
    ("prefers-reduced-transparency", "Reduced transparency (`prefers-reduced-transparency`)"),
    ("forced-colors", "Forced colours / high contrast (`forced-colors`)"),
]

_METHOD_NOTE = (
    "Signals are collected from the page HTML (inline styles, "
    "`<meta name=\"color-scheme\">`, `matchMedia` scripts) and from fetched "
    "stylesheets (capped per page; shared CSS is cached). They are evidence "
    "of effort, **not** EN 301 549 clause 9.7 conformance: a page with no "
    "media query can still comply, and a page with one can still break in "
    "forced-colours mode. Only manual testing can clear a site."
)

_CSV_FIELDNAMES = [
    "country_code",
    "url",
    "domain",
    "is_reachable",
    "meta_color_scheme",
    "features",
    "override_signals",
    "design_systems",
    "theme_toggle_hints",
    "stylesheets_checked",
    "stylesheets_total",
    "prefers-color-scheme",
    "prefers-reduced-motion",
    "prefers-contrast",
    "prefers-reduced-transparency",
    "forced-colors",
    "color-scheme",
    "forced-color-adjust-none",
    "last_scanned",
]


# ---------------------------------------------------------------------------
# Database helpers
# ---------------------------------------------------------------------------

def _parse_json_list(raw: str | None) -> list[str]:
    """Return a string list parsed from a JSON column value."""
    if not raw:
        return []
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return []
    return [item for item in parsed if isinstance(item, str)] if isinstance(parsed, list) else []


def _parse_json_dict(raw: str | None) -> dict:
    """Return a dict parsed from a JSON column value (empty on failure)."""
    if not raw:
        return {}
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return {}
    return parsed if isinstance(parsed, dict) else {}


def _hostname_from_url(url: str) -> str:
    """Return the hostname portion of a URL, or an empty string on failure."""
    try:
        return urlparse(url).hostname or ""
    except ValueError:
        return ""


def _initial_page_record(row: sqlite3.Row) -> dict[str, object]:
    """Return the initial merged record for a URL's first scan row."""
    return {
        "url": row["url"],
        "country_code": row["country_code"],
        "domain": _hostname_from_url(row["url"]),
        "is_reachable": bool(row["is_reachable"]),
        "meta_color_scheme": row["meta_color_scheme"],
        "features": set(_parse_json_list(row["features"])),
        "feature_sources": _merge_sources({}, _parse_json_dict(row["feature_sources"])),
        "theme_toggle_hints": set(_parse_json_list(row["theme_toggle_hints"])),
        "override_signals": set(_parse_json_list(row["override_signals"])),
        "design_systems": set(_parse_json_list(row["design_systems"])),
        "stylesheets_checked": int(row["stylesheets_checked"] or 0),
        "stylesheets_total": int(row["stylesheets_total"] or 0),
        "error_message": row["error_message"] or "",
        "last_scanned": row["scanned_at"],
    }


def _merge_sources(existing: dict, incoming: dict) -> dict:
    """Merge two feature_sources dicts, keeping the per-origin maximum.

    Occurrence counts are kept at their per-scan maximum rather than summed,
    so a URL re-scanned three times does not report three times the evidence.
    """
    merged: dict[str, dict[str, int]] = {
        feature: dict(counts) for feature, counts in existing.items()
    }
    for feature, counts in incoming.items():
        if not isinstance(counts, dict):
            continue
        target = merged.setdefault(str(feature), {})
        for origin, count in counts.items():
            if not isinstance(count, int):
                continue
            target[str(origin)] = max(target.get(str(origin), 0), count)
    return merged


def _merge_page_record(record: dict[str, object], row: sqlite3.Row) -> None:
    """Merge another scan row for the same URL into *record* (in place)."""
    record["is_reachable"] = bool(record["is_reachable"]) or bool(row["is_reachable"])
    for key in ("features", "theme_toggle_hints", "override_signals", "design_systems"):
        record[key] = set(record[key]) | set(_parse_json_list(row[key]))
    record["feature_sources"] = _merge_sources(
        record["feature_sources"], _parse_json_dict(row["feature_sources"])
    )
    if row["meta_color_scheme"]:
        record["meta_color_scheme"] = row["meta_color_scheme"]
    record["stylesheets_checked"] = max(
        int(record["stylesheets_checked"]), int(row["stylesheets_checked"] or 0)
    )
    record["stylesheets_total"] = max(
        int(record["stylesheets_total"]), int(row["stylesheets_total"] or 0)
    )
    if row["error_message"]:
        record["error_message"] = row["error_message"]
    scanned_at = row["scanned_at"]
    if scanned_at and (not record["last_scanned"] or str(scanned_at) > str(record["last_scanned"])):
        record["last_scanned"] = scanned_at


def _load_page_records(conn: sqlite3.Connection) -> list[dict[str, object]]:
    """Return one merged record per URL across all scan batches.

    Rows are read in scan order and merged so that every aggregate in the
    report derives from exactly the same per-URL records the JSON ``by_url``
    array carries.
    """
    rows = conn.execute(
        """
        SELECT url, country_code, is_reachable, meta_color_scheme, features,
               feature_sources, theme_toggle_hints, override_signals,
               design_systems, stylesheets_checked, stylesheets_total,
               error_message, scanned_at
        FROM url_preference_results
        ORDER BY country_code, url, scanned_at ASC
        """
    ).fetchall()

    records: dict[tuple[str, str], dict[str, object]] = {}
    for row in rows:
        key = (row["country_code"], row["url"])
        if key not in records:
            records[key] = _initial_page_record(row)
        else:
            _merge_page_record(records[key], row)
    return sorted(records.values(), key=lambda r: (str(r["country_code"]), str(r["url"])))


# ---------------------------------------------------------------------------
# Aggregation (all derived from the merged per-URL records)
# ---------------------------------------------------------------------------

def _aggregate(records: list[dict[str, object]]) -> dict:
    """Return corpus-level totals, feature counts, and adoption counts."""
    feature_counts: Counter[str] = Counter()
    adoption_counts: Counter[str] = Counter()
    for record in records:
        for feature in record["features"]:
            feature_counts[feature] += 1
        for system in record["design_systems"]:
            adoption_counts[system] += 1

    reachable = [r for r in records if r["is_reachable"]]
    return {
        "total_scanned": len(records),
        "total_reachable": len(reachable),
        "total_css_checked": sum(1 for r in records if r["stylesheets_checked"] > 0),
        "total_with_signals": sum(1 for r in records if r["features"]),
        "total_with_override_risk": sum(1 for r in records if r["override_signals"]),
        "total_with_design_system": sum(1 for r in records if r["design_systems"]),
        "feature_counts": dict(feature_counts),
        "adoption_counts": dict(adoption_counts),
    }


def _aggregate_by_country(records: list[dict[str, object]]) -> list[dict]:
    """Return per-country aggregates computed the same way as the total."""
    grouped: dict[str, list[dict[str, object]]] = defaultdict(list)
    for record in records:
        grouped[str(record["country_code"])].append(record)

    by_country: list[dict] = []
    for country_code in sorted(grouped):
        country_records = grouped[country_code]
        agg = _aggregate(country_records)
        agg["country_code"] = country_code
        by_country.append(agg)
    return by_country


def _registry_adoption(
    registry: DesignSystemRegistry,
    records: list[dict[str, object]],
) -> list[dict]:
    """Return curated entries with their page-level adoption counts."""
    adoption: list[dict] = []
    for system in registry.all_systems():
        pages_matched = sum(1 for r in records if system.name in r["design_systems"])
        adoption.append(
            {
                "name": system.name,
                "country_code": system.country_code,
                "type": system.type,
                "scope": system.scope,
                "url": system.url,
                "confidence": system.confidence,
                "needs_review": system.needs_review,
                "has_signatures": system.has_signatures,
                "adoption_signatures": list(system.adoption_signatures),
                "pages_matched": pages_matched,
            }
        )
    return adoption


def _serialize_record(record: dict[str, object]) -> dict:
    """Return a JSON-friendly copy of a merged per-URL record for ``by_url``."""
    return {
        "url": record["url"],
        "country_code": record["country_code"],
        "domain": record["domain"],
        "is_reachable": record["is_reachable"],
        "meta_color_scheme": record["meta_color_scheme"],
        "features": sorted(record["features"]),
        "feature_sources": record["feature_sources"],
        "theme_toggle_hints": sorted(record["theme_toggle_hints"]),
        "override_signals": sorted(record["override_signals"]),
        "design_systems": sorted(record["design_systems"]),
        "stylesheets_checked": record["stylesheets_checked"],
        "stylesheets_total": record["stylesheets_total"],
        "error_message": record["error_message"],
        "last_scanned": record["last_scanned"],
    }


def _write_csv(records: list[dict[str, object]], csv_path: Path) -> None:
    """Write per-URL preference signals to a UTF-8 BOM CSV file.

    One row per URL; the per-feature columns are booleans so a reader can
    recompute any published aggregate in a spreadsheet.
    """
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=_CSV_FIELDNAMES, lineterminator="\r\n")
    writer.writeheader()
    for record in records:
        features = set(record["features"])
        row = {
            "country_code": record["country_code"],
            "url": record["url"],
            "domain": record["domain"],
            "is_reachable": int(bool(record["is_reachable"])),
            "meta_color_scheme": record["meta_color_scheme"] or "",
            "features": "|".join(sorted(features)),
            "override_signals": "|".join(sorted(record["override_signals"])),
            "design_systems": "|".join(sorted(record["design_systems"])),
            "theme_toggle_hints": "|".join(sorted(record["theme_toggle_hints"])),
            "stylesheets_checked": record["stylesheets_checked"],
            "stylesheets_total": record["stylesheets_total"],
            "last_scanned": record["last_scanned"] or "",
        }
        for feature in PREFERENCE_FEATURES:
            row[feature] = int(feature in features)
        row["forced-color-adjust-none"] = int(bool(record["override_signals"]))
        writer.writerow(row)
    # Write UTF-8 BOM so Excel opens the file correctly without an import wizard.
    csv_path.write_bytes(b"\xef\xbb\xbf" + buf.getvalue().encode("utf-8"))


# ---------------------------------------------------------------------------
# Stats block builder
# ---------------------------------------------------------------------------

def _pct(num: int, denom: int) -> str:
    """Format *num*/*denom* as a percentage, or an em dash when undefined."""
    return f"{num / denom * 100:.1f}%" if denom else "—"


def _summary_lines(
    summary: dict,
    generated_at: str,
    total_available: int,
    last_scan: str | None,
    registry_coverage: dict[str, int],
) -> list[str]:
    """Return the headline coverage and signal lines."""
    scanned = summary.get("total_scanned", 0)
    reachable = summary.get("total_reachable", 0)
    lines = [
        _STATS_MARKER_START,
        "",
        f"_Stats as of {generated_at} — last scan: {(last_scan or '')[:10] or '—'}_",
        "",
        "**Browser user preferences and design-system adoption**",
        "",
    ]
    if total_available > 0:
        lines.append(
            f"**{scanned:,}** of **{total_available:,}** available pages scanned "
            f"(**{_pct(scanned, total_available)}** coverage)"
        )
    else:
        lines.append(f"**{scanned:,}** pages scanned")

    lines += [
        f"**{reachable:,}** of **{scanned:,}** scanned pages were reachable "
        f"(**{_pct(reachable, scanned)}**)",
        f"**{summary.get('total_css_checked', 0):,}** of **{reachable:,}** reachable "
        f"pages had at least one stylesheet checked (CSS tier: "
        f"**{_pct(summary.get('total_css_checked', 0), reachable)}**)",
        f"**{summary.get('total_with_signals', 0):,}** of **{reachable:,}** reachable "
        f"pages show at least one user-preference signal "
        f"(**{_pct(summary.get('total_with_signals', 0), reachable)}**)",
        f"Pages containing an explicit override (`forced-color-adjust: none`): "
        f"**{summary.get('total_with_override_risk', 0):,}** — a *risk signal* for "
        f"manual review under EN 301 549 clause 9.7, not a confirmed failure",
        f"Pages matching the HTML signatures of a curated design system: "
        f"**{summary.get('total_with_design_system', 0):,}**",
        "",
        f"> Registry coverage: **{registry_coverage.get('with_adoption_signatures', 0)}** "
        f"of **{registry_coverage.get('total', 0)}** curated design-system entries "
        f"have confirmed adoption signatures "
        f"(**{registry_coverage.get('needs_review', 0)}** entries still need review). "
        f"Systems without signatures cannot yet be measured for adoption.",
        "",
    ]
    return lines


def _feature_lines(feature_counts: dict[str, int], reachable: int) -> list[str]:
    """Return the per-feature detection table."""
    lines = [
        "---",
        "",
        "## Signals detected",
        "",
        "| Signal | Pages | % of reachable |",
        "|--------|------:|---------------:|",
    ]
    for feature, label in _FEATURE_LABELS:
        count = feature_counts.get(feature, 0)
        lines.append(f"| {label} | {count:,} | {_pct(count, reachable)} |")
    lines += [
        "",
        "Counts are pages where the signal appeared in the page HTML **or** a "
        "fetched stylesheet. Attribution (HTML vs first-party CSS vs "
        "third-party CSS) is in the JSON ``feature_sources`` field.",
    ]
    return lines


def _system_lines(adoption: list[dict], summary: dict) -> list[str]:
    """Return the design-system registry + adoption table."""
    lines = [
        "",
        "---",
        "",
        "## Design systems and adoption",
        "",
        "| Design system | Country | Type | Signatures | Pages matched |",
        "|---------------|---------|------|-----------:|--------------:|",
    ]
    for entry in adoption:
        country = country_code_to_display_name(entry["country_code"]) if entry["country_code"] else "—"
        sig = "✓" if entry["has_signatures"] else "not curated"
        review = " ⚠" if entry["needs_review"] else ""
        lines.append(
            f"| [{entry['name']}]({entry['url']}){review} | {country} | "
            f"{entry['type']} | {sig} | {entry['pages_matched']:,} |"
        )
    lines += [
        "",
        "**Pages matched** is the number of scanned pages whose HTML contains "
        "that system's adoption signatures (class prefixes, asset paths). It "
        "measures footprint on the pages in this corpus only — systems are "
        "adopted outside these domains too, and an empty signature list means "
        "adoption is not yet measurable for that entry.",
        "",
        "⚠ = entry flagged for review (confidence below high or an unconfirmed "
        "classification). Registry source: "
        "[`data/design-systems.yaml`](https://github.com/mgifford/eu-plus-government-scans/blob/main/data/design-systems.yaml).",
    ]
    return lines


def _country_lines(by_country: list[dict], seed_counts: dict[str, int]) -> list[str]:
    """Return the per-country breakdown table."""
    lines = [
        "",
        "---",
        "",
        "## User-preference signals by country",
        "",
        "| Country | Scanned | Available | Reachable | CSS checked | Signal pages | Signal % | Dark scheme | Reduced motion | Forced colours | Override risk | Design-system pages |",
        "|---------|--------:|----------:|----------:|------------:|-------------:|---------:|------------:|---------------:|---------------:|--------------:|--------------------:|",
    ]
    totals: Counter[str] = Counter()
    for row in by_country:
        cc = row["country_code"]
        available = seed_counts.get(cc, 0)
        features = row["feature_counts"]
        signal_pct = _pct(row["total_with_signals"], row["total_reachable"])
        lines.append(
            f"| {country_code_to_display_name(cc)} | {row['total_scanned']:,} | "
            f"{available:,} | {row['total_reachable']:,} | {row['total_css_checked']:,} | "
            f"{row['total_with_signals']:,} | {signal_pct} | "
            f"{features.get('prefers-color-scheme', 0):,} | "
            f"{features.get('prefers-reduced-motion', 0):,} | "
            f"{features.get('forced-colors', 0):,} | "
            f"{row['total_with_override_risk']:,} | "
            f"{row['total_with_design_system']:,} |"
        )
        for key in (
            "total_scanned", "total_reachable", "total_css_checked",
            "total_with_signals", "total_with_override_risk",
            "total_with_design_system",
        ):
            totals[key] += row[key]
    for feature in ("prefers-color-scheme", "prefers-reduced-motion", "forced-colors"):
        totals[feature] += sum(r["feature_counts"].get(feature, 0) for r in by_country)

    signal_pct = _pct(totals["total_with_signals"], totals["total_reachable"])
    lines.append(
        f"| **Total** | **{totals['total_scanned']:,}** | "
        f"**{sum(seed_counts.values()):,}** | **{totals['total_reachable']:,}** | "
        f"**{totals['total_css_checked']:,}** | **{totals['total_with_signals']:,}** | "
        f"**{signal_pct}** | **{totals['prefers-color-scheme']:,}** | "
        f"**{totals['prefers-reduced-motion']:,}** | **{totals['forced-colors']:,}** | "
        f"**{totals['total_with_override_risk']:,}** | "
        f"**{totals['total_with_design_system']:,}** |"
    )
    return lines


def _build_stats_block(
    summary: dict,
    generated_at: str,
    total_available: int,
    by_country: list[dict],
    seed_counts: dict[str, int],
    feature_counts: dict[str, int],
    adoption: list[dict],
    registry_coverage: dict[str, int],
    last_scan: str | None,
) -> str:
    """Return the full Markdown stats block to inject between the markers."""
    if not summary or not summary.get("total_scanned"):
        return (
            f"{_STATS_MARKER_START}\n\n"
            "_No scan data yet — stats update automatically after every scan run._\n\n"
            f"{_STATS_MARKER_END}"
        )

    lines = _summary_lines(summary, generated_at, total_available, last_scan, registry_coverage)
    lines += _feature_lines(feature_counts, summary.get("total_reachable", 0))
    lines += _system_lines(adoption, summary)
    lines += _country_lines(by_country, seed_counts)
    lines += [
        "",
        "---",
        "",
        "## How to read these numbers",
        "",
        _METHOD_NOTE,
        "",
        "📥 Machine-readable results: "
        "[user-preferences-data.json](https://github.com/mgifford/eu-plus-government-scans/actions/workflows/generate-scan-progress.yml) "
        "(`by_url` carries one row per scanned URL so every aggregate above can "
        "be independently recomputed) and `user-preferences-data.csv` "
        "(same rows, one per URL, boolean columns per signal), both published "
        "as workflow artifacts.",
        "",
        "Context: [EN 301 549 clause 9.7 — user preferences for web pages]"
        "(https://www.webyes.com/blogs/en-301-549-user-preferences/).",
        "",
        _STATS_MARKER_END,
    ]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def generate_preference_report(
    db_path: Path,
    page_path: Path,
    data_path: Path,
    csv_path: Path,
    toon_seeds_dir: Path | None = None,
    registry_path: Path | None = None,
) -> bool:
    """Update *page_path* stats block and write the JSON and CSV data files.

    Args:
        db_path: Path to the SQLite metadata database.
        page_path: Path to the ``docs/user-preferences.md`` page.
        data_path: Output path for the JSON data file.
        csv_path: Output path for the CSV data file.
        toon_seeds_dir: Directory of ``*.toon`` seeds for coverage denominators.
        registry_path: Optional path to ``data/design-systems.yaml``.

    Returns:
        ``True`` on success, ``False`` when the markers are missing from
        *page_path* (the page is left unchanged in that case).
    """
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    registry = DesignSystemRegistry(registry_path)

    if not db_path.exists():
        records: list[dict[str, object]] = []
    else:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        try:
            records = _load_page_records(conn)
        finally:
            conn.close()

    summary = _aggregate(records)
    by_country = _aggregate_by_country(records)
    adoption = _registry_adoption(registry, records)
    registry_coverage = registry.coverage()
    last_scan = max((str(r["last_scanned"]) for r in records if r["last_scanned"]), default=None)

    seed_counts = count_toon_seed_urls(toon_seeds_dir) if toon_seeds_dir else {}
    total_available = sum(seed_counts.values())

    data_path.parent.mkdir(parents=True, exist_ok=True)
    data: dict = {
        "generated_at": generated_at,
        "method": {
            "tiers": ["html", "css"],
            "features": list(PREFERENCE_FEATURES),
            "override_property": "forced-color-adjust: none",
            "interpretation": _METHOD_NOTE,
        },
        "summary": {
            **summary,
            "total_batches": _count_batches(db_path),
            "total_available": total_available,
            "last_scan": last_scan,
        },
        "design_system_registry": {
            "coverage": registry_coverage,
            "entries": adoption,
        },
        "by_country": by_country,
        "by_url": [_serialize_record(r) for r in records],
    }
    data_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Data file written: {data_path}")

    _write_csv(records, csv_path)
    print(f"CSV file written: {csv_path}")

    if not page_path.exists():
        print(f"User-preferences page not found: {page_path}", file=sys.stderr)
        return False

    content = page_path.read_text(encoding="utf-8")
    start_idx = content.find(_STATS_MARKER_START)
    end_idx = content.find(_STATS_MARKER_END)
    if start_idx == -1 or end_idx == -1:
        print(
            f"Stats markers not found in {page_path}. "
            f"Add {_STATS_MARKER_START!r} and {_STATS_MARKER_END!r} to the file.",
            file=sys.stderr,
        )
        return False

    new_block = _build_stats_block(
        summary, generated_at, total_available, by_country, seed_counts,
        summary["feature_counts"], adoption, registry_coverage, last_scan,
    )
    new_content = (
        content[:start_idx]
        + new_block
        + content[end_idx + len(_STATS_MARKER_END):]
    )
    page_path.write_text(new_content, encoding="utf-8")
    print(f"User-preferences page updated: {page_path}")

    print("\n" + "=" * 60)
    print("USER-PREFERENCE STATS SUMMARY")
    print("=" * 60)
    reachable = summary["total_reachable"]
    print(f"Pages scanned     : {summary['total_scanned']:,}"
          + (f" / {total_available:,} available ({summary['total_scanned'] / total_available * 100:.1f}% coverage)"
             if total_available else ""))
    print(f"Reachable         : {reachable:,}")
    print(f"CSS tier checked  : {summary['total_css_checked']:,}")
    print(f"Signal pages      : {summary['total_with_signals']:,} "
          f"({_pct(summary['total_with_signals'], reachable)} of reachable)")
    print(f"Override risk     : {summary['total_with_override_risk']:,}")
    print(f"Design-system hit : {summary['total_with_design_system']:,}")
    print("=" * 60)
    return True


def _count_batches(db_path: Path) -> int:
    """Return the number of distinct scan batches in the database (0 if absent)."""
    if not db_path.exists():
        return 0
    conn = sqlite3.connect(db_path)
    try:
        row = conn.execute(
            "SELECT COUNT(DISTINCT scan_id) FROM url_preference_results"
        ).fetchone()
        return int(row[0]) if row else 0
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description=(
            "Generate aggregate user-preference signal stats and update "
            "docs/user-preferences.md with a live stats block."
        )
    )
    parser.add_argument(
        "--page",
        help="Path to the user-preferences Markdown page "
             "(default: docs/user-preferences.md)",
        type=Path,
        default=Path("docs/user-preferences.md"),
    )
    parser.add_argument(
        "--data",
        help="Output path for the JSON data file "
             "(default: docs/user-preferences-data.json)",
        type=Path,
        default=Path("docs/user-preferences-data.json"),
    )
    parser.add_argument(
        "--csv",
        help="Output path for the CSV data file "
             "(default: docs/user-preferences-data.csv)",
        type=Path,
        default=Path("docs/user-preferences-data.csv"),
    )
    parser.add_argument(
        "--db",
        help="Database file path (overrides settings)",
        type=Path,
    )
    parser.add_argument(
        "--seeds-dir",
        help="Directory containing TOON seed files for scan coverage "
             "(default: data/toon-seeds/countries)",
        type=Path,
        default=Path("data/toon-seeds/countries"),
    )
    parser.add_argument(
        "--registry",
        help="Path to the design-system registry (default: data/design-systems.yaml)",
        type=Path,
        default=None,
    )

    args = parser.parse_args()

    if args.db:
        db_path = args.db
    else:
        settings = load_settings()
        db_path = Path(settings.metadata_db_url.replace("sqlite:///", ""))

    try:
        ok = generate_preference_report(
            db_path, args.page, args.data, args.csv, args.seeds_dir, args.registry
        )
        if not ok:
            sys.exit(1)
    except Exception as exc:
        print(f"Error generating user-preferences report: {exc}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
