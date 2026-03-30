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
import math
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
            COUNT(DISTINCT CASE WHEN facebook_links != '[]' THEN url ELSE NULL END)  AS facebook_pages,
            COUNT(DISTINCT CASE WHEN linkedin_links != '[]' THEN url ELSE NULL END)  AS linkedin_pages,
            MIN(scanned_at)                                                             AS first_scan,
            MAX(scanned_at)                                                             AS last_scan
        FROM url_social_media_results
        """
    ).fetchone()
    if row is None:
        return {}
    return dict(row)


def _query_by_country(conn: sqlite3.Connection) -> list[dict]:
    """Return per-country social media platform totals with tier breakdown.

    Uses COUNT(DISTINCT CASE WHEN … THEN url END) so that each URL is counted
    at most once per country, even when a URL appears in multiple scan batches.
    Includes both per-platform link counts and social-tier distribution for
    use in the per-country tables on the social media stats page.
    """
    rows = conn.execute(
        """
        SELECT
            country_code,
            COUNT(DISTINCT url)                                                                                    AS total_scanned,
            COUNT(DISTINCT CASE WHEN is_reachable = 1               THEN url ELSE NULL END)                        AS reachable,
            COUNT(DISTINCT CASE WHEN twitter_links != '[]'          THEN url ELSE NULL END)                        AS twitter_pages,
            COUNT(DISTINCT CASE WHEN x_links       != '[]'          THEN url ELSE NULL END)                        AS x_pages,
            COUNT(DISTINCT CASE WHEN bluesky_links  != '[]'         THEN url ELSE NULL END)                        AS bluesky_pages,
            COUNT(DISTINCT CASE WHEN mastodon_links != '[]'         THEN url ELSE NULL END)                        AS mastodon_pages,
            COUNT(DISTINCT CASE WHEN facebook_links != '[]'         THEN url ELSE NULL END)                        AS facebook_pages,
            COUNT(DISTINCT CASE WHEN linkedin_links != '[]'         THEN url ELSE NULL END)                        AS linkedin_pages,
            COUNT(DISTINCT CASE WHEN social_tier = 'twitter_only'   THEN url ELSE NULL END)                        AS twitter_only,
            COUNT(DISTINCT CASE WHEN social_tier = 'modern_only'    THEN url ELSE NULL END)                        AS modern_only,
            COUNT(DISTINCT CASE WHEN social_tier = 'mixed'          THEN url ELSE NULL END)                        AS mixed,
            COUNT(DISTINCT CASE WHEN social_tier = 'no_social'      THEN url ELSE NULL END)                        AS no_social,
            COUNT(DISTINCT CASE WHEN (twitter_links != '[]' OR x_links != '[]'
                                      OR facebook_links != '[]'
                                      OR linkedin_links != '[]')     THEN url ELSE NULL END)                        AS has_any_legacy,
            COUNT(DISTINCT CASE WHEN (bluesky_links != '[]' OR mastodon_links != '[]')      THEN url ELSE NULL END) AS has_any_modern,
            MIN(scanned_at)                                                                                         AS first_scan,
            MAX(scanned_at)                                                                                         AS last_scan
        FROM url_social_media_results
        GROUP BY country_code
        ORDER BY country_code
        """
    ).fetchall()
    return [dict(r) for r in rows]


# ---------------------------------------------------------------------------
# SVG pie chart builder
# ---------------------------------------------------------------------------

def _build_pie_svg(
    twitter_only: int,
    modern_only: int,
    mixed: int,
    no_social: int,
    pie_aria: str,
) -> list[str]:
    """Return lines of an inline, accessible SVG pie chart.

    The chart is self-contained (no external dependencies) and fully accessible:
    each segment carries a ``<title>`` element, and the root ``<svg>`` element
    is linked to ``<title>`` and ``<desc>`` elements via ``aria-labelledby``.
    SVG is preferred over ``<canvas>`` because SVG elements live in the DOM and
    are natively traversable by assistive technologies without JavaScript.
    """
    total = twitter_only + modern_only + mixed + no_social
    if total == 0:
        return ['<p style="font-size:0.85em;color:#666;text-align:center;">No data available.</p>']

    def pct(n: int) -> str:
        return f"{n / total * 100:.1f}%" if total else "0.0%"

    segments = [
        (twitter_only, "#1a8cd8", "Twitter/X only"),
        (modern_only, "#0085ff", "Modern only"),
        (mixed,       "#7856ff", "Mixed"),
        (no_social,   "#cccccc", "No Social"),
    ]

    cx, cy, r = 120, 110, 90
    paths: list[str] = []
    current_angle = -math.pi / 2  # start at 12 o'clock

    for count, color, label in segments:
        if count == 0:
            continue
        angle = 2 * math.pi * count / total
        # Guard against single full-circle segment
        if total == count:
            paths.append(
                f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{color}">'
                f'<title>{label}: {count:,} ({pct(count)})</title></circle>'
            )
            break
        end_angle = current_angle + angle
        x1 = cx + r * math.cos(current_angle)
        y1 = cy + r * math.sin(current_angle)
        x2 = cx + r * math.cos(end_angle)
        y2 = cy + r * math.sin(end_angle)
        large_arc = 1 if angle > math.pi else 0
        paths.append(
            f'<path d="M {cx},{cy} L {x1:.3f},{y1:.3f} A {r},{r} 0 {large_arc},1'
            f' {x2:.3f},{y2:.3f} Z" fill="{color}" stroke="#fff" stroke-width="1">'
            f'<title>{label}: {count:,} ({pct(count)})</title></path>'
        )
        current_angle = end_angle

    # Legend below the circle
    legend: list[str] = []
    ly = cy + r + 16
    for count, color, label in segments:
        legend.append(f'<rect x="20" y="{ly}" width="14" height="14" fill="{color}"/>')
        legend.append(
            f'<text x="40" y="{ly + 11}" font-size="11"'
            f' font-family="sans-serif" fill="#333">'
            f'{label} ({pct(count)})</text>'
        )
        ly += 22

    svg_height = ly + 10
    return [
        f'<svg role="img" aria-labelledby="pie-title pie-desc"'
        f' viewBox="0 0 240 {svg_height}" width="240" height="{svg_height}"'
        f' xmlns="http://www.w3.org/2000/svg">',
        '<title id="pie-title">Social media tier distribution</title>',
        f'<desc id="pie-desc">{pie_aria}</desc>',
        *paths,
        *legend,
        '</svg>',
    ]


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
            provided, the block includes per-country breakdown tables, a pie
            chart, sortable table, and accessible tooltips for small numbers.
        seed_counts: Mapping of country_code → available page count from
            toon seed files.  Used for the "Available" column in the per-country
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
    twitter = summary.get("twitter_pages") or 0
    x_pages = summary.get("x_pages") or 0
    bluesky = summary.get("bluesky_pages") or 0
    mastodon = summary.get("mastodon_pages") or 0
    facebook = summary.get("facebook_pages") or 0
    linkedin = summary.get("linkedin_pages") or 0
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
        l = _month(last)
        if f and l:
            return f if f == l else f"{f} – {l}"
        return f or l or "—"

    lines = [
        _STATS_MARKER_START,
        "",
    ]

    # Pre-compute per-country totals (needed for pie chart and total rows).
    # The SVG pie chart is added first (float:right) so that the stats text
    # that follows wraps around it.
    if by_country:
        seed_counts = seed_counts or {}
        tot_scanned = sum(r["total_scanned"] for r in by_country)
        tot_avail = sum(seed_counts.values())
        tot_reachable = sum(r["reachable"] for r in by_country)
        tot_twitter_only = sum(r.get("twitter_only", 0) for r in by_country)
        tot_modern_only = sum(r.get("modern_only", 0) for r in by_country)
        tot_mixed = sum(r.get("mixed", 0) for r in by_country)
        tot_no_social = sum(r.get("no_social", 0) for r in by_country)
        tot_tw = sum(r.get("twitter_pages", 0) for r in by_country)
        tot_x = sum(r.get("x_pages", 0) for r in by_country)
        tot_bsky = sum(r.get("bluesky_pages", 0) for r in by_country)
        tot_mast = sum(r.get("mastodon_pages", 0) for r in by_country)
        tot_fb = sum(r.get("facebook_pages", 0) for r in by_country)
        tot_li = sum(r.get("linkedin_pages", 0) for r in by_country)

        # SVG pie chart: floated right so the stats text wraps to its left.
        # SVG is preferred over <canvas> because SVG elements live in the DOM
        # and are natively traversable by assistive technologies without JS.
        # Use the pie total (classified pages only) as the denominator so the
        # percentages in <desc> are consistent with the segment <title> elements.
        pie_total = tot_twitter_only + tot_modern_only + tot_mixed + tot_no_social
        pie_aria = (
            f"Pie chart: social media tier distribution across {tot_scanned:,} scanned pages. "
            f"Legacy only: {tot_twitter_only:,} ({_pct(tot_twitter_only, tot_scanned)}), "
            f"Modern only: {tot_modern_only:,} ({_pct(tot_modern_only, tot_scanned)}), "
            f"Mixed: {tot_mixed:,} ({_pct(tot_mixed, tot_scanned)}), "
            f"No Social: {tot_no_social:,} ({_pct(tot_no_social, tot_scanned)})"
        )
        lines += [
            '<div id="sm-tier-pie-container" style="float:right;margin:0 0 1rem 1.5rem;'
            'width:260px;max-width:45%;">',
            *_build_pie_svg(
                tot_twitter_only, tot_modern_only, tot_mixed, tot_no_social,
                pie_aria,
            ),
            '<p style="text-align:center;font-size:0.75em;margin:0.3rem 0 0;'
            'color:#555;font-style:italic;">Social media tier distribution</p>',
            '</div>',
            "",
        ]

    lines += [
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
    ]

    # Platform overview table
    lines += [
        "**Legacy social media** (older, centralised platforms):",
        "",
        "| Platform | Pages with link | % of scanned | % of reachable |",
        "|----------|----------------|:------------:|:--------------:|",
        f"| 🐦 Twitter | **{twitter:,}** | {_pct(twitter, scanned)} | {_pct(twitter, reachable)} |",
        f"| ✖ X | **{x_pages:,}** | {_pct(x_pages, scanned)} | {_pct(x_pages, reachable)} |",
        f"| 👍 Facebook | **{facebook:,}** | {_pct(facebook, scanned)} | {_pct(facebook, reachable)} |",
        f"| 💼 LinkedIn | **{linkedin:,}** | {_pct(linkedin, scanned)} | {_pct(linkedin, reachable)} |",
        "",
        "**Modern / open social media** (decentralised or open platforms):",
        "",
        "| Platform | Pages with link | % of scanned | % of reachable |",
        "|----------|----------------|:------------:|:--------------:|",
        f"| 🦋 Bluesky | **{bluesky:,}** | {_pct(bluesky, scanned)} | {_pct(bluesky, reachable)} |",
        f"| 🐘 Mastodon / Fediverse | **{mastodon:,}** | {_pct(mastodon, scanned)} | {_pct(mastodon, reachable)} |",
    ]

    if by_country:
        lines += [
            "",
            '<div style="clear:both;"></div>',
        ]

    lines += [
        "",
        "📥 Machine-readable results: "
        "[social-media-data.json](social-media-data.json)",
    ]

    # Per-country breakdown table
    # Column order: Country | Scanned | Available | Reachable | No Social |
    #   Legacy-only | Twitter | X | Facebook | LinkedIn |
    #   Modern | Mixed | Bluesky | Mastodon | Scan Period
    #
    # "Available" = total pages in the TOON seed file (all government pages tracked).
    # "Reachable" = pages that returned a valid HTTP response when scanned
    #               (not 404 / 500 / timeout).
    if by_country:
        lines += [
            "",
            "---",
            "",
            "## Social Media Scan by Country",
            "",
            "**Available**: all government pages tracked in our domain list. "
            "**Reachable**: of those scanned, pages that returned a valid HTTP response "
            "(not an error or timeout). "
            "Tier columns classify each page by its overall social media presence; "
            "platform columns count pages with at least one link to that platform — "
            "a page may appear in more than one platform column.",
            "",
            "| Country | Scanned | Available | Reachable | No Social | Legacy-only |"
            " Twitter | X | Facebook | LinkedIn | Modern | Mixed | Bluesky | Mastodon | Scan Period |",
            "|---------|---------|-----------|-----------|-----------|-------------|"
            "---------|---|----------|----------|--------|-------|---------|----------|-------------|",
        ]
        for row in by_country:
            cc = row["country_code"]
            available = seed_counts.get(cc, 0)
            avail_str = f"{available:,}" if available else "—"
            period = _scan_period(row.get("first_scan"), row.get("last_scan"))
            lines.append(
                f"| {cc} | {row['total_scanned']:,} | {avail_str} | {row['reachable']:,} | "
                f"{row.get('no_social', 0):,} | {row.get('twitter_only', 0):,} | "
                f"{row.get('twitter_pages', 0):,} | {row.get('x_pages', 0):,} | "
                f"{row.get('facebook_pages', 0):,} | {row.get('linkedin_pages', 0):,} | "
                f"{row.get('modern_only', 0):,} | {row.get('mixed', 0):,} | "
                f"{row.get('bluesky_pages', 0):,} | {row.get('mastodon_pages', 0):,} | "
                f"{period} |"
            )

        # totals row
        tot_avail_str = f"**{tot_avail:,}**" if tot_avail else "—"
        lines.append(
            f"| **Total** | **{tot_scanned:,}** | {tot_avail_str} | **{tot_reachable:,}** | "
            f"**{tot_no_social:,}** | **{tot_twitter_only:,}** | "
            f"**{tot_tw:,}** | **{tot_x:,}** | **{tot_fb:,}** | **{tot_li:,}** | "
            f"**{tot_modern_only:,}** | **{tot_mixed:,}** | "
            f"**{tot_bsky:,}** | **{tot_mast:,}** | — |"
        )

        lines += _build_interactive_block()


    lines += [
        "",
        _STATS_MARKER_END,
    ]
    return "\n".join(lines)


def _build_interactive_block() -> list[str]:
    """Return the CSS ``<style>`` and JavaScript ``<script>`` lines.

    The returned lines are appended at the end of the stats section.  They
    provide two interactive enhancements:

    1. Sortable column headers on the "Social Media Scan by Country" table.
    2. Accessible WCAG 2.2 AA tooltips (role="tooltip" + aria-describedby)
       for numeric cells whose value is less than 25.
    """
    css = """\
<style>
/* Pie chart container — floats right so stats text wraps to its left */
#sm-tier-pie-container { float: right; margin: 0 0 1rem 1.5rem; width: 260px; max-width: 45%; }

/* Accessible tooltip trigger */
.sm-tip {
  position: relative;
  display: inline-block;
  cursor: help;
  text-decoration: underline dotted;
  text-underline-offset: 2px;
}
/* Tooltip popup — hidden until hover/focus */
.sm-tooltip-popup {
  visibility: hidden;
  position: absolute;
  bottom: calc(100% + 6px);
  left: 50%;
  transform: translateX(-50%);
  background: #222;
  color: #fff;
  padding: 5px 9px;
  border-radius: 4px;
  font-size: 0.78em;
  white-space: normal;
  z-index: 200;
  min-width: 180px;
  max-width: 260px;
  line-height: 1.4;
}
.sm-tooltip-popup::after {
  content: '';
  position: absolute;
  top: 100%;
  left: 50%;
  transform: translateX(-50%);
  border: 5px solid transparent;
  border-top-color: #222;
}
/* Show tooltip on hover or keyboard focus */
.sm-tip:hover .sm-tooltip-popup,
.sm-tip:focus .sm-tooltip-popup { visibility: visible; }

/* Sortable table column headers */
.sm-sortable th[aria-sort] { cursor: pointer; white-space: nowrap; user-select: none; }
.sm-sortable th[aria-sort]:hover,
.sm-sortable th[aria-sort]:focus-visible { text-decoration: underline; outline: 2px solid currentColor; outline-offset: 2px; }
.sm-sortable th[aria-sort="ascending"]::after  { content: " ▲"; font-size: 0.75em; }
.sm-sortable th[aria-sort="descending"]::after { content: " ▼"; font-size: 0.75em; }
.sm-sortable th[aria-sort="none"]::after       { content: " ⇅"; font-size: 0.75em; opacity: 0.5; }
</style>"""

    js = """\
<script>
(function () {
  "use strict";

  // ── Accessible tooltips ──────────────────────────────────────────────────
  // Numbers < 25 in the country table get a WCAG 2.2 AA tooltip
  // (role="tooltip" + aria-describedby, visible on hover and keyboard focus).
  var _tipSeq = 0;

  function addTooltips() {
    var countryTable = _findCountryTable();
    if (!countryTable) return;

    var headers = Array.from(countryTable.querySelectorAll("thead th"));
    // Numeric columns are all except Country (0) and Scan Period
    var numericCols = [];
    headers.forEach(function (th, i) {
      var t = th.textContent.trim();
      if (t !== "Country" && t !== "Scan Period" && t !== "Non-X Score") {
        numericCols.push(i);
      }
    });

    countryTable.querySelectorAll("tbody tr").forEach(function (row) {
      var cells = row.querySelectorAll("td");
      // Skip the totals row
      if (cells[0] && cells[0].textContent.includes("Total")) return;
      numericCols.forEach(function (ci) {
        var cell = cells[ci];
        if (!cell) return;
        var raw = cell.textContent.replace(/,/g, "").trim();
        var n = parseInt(raw, 10);
        if (isNaN(n) || n <= 0 || n >= 25) return;
        var id = "sm-tip-" + (++_tipSeq);
        var country = cells[0] ? cells[0].textContent.trim() : "";
        var colName = headers[ci] ? headers[ci].textContent.trim() : "";
        // Store original value so sorting still works after innerHTML change
        cell.dataset.sortVal = String(n);
        cell.innerHTML =
          '<span class="sm-tip" tabindex="0" aria-describedby="' + id + '">' +
          cell.textContent +
          "</span>" +
          '<span role="tooltip" id="' + id + '" class="sm-tooltip-popup">' +
          colName + ": " + n + " for " + country +
          ". Small sample — interpret with caution." +
          "</span>";
      });
    });

    // Allow Escape key to dismiss any focused tooltip
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape") {
        var active = document.activeElement;
        if (active && active.classList.contains("sm-tip")) active.blur();
      }
    });
  }

  // ── Sortable column headers ──────────────────────────────────────────────
  function addSortable() {
    var countryTable = _findCountryTable();
    if (!countryTable) return;

    countryTable.classList.add("sm-sortable");
    var headers = Array.from(countryTable.querySelectorAll("thead th"));
    headers.forEach(function (th, ci) {
      th.setAttribute("aria-sort", "none");
      th.setAttribute("tabindex", "0");
      function doSort(e) {
        if (e.type === "keydown" && e.key !== "Enter" && e.key !== " ") return;
        if (e.type === "keydown") e.preventDefault();
        var asc = th.getAttribute("aria-sort") !== "ascending";
        headers.forEach(function (h) { h.setAttribute("aria-sort", "none"); });
        th.setAttribute("aria-sort", asc ? "ascending" : "descending");
        _sortTable(countryTable, ci, asc);
      }
      th.addEventListener("click", doSort);
      th.addEventListener("keydown", doSort);
    });
  }

  function _getCellVal(cell) {
    if (!cell) return null;
    // Prefer the data attribute set when a tooltip was injected
    if (cell.dataset && cell.dataset.sortVal !== undefined) {
      return parseInt(cell.dataset.sortVal, 10);
    }
    // Use textContent directly — CSS ::after pseudo-elements and Markdown bold
    // markers are not included in textContent, so no stripping is needed.
    var text = cell.textContent.trim();
    if (text === "—" || text === "") return null;
    if (text.endsWith("%")) return parseFloat(text) || 0;
    var n = parseInt(text.replace(/,/g, ""), 10);
    return isNaN(n) ? text.toLowerCase() : n;
  }

  function _sortTable(table, ci, asc) {
    var tbody = table.querySelector("tbody");
    if (!tbody) return;
    var rows = Array.from(tbody.querySelectorAll("tr"));
    // Pin the Total row to the bottom
    var pinned = null;
    if (rows.length && rows[rows.length - 1].textContent.includes("Total")) {
      pinned = rows.pop();
    }
    rows.sort(function (a, b) {
      var av = _getCellVal(a.querySelectorAll("td")[ci]);
      var bv = _getCellVal(b.querySelectorAll("td")[ci]);
      if (av === null) return asc ? 1 : -1;
      if (bv === null) return asc ? -1 : 1;
      if (typeof av === "number" && typeof bv === "number") return asc ? av - bv : bv - av;
      return asc
        ? String(av).localeCompare(String(bv))
        : String(bv).localeCompare(String(av));
    });
    rows.forEach(function (r) { tbody.appendChild(r); });
    if (pinned) tbody.appendChild(pinned);
  }}

  // ── Pie chart ────────────────────────────────────────────────────────────
  function _buildPie() {{
    var canvas = document.getElementById("sm-tier-pie");
    if (!canvas || !window.Chart) return;
    var total = SM_PIE.twitterOnly + SM_PIE.modernOnly + SM_PIE.mixed + SM_PIE.noSocial;
    function pct(n) {{ return total ? (n / total * 100).toFixed(1) + "%" : "—"; }}
    new Chart(canvas, {{
      type: "pie",
      data: {{
        labels: [
          "Legacy only (" + pct(SM_PIE.twitterOnly) + ")",
          "Modern only (" + pct(SM_PIE.modernOnly) + ")",
          "Mixed (" + pct(SM_PIE.mixed) + ")",
          "No Social (" + pct(SM_PIE.noSocial) + ")"
        ],
        datasets: [{{
          data: [SM_PIE.twitterOnly, SM_PIE.modernOnly, SM_PIE.mixed, SM_PIE.noSocial],
          backgroundColor: ["#1a8cd8", "#0085ff", "#7856ff", "#cccccc"],
          borderWidth: 1,
          borderColor: "#fff"
        }}]
      }},
      options: {{
        responsive: true,
        plugins: {{
          legend: {{ position: "bottom", labels: {{ font: {{ size: 11 }}, boxWidth: 14 }} }},
          tooltip: {{
            callbacks: {{
              label: function (ctx) {{
                var v = ctx.raw;
                var p = total ? (v / total * 100).toFixed(1) + "%" : "—";
                return " " + v.toLocaleString() + " pages (" + p + ")";
              }}
            }}
          }}
        }}
      }}
    }});
  }}

  function _loadChartJs() {{
    if (window.Chart) {{ _buildPie(); return; }}
    var s = document.createElement("script");
    s.src = "{_CHART_JS_CDN}";
    s.crossOrigin = "anonymous";
    s.onload = _buildPie;
    s.onerror = function () {{
      var c = document.getElementById("sm-tier-pie-container");
      if (c) {{
        c.innerHTML =
          '<p style="font-size:0.85em;color:#666;text-align:center;">' +
          "Chart unavailable. See the platform table for data." +
          "</p>";
      }}
    }};
    document.head.appendChild(s);
  }}

  // ── Helpers ──────────────────────────────────────────────────────────────
  function _findCountryTable() {
    var found = null;
    document.querySelectorAll("table").forEach(function (t) {
      t.querySelectorAll("th").forEach(function (th) {
        if (th.textContent.trim() === "Non-X Score") found = t;
      });
    });
    return found;
  }

  // ── Init ─────────────────────────────────────────────────────────────────
  function _init() {
    addTooltips();
    addSortable();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", _init);
  } else {
    _init();
  }
})();
</script>"""

    return ["", css, "", js]


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
            "facebook_pages": summary.get("facebook_pages") or 0,
            "linkedin_pages": summary.get("linkedin_pages") or 0,
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

    new_block = _build_stats_block(summary, generated_at, total_available, by_country, seed_counts)
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
