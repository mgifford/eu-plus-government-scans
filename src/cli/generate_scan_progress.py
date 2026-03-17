"""CLI tool to generate a multi-scan progress report from the database.

Produces a Markdown summary that shows how far along each scan type
(URL validation, social media, technology) is across all countries,
so stakeholders can see overall coverage at a glance.
"""

from __future__ import annotations

import argparse
import sqlite3
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

from src.lib.settings import load_settings


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _progress_bar(completed: int, total: int, width: int = 20) -> str:
    """Return a simple ASCII progress bar."""
    if total == 0:
        return "░" * width + " (no data)"
    pct = completed / total
    filled = int(pct * width)
    bar = "█" * filled + "░" * (width - filled)
    return f"{bar} {pct * 100:.1f}%"


# ---------------------------------------------------------------------------
# report generation
# ---------------------------------------------------------------------------

def generate_progress_report(db_path: Path, output_path: Path) -> None:
    """Generate a comprehensive scan-progress report from the database."""

    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    if not db_path.exists():
        with output_path.open("w") as f:
            f.write("# Scan Progress Report\n\n")
            f.write(f"_Generated: {generated_at}_\n\n")
            f.write("No scan data available yet. Run a scan first.\n")
        print(f"Report generated (empty): {output_path}")
        return

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    try:
        _write_report(conn, output_path, generated_at)
    finally:
        conn.close()

    print(f"Report generated: {output_path}")


def _query_url_validation(conn: sqlite3.Connection) -> dict[str, dict]:
    """Return per-country URL validation stats from the database."""
    result: dict[str, dict] = {}
    for row in conn.execute(
        """
        SELECT country_code,
               COUNT(DISTINCT url)                                   AS total,
               SUM(CASE WHEN is_valid = 1       THEN 1 ELSE 0 END)  AS valid,
               SUM(CASE WHEN is_valid = 0       THEN 1 ELSE 0 END)  AS invalid,
               MAX(validated_at)                                     AS last_scan
        FROM url_validation_results
        GROUP BY country_code
        ORDER BY country_code
        """
    ):
        result[row["country_code"]] = dict(row)
    return result


def _query_social_media(conn: sqlite3.Connection) -> dict[str, dict]:
    """Return per-country social media scan stats from the database."""
    result: dict[str, dict] = {}
    for row in conn.execute(
        """
        SELECT country_code,
               COUNT(DISTINCT url)                                        AS total,
               SUM(CASE WHEN is_reachable = 1   THEN 1 ELSE 0 END)       AS reachable,
               SUM(CASE WHEN social_tier = 'twitter_only'  THEN 1 ELSE 0 END) AS twitter_only,
               SUM(CASE WHEN social_tier = 'modern_only'   THEN 1 ELSE 0 END) AS modern_only,
               SUM(CASE WHEN social_tier = 'mixed'         THEN 1 ELSE 0 END) AS mixed,
               SUM(CASE WHEN social_tier = 'no_social'     THEN 1 ELSE 0 END) AS no_social,
               SUM(CASE WHEN social_tier = 'unreachable'   THEN 1 ELSE 0 END) AS unreachable,
               MAX(scanned_at)                                             AS last_scan
        FROM url_social_media_results
        GROUP BY country_code
        ORDER BY country_code
        """
    ):
        result[row["country_code"]] = dict(row)
    return result


def _query_social_media_platforms(conn: sqlite3.Connection) -> dict[str, dict]:
    """Return per-country platform-level social media link counts.

    Counts the number of scanned pages that contain at least one link to each
    platform (Twitter, X, Bluesky, Mastodon), derived from the stored JSON lists.
    """
    result: dict[str, dict] = {}
    for row in conn.execute(
        """
        SELECT country_code,
               COUNT(DISTINCT url)                                            AS total,
               SUM(CASE WHEN twitter_links  != '[]' THEN 1 ELSE 0 END)       AS has_twitter,
               SUM(CASE WHEN x_links        != '[]' THEN 1 ELSE 0 END)       AS has_x,
               SUM(CASE WHEN bluesky_links  != '[]' THEN 1 ELSE 0 END)       AS has_bluesky,
               SUM(CASE WHEN mastodon_links != '[]' THEN 1 ELSE 0 END)       AS has_mastodon,
               SUM(CASE WHEN is_reachable = 1       THEN 1 ELSE 0 END)       AS reachable,
               SUM(CASE WHEN (twitter_links != '[]' OR x_links != '[]')
                             THEN 1 ELSE 0 END)                               AS has_any_legacy,
               SUM(CASE WHEN (bluesky_links != '[]' OR mastodon_links != '[]')
                             THEN 1 ELSE 0 END)                               AS has_any_modern
        FROM url_social_media_results
        GROUP BY country_code
        ORDER BY country_code
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


def _write_overall_coverage(
    f,
    url_val: dict[str, dict],
    social: dict[str, dict],
    tech: dict[str, dict],
) -> None:
    """Write the overall coverage section."""
    uv_total = sum(d["total"] for d in url_val.values())
    uv_valid = sum(d["valid"] for d in url_val.values())
    sm_total = sum(d["total"] for d in social.values())
    sm_reachable = sum(d["reachable"] for d in social.values())
    tech_total = sum(d["total"] for d in tech.values())

    f.write("## Overall Coverage\n\n")
    f.write("| Scan Type | URLs Scanned | Coverage |\n")
    f.write("|-----------|-------------|----------|\n")
    f.write(
        f"| URL Validation | {uv_total:,} URLs "
        f"({uv_valid:,} valid) | "
        f"{_progress_bar(uv_valid, uv_total)} |\n"
    )
    f.write(
        f"| Social Media | {sm_total:,} URLs scanned "
        f"({sm_reachable:,} reachable) | "
        f"{_progress_bar(sm_reachable, sm_total)} |\n"
    )
    f.write(
        f"| Technology | {tech_total:,} URLs scanned | "
        f"{'(manual scan)' if tech_total == 0 else _progress_bar(tech_total, sm_total or uv_total or 1)} |\n"
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
    f.write("| Country | Total | Valid | Invalid | Last Scan | Coverage |\n")
    f.write("|---------|-------|-------|---------|-----------|----------|\n")
    for cc in all_countries:
        if cc not in url_val:
            continue
        d = url_val[cc]
        last = (d["last_scan"] or "—")[:10]
        f.write(
            f"| {cc} | {d['total']:,} | {d['valid']:,} | "
            f"{d['invalid']:,} | {last} | "
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
        "Mixed | No Social | Last Scan |\n"
    )
    f.write(
        "|---------|---------|-----------|-------------|--------|"
        "-------|-----------|----------|\n"
    )
    for cc in all_countries:
        if cc not in social:
            continue
        d = social[cc]
        last = (d["last_scan"] or "—")[:10]
        f.write(
            f"| {cc} | {d['total']:,} | {d['reachable']:,} | "
            f"{d['twitter_only']:,} | {d['modern_only']:,} | "
            f"{d['mixed']:,} | {d['no_social']:,} | {last} |\n"
        )
    f.write("\n")


def _write_social_media_platform_breakdown(
    f, platforms: dict[str, dict], all_countries: list[str]
) -> None:
    """Write a per-platform social media link count table.

    Shows how many reachable pages per country contain at least one link to
    each individual platform (Twitter, X, Bluesky, Mastodon).
    """
    if not platforms:
        return

    # Aggregate totals for the summary row
    total_reachable = sum(d["reachable"] for d in platforms.values())
    total_twitter = sum(d["has_twitter"] for d in platforms.values())
    total_x = sum(d["has_x"] for d in platforms.values())
    total_bluesky = sum(d["has_bluesky"] for d in platforms.values())
    total_mastodon = sum(d["has_mastodon"] for d in platforms.values())
    total_legacy = sum(d["has_any_legacy"] for d in platforms.values())
    total_modern = sum(d["has_any_modern"] for d in platforms.values())

    f.write("## Social Media Platform Breakdown\n\n")
    f.write(
        "Number of **reachable** pages per country that link to each platform. "
        "A page may link to more than one platform.\n\n"
    )
    f.write(
        "| Country | Reachable | Twitter | X | Bluesky | Mastodon "
        "| Legacy % | Modern % |\n"
    )
    f.write(
        "|---------|-----------|---------|---|---------|----------"
        "|----------|----------|\n"
    )
    for cc in all_countries:
        if cc not in platforms:
            continue
        d = platforms[cc]
        r = d["reachable"]
        if r > 0:
            legacy_pct = f"{d['has_any_legacy'] / r * 100:.1f}%"
            modern_pct = f"{d['has_any_modern'] / r * 100:.1f}%"
        else:
            legacy_pct = "—"
            modern_pct = "—"
        f.write(
            f"| {cc} | {d['reachable']:,} | {d['has_twitter']:,} | "
            f"{d['has_x']:,} | {d['has_bluesky']:,} | {d['has_mastodon']:,} | "
            f"{legacy_pct} | {modern_pct} |\n"
        )

    # Summary / totals row
    if total_reachable > 0:
        summary_legacy = f"**{total_legacy / total_reachable * 100:.1f}%**"
        summary_modern = f"**{total_modern / total_reachable * 100:.1f}%**"
    else:
        summary_legacy = "**—**"
        summary_modern = "**—**"
    f.write(
        f"| **Total** | **{total_reachable:,}** | **{total_twitter:,}** | "
        f"**{total_x:,}** | **{total_bluesky:,}** | **{total_mastodon:,}** | "
        f"{summary_legacy} | {summary_modern} |\n"
    )
    f.write("\n")

    # Narrative summary
    f.write(
        "> **Legacy platforms** (Twitter / X) vs **modern open platforms** "
        "(Bluesky / Mastodon) — percentages are share of reachable pages "
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
        "3. **URL Validation** — runs every 6 hours in the background; "
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


def _write_report(conn: sqlite3.Connection, output_path: Path, generated_at: str) -> None:
    """Query the database and write the Markdown report."""

    url_val = _query_url_validation(conn)
    social = _query_social_media(conn)
    platforms = _query_social_media_platforms(conn)
    tech = _query_technology(conn)

    all_countries = sorted(set(url_val) | set(social) | set(tech))

    with output_path.open("w", encoding="utf-8") as f:
        f.write("# Scan Progress Report\n\n")
        f.write(f"_Generated: {generated_at}_\n\n")
        f.write(
            "This report tracks how far along each scan type is across all "
            "countries. It is regenerated automatically after every scan run.\n\n"
        )

        totals = _write_overall_coverage(f, url_val, social, tech)
        uv_total, uv_valid, sm_total, sm_reachable, tech_total = totals

        _write_url_validation_table(f, url_val, all_countries)
        _write_social_media_table(f, social, all_countries)
        _write_social_media_platform_breakdown(f, platforms, all_countries)
        _write_technology_table(f, tech, all_countries)
        _write_pending_sections(f, url_val, social)
        _write_priority_guide(f)

    # Print console summary
    print("\n" + "=" * 70)
    print("SCAN PROGRESS SUMMARY")
    print("=" * 70)
    print(f"URL Validation : {uv_valid:,} / {uv_total:,} URLs valid")
    print(f"Social Media   : {sm_reachable:,} / {sm_total:,} URLs reachable")
    print(f"Technology     : {tech_total:,} URLs scanned")
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

    args = parser.parse_args()

    if args.db:
        db_path = args.db
    else:
        settings = load_settings()
        db_path = Path(settings.metadata_db_url.replace("sqlite:///", ""))

    try:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        generate_progress_report(db_path, args.output)
    except Exception as exc:
        print(f"Error generating report: {exc}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
