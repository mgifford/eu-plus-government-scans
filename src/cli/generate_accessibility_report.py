"""CLI tool to generate the accessibility statement scanning stats page.

Queries the metadata database for aggregate accessibility scan statistics
and updates ``docs/accessibility-statements.md`` with a live stats block
between ``<!-- ACCESSIBILITY_STATS_START -->`` and
``<!-- ACCESSIBILITY_STATS_END -->`` markers.  A summary JSON data file
(``docs/accessibility-data.json``) is also written so that external tools
and the page itself can link directly to the machine-readable results.
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

from src.lib.country_utils import country_filename_to_code
from src.lib.settings import load_settings


# ---------------------------------------------------------------------------
# HTML comment markers
# ---------------------------------------------------------------------------

_STATS_MARKER_START = "<!-- ACCESSIBILITY_STATS_START -->"
_STATS_MARKER_END = "<!-- ACCESSIBILITY_STATS_END -->"


# ---------------------------------------------------------------------------
# Toon seed helpers
# ---------------------------------------------------------------------------

def _count_toon_seed_urls(toon_seeds_dir: Path) -> dict[str, int]:
    """Return a mapping of country_code → page_count from toon seed files.

    Reads every ``*.toon`` file in *toon_seeds_dir* and extracts the
    ``page_count`` field.  Returns an empty dict when the directory does
    not exist or contains no seed files.
    """
    counts: dict[str, int] = {}
    if not toon_seeds_dir.is_dir():
        return counts
    for toon_file in toon_seeds_dir.glob("*.toon"):
        try:
            data = json.loads(toon_file.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        country_code = country_filename_to_code(toon_file.stem)
        counts[country_code] = int(data.get("page_count") or 0)
    return counts


# ---------------------------------------------------------------------------
# Database helpers
# ---------------------------------------------------------------------------

def _query_summary(conn: sqlite3.Connection) -> dict:
    """Return aggregate accessibility scan totals from the database.

    Each URL may appear in multiple scan batches (one row per (url, scan_id)).
    All per-URL counts use COUNT(DISTINCT CASE WHEN … THEN url END) so that a
    URL is counted at most once regardless of how many scan batches it appears
    in.
    """
    row = conn.execute(
        """
        SELECT
            COUNT(DISTINCT scan_id)                                                         AS total_batches,
            COUNT(DISTINCT url)                                                             AS total_scanned,
            COUNT(DISTINCT CASE WHEN is_reachable = 1    THEN url ELSE NULL END)           AS total_reachable,
            COUNT(DISTINCT CASE WHEN has_statement = 1   THEN url ELSE NULL END)           AS total_has_statement,
            COUNT(DISTINCT CASE WHEN found_in_footer = 1 THEN url ELSE NULL END)           AS total_in_footer,
            MIN(scanned_at)                                                                 AS first_scan,
            MAX(scanned_at)                                                                 AS last_scan
        FROM url_accessibility_results
        """
    ).fetchone()
    if row is None:
        return {}
    return dict(row)


def _query_by_country(conn: sqlite3.Connection) -> list[dict]:
    """Return per-country accessibility scan totals.

    Uses COUNT(DISTINCT CASE WHEN … THEN url END) so that each URL is counted
    at most once per country, even when a URL appears in multiple scan batches.
    """
    rows = conn.execute(
        """
        SELECT
            country_code,
            COUNT(DISTINCT url)                                                             AS total_scanned,
            COUNT(DISTINCT CASE WHEN is_reachable = 1    THEN url ELSE NULL END)           AS reachable,
            COUNT(DISTINCT CASE WHEN has_statement = 1   THEN url ELSE NULL END)           AS has_statement,
            COUNT(DISTINCT CASE WHEN found_in_footer = 1 THEN url ELSE NULL END)           AS found_in_footer,
            MIN(scanned_at)                                                                 AS first_scan,
            MAX(scanned_at)                                                                 AS last_scan
        FROM url_accessibility_results
        GROUP BY country_code
        ORDER BY country_code
        """
    ).fetchall()
    return [dict(r) for r in rows]


# ---------------------------------------------------------------------------
# Stats block builder
# ---------------------------------------------------------------------------

def _build_stats_block(
    summary: dict,
    generated_at: str,
    total_available: int = 0,
    by_country: list[dict] | None = None,
    seed_counts: dict[str, int] | None = None,
) -> str:
    """Return a Markdown stats block to inject between the markers.

    Args:
        summary: Aggregate stats from ``_query_summary()``.
        generated_at: Human-readable timestamp string.
        total_available: Total pages across all toon seed files.  When > 0,
            the block includes a "X of Y available pages scanned" coverage line.
        by_country: Per-country rows from ``_query_by_country()``.  When
            provided, the block includes a per-country breakdown table.
        seed_counts: Mapping of country_code → available page count from toon
            seed files.  Used for the "Available" column in the per-country
            table when *by_country* is provided.
    """
    if not summary or not summary.get("total_scanned"):
        return (
            f"{_STATS_MARKER_START}\n\n"
            "_No scan data yet — stats update automatically after every scan run._\n\n"
            f"{_STATS_MARKER_END}"
        )

    batches = summary.get("total_batches") or 0
    scanned = summary.get("total_scanned") or 0
    reachable = summary.get("total_reachable") or 0
    has_statement = summary.get("total_has_statement") or 0
    in_footer = summary.get("total_in_footer") or 0
    last_scan = (summary.get("last_scan") or "")[:10] or "—"

    def _pct(num: int, denom: int) -> str:
        return f"{num / denom * 100:.1f}%" if denom else "—"

    def _month(ts: str | None) -> str:
        if not ts:
            return "—"
        try:
            return datetime.fromisoformat(ts[:19]).strftime("%b %Y")
        except (ValueError, TypeError):
            return ts[:7]

    def _scan_period(first: str | None, last: str | None) -> str:
        f = _month(first)
        last_month = _month(last)
        if f and last_month:
            return f if f == last_month else f"{f} – {last_month}"
        return f or last_month or "—"

    lines = [
        _STATS_MARKER_START,
        "",
        f"_Stats as of {generated_at} — last scan: {last_scan}_",
        "",
        f"**{batches:,}** scan batches run",
        "",
    ]

    if total_available > 0:
        scan_pct = _pct(scanned, total_available)
        lines.append(
            f"**{scanned:,}** of **{total_available:,}** available pages scanned "
            f"(**{scan_pct}** coverage)"
        )
    else:
        lines.append(f"**{scanned:,}** pages scanned")

    lines += [
        f"**{reachable:,}** of **{scanned:,}** scanned pages were reachable "
        f"(**{_pct(reachable, scanned)}**)",
        f"**{has_statement:,}** of **{reachable:,}** reachable pages have an "
        f"accessibility statement (**{_pct(has_statement, reachable)}**)",
        f"**{in_footer:,}** pages have the statement link in the footer "
        f"(**{_pct(in_footer, has_statement)}** of pages with a statement)",
        "",
        "📥 Machine-readable results: "
        "[accessibility-data.json](accessibility-data.json)",
    ]

    # Per-country breakdown table
    if by_country:
        seed_counts = seed_counts or {}

        lines += [
            "",
            "---",
            "",
            "## Accessibility Statement Scan by Country",
            "",
            "| Country | Scanned | Available | Reachable | Has Statement | In Footer | Statement % | Scan Period |",
            "|---------|---------|-----------|-----------|--------------|-----------|------------|-------------|",
        ]
        for row in by_country:
            cc = row["country_code"]
            available = seed_counts.get(cc, 0)
            avail_str = f"{available:,}" if available else "—"
            period = _scan_period(row.get("first_scan"), row.get("last_scan"))
            stmt_pct = _pct(row.get("has_statement", 0), row.get("reachable", 0))
            lines.append(
                f"| {cc} | {row['total_scanned']:,} | {avail_str} | {row['reachable']:,} | "
                f"{row.get('has_statement', 0):,} | {row.get('found_in_footer', 0):,} | "
                f"{stmt_pct} | {period} |"
            )

        # totals row
        tot_scanned = sum(r["total_scanned"] for r in by_country)
        tot_avail = sum(seed_counts.values())
        tot_avail_str = f"**{tot_avail:,}**" if tot_avail else "—"
        tot_reachable = sum(r["reachable"] for r in by_country)
        tot_has_statement = sum(r.get("has_statement", 0) for r in by_country)
        tot_in_footer = sum(r.get("found_in_footer", 0) for r in by_country)
        tot_stmt_pct = _pct(tot_has_statement, tot_reachable)
        lines.append(
            f"| **Total** | **{tot_scanned:,}** | {tot_avail_str} | **{tot_reachable:,}** | "
            f"**{tot_has_statement:,}** | **{tot_in_footer:,}** | **{tot_stmt_pct}** | — |"
        )
        lines += [
            "",
            "> **Statement %** is the percentage of *reachable* pages that contain "
            "at least one link to an accessibility statement.",
        ]

    lines += [
        "",
        _STATS_MARKER_END,
    ]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def generate_accessibility_report(
    db_path: Path,
    page_path: Path,
    data_path: Path,
    toon_seeds_dir: Path | None = None,
) -> bool:
    """Update *page_path* stats block and write *data_path* JSON.

    Args:
        db_path: Path to the SQLite metadata database.
        page_path: Path to the ``docs/accessibility-statements.md`` Markdown page.
        data_path: Output path for the machine-readable JSON data file.
        toon_seeds_dir: Directory containing ``*.toon`` seed files.  When
            provided the stats block will include a "X of Y available pages
            scanned" coverage line and ``total_available`` is written to the
            JSON file.

    Returns ``True`` on success, ``False`` when the markers are missing from
    *page_path* (the page is left unchanged in that case).
    """
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    if not db_path.exists():
        summary: dict = {}
        by_country: list[dict] = []
    else:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        try:
            summary = _query_summary(conn)
            by_country = _query_by_country(conn)
        finally:
            conn.close()

    seed_counts = _count_toon_seed_urls(toon_seeds_dir) if toon_seeds_dir else {}
    total_available = sum(seed_counts.values())

    # --- write the JSON data file -----------------------------------------
    data_path.parent.mkdir(parents=True, exist_ok=True)
    data: dict = {
        "generated_at": generated_at,
        "summary": {
            "total_batches": summary.get("total_batches") or 0,
            "total_scanned": summary.get("total_scanned") or 0,
            "total_reachable": summary.get("total_reachable") or 0,
            "total_available": total_available,
            "total_has_statement": summary.get("total_has_statement") or 0,
            "total_in_footer": summary.get("total_in_footer") or 0,
            "first_scan": summary.get("first_scan"),
            "last_scan": summary.get("last_scan"),
        },
        "by_country": by_country,
    }
    data_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Data file written: {data_path}")

    # --- update the Markdown page -----------------------------------------
    if not page_path.exists():
        print(f"Accessibility page not found: {page_path}", file=sys.stderr)
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

    new_block = _build_stats_block(summary, generated_at, total_available, by_country, seed_counts)
    new_content = (
        content[:start_idx]
        + new_block
        + content[end_idx + len(_STATS_MARKER_END):]
    )
    page_path.write_text(new_content, encoding="utf-8")
    print(f"Accessibility page updated: {page_path}")

    # --- console summary --------------------------------------------------
    print("\n" + "=" * 60)
    print("ACCESSIBILITY STATS SUMMARY")
    print("=" * 60)
    print(f"Batches run       : {summary.get('total_batches', 0):,}")
    scanned = summary.get("total_scanned", 0)
    reachable = summary.get("total_reachable", 0)
    has_statement = summary.get("total_has_statement", 0)
    in_footer = summary.get("total_in_footer", 0)
    if total_available:
        print(f"Pages scanned     : {scanned:,} / {total_available:,} available "
              f"({scanned / total_available * 100:.1f}% coverage)")
    else:
        print(f"Pages scanned     : {scanned:,}")
    print(f"Reachable         : {reachable:,} / {scanned:,}")
    print(f"Has statement     : {has_statement:,} / {reachable:,}")
    print(f"Found in footer   : {in_footer:,}")
    print("=" * 60)

    return True


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description=(
            "Generate aggregate accessibility statement scan stats and update "
            "docs/accessibility-statements.md with a live stats block."
        )
    )
    parser.add_argument(
        "--page",
        help="Path to the accessibility Markdown page "
             "(default: docs/accessibility-statements.md)",
        type=Path,
        default=Path("docs/accessibility-statements.md"),
    )
    parser.add_argument(
        "--data",
        help="Output path for the JSON data file "
             "(default: docs/accessibility-data.json)",
        type=Path,
        default=Path("docs/accessibility-data.json"),
    )
    parser.add_argument(
        "--db",
        help="Database file path (overrides settings)",
        type=Path,
    )
    parser.add_argument(
        "--seeds-dir",
        help=(
            "Directory containing TOON seed files used to calculate scan "
            "coverage (default: data/toon-seeds/countries)"
        ),
        type=Path,
        default=Path("data/toon-seeds/countries"),
    )

    args = parser.parse_args()

    if args.db:
        db_path = args.db
    else:
        settings = load_settings()
        db_path = Path(settings.metadata_db_url.replace("sqlite:///", ""))

    try:
        ok = generate_accessibility_report(db_path, args.page, args.data, args.seeds_dir)
        if not ok:
            sys.exit(1)
    except Exception as exc:
        print(f"Error generating accessibility report: {exc}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
