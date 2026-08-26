"""CLI tool to generate a technology–Lighthouse correlation report.

Joins ``url_tech_results`` with ``url_lighthouse_results`` on
``(url, country_code)`` to answer questions like:

* What are the average Lighthouse accessibility scores for Drupal sites
  vs WordPress sites across the monitored government domains?
* Do certain CMS platforms correlate with better or worse performance?
* Are there patterns across the ~90 sites being monitored?

Produces:

* ``docs/tech-lighthouse.md`` — Markdown report with per-technology
  Lighthouse score averages.
* ``docs/tech-lighthouse-data.json`` — machine-readable JSON with full
  per-URL drilldown data.
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

from src.lib.country_utils import country_code_to_display_name
from src.lib.settings import load_settings


# ---------------------------------------------------------------------------
# HTML comment markers
# ---------------------------------------------------------------------------

_MARKER_START = "<!-- TECH_LIGHTHOUSE_STATS_START -->"
_MARKER_END = "<!-- TECH_LIGHTHOUSE_STATS_END -->"


# ---------------------------------------------------------------------------
# Database queries
# ---------------------------------------------------------------------------

def _query_tech_lighthouse_join(conn: sqlite3.Connection) -> list[dict]:
    """Return per-URL rows joining technology detections with Lighthouse scores.

    Uses the latest scan for each URL from both tables.  Only includes URLs
    that have both a technology detection (non-empty) and a successful
    Lighthouse audit (no error, at least one score).
    """
    rows = conn.execute(
        """
        WITH latest_tech AS (
            SELECT url, country_code, technologies, scanned_at
            FROM url_tech_results AS t
            WHERE error_message IS NULL
              AND technologies != '{}'
              AND scanned_at = (
                  SELECT MAX(scanned_at)
                  FROM url_tech_results AS t2
                  WHERE t2.url = t.url
                    AND t2.country_code = t.country_code
                    AND t2.error_message IS NULL
              )
        ),
        latest_lighthouse AS (
            SELECT url, country_code,
                   performance_score, accessibility_score,
                   best_practices_score, seo_score, scanned_at
            FROM url_lighthouse_results AS l
            WHERE error_message IS NULL
              AND (performance_score IS NOT NULL
                   OR accessibility_score IS NOT NULL
                   OR best_practices_score IS NOT NULL
                   OR seo_score IS NOT NULL)
              AND scanned_at = (
                  SELECT MAX(scanned_at)
                  FROM url_lighthouse_results AS l2
                  WHERE l2.url = l.url
                    AND l2.country_code = l.country_code
                    AND l2.error_message IS NULL
              )
        )
        SELECT
            t.url,
            t.country_code,
            t.technologies,
            l.performance_score,
            l.accessibility_score,
            l.best_practices_score,
            l.seo_score
        FROM latest_tech t
        INNER JOIN latest_lighthouse l
            ON t.url = l.url AND t.country_code = l.country_code
        """
    ).fetchall()
    return [dict(r) for r in rows]


def _query_tech_only_count(conn: sqlite3.Connection) -> dict:
    """Return per-country counts of URLs with tech detections (no lighthouse join)."""
    result: dict[str, dict] = {}
    for row in conn.execute(
        """
        SELECT country_code,
               COUNT(DISTINCT url) AS total
        FROM url_tech_results
        WHERE error_message IS NULL
          AND technologies != '{}'
        GROUP BY country_code
        """
    ):
        result[row["country_code"]] = dict(row)
    return result


def _query_lighthouse_only_count(conn: sqlite3.Connection) -> dict:
    """Return per-country counts of URLs with lighthouse scores (no tech join)."""
    result: dict[str, dict] = {}
    for row in conn.execute(
        """
        SELECT country_code,
               COUNT(DISTINCT url) AS total
        FROM url_lighthouse_results
        WHERE error_message IS NULL
          AND (performance_score IS NOT NULL
               OR accessibility_score IS NOT NULL
               OR best_practices_score IS NOT NULL
               OR seo_score IS NOT NULL)
        GROUP BY country_code
        """
    ):
        result[row["country_code"]] = dict(row)
    return result


# ---------------------------------------------------------------------------
# Aggregation
# ---------------------------------------------------------------------------

def _parse_tech_names(raw: str) -> list[str]:
    """Extract technology names from a JSON technologies column."""
    try:
        techs = json.loads(raw or "{}")
    except (json.JSONDecodeError, TypeError):
        return []
    if not isinstance(techs, dict):
        return []
    return list(techs.keys())


def _aggregate_by_technology(rows: list[dict]) -> list[dict]:
    """Aggregate Lighthouse scores grouped by technology name.

    Returns a list of dicts sorted by page count descending, each with:
    technology, pages, avg_performance, avg_accessibility,
    avg_best_practices, avg_seo, countries.
    """
    tech_data: dict[str, dict] = {}

    for row in rows:
        tech_names = _parse_tech_names(row["technologies"])
        perf = row["performance_score"]
        a11y = row["accessibility_score"]
        bp = row["best_practices_score"]
        seo = row["seo_score"]
        cc = row["country_code"]

        for tech in tech_names:
            if tech not in tech_data:
                tech_data[tech] = {
                    "technology": tech,
                    "pages": 0,
                    "performance_scores": [],
                    "accessibility_scores": [],
                    "best_practices_scores": [],
                    "seo_scores": [],
                    "countries": set(),
                }
            d = tech_data[tech]
            d["pages"] += 1
            d["countries"].add(cc)
            if perf is not None:
                d["performance_scores"].append(perf)
            if a11y is not None:
                d["accessibility_scores"].append(a11y)
            if bp is not None:
                d["best_practices_scores"].append(bp)
            if seo is not None:
                d["seo_scores"].append(seo)

    result = []
    for tech, d in tech_data.items():
        def _avg(vals: list[float]) -> float | None:
            return round(sum(vals) / len(vals), 4) if vals else None

        result.append({
            "technology": tech,
            "pages": d["pages"],
            "countries": len(d["countries"]),
            "avg_performance": _avg(d["performance_scores"]),
            "avg_accessibility": _avg(d["accessibility_scores"]),
            "avg_best_practices": _avg(d["best_practices_scores"]),
            "avg_seo": _avg(d["seo_scores"]),
        })

    result.sort(key=lambda x: (-x["pages"], x["technology"]))
    return result


def _aggregate_by_country_and_technology(rows: list[dict]) -> dict[str, list[dict]]:
    """Aggregate Lighthouse scores grouped by (country, technology)."""
    cc_tech_data: dict[tuple[str, str], dict] = {}

    for row in rows:
        tech_names = _parse_tech_names(row["technologies"])
        cc = row["country_code"]
        perf = row["performance_score"]
        a11y = row["accessibility_score"]
        bp = row["best_practices_score"]
        seo = row["seo_score"]

        for tech in tech_names:
            key = (cc, tech)
            if key not in cc_tech_data:
                cc_tech_data[key] = {
                    "country_code": cc,
                    "technology": tech,
                    "pages": 0,
                    "performance_scores": [],
                    "accessibility_scores": [],
                    "best_practices_scores": [],
                    "seo_scores": [],
                }
            d = cc_tech_data[key]
            d["pages"] += 1
            if perf is not None:
                d["performance_scores"].append(perf)
            if a11y is not None:
                d["accessibility_scores"].append(a11y)
            if bp is not None:
                d["best_practices_scores"].append(bp)
            if seo is not None:
                d["seo_scores"].append(seo)

    by_country: dict[str, list[dict]] = defaultdict(list)
    for (cc, tech), d in cc_tech_data.items():
        def _avg(vals: list[float]) -> float | None:
            return round(sum(vals) / len(vals), 4) if vals else None

        by_country[cc].append({
            "technology": tech,
            "pages": d["pages"],
            "avg_performance": _avg(d["performance_scores"]),
            "avg_accessibility": _avg(d["accessibility_scores"]),
            "avg_best_practices": _avg(d["best_practices_scores"]),
            "avg_seo": _avg(d["seo_scores"]),
        })

    for cc in by_country:
        by_country[cc].sort(key=lambda x: (-x["pages"], x["technology"]))
    return dict(by_country)


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------

def _format_score(val: float | None) -> str:
    """Format a 0–1 Lighthouse score as a 0–100 integer string."""
    if val is None:
        return "—"
    return f"{val * 100:.0f}"


def _build_report_markdown(
    tech_rows: list[dict],
    generated_at: str,
    total_tech_urls: int,
    total_lighthouse_urls: int,
    total_overlap: int,
) -> str:
    """Build the Markdown report content."""
    by_tech = _aggregate_by_technology(tech_rows)

    lines = [
        "---",
        "title: Technology & Lighthouse Correlation",
        "layout: page",
        "---",
        "",
        "<!-- TECH_LIGHTHOUSE_STATS_START -->",
        "",
        f"_Generated: {generated_at}_",
        "",
        f"**{total_overlap:,}** URLs with both technology detection and Lighthouse scores",
        f"out of **{total_tech_urls:,}** technology-detected URLs and "
        f"**{total_lighthouse_urls:,}** Lighthouse-audited URLs",
        "",
        "---",
        "",
    ]

    if not by_tech:
        lines.append(
            "_No correlated data available yet. This report requires both "
            "technology detection (Wappalyzer) and Lighthouse scans to have "
            "processed the same URLs._\n"
        )
    else:
        # Overall technology summary table
        lines += [
            "## Lighthouse Scores by Technology (All Countries)",
            "",
            "Average Google Lighthouse scores (0–100) for pages where each "
            "technology was detected. Higher is better.",
            "",
            "| # | Technology | Pages | Countries | Perf | A11y | Best Prac | SEO |",
            "|--:|-----------|------:|----------:|-----:|-----:|----------:|----:|",
        ]
        for rank, t in enumerate(by_tech[:30], start=1):
            lines.append(
                f"| {rank} | {t['technology']} | **{t['pages']:,}** | "
                f"{t['countries']} | "
                f"{_format_score(t['avg_performance'])} | "
                f"{_format_score(t['avg_accessibility'])} | "
                f"{_format_score(t['avg_best_practices'])} | "
                f"{_format_score(t['avg_seo'])} |"
            )
        lines.append("")

        # Per-country breakdown for top technologies
        by_cc_tech = _aggregate_by_country_and_technology(tech_rows)

        lines += [
            "## Top Technologies by Country",
            "",
            "Average accessibility score (0–100) for the top 10 most-detected "
            "technologies, broken down by country.",
            "",
        ]

        # Build header
        all_countries = sorted(by_cc_tech.keys())
        headerCountries = [country_code_to_display_name(cc) for cc in all_countries[:15]]
        if len(all_countries) > 15:
            headerCountries.append("…")

        lines.append("| Technology | " + " | ".join(headerCountries) + " |")
        lines.append("|-----------|" + "|".join(["-----:"] * len(headerCountries)) + "|")

        for t in by_tech[:10]:
            cells = []
            for cc in all_countries[:15]:
                cc_techs = {x["technology"]: x for x in by_cc_tech.get(cc, [])}
                if t["technology"] in cc_techs:
                    cells.append(_format_score(cc_techs[t["technology"]]["avg_accessibility"]))
                else:
                    cells.append("—")
            lines.append(f"| {t['technology']} | " + " | ".join(cells) + " |")
        lines.append("")

    lines += [
        "---",
        "",
        "📥 Machine-readable results: "
        "[Download technology-Lighthouse correlation data (JSON)](tech-lighthouse-data.json)",
        "",
        "<!-- TECH_LIGHTHOUSE_STATS_END -->",
    ]

    return "\n".join(lines)


def generate_tech_lighthouse_report(
    db_path: Path,
    output_path: Path,
    data_path: Path,
) -> bool:
    """Generate the technology–Lighthouse correlation report.

    Args:
        db_path: Path to the SQLite metadata database.
        output_path: Output path for ``docs/tech-lighthouse.md``.
        data_path: Output path for ``docs/tech-lighthouse-data.json``.

    Returns ``True`` on success.
    """
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    if not db_path.exists():
        print(f"Database not found: {db_path}", file=sys.stderr)
        return False

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        tech_lh_rows = _query_tech_lighthouse_join(conn)
        tech_counts = _query_tech_only_count(conn)
        lh_counts = _query_lighthouse_only_count(conn)
    finally:
        conn.close()

    total_tech_urls = sum(d["total"] for d in tech_counts.values())
    total_lighthouse_urls = sum(d["total"] for d in lh_counts.values())
    total_overlap = len(set(r["url"] for r in tech_lh_rows))

    # Build markdown report
    md = _build_report_markdown(
        tech_lh_rows, generated_at, total_tech_urls, total_lighthouse_urls, total_overlap,
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(md, encoding="utf-8")
    print(f"Report written: {output_path}")

    # Build JSON data file
    by_tech = _aggregate_by_technology(tech_lh_rows)
    by_cc_tech = _aggregate_by_country_and_technology(tech_lh_rows)

    data = {
        "generated_at": generated_at,
        "summary": {
            "total_tech_urls": total_tech_urls,
            "total_lighthouse_urls": total_lighthouse_urls,
            "total_overlap": total_overlap,
        },
        "by_technology": by_tech,
        "by_country_and_technology": {
            cc: techs for cc, techs in sorted(by_cc_tech.items())
        },
    }
    data_path.parent.mkdir(parents=True, exist_ok=True)
    data_path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"Data file written: {data_path}")

    # Console summary
    print("\n" + "=" * 60)
    print("TECHNOLOGY–LIGHTHOUSE CORRELATION SUMMARY")
    print("=" * 60)
    print(f"Tech-detected URLs     : {total_tech_urls:,}")
    print(f"Lighthouse-audited URLs: {total_lighthouse_urls:,}")
    print(f"Overlap (both)         : {total_overlap:,}")
    if by_tech:
        print("\nTop 10 technologies by page count:")
        for t in by_tech[:10]:
            a11y = _format_score(t["avg_accessibility"])
            print(f"  {t['technology']}: {t['pages']:,} pages, a11y={a11y}")
    print("=" * 60)

    return True


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description=(
            "Generate a technology–Lighthouse correlation report showing "
            "average Lighthouse scores grouped by detected technology."
        )
    )
    parser.add_argument(
        "--page",
        help="Output Markdown path (default: docs/tech-lighthouse.md)",
        type=Path,
        default=Path("docs/tech-lighthouse.md"),
    )
    parser.add_argument(
        "--data",
        help="Output JSON path (default: docs/tech-lighthouse-data.json)",
        type=Path,
        default=Path("docs/tech-lighthouse-data.json"),
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
        ok = generate_tech_lighthouse_report(db_path, args.page, args.data)
        if not ok:
            sys.exit(1)
    except Exception as exc:
        print(f"Error generating report: {exc}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
