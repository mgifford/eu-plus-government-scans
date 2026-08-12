"""Generate the country-by-service third-party dependency matrix.

The relationship dataset records which external hosts each government page loads
assets from.  Rendered as a node-link graph that signal is invisible: the shape
is hub-and-spoke with half the nodes as leaves, and a country like the UK has
tens of thousands of dependency edges against a graph budget of 150.

The same data as a country x service matrix answers the question directly --
"which external services do government sites depend on, and how widely" -- in a
form that stays readable at full size.

Each cell is the share of a country's scanned government domains that load at
least one asset from that service.  Distinct domains rather than edge counts, so
one heavily-crawled site cannot dominate a country's row.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from src.lib.country_utils import (
    country_code_to_display_name,
    country_filename_to_code,
    iter_seed_toon_files,
)
from src.lib.relationship_shards import iter_rows

# Relationship types that represent a loaded asset rather than a navigable link.
# A link to a social platform is an editorial choice; a script load is a runtime
# dependency, which is the question this page is about.
DEPENDENCY_TYPES = frozenset({
    "script_dependency",
    "stylesheet_dependency",
    "font_or_preload_dependency",
    "image_or_media_dependency",
})

DEFAULT_TOON_DIR = Path("data/toon-seeds/countries")
DEFAULT_SHARD_DIR = Path("docs/data/relationships")
DEFAULT_PAGE = Path("docs/dependency-matrix.md")
DEFAULT_JSON = Path("docs/data/dependency-matrix.json")
DEFAULT_CSV = Path("docs/data/dependency-matrix.csv")

# Buckets are fixed rather than quantiles so a cell means the same thing between
# runs and between countries.  Upper bound is exclusive.
BUCKETS: tuple[tuple[float, str], ...] = (
    (0.0, "b0"),
    (10.0, "b1"),
    (25.0, "b2"),
    (50.0, "b3"),
    (75.0, "b4"),
    (100.01, "b5"),
)


def build_country_index(toon_dir: Path) -> dict[str, str]:
    """Map registrable domain to country code, from the seed files.

    Relationship rows carry the *registrable* domain of the source, while the
    seeds list canonical hostnames that are often subdomains, so the two are
    matched at the registrable level.  Deriving the country from the TLD instead
    -- as the network page does -- invents countries out of ``.scot``, ``.cat``
    and ``.com``; this resolves 98% of source domains to a real seed country.

    Args:
        toon_dir: Directory holding the per-country seed files.

    Returns:
        Registrable domain to country code.
    """
    from tldextract import TLDExtract

    # Offline: never fetch the public suffix list during a report build.
    extract = TLDExtract(suffix_list_urls=())

    index: dict[str, str] = {}
    for path in iter_seed_toon_files(toon_dir):
        country_code = country_filename_to_code(path.stem)
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        for entry in data.get("domains", []):
            hostname = (entry.get("canonical_domain") or "").lower()
            if not hostname:
                continue
            registrable = extract("https://" + hostname).registered_domain or hostname
            index.setdefault(registrable, country_code)
    return index


def build_matrix(
    rows: Iterable[dict],
    country_index: dict[str, str],
    top_services: int = 20,
) -> dict:
    """Aggregate relationship rows into the country-by-service matrix.

    Args:
        rows: Relationship rows.
        country_index: Registrable domain to country code.
        top_services: How many services to keep, ranked by how many countries
            they appear in and then by how many domains depend on them.

    Returns:
        The matrix payload, ready to serialise.
    """
    scanned: dict[str, set[str]] = defaultdict(set)
    depends: dict[tuple[str, str], set[str]] = defaultdict(set)
    service_countries: dict[str, set[str]] = defaultdict(set)
    service_domains: dict[str, set[str]] = defaultdict(set)

    for row in rows:
        # A retired dependency is part of the history, not of today's corpus.
        if row.get("active") is False:
            continue

        source = row.get("source_domain", "")
        country = country_index.get(source.lower())
        if country is None:
            continue
        scanned[country].add(source)

        if row.get("relationship_type") not in DEPENDENCY_TYPES:
            continue
        if row.get("target_category") == "known_government":
            continue

        service = row.get("target_domain", "")
        if not service:
            continue
        depends[(country, service)].add(source)
        service_countries[service].add(country)
        service_domains[service].add(source)

    services = sorted(
        service_countries,
        key=lambda s: (-len(service_countries[s]), -len(service_domains[s]), s),
    )[:top_services]

    countries = sorted(scanned, key=lambda c: (-len(scanned[c]), c))

    cells: list[dict] = []
    for country in countries:
        total = len(scanned[country])
        for service in services:
            domains = len(depends.get((country, service), ()))
            cells.append({
                "country_code": country,
                "country": country_code_to_display_name(country),
                "service": service,
                "domains": domains,
                "scanned_domains": total,
                "percent": round(domains / total * 100, 1) if total else 0.0,
            })

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "metric": (
            "Share of a country's scanned government domains that load at least "
            "one asset from the service."
        ),
        "dependency_types": sorted(DEPENDENCY_TYPES),
        "countries": [
            {
                "country_code": c,
                "country": country_code_to_display_name(c),
                "scanned_domains": len(scanned[c]),
            }
            for c in countries
        ],
        "services": [
            {
                "service": s,
                "countries": len(service_countries[s]),
                "domains": len(service_domains[s]),
            }
            for s in services
        ],
        "cells": cells,
    }


def bucket_for(percent: float) -> str:
    """Return the bucket class for a percentage.

    Zero gets its own bucket: "no dependency at all" is a different statement
    from "a small share", and the table renders it as an em dash rather than a
    pale colour that reads as a rounding artefact.
    """
    if percent <= 0:
        return "b0"
    for upper, name in BUCKETS[1:]:
        if percent < upper:
            return name
    return "b5"


def _write_csv(matrix: dict, path: Path) -> None:
    """Write one row per country/service pair, for independent verification."""
    path.parent.mkdir(parents=True, exist_ok=True)
    # UTF-8 BOM so the file opens directly in Excel, matching the other exports.
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow([
            "country_code", "country", "service",
            "domains_depending", "scanned_domains", "percent",
        ])
        for cell in matrix["cells"]:
            writer.writerow([
                cell["country_code"], cell["country"], cell["service"],
                cell["domains"], cell["scanned_domains"], cell["percent"],
            ])


def render_page(matrix: dict) -> str:
    """Render the matrix as an accessible HTML table inside a Jekyll page.

    The value is written into every cell, so colour is a redundant second
    encoding rather than the only one -- a heatmap that carries meaning in
    colour alone fails WCAG 1.4.1, and this table has to be readable in
    forced-colors mode and in print too.
    """
    countries = matrix["countries"]
    services = matrix["services"]
    by_key = {(c["country_code"], c["service"]): c for c in matrix["cells"]}

    lines: list[str] = [
        "---",
        "title: Third-Party Dependencies by Country",
        "layout: page",
        "---",
        "",
        "<!-- Generated by src/cli/generate_dependency_matrix.py — do not edit by hand. -->",
        "",
        f"_Generated {matrix['generated_at'][:16].replace('T', ' ')} UTC_",
        "",
        "Each cell is the share of that country's scanned government domains that load "
        "at least one asset — script, stylesheet, font or media — from that service. "
        "Counting distinct domains rather than requests keeps one heavily-crawled site "
        "from dominating a row.",
        "",
        "Services are ranked by how many countries they appear in. Download the backing "
        "data as [JSON](data/dependency-matrix.json) or "
        "[CSV](data/dependency-matrix.csv) to reproduce any figure here.",
        "",
        '<div class="dep-matrix-legend">',
        "  <span>Share of a country's domains:</span>",
        '  <span class="dep-key dep-b0">0</span>',
        '  <span class="dep-key dep-b1">&lt;10%</span>',
        '  <span class="dep-key dep-b2">10–24%</span>',
        '  <span class="dep-key dep-b3">25–49%</span>',
        '  <span class="dep-key dep-b4">50–74%</span>',
        '  <span class="dep-key dep-b5">75%+</span>',
        "</div>",
        "",
        '<div class="dep-matrix-scroll" tabindex="0" role="region" '
        'aria-label="Third-party dependency matrix, scrollable">',
        '<table class="dep-matrix">',
        "  <caption>Share of scanned government domains loading assets from each "
        f"third-party service, {len(countries)} countries by {len(services)} services."
        "</caption>",
        "  <thead>",
        '    <tr><th scope="col">Country</th>'
        '<th scope="col" class="dep-num">Domains</th>',
    ]
    for service in services:
        lines.append(
            f'      <th scope="col"><span class="dep-service">{service["service"]}</span></th>'
        )
    lines += ["    </tr>", "  </thead>", "  <tbody>"]

    for country in countries:
        lines.append("    <tr>")
        lines.append(f'      <th scope="row">{country["country"]}</th>')
        lines.append(f'      <td class="dep-num">{country["scanned_domains"]:,}</td>')
        for service in services:
            cell = by_key[(country["country_code"], service["service"])]
            percent = cell["percent"]
            bucket = bucket_for(percent)
            if percent == 0:
                lines.append(
                    f'      <td class="dep-cell dep-{bucket}">'
                    f'<span aria-hidden="true">—</span>'
                    f'<span class="sr-only">0 percent</span></td>'
                )
            else:
                label = (
                    f'{cell["domains"]} of {cell["scanned_domains"]} '
                    f'{country["country"]} domains load {service["service"]}'
                )
                # Whole percent keeps the column's decimal points aligned; a
                # non-zero value that rounds to nothing says "<1%" rather than
                # "0%", which would contradict the cell's own colour.  Exact
                # figures stay in the JSON and CSV.
                shown = "&lt;1%" if percent < 0.5 else f"{round(percent)}%"
                lines.append(
                    f'      <td class="dep-cell dep-{bucket}" title="{label}">'
                    f'{shown}</td>'
                )
        lines.append("    </tr>")

    lines += ["  </tbody>", "</table>", "</div>", ""]
    return "\n".join(lines)


def parse_args(args: list[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--toon-dir", type=Path, default=DEFAULT_TOON_DIR)
    parser.add_argument("--shard-dir", type=Path, default=DEFAULT_SHARD_DIR)
    parser.add_argument("--output", type=Path, default=DEFAULT_PAGE)
    parser.add_argument("--json-output", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--csv-output", type=Path, default=DEFAULT_CSV)
    parser.add_argument(
        "--top-services",
        type=int,
        default=20,
        help="Number of services to include as columns (default: 20).",
    )
    return parser.parse_args(args)


def main(args: list[str] | None = None) -> int:
    """Entry point."""
    parsed = parse_args(args)

    country_index = build_country_index(parsed.toon_dir)
    if not country_index:
        print(f"No seed files under {parsed.toon_dir}; nothing to do.")
        return 1

    matrix = build_matrix(
        iter_rows(parsed.shard_dir),
        country_index,
        top_services=parsed.top_services,
    )
    if not matrix["cells"]:
        print("No dependency relationships found; nothing to write.")
        return 1

    parsed.json_output.parent.mkdir(parents=True, exist_ok=True)
    parsed.json_output.write_text(
        json.dumps(matrix, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    _write_csv(matrix, parsed.csv_output)

    parsed.output.parent.mkdir(parents=True, exist_ok=True)
    parsed.output.write_text(render_page(matrix), encoding="utf-8")

    print(f"Wrote {parsed.output}")
    print(f"  {len(matrix['countries'])} countries x {len(matrix['services'])} services")
    print(f"  {parsed.json_output}")
    print(f"  {parsed.csv_output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
