"""CLI tool to generate government domains listing pages from TOON seed files.

Reads all country TOON files and produces:

- An index page (``docs/domains.md``) listing every country with its domain
  and page counts, linking to that country's own page.
- One page per country (``docs/domains/<slug>.md``) containing the full
  domain table for that country only.

Splitting by country keeps each generated page a reasonable size — the
previous single-page report combined every country's table into one file
(~14 MB, 36k+ table rows for 31 countries), which was slow to download and
effectively unusable on mobile connections.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _load_toon(path: Path) -> dict:
    """Load and return a TOON JSON file, or empty dict on error."""
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"Warning: could not read {path}: {exc}", file=sys.stderr)
        return {}


def _country_sort_key(entry: tuple[str, dict]) -> str:
    """Sort key for (filename, toon_data) tuples: use country name."""
    _name, data = entry
    return data.get("country", "").lower()


def _page_link_label(url: str) -> str:
    """Build descriptive anchor text for page URLs.

    Args:
        url: Absolute page URL.

    Returns:
        Human-readable link text describing the destination page.
        Returns ``"Visit linked site"`` when the URL cannot be parsed or does
        not include a hostname.
    """
    try:
        parsed = urlparse(url)
    except ValueError:
        return "Visit linked site"
    if not parsed.hostname:
        return "Visit linked site"
    path = parsed.path if parsed.path and parsed.path != "/" else ""
    if not path:
        return f"Visit {parsed.hostname} homepage"
    return f"Visit {parsed.hostname}{path}"


def _write_country_page(
    output_path: Path, slug: str, country: str, data: dict
) -> None:
    """Write a single country's full domain table to its own page."""
    domains = data.get("domains", [])
    page_count = data.get("page_count", 0)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        f.write(
            f"---\ntitle: {country} Government Domains\nlayout: page\n"
            f"permalink: /domains/{slug}.html\n---\n\n"
        )
        f.write("[← Back to all countries](../domains.html)\n\n")
        f.write(f"**{len(domains):,} domains** · **{page_count:,} pages**\n\n")

        if domains:
            f.write("| Domain | Pages |\n")
            f.write("|--------|-------|\n")
            for domain_entry in sorted(
                domains, key=lambda d: d.get("canonical_domain", "")
            ):
                canonical = domain_entry.get("canonical_domain", "")
                pages = domain_entry.get("pages", [])
                page_links = ", ".join(
                    f"[{_page_link_label(p['url'])}]({p['url']})"
                    for p in pages[:3]
                )
                if len(pages) > 3:
                    page_links += f" _(+{len(pages) - 3} more)_"
                f.write(f"| `{canonical}` | {page_links} |\n")
        else:
            f.write("_No domains listed._\n")


# ---------------------------------------------------------------------------
# report generation
# ---------------------------------------------------------------------------

def generate_domains_report(
    toon_dir: Path, output_path: Path, countries_dir: Path | None = None
) -> None:
    """Generate the domains index page and per-country pages from TOON files.

    Args:
        toon_dir: Directory containing country TOON seed files.
        output_path: Path for the index page (e.g. ``docs/domains.md``).
        countries_dir: Directory for per-country pages (default:
            ``<output_path parent>/domains``).
    """

    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    if countries_dir is None:
        countries_dir = output_path.parent / "domains"

    toon_files = sorted(toon_dir.glob("*.toon"))
    if not toon_files:
        with output_path.open("w", encoding="utf-8") as f:
            f.write("---\ntitle: Government Domains\nlayout: page\n---\n\n")
            f.write(f"_Generated: {generated_at}_\n\n")
            f.write("No TOON seed files found.\n")
        print(f"Domains report generated (empty): {output_path}")
        return

    # Load all TOON data
    entries: list[tuple[str, dict]] = []
    for path in toon_files:
        data = _load_toon(path)
        if data:
            entries.append((path.stem, data))

    entries.sort(key=_country_sort_key)

    total_countries = len(entries)
    total_domains = sum(len(d.get("domains", [])) for _, d in entries)
    total_pages = sum(d.get("page_count", 0) for _, d in entries)

    # Per-country pages
    for slug, data in entries:
        country = data.get("country", "Unknown")
        _write_country_page(countries_dir / f"{slug}.md", slug, country, data)

    # Index page
    with output_path.open("w", encoding="utf-8") as f:
        f.write("---\ntitle: Government Domains\nlayout: page\n---\n\n")
        f.write(f"_Generated: {generated_at}_\n\n")
        f.write(
            "This page lists all government domains tracked in the dataset, "
            "grouped by country. Data is sourced from the "
            "[TOON seed files](https://github.com/mgifford/eu-plus-government-scans"
            "/tree/main/data/toon-seeds/countries) in the repository. Each "
            "country's full domain list is on its own page to keep page size "
            "manageable.\n\n"
        )
        f.write(
            f"**{total_countries} countries** · "
            f"**{total_domains:,} domains** · "
            f"**{total_pages:,} pages**\n\n"
        )

        f.write("## Countries\n\n")
        f.write("| Country | Domains | Pages |\n")
        f.write("|---------|---------|-------|\n")
        for slug, data in entries:
            country = data.get("country", "Unknown")
            domain_count = len(data.get("domains", []))
            page_count = data.get("page_count", 0)
            f.write(
                f"| [{country}](domains/{slug}.html) "
                f"| {domain_count:,} | {page_count:,} |\n"
            )

    print(
        f"Domains report generated: {output_path} "
        f"({total_countries} countries, {total_domains:,} domains, "
        f"per-country pages in {countries_dir})"
    )


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description=(
            "Generate a government domains index page and per-country pages "
            "from TOON seed files."
        )
    )
    parser.add_argument(
        "--output",
        "-o",
        help="Output file path for the index page (default: docs/domains.md)",
        type=Path,
        default=Path("docs/domains.md"),
    )
    parser.add_argument(
        "--toon-dir",
        help="Directory containing TOON seed files (default: data/toon-seeds/countries)",
        type=Path,
        default=Path("data/toon-seeds/countries"),
    )
    parser.add_argument(
        "--countries-dir",
        help="Directory for per-country pages (default: <output dir>/domains)",
        type=Path,
        default=None,
    )

    args = parser.parse_args()

    try:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        generate_domains_report(args.toon_dir, args.output, args.countries_dir)
    except Exception as exc:
        print(f"Error generating domains report: {exc}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
