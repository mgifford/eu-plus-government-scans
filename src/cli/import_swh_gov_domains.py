#!/usr/bin/env python3
"""Import government domain data from Software Heritage's world-gov-domain-names dataset.

This script downloads the Software Heritage government domain dataset,
filters for European countries, deduplicates against existing TOON seeds,
and saves new domains to data/imports/.

Usage:
    python -m src.cli.import_swh_gov_domains [--dry-run] [--output-dir data/imports]
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple
from urllib.request import urlopen

# European countries in the Software Heritage dataset
# Maps ISO3 codes to country names used in TOON seed filenames
EUROPEAN_COUNTRIES_ISO3: Set[str] = {
    "AUT", "BEL", "BGR", "HRV", "CYP", "CZE", "DNK", "EST", "FIN",
    "FRA", "DEU", "GRC", "HUN", "IRL", "ITA", "LVA", "LTU", "LUX",
    "MLT", "NLD", "POL", "PRT", "ROU", "SVK", "SVN", "ESP", "SWE",
    # Non-EU European countries
    "GBR", "CHE", "NOR", "ISL", "SRB", "BIH", "MNE", "MKD", "ALB",
    "XKX", "MDA", "UKR", "BLR", "RUS", "GEO", "ARM", "AZE",
    "AND", "LIE", "MCO", "SMR", "VAT",
}

# Map ISO3 codes to country names
ISO3_TO_COUNTRY: Dict[str, str] = {
    "AUT": "Austria",
    "BEL": "Belgium",
    "BGR": "Bulgaria",
    "HRV": "Croatia",
    "CYP": "Republic of Cyprus",
    "CZE": "Czechia",
    "DNK": "Denmark",
    "EST": "Estonia",
    "FIN": "Finland",
    "FRA": "France",
    "DEU": "Germany",
    "GRC": "Greece",
    "HUN": "Hungary",
    "IRL": "Ireland",
    "ITA": "Italy",
    "LVA": "Latvia",
    "LTU": "Lithuania",
    "LUX": "Luxembourg",
    "MLT": "Malta",
    "NLD": "Netherlands",
    "POL": "Poland",
    "PRT": "Portugal",
    "ROU": "Romania",
    "SVK": "Slovakia",
    "SVN": "Slovenia",
    "ESP": "Spain",
    "SWE": "Sweden",
    "GBR": "United Kingdom",
    "CHE": "Switzerland",
    "NOR": "Norway",
    "ISL": "Iceland",
    "SRB": "Serbia",
    "BIH": "Bosnia and Herzegovina",
    "MNE": "Montenegro",
    "MKD": "North Macedonia",
    "ALB": "Albania",
    "XKX": "Kosovo",
    "MDA": "Moldova",
    "UKR": "Ukraine",
    "BLR": "Belarus",
    "RUS": "Russia",
    "GEO": "Georgia",
    "ARM": "Armenia",
    "AZE": "Azerbaijan",
    "AND": "Andorra",
    "LIE": "Liechtenstein",
    "MCO": "Monaco",
    "SMR": "San Marino",
    "VAT": "Holy See",
}

# Software Heritage dataset URLs
SWH_CENTRAL_GOV_URL = "https://gitlab.softwareheritage.org/swh/products/insights/world-gov-domain-names/-/raw/main/public-sector-central-gov.csv"
SWH_PUBLIC_SECTOR_URL = "https://gitlab.softwareheritage.org/swh/products/insights/world-gov-domain-names/-/raw/main/public-sector.csv"


def fetch_csv(url: str) -> List[Dict[str, str]]:
    """Fetch CSV data from a URL."""
    print(f"Fetching {url}...")
    with urlopen(url) as response:
        content = response.read().decode("utf-8")
        reader = csv.DictReader(io.StringIO(content))
        return list(reader)


def extract_existing_domains(toon_dir: Path) -> Dict[str, Set[str]]:
    """Extract existing domains from TOON seed files.

    Returns:
        Dictionary mapping country name to set of domains.
    """
    existing: Dict[str, Set[str]] = {}

    index_path = toon_dir / "index.json"
    if not index_path.exists():
        print(f"Warning: {index_path} not found")
        return existing

    with open(index_path) as f:
        index = json.load(f)

    for country_info in index["countries"]:
        country_name = country_info["country"]
        toon_file = toon_dir / country_info["file"].replace("data/toon-seeds/", "")

        if not toon_file.exists():
            print(f"Warning: {toon_file} not found for {country_name}")
            continue

        domains: Set[str] = set()
        try:
            with open(toon_file) as f:
                toon_data = json.load(f)
                for domain_entry in toon_data.get("domains", []):
                    canonical = domain_entry.get("canonical_domain", "")
                    if canonical:
                        domains.add(canonical.lower())
        except json.JSONDecodeError as e:
            print(f"Warning: Failed to parse {toon_file}: {e}")
            continue

        existing[country_name] = domains
        print(f"  {country_name}: {len(domains)} existing domains")

    return existing


def normalize_domain(domain: str) -> str:
    """Normalize a domain for comparison."""
    domain = domain.strip().lower()
    # Remove trailing dot
    if domain.endswith("."):
        domain = domain[:-1]
    # Remove www. prefix for comparison
    if domain.startswith("www."):
        domain = domain[4:]
    return domain


def extract_iso3_from_country(country_field: str) -> str:
    """Extract ISO3 code from country field (format: ISO3_country_name)."""
    parts = country_field.split("_", 1)
    if len(parts) >= 1:
        return parts[0].upper()
    return ""


def filter_european_domains(
    central_gov_data: List[Dict[str, str]],
    public_sector_data: List[Dict[str, str]],
) -> Dict[str, Set[str]]:
    """Filter domains for European countries.

    Returns:
        Dictionary mapping country name to set of normalized domains.
    """
    european_domains: Dict[str, Set[str]] = {}

    # Process central government domains
    for row in central_gov_data:
        country_field = row.get("country", "")
        iso3 = extract_iso3_from_country(country_field)
        domain = row.get("domain", "")

        if iso3 not in EUROPEAN_COUNTRIES_ISO3:
            continue

        country_name = ISO3_TO_COUNTRY.get(iso3, country_field)
        if country_name not in european_domains:
            european_domains[country_name] = set()

        if domain:
            european_domains[country_name].add(normalize_domain(domain))

    # Process public sector domains for European countries
    for row in public_sector_data:
        country_field = row.get("country", "")
        iso3 = extract_iso3_from_country(country_field)
        subdomain = row.get("subdomain", "")
        parent_domain = row.get("parent_domain", "")

        if iso3 not in EUROPEAN_COUNTRIES_ISO3:
            continue

        country_name = ISO3_TO_COUNTRY.get(iso3, country_field)
        if country_name not in european_domains:
            european_domains[country_name] = set()

        # Add subdomain (full hostname) and parent domain
        if subdomain:
            european_domains[country_name].add(normalize_domain(subdomain))
        if parent_domain:
            european_domains[country_name].add(normalize_domain(parent_domain))

    return european_domains


def find_new_domains(
    sh_domains: Dict[str, Set[str]],
    existing_domains: Dict[str, Set[str]],
) -> Dict[str, List[str]]:
    """Find new domains not already in existing TOON seeds.

    Returns:
        Dictionary mapping country name to list of new domains.
    """
    new_domains: Dict[str, List[str]] = {}

    for country_name, domains in sh_domains.items():
        existing = existing_domains.get(country_name, set())
        new = sorted(d for d in domains if d not in existing)

        if new:
            new_domains[country_name] = new

    return new_domains


def save_import(
    new_domains: Dict[str, List[str]],
    output_dir: Path,
    dry_run: bool = False,
) -> None:
    """Save new domains to import files."""
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save summary
    summary_path = output_dir / "swh_gov_domains_import.json"
    summary = {
        "source": "Software Heritage world-gov-domain-names",
        "url": "https://gitlab.softwareheritage.org/swh/products/insights/world-gov-domain-names",
        "countries": {},
        "total_new_domains": 0,
    }

    total_new = 0
    for country_name, domains in sorted(new_domains.items()):
        summary["countries"][country_name] = {
            "count": len(domains),
            "domains": domains,
        }
        total_new += len(domains)

    summary["total_new_domains"] = total_new

    if not dry_run:
        with open(summary_path, "w") as f:
            json.dump(summary, f, indent=2)
        print(f"\nSaved summary to {summary_path}")

        # Save per-country CSV files
        for country_name, domains in sorted(new_domains.items()):
            csv_path = output_dir / f"swh_{country_name.lower().replace(' ', '_')}.csv"
            with open(csv_path, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["domain", "source"])
                for domain in sorted(domains):
                    writer.writerow([domain, "swh_gov_domains"])
            print(f"  Saved {len(domains)} domains to {csv_path}")
    else:
        print(f"\n[DRY RUN] Would save {total_new} new domains to {output_dir}")

    # Print summary
    print(f"\nSummary:")
    print(f"  Total new domains: {total_new}")
    print(f"  Countries with new domains: {len(new_domains)}")

    for country_name, domains in sorted(new_domains.items()):
        print(f"    {country_name}: {len(domains)} new domains")


def main(args: list[str] | None = None) -> int:
    """Main entry point."""
    parsed = parse_args(args)

    # Extract existing domains from TOON seeds
    toon_dir = Path("data/toon-seeds")
    print("Extracting existing domains from TOON seeds...")
    existing_domains = extract_existing_domains(toon_dir)
    print(f"Found {sum(len(d) for d in existing_domains.values())} existing domains across {len(existing_domains)} countries\n")

    # Fetch Software Heritage data
    print("Fetching Software Heritage data...")
    central_gov_data = fetch_csv(SWH_CENTRAL_GOV_URL)
    public_sector_data = fetch_csv(SWH_PUBLIC_SECTOR_URL)
    print(f"  Central government domains: {len(central_gov_data)}")
    print(f"  Public sector domains: {len(public_sector_data)}\n")

    # Filter for European countries
    print("Filtering for European countries...")
    sh_domains = filter_european_domains(central_gov_data, public_sector_data)
    print(f"Found {sum(len(d) for d in sh_domains.values())} domains across {len(sh_domains)} European countries\n")

    # Find new domains
    print("Finding new domains not in TOON seeds...")
    new_domains = find_new_domains(sh_domains, existing_domains)

    # Save results
    output_dir = Path(parsed.output_dir)
    save_import(new_domains, output_dir, dry_run=parsed.dry_run)

    return 0


def parse_args(args: list[str] | None = None) -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Import government domains from Software Heritage dataset."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be imported without saving",
    )
    parser.add_argument(
        "--output-dir",
        default="data/imports",
        help="Output directory for import files (default: data/imports)",
    )
    return parser.parse_args(args)


if __name__ == "__main__":
    sys.exit(main())
