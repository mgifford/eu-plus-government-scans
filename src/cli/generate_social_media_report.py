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

from src.lib.settings import load_settings


# ---------------------------------------------------------------------------
# HTML comment markers
# ---------------------------------------------------------------------------

_STATS_MARKER_START = "<!-- SOCIAL_MEDIA_STATS_START -->"
_STATS_MARKER_END = "<!-- SOCIAL_MEDIA_STATS_END -->"


# ---------------------------------------------------------------------------
# Database helpers
# ---------------------------------------------------------------------------

def _query_summary(conn: sqlite3.Connection) -> dict:
    """Return aggregate social media scan totals from the database.

    Only the most recent scan result for each URL is considered so that
    counts do not exceed the number of distinct URLs.
    """
    row = conn.execute(
        """
        SELECT
            COUNT(DISTINCT scan_id)                                     AS total_batches,
            COUNT(*)                                                    AS total_scanned,
            SUM(CASE WHEN is_reachable = 1       THEN 1 ELSE 0 END)    AS total_reachable,
            SUM(CASE WHEN twitter_links != '[]'  THEN 1 ELSE 0 END)    AS twitter_pages,
            SUM(CASE WHEN x_links       != '[]'  THEN 1 ELSE 0 END)    AS x_pages,
            SUM(CASE WHEN bluesky_links  != '[]' THEN 1 ELSE 0 END)    AS bluesky_pages,
            SUM(CASE WHEN mastodon_links != '[]' THEN 1 ELSE 0 END)    AS mastodon_pages,
            MIN(scanned_at)                                             AS first_scan,
            MAX(scanned_at)                                             AS last_scan
        FROM (
            SELECT url, scan_id, is_reachable,
                   twitter_links, x_links, bluesky_links, mastodon_links,
                   scanned_at,
                   ROW_NUMBER() OVER (
                       PARTITION BY url ORDER BY scanned_at DESC
                   ) AS rn
            FROM url_social_media_results
        )
        WHERE rn = 1
        """
    ).fetchone()
    if row is None:
        return {}
    return dict(row)


def _query_by_country(conn: sqlite3.Connection) -> list[dict]:
    """Return per-country social media platform totals.

    Only the most recent scan result for each URL is considered.
    """
    rows = conn.execute(
        """
        SELECT
            latest.country_code,
            COUNT(*)                                                    AS total_scanned,
            SUM(CASE WHEN is_reachable = 1       THEN 1 ELSE 0 END)    AS reachable,
            SUM(CASE WHEN twitter_links != '[]'  THEN 1 ELSE 0 END)    AS twitter_pages,
            SUM(CASE WHEN x_links       != '[]'  THEN 1 ELSE 0 END)    AS x_pages,
            SUM(CASE WHEN bluesky_links  != '[]' THEN 1 ELSE 0 END)    AS bluesky_pages,
            SUM(CASE WHEN mastodon_links != '[]' THEN 1 ELSE 0 END)    AS mastodon_pages,
            MAX(scanned_at)                                             AS last_scan
        FROM (
            SELECT url, country_code, is_reachable,
                   twitter_links, x_links, bluesky_links, mastodon_links,
                   scanned_at,
                   ROW_NUMBER() OVER (
                       PARTITION BY url ORDER BY scanned_at DESC
                   ) AS rn
            FROM url_social_media_results
        ) latest
        WHERE latest.rn = 1
        GROUP BY latest.country_code
        ORDER BY latest.country_code
        """
    ).fetchall()
    return [dict(r) for r in rows]


# ---------------------------------------------------------------------------
# Stats block builder
# ---------------------------------------------------------------------------

def _build_stats_block(summary: dict, generated_at: str) -> str:
    """Return a Markdown stats block to inject between the markers."""
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

    def _pct_of_scanned(n: int) -> str:
        """Return 'n / scanned * 100' as a formatted percentage string."""
        return f"{n / scanned * 100:.1f}%" if scanned else "—"

    lines = [
        _STATS_MARKER_START,
        "",
        f"_Stats as of {generated_at} — last scan: {last_scan}_",
        "",
        f"**{batches:,}** scan batches run &nbsp;|&nbsp; "
        f"**{scanned:,}** pages scanned &nbsp;|&nbsp; "
        f"**{reachable:,}** reachable ({_pct_of_scanned(reachable)})",
        "",
        "| Platform | Pages with a link | % of Scanned Pages |",
        "|----------|-------------------|--------------------|",
        f"| 🐦 Twitter | **{twitter:,}** | {_pct_of_scanned(twitter)} |",
        f"| ✖ X | **{x_pages:,}** | {_pct_of_scanned(x_pages)} |",
        f"| 🦋 Bluesky | **{bluesky:,}** | {_pct_of_scanned(bluesky)} |",
        f"| 🐘 Mastodon / Fediverse | **{mastodon:,}** | {_pct_of_scanned(mastodon)} |",
        "",
        "> A single page may link to more than one platform.  "
        "Percentages show the share of all scanned pages that link to each platform.",
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
) -> bool:
    """Update *page_path* stats block and write *data_path* JSON.

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

    # --- write the JSON data file -----------------------------------------
    data_path.parent.mkdir(parents=True, exist_ok=True)
    data: dict = {
        "generated_at": generated_at,
        "summary": {
            "total_batches": summary.get("total_batches") or 0,
            "total_scanned": summary.get("total_scanned") or 0,
            "total_reachable": summary.get("total_reachable") or 0,
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

    new_block = _build_stats_block(summary, generated_at)
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
    print(f"Sites crawled: {summary.get('total_scanned', 0):,} "
          f"({summary.get('total_reachable', 0):,} reachable)")
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

    args = parser.parse_args()

    if args.db:
        db_path = args.db
    else:
        settings = load_settings()
        db_path = Path(settings.metadata_db_url.replace("sqlite:///", ""))

    try:
        ok = generate_social_media_report(db_path, args.page, args.data)
        if not ok:
            sys.exit(1)
    except Exception as exc:
        print(f"Error generating social media report: {exc}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
