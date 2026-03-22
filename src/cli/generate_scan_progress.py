"""CLI tool to generate a multi-scan progress report from the database.

Produces a Markdown summary that shows how far along each scan type
(URL validation, social media, technology) is across all countries,
so stakeholders can see overall coverage at a glance.
"""

from __future__ import annotations

import argparse
import io
import json
import sqlite3
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

from src.lib.country_utils import country_filename_to_code
from src.lib.settings import load_settings


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

# Markers used in docs/index.md to delimit the auto-generated progress block.
_PROGRESS_MARKER_START = "<!-- SCAN_PROGRESS_START -->"
_PROGRESS_MARKER_END = "<!-- SCAN_PROGRESS_END -->"

def _progress_bar(completed: int, total: int, width: int = 20) -> str:
    """Return a simple ASCII progress bar."""
    if total == 0:
        return "░" * width + " (no data)"
    pct = completed / total
    filled = int(pct * width)
    bar = "█" * filled + "░" * (width - filled)
    return f"{bar} {pct * 100:.1f}%"


def _format_month_range(first: str | None, last: str | None) -> str:
    """Return a human-readable month range string.

    Both *first* and *last* are ISO-8601 timestamp strings (or None).
    Returns e.g. ``"Jan 2024 – Mar 2024"`` or ``"Mar 2024"`` when they are
    in the same month, or ``"—"`` when no data is available.
    """
    if not first and not last:
        return "—"

    def _to_month(ts: str) -> str:
        # Handle both "YYYY-MM-DD..." and "YYYY-MM-DDTHH:MM:SS..." formats.
        try:
            return datetime.fromisoformat(ts[:19]).strftime("%b %Y")
        except (ValueError, TypeError):
            return ts[:7]  # Fall back to "YYYY-MM"

    first_m = _to_month(first) if first else None
    last_m = _to_month(last) if last else None

    if first_m and last_m:
        return first_m if first_m == last_m else f"{first_m} – {last_m}"
    return first_m or last_m or "—"


def _count_available_pages(toon_dir: Path) -> dict[str, int]:
    """Return per-country total available page counts from TOON seed files.

    Reads each ``*.toon`` file in *toon_dir* and extracts the ``page_count``
    field.  The filename (without extension) is converted to a country code via
    :func:`country_filename_to_code`.  Returns an empty dict when *toon_dir*
    does not exist.
    """
    if not toon_dir.is_dir():
        return {}
    result: dict[str, int] = {}
    for toon_file in toon_dir.glob("*.toon"):
        try:
            data = json.loads(toon_file.read_text(encoding="utf-8"))
            page_count = int(data.get("page_count") or 0)
            if page_count:
                cc = country_filename_to_code(toon_file.stem)
                result[cc] = page_count
        except (json.JSONDecodeError, ValueError, OSError):
            continue
    return result


# ---------------------------------------------------------------------------
# report generation
# ---------------------------------------------------------------------------

def generate_progress_report(
    db_path: Path,
    output_path: Path,
    toon_dir: Path | None = None,
) -> None:
    """Generate a comprehensive scan-progress report from the database.

    *toon_dir* is an optional path to the TOON seed files directory
    (e.g. ``data/toon-seeds/countries``).  When provided, each country's
    total available page count is shown alongside the scanned count so the
    coverage percentage is meaningful (scanned / available).
    """

    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    if not db_path.exists():
        with output_path.open("w") as f:
            f.write("# Scan Progress Report\n\n")
            f.write(f"_Generated: {generated_at}_\n\n")
            f.write("No scan data available yet. Run a scan first.\n")
        print(f"Report generated (empty): {output_path}")
        return

    available = _count_available_pages(toon_dir) if toon_dir else {}

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    try:
        _write_report(conn, output_path, generated_at, available)
    finally:
        conn.close()

    print(f"Report generated: {output_path}")


def update_index_progress(
    index_path: Path,
    db_path: Path,
    toon_dir: Path | None = None,
) -> bool:
    """Replace the progress block in *index_path* with fresh scan stats.

    The block is delimited by ``<!-- SCAN_PROGRESS_START -->`` and
    ``<!-- SCAN_PROGRESS_END -->`` HTML comments.  If the markers are not
    found, the file is left unchanged and ``False`` is returned.

    *toon_dir* is an optional path to the TOON seed files directory.  When
    provided, coverage percentages reflect *scanned / available* pages.

    Returns ``True`` when the index file was successfully updated.
    """
    if not index_path.exists():
        print(f"Index file not found: {index_path}", file=sys.stderr)
        return False

    content = index_path.read_text(encoding="utf-8")
    start_idx = content.find(_PROGRESS_MARKER_START)
    end_idx = content.find(_PROGRESS_MARKER_END)

    if start_idx == -1 or end_idx == -1:
        print(
            f"Progress markers not found in {index_path}. "
            "Add <!-- SCAN_PROGRESS_START --> and <!-- SCAN_PROGRESS_END --> "
            "to the file first.",
            file=sys.stderr,
        )
        return False

    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    buf = io.StringIO()
    buf.write(_PROGRESS_MARKER_START + "\n\n")
    buf.write(f"_Progress as of {generated_at}_\n\n")

    if db_path.exists():
        available = _count_available_pages(toon_dir) if toon_dir else {}

        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        try:
            url_val = _query_url_validation(conn)
            social = _query_social_media(conn)
            platforms = _query_social_media_platforms(conn)
            tech = _query_technology(conn)
            lighthouse = _query_lighthouse(conn)
        finally:
            conn.close()

        uv_total = sum(d["total"] for d in url_val.values())
        uv_valid = sum(d["valid"] for d in url_val.values())
        sm_total = sum(d["total"] for d in social.values())
        sm_reachable = sum(d["reachable"] for d in social.values())
        tech_total = sum(d["total"] for d in tech.values())
        lh_total = sum(d["total"] for d in lighthouse.values())
        all_countries = sorted(set(url_val) | set(social) | set(tech) | set(lighthouse))

        total_available = (
            sum(available.get(cc, 0) for cc in all_countries)
            if available
            else 0
        )

        sm_avail = total_available or sm_total
        uv_avail = total_available or uv_total

        buf.write("| Scan Type | Pages Scanned | Available | Coverage |\n")
        buf.write("|-----------|--------------|-----------|----------|\n")
        buf.write(
            f"| Social Media | {sm_total:,} scanned "
            f"({sm_reachable:,} reachable) | "
            f"{sm_avail:,} | "
            f"{_progress_bar(sm_total, sm_avail)} |\n"
        )
        buf.write(
            f"| URL Validation | {uv_total:,} scanned "
            f"({uv_valid:,} valid) | "
            f"{uv_avail:,} | "
            f"{_progress_bar(uv_total, uv_avail)} |\n"
        )
        if tech_total:
            buf.write(
                f"| Technology | {tech_total:,} URLs scanned | "
                f"— | "
                f"{_progress_bar(tech_total, sm_avail or uv_avail or 1)} |\n"
            )
        if lh_total:
            buf.write(
                f"| Lighthouse | {lh_total:,} URLs scanned | "
                f"— | "
                f"{_progress_bar(lh_total, sm_avail or uv_avail or 1)} |\n"
            )
        buf.write("\n")

        # Per-platform breakdown (answers "of pages scanned, how many have each platform?")
        total_twitter = sum(d["has_twitter"] for d in platforms.values())
        total_x = sum(d["has_x"] for d in platforms.values())
        total_bluesky = sum(d["has_bluesky"] for d in platforms.values())
        total_mastodon = sum(d["has_mastodon"] for d in platforms.values())

        if sm_total > 0:
            buf.write("**Social media platforms** (% of scanned pages):\n\n")
            buf.write("| Platform | Pages | % of Scanned |\n")
            buf.write("|----------|-------|--------------|\n")
            buf.write(
                f"| 🐦 Twitter | {total_twitter:,} | "
                f"{total_twitter / sm_total * 100:.1f}% |\n"
            )
            buf.write(
                f"| ✖ X | {total_x:,} | "
                f"{total_x / sm_total * 100:.1f}% |\n"
            )
            buf.write(
                f"| 🦋 Bluesky | {total_bluesky:,} | "
                f"{total_bluesky / sm_total * 100:.1f}% |\n"
            )
            buf.write(
                f"| 🐘 Mastodon | {total_mastodon:,} | "
                f"{total_mastodon / sm_total * 100:.1f}% |\n"
            )
            buf.write("\n")

        buf.write(
            f"**{len(all_countries)} countries** with scan data. "
            "See the [Scan Progress Report](scan-progress.md) for full details.\n\n"
        )
    else:
        buf.write(
            "_No scan data yet — progress updates automatically after every scan run._\n\n"
        )

    buf.write(_PROGRESS_MARKER_END)

    new_block = buf.getvalue()
    new_content = (
        content[:start_idx]
        + new_block
        + content[end_idx + len(_PROGRESS_MARKER_END):]
    )
    index_path.write_text(new_content, encoding="utf-8")
    print(f"Index updated: {index_path}")
    return True


def _query_url_validation(conn: sqlite3.Connection) -> dict[str, dict]:
    """Return per-country URL validation stats from the database.

    Only the most recent validation result for each URL is considered so that
    valid/invalid counts do not exceed the number of distinct URLs.  The
    first_scan/last_scan date range is taken across *all* validation rows for
    each country so the displayed scan period remains accurate.
    """
    result: dict[str, dict] = {}
    for row in conn.execute(
        """
        SELECT latest.country_code,
               COUNT(*)                                               AS total,
               SUM(CASE WHEN latest.is_valid = 1 THEN 1 ELSE 0 END) AS valid,
               SUM(CASE WHEN latest.is_valid = 0 THEN 1 ELSE 0 END) AS invalid,
               dates.first_scan,
               dates.last_scan
        FROM (
            SELECT url, country_code, is_valid,
                   ROW_NUMBER() OVER (
                       PARTITION BY url ORDER BY validated_at DESC
                   ) AS rn
            FROM url_validation_results
        ) latest
        JOIN (
            SELECT country_code,
                   MIN(validated_at) AS first_scan,
                   MAX(validated_at) AS last_scan
            FROM url_validation_results
            GROUP BY country_code
        ) dates ON dates.country_code = latest.country_code
        WHERE latest.rn = 1
        GROUP BY latest.country_code
        ORDER BY latest.country_code
        """
    ):
        result[row["country_code"]] = dict(row)
    return result


def _query_social_media(conn: sqlite3.Connection) -> dict[str, dict]:
    """Return per-country social media scan stats from the database.

    Only the most recent scan result for each URL is considered so that
    reachable/tier counts do not exceed the number of distinct URLs.
    """
    result: dict[str, dict] = {}
    for row in conn.execute(
        """
        SELECT latest.country_code,
               COUNT(*)                                                        AS total,
               SUM(CASE WHEN latest.is_reachable = 1   THEN 1 ELSE 0 END)    AS reachable,
               SUM(CASE WHEN latest.social_tier = 'twitter_only'  THEN 1 ELSE 0 END) AS twitter_only,
               SUM(CASE WHEN latest.social_tier = 'modern_only'   THEN 1 ELSE 0 END) AS modern_only,
               SUM(CASE WHEN latest.social_tier = 'mixed'         THEN 1 ELSE 0 END) AS mixed,
               SUM(CASE WHEN latest.social_tier = 'no_social'     THEN 1 ELSE 0 END) AS no_social,
               SUM(CASE WHEN latest.social_tier = 'unreachable'   THEN 1 ELSE 0 END) AS unreachable,
               dates.first_scan,
               dates.last_scan
        FROM (
            SELECT url, country_code, is_reachable, social_tier,
                   ROW_NUMBER() OVER (
                       PARTITION BY url ORDER BY scanned_at DESC
                   ) AS rn
            FROM url_social_media_results
        ) latest
        JOIN (
            SELECT country_code,
                   MIN(scanned_at) AS first_scan,
                   MAX(scanned_at) AS last_scan
            FROM url_social_media_results
            GROUP BY country_code
        ) dates ON dates.country_code = latest.country_code
        WHERE latest.rn = 1
        GROUP BY latest.country_code
        ORDER BY latest.country_code
        """
    ):
        result[row["country_code"]] = dict(row)
    return result


def _query_social_media_platforms(conn: sqlite3.Connection) -> dict[str, dict]:
    """Return per-country platform-level social media link counts.

    Counts the number of scanned pages that contain at least one link to each
    platform (Twitter, X, Bluesky, Mastodon), derived from the stored JSON lists.
    Only the most recent scan result for each URL is considered.
    """
    result: dict[str, dict] = {}
    for row in conn.execute(
        """
        SELECT latest.country_code,
               COUNT(*)                                                        AS total,
               SUM(CASE WHEN latest.twitter_links  != '[]' THEN 1 ELSE 0 END) AS has_twitter,
               SUM(CASE WHEN latest.x_links        != '[]' THEN 1 ELSE 0 END) AS has_x,
               SUM(CASE WHEN latest.bluesky_links  != '[]' THEN 1 ELSE 0 END) AS has_bluesky,
               SUM(CASE WHEN latest.mastodon_links != '[]' THEN 1 ELSE 0 END) AS has_mastodon,
               SUM(CASE WHEN latest.is_reachable = 1       THEN 1 ELSE 0 END) AS reachable,
               SUM(CASE WHEN (latest.twitter_links != '[]' OR latest.x_links != '[]')
                             THEN 1 ELSE 0 END)                                AS has_any_legacy,
               SUM(CASE WHEN (latest.bluesky_links != '[]' OR latest.mastodon_links != '[]')
                             THEN 1 ELSE 0 END)                                AS has_any_modern
        FROM (
            SELECT url, country_code, is_reachable,
                   twitter_links, x_links, bluesky_links, mastodon_links,
                   ROW_NUMBER() OVER (
                       PARTITION BY url ORDER BY scanned_at DESC
                   ) AS rn
            FROM url_social_media_results
        ) latest
        WHERE latest.rn = 1
        GROUP BY latest.country_code
        ORDER BY latest.country_code
        """
    ):
        result[row["country_code"]] = dict(row)
    return result


def _query_technology(conn: sqlite3.Connection) -> dict[str, dict]:
    """Return per-country technology scan stats from the database."""
    result: dict[str, dict] = {}
    for row in conn.execute(
        """
        SELECT country_code,
               COUNT(DISTINCT url)  AS total,
               MAX(scanned_at)      AS last_scan
        FROM url_tech_results
        GROUP BY country_code
        ORDER BY country_code
        """
    ):
        result[row["country_code"]] = dict(row)
    return result


def _query_lighthouse(conn: sqlite3.Connection) -> dict[str, dict]:
    """Return per-country Google Lighthouse scan stats from the database."""
    result: dict[str, dict] = {}
    for row in conn.execute(
        """
        SELECT country_code,
               COUNT(DISTINCT url)                                        AS total,
               AVG(CASE WHEN performance_score IS NOT NULL
                        THEN performance_score END)                       AS avg_performance,
               AVG(CASE WHEN accessibility_score IS NOT NULL
                        THEN accessibility_score END)                     AS avg_accessibility,
               AVG(CASE WHEN best_practices_score IS NOT NULL
                        THEN best_practices_score END)                    AS avg_best_practices,
               AVG(CASE WHEN seo_score IS NOT NULL
                        THEN seo_score END)                               AS avg_seo,
               MAX(scanned_at)                                            AS last_scan
        FROM url_lighthouse_results
        WHERE error_message IS NULL
        GROUP BY country_code
        ORDER BY country_code
        """
    ):
        result[row["country_code"]] = dict(row)
    return result


def _write_overall_coverage(
    f,
    url_val: dict[str, dict],
    social: dict[str, dict],
    tech: dict[str, dict],
    lighthouse: dict[str, dict] | None = None,
    available: dict[str, int] | None = None,
) -> None:
    """Write the overall coverage section.

    *available* is an optional per-country dict of total pages from TOON seed
    files.  When provided, coverage percentages are shown as
    *scanned / available* (a meaningful ≤100% figure).  Without it, the
    section still shows raw counts without a misleading progress bar.
    """
    uv_total = sum(d["total"] for d in url_val.values())
    uv_valid = sum(d["valid"] for d in url_val.values())
    sm_total = sum(d["total"] for d in social.values())
    sm_reachable = sum(d["reachable"] for d in social.values())
    tech_total = sum(d["total"] for d in tech.values())
    lh_total = sum(d["total"] for d in (lighthouse or {}).values())

    all_scan_countries = set(url_val) | set(social)
    total_available = (
        sum(available.get(cc, 0) for cc in all_scan_countries)
        if available
        else 0
    )

    f.write("## Overall Coverage\n\n")
    f.write("| Scan Type | Pages Scanned | Available | Coverage |\n")
    f.write("|-----------|--------------|-----------|----------|\n")

    uv_avail = total_available or uv_total
    f.write(
        f"| URL Validation | {uv_total:,} scanned "
        f"({uv_valid:,} valid) | "
        f"{uv_avail:,} | "
        f"{_progress_bar(uv_total, uv_avail)} |\n"
    )

    sm_avail = total_available or sm_total
    f.write(
        f"| Social Media | {sm_total:,} scanned "
        f"({sm_reachable:,} reachable) | "
        f"{sm_avail:,} | "
        f"{_progress_bar(sm_total, sm_avail)} |\n"
    )
    f.write(
        f"| Technology | {tech_total:,} URLs scanned | "
        f"— | "
        f"{'(manual scan)' if tech_total == 0 else _progress_bar(tech_total, sm_avail or uv_avail or 1)} |\n"
    )
    f.write(
        f"| Lighthouse | {lh_total:,} URLs scanned | "
        f"— | "
        f"{'(manual scan)' if lh_total == 0 else _progress_bar(lh_total, sm_avail or uv_avail or 1)} |\n"
    )
    f.write("\n")

    return uv_total, uv_valid, sm_total, sm_reachable, tech_total


def _write_url_validation_table(
    f, url_val: dict[str, dict], all_countries: list[str]
) -> None:
    """Write the per-country URL validation table."""
    if not url_val:
        return
    f.write("## URL Validation by Country\n\n")
    f.write("| Country | Total | Valid | Invalid | Scan Period | Coverage |\n")
    f.write("|---------|-------|-------|---------|-------------|----------|\n")
    for cc in all_countries:
        if cc not in url_val:
            continue
        d = url_val[cc]
        scan_period = _format_month_range(d.get("first_scan"), d.get("last_scan"))
        f.write(
            f"| {cc} | {d['total']:,} | {d['valid']:,} | "
            f"{d['invalid']:,} | {scan_period} | "
            f"{_progress_bar(d['valid'], d['total'], 15)} |\n"
        )
    f.write("\n")


def _write_social_media_table(
    f, social: dict[str, dict], all_countries: list[str]
) -> None:
    """Write the per-country social media scan table."""
    if not social:
        return
    f.write("## Social Media Scan by Country\n\n")
    f.write(
        "| Country | Scanned | Reachable | Twitter-only | Modern | "
        "Mixed | No Social | Scan Period |\n"
    )
    f.write(
        "|---------|---------|-----------|-------------|--------|"
        "-------|-----------|-------------|\n"
    )
    for cc in all_countries:
        if cc not in social:
            continue
        d = social[cc]
        scan_period = _format_month_range(d.get("first_scan"), d.get("last_scan"))
        f.write(
            f"| {cc} | {d['total']:,} | {d['reachable']:,} | "
            f"{d['twitter_only']:,} | {d['modern_only']:,} | "
            f"{d['mixed']:,} | {d['no_social']:,} | {scan_period} |\n"
        )
    f.write("\n")


def _write_social_media_platform_breakdown(
    f, platforms: dict[str, dict], all_countries: list[str]
) -> None:
    """Write a per-platform social media link count table.

    Shows how many scanned pages per country contain at least one link to each
    individual platform (Twitter, X, Bluesky, Mastodon).  Percentages are
    calculated as *platform pages / total scanned pages* so they answer the
    question "of the pages scanned, how many have each social media platform?"
    A single page may link to more than one platform.
    """
    if not platforms:
        return

    # Aggregate totals for the summary row
    total_scanned = sum(d["total"] for d in platforms.values())
    total_reachable = sum(d["reachable"] for d in platforms.values())
    total_twitter = sum(d["has_twitter"] for d in platforms.values())
    total_x = sum(d["has_x"] for d in platforms.values())
    total_bluesky = sum(d["has_bluesky"] for d in platforms.values())
    total_mastodon = sum(d["has_mastodon"] for d in platforms.values())
    total_legacy = sum(d["has_any_legacy"] for d in platforms.values())
    total_modern = sum(d["has_any_modern"] for d in platforms.values())

    f.write("## Social Media Platform Breakdown\n\n")
    f.write(
        "Number of **scanned** pages per country that link to each platform. "
        "A page may link to more than one platform.  "
        "Percentages show the share of all scanned pages.\n\n"
    )
    f.write(
        "| Country | Scanned | Reachable | Twitter | X | Bluesky | Mastodon "
        "| Legacy % | Modern % |\n"
    )
    f.write(
        "|---------|---------|-----------|---------|---|---------|----------"
        "|----------|----------|\n"
    )
    for cc in all_countries:
        if cc not in platforms:
            continue
        d = platforms[cc]
        t = d["total"]
        if t > 0:
            legacy_pct = f"{d['has_any_legacy'] / t * 100:.1f}%"
            modern_pct = f"{d['has_any_modern'] / t * 100:.1f}%"
        else:
            legacy_pct = "—"
            modern_pct = "—"
        f.write(
            f"| {cc} | {d['total']:,} | {d['reachable']:,} | "
            f"{d['has_twitter']:,} | {d['has_x']:,} | "
            f"{d['has_bluesky']:,} | {d['has_mastodon']:,} | "
            f"{legacy_pct} | {modern_pct} |\n"
        )

    # Summary / totals row
    if total_scanned > 0:
        summary_legacy = f"**{total_legacy / total_scanned * 100:.1f}%**"
        summary_modern = f"**{total_modern / total_scanned * 100:.1f}%**"
    else:
        summary_legacy = "**—**"
        summary_modern = "**—**"
    f.write(
        f"| **Total** | **{total_scanned:,}** | **{total_reachable:,}** | "
        f"**{total_twitter:,}** | **{total_x:,}** | "
        f"**{total_bluesky:,}** | **{total_mastodon:,}** | "
        f"{summary_legacy} | {summary_modern} |\n"
    )
    f.write("\n")

    # Narrative summary
    f.write(
        "> **Legacy platforms** (Twitter / X) vs **modern open platforms** "
        "(Bluesky / Mastodon) — percentages are share of all scanned pages "
        "that contain at least one link to any platform in that group.\n\n"
    )


def _write_technology_table(
    f, tech: dict[str, dict], all_countries: list[str]
) -> None:
    """Write the per-country technology scan table (or a placeholder)."""
    if not tech:
        f.write(
            "## Technology Scan\n\n"
            "_No technology scans have been run yet. "
            "Trigger the **Scan Technology Stack** workflow manually._\n\n"
        )
        return
    f.write("## Technology Scan by Country\n\n")
    f.write("| Country | URLs Scanned | Last Scan |\n")
    f.write("|---------|-------------|----------|\n")
    for cc in all_countries:
        if cc not in tech:
            continue
        d = tech[cc]
        last = (d["last_scan"] or "—")[:10]
        f.write(f"| {cc} | {d['total']:,} | {last} |\n")
    f.write("\n")


def _write_lighthouse_table(
    f, lighthouse: dict[str, dict], all_countries: list[str]
) -> None:
    """Write the per-country Google Lighthouse scan table (or a placeholder).

    Shows average scores (×100) for Performance, Accessibility,
    Best Practices, and SEO alongside the last-scan date.
    """
    if not lighthouse:
        f.write(
            "## Lighthouse Scan\n\n"
            "_No Lighthouse scans have been run yet. "
            "Trigger the **Scan Lighthouse** workflow manually._\n\n"
        )
        return

    def _pct(val: float | None) -> str:
        return f"{val * 100:.0f}" if val is not None else "—"

    f.write("## Lighthouse Scan by Country\n\n")
    f.write(
        "| Country | URLs | Perf | A11y | Best Practices | SEO | Last Scan |\n"
    )
    f.write(
        "|---------|------|------|------|----------------|-----|----------|\n"
    )
    for cc in all_countries:
        if cc not in lighthouse:
            continue
        d = lighthouse[cc]
        last = (d["last_scan"] or "—")[:10]
        f.write(
            f"| {cc} | {d['total']:,} | "
            f"{_pct(d.get('avg_performance'))} | "
            f"{_pct(d.get('avg_accessibility'))} | "
            f"{_pct(d.get('avg_best_practices'))} | "
            f"{_pct(d.get('avg_seo'))} | "
            f"{last} |\n"
        )
    f.write("\n")
    f.write(
        "> Scores are averages across all successfully audited URLs, "
        "displayed as 0–100 (multiply source values × 100).\n\n"
    )


def _write_pending_sections(
    f,
    url_val: dict[str, dict],
    social: dict[str, dict],
) -> None:
    """Highlight countries that still need a particular scan type."""
    not_social = sorted(set(url_val) - set(social))
    not_url_val = sorted(set(social) - set(url_val))

    if not_social:
        f.write("## Countries Pending Social Media Scan\n\n")
        f.write(
            "These countries have URL validation data but have not yet been "
            "scanned for social media links:\n\n"
        )
        f.write(", ".join(f"`{cc}`" for cc in not_social) + "\n\n")

    if not_url_val:
        f.write("## Countries With Social Scan But No URL Validation\n\n")
        f.write(
            "These countries have social media scan data but no URL "
            "validation data (URL validation may have been skipped because "
            "the social scan already confirmed reachability):\n\n"
        )
        f.write(", ".join(f"`{cc}`" for cc in not_url_val) + "\n\n")


def _write_priority_guide(f) -> None:
    """Write the scan priority guide section."""
    f.write("## Scan Priority Guide\n\n")
    f.write(
        "Scans are ordered from **highest** to **lowest** priority:\n\n"
    )
    f.write(
        "1. **Social Media Scan** — runs every 3 hours; downloads and "
        "parses full pages, confirming reachability *and* detecting social "
        "links in one pass.\n"
    )
    f.write(
        "2. **Technology Scan** — run on demand; detects CMS, framework, "
        "and analytics platforms.\n"
    )
    f.write(
        "3. **Lighthouse Scan** — run on demand; measures performance, "
        "accessibility (WCAG), best practices, and SEO for each URL.\n"
    )
    f.write(
        "4. **URL Validation** — runs every 6 hours in the background; "
        "a lightweight redirect/404 check that is **automatically skipped** "
        "for URLs already confirmed reachable by a higher-priority scan "
        "within the last 30 days.\n"
    )
    f.write("\n")
    f.write(
        "> **Tip:** Run a social media scan first for a new country — "
        "this simultaneously validates all URLs *and* collects social "
        "media data, avoiding a separate URL-only pass.\n"
    )


def _write_report(
    conn: sqlite3.Connection,
    output_path: Path,
    generated_at: str,
    available: dict[str, int] | None = None,
) -> None:
    """Query the database and write the Markdown report."""

    url_val = _query_url_validation(conn)
    social = _query_social_media(conn)
    platforms = _query_social_media_platforms(conn)
    tech = _query_technology(conn)
    lighthouse = _query_lighthouse(conn)

    all_countries = sorted(set(url_val) | set(social) | set(tech) | set(lighthouse))

    with output_path.open("w", encoding="utf-8") as f:
        f.write("# Scan Progress Report\n\n")
        f.write(f"_Generated: {generated_at}_\n\n")
        f.write(
            "This report tracks how far along each scan type is across all "
            "countries. It is regenerated automatically after every scan run.\n\n"
        )

        totals = _write_overall_coverage(f, url_val, social, tech, lighthouse, available)
        uv_total, uv_valid, sm_total, sm_reachable, tech_total = totals

        _write_url_validation_table(f, url_val, all_countries)
        _write_social_media_table(f, social, all_countries)
        _write_social_media_platform_breakdown(f, platforms, all_countries)
        _write_technology_table(f, tech, all_countries)
        _write_lighthouse_table(f, lighthouse, all_countries)
        _write_pending_sections(f, url_val, social)
        _write_priority_guide(f)

    lh_total = sum(d["total"] for d in lighthouse.values())
    # Print console summary
    print("\n" + "=" * 70)
    print("SCAN PROGRESS SUMMARY")
    print("=" * 70)
    print(f"URL Validation : {uv_valid:,} / {uv_total:,} URLs valid")
    print(f"Social Media   : {sm_reachable:,} / {sm_total:,} URLs reachable")
    print(f"Technology     : {tech_total:,} URLs scanned")
    print(f"Lighthouse     : {lh_total:,} URLs scanned")
    print(f"Countries      : {len(all_countries)} with data")
    print("=" * 70)


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description=(
            "Generate a multi-scan progress report showing URL validation, "
            "social media scan, and technology scan coverage."
        )
    )
    parser.add_argument(
        "--output",
        "-o",
        help="Output file path for the report (default: docs/scan-progress.md)",
        type=Path,
        default=Path("docs/scan-progress.md"),
    )
    parser.add_argument(
        "--db",
        help="Database file path (overrides settings)",
        type=Path,
    )
    parser.add_argument(
        "--update-index",
        help=(
            "Path to docs/index.md (or similar) whose "
            "<!-- SCAN_PROGRESS_START/END --> block should be updated with "
            "the latest scan summary (default: docs/index.md)"
        ),
        type=Path,
        nargs="?",
        const=Path("docs/index.md"),
        default=None,
        metavar="INDEX_PATH",
    )
    parser.add_argument(
        "--toon-dir",
        help=(
            "Path to the TOON seed files directory used to determine total "
            "available pages per country "
            "(default: data/toon-seeds/countries)"
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

    toon_dir = args.toon_dir if args.toon_dir.is_dir() else None

    try:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        generate_progress_report(db_path, args.output, toon_dir=toon_dir)
        if args.update_index is not None:
            update_index_progress(args.update_index, db_path, toon_dir=toon_dir)
    except Exception as exc:
        print(f"Error generating report: {exc}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
