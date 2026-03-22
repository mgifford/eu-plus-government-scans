"""CLI tool to generate the social media scanning stats page.

Queries the metadata database for aggregate social media scan statistics
and updates ``docs/social-media.md`` with a live stats block between
``<!-- SOCIAL_MEDIA_STATS_START -->`` and ``<!-- SOCIAL_MEDIA_STATS_END -->``
markers.  A summary JSON data file (``docs/social-media-data.json``) is also
written so that external tools and the page itself can link directly to the
machine-readable results.
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

_STATS_MARKER_START = "<!-- SOCIAL_MEDIA_STATS_START -->"
_STATS_MARKER_END = "<!-- SOCIAL_MEDIA_STATS_END -->"


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
    """Return aggregate social media scan totals from the database.

    Each URL may appear in multiple scan batches (one row per (url, scan_id)).
    All per-URL counts use COUNT(DISTINCT CASE WHEN … THEN url END) so that a
    URL is counted at most once regardless of how many scan batches it appears
    in.
    """
    row = conn.execute(
        """
        SELECT
            COUNT(DISTINCT scan_id)                                                     AS total_batches,
            COUNT(DISTINCT url)                                                         AS total_scanned,
            COUNT(DISTINCT CASE WHEN is_reachable = 1      THEN url ELSE NULL END)     AS total_reachable,
            COUNT(DISTINCT CASE WHEN twitter_links != '[]' THEN url ELSE NULL END)     AS twitter_pages,
            COUNT(DISTINCT CASE WHEN x_links       != '[]' THEN url ELSE NULL END)     AS x_pages,
            COUNT(DISTINCT CASE WHEN bluesky_links  != '[]' THEN url ELSE NULL END)    AS bluesky_pages,
            COUNT(DISTINCT CASE WHEN mastodon_links != '[]' THEN url ELSE NULL END)    AS mastodon_pages,
            MIN(scanned_at)                                                             AS first_scan,
            MAX(scanned_at)                                                             AS last_scan
        FROM url_social_media_results
        """
    ).fetchone()
    if row is None:
        return {}
    return dict(row)


def _query_by_country(conn: sqlite3.Connection) -> list[dict]:
    """Return per-country social media platform totals.

    Uses COUNT(DISTINCT CASE WHEN … THEN url END) so that each URL is counted
    at most once per country, even when a URL appears in multiple scan batches.
    """
    rows = conn.execute(
        """
        SELECT
            country_code,
            COUNT(DISTINCT url)                                                         AS total_scanned,
            COUNT(DISTINCT CASE WHEN is_reachable = 1      THEN url ELSE NULL END)     AS reachable,
            COUNT(DISTINCT CASE WHEN twitter_links != '[]' THEN url ELSE NULL END)     AS twitter_pages,
            COUNT(DISTINCT CASE WHEN x_links       != '[]' THEN url ELSE NULL END)     AS x_pages,
            COUNT(DISTINCT CASE WHEN bluesky_links  != '[]' THEN url ELSE NULL END)    AS bluesky_pages,
            COUNT(DISTINCT CASE WHEN mastodon_links != '[]' THEN url ELSE NULL END)    AS mastodon_pages,
            MAX(scanned_at)                                                             AS last_scan
        FROM url_social_media_results
        GROUP BY country_code
        ORDER BY country_code
        """
    ).fetchall()
    return [dict(r) for r in rows]


# ---------------------------------------------------------------------------
# Stats block builder
# ---------------------------------------------------------------------------

def _build_stats_block(summary: dict, generated_at: str, total_available: int = 0) -> str:
    """Return a Markdown stats block to inject between the markers.

    Args:
        summary: Aggregate stats from ``_query_summary()``.
        generated_at: Human-readable timestamp string.
        total_available: Total pages across all toon seed files.  When > 0,
            the block includes a "X of Y available pages scanned" coverage line.
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
    twitter = summary.get("twitter_pages") or 0
    x_pages = summary.get("x_pages") or 0
    bluesky = summary.get("bluesky_pages") or 0
    mastodon = summary.get("mastodon_pages") or 0
    last_scan = (summary.get("last_scan") or "")[:10] or "—"

    def _pct(num: int, denom: int) -> str:
        return f"{num / denom * 100:.1f}%" if denom else "—"

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

    reach_pct = _pct(reachable, scanned)
    lines += [
        f"**{reachable:,}** of **{scanned:,}** scanned pages were reachable "
        f"(**{reach_pct}**)",
        "",
        "| Platform | Pages with link | % of scanned | % of reachable |",
        "|----------|----------------|:------------:|:--------------:|",
        f"| 🐦 Twitter | **{twitter:,}** | {_pct(twitter, scanned)} | {_pct(twitter, reachable)} |",
        f"| ✖ X | **{x_pages:,}** | {_pct(x_pages, scanned)} | {_pct(x_pages, reachable)} |",
        f"| 🦋 Bluesky | **{bluesky:,}** | {_pct(bluesky, scanned)} | {_pct(bluesky, reachable)} |",
        f"| 🐘 Mastodon / Fediverse | **{mastodon:,}** | {_pct(mastodon, scanned)} | {_pct(mastodon, reachable)} |",
        "",
        "📥 Machine-readable results: "
        "[social-media-data.json](social-media-data.json)",
        "",
        _STATS_MARKER_END,
    ]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def generate_social_media_report(
    db_path: Path,
    page_path: Path,
    data_path: Path,
    toon_seeds_dir: Path | None = None,
) -> bool:
    """Update *page_path* stats block and write *data_path* JSON.

    Args:
        db_path: Path to the SQLite metadata database.
        page_path: Path to the ``docs/social-media.md`` Markdown page.
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
            "twitter_pages": summary.get("twitter_pages") or 0,
            "x_pages": summary.get("x_pages") or 0,
            "bluesky_pages": summary.get("bluesky_pages") or 0,
            "mastodon_pages": summary.get("mastodon_pages") or 0,
            "first_scan": summary.get("first_scan"),
            "last_scan": summary.get("last_scan"),
        },
        "by_country": by_country,
    }
    data_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Data file written: {data_path}")

    # --- update the Markdown page -----------------------------------------
    if not page_path.exists():
        print(f"Social media page not found: {page_path}", file=sys.stderr)
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

    new_block = _build_stats_block(summary, generated_at, total_available)
    new_content = (
        content[:start_idx]
        + new_block
        + content[end_idx + len(_STATS_MARKER_END):]
    )
    page_path.write_text(new_content, encoding="utf-8")
    print(f"Social media page updated: {page_path}")

    # --- console summary --------------------------------------------------
    print("\n" + "=" * 60)
    print("SOCIAL MEDIA STATS SUMMARY")
    print("=" * 60)
    print(f"Batches run  : {summary.get('total_batches', 0):,}")
    scanned = summary.get('total_scanned', 0)
    reachable = summary.get('total_reachable', 0)
    if total_available:
        print(f"Pages scanned: {scanned:,} / {total_available:,} available "
              f"({scanned / total_available * 100:.1f}% coverage)")
    else:
        print(f"Sites crawled: {scanned:,} ({reachable:,} reachable)")
    print(f"Reachable    : {reachable:,} / {scanned:,}")
    print(f"Twitter pages: {summary.get('twitter_pages', 0):,}")
    print(f"X pages      : {summary.get('x_pages', 0):,}")
    print(f"Bluesky pages: {summary.get('bluesky_pages', 0):,}")
    print(f"Mastodon pages:{summary.get('mastodon_pages', 0):,}")
    print("=" * 60)

    return True


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description=(
            "Generate aggregate social media scan stats and update "
            "docs/social-media.md with a live stats block."
        )
    )
    parser.add_argument(
        "--page",
        help="Path to the social-media Markdown page (default: docs/social-media.md)",
        type=Path,
        default=Path("docs/social-media.md"),
    )
    parser.add_argument(
        "--data",
        help="Output path for the JSON data file (default: docs/social-media-data.json)",
        type=Path,
        default=Path("docs/social-media-data.json"),
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
        ok = generate_social_media_report(db_path, args.page, args.data, args.seeds_dir)
        if not ok:
            sys.exit(1)
    except Exception as exc:
        print(f"Error generating social media report: {exc}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
