#!/usr/bin/env python3
"""Import government domains by scraping a list of URLs for external links.

Fetches one or more source pages (e.g. Belgian government audit lists), extracts
all external links, filters for likely government domains, validates that each
domain resolves, deduplicates against existing TOON seeds, and saves new domains
to data/imports/.

Usage:
    python -m src.cli.import_url_domains \\
        --url https://accessibility.belgium.be/fr/actualites/... \\
        --url https://www.vlaanderen.be/inter/... \\
        [--country BEL] [--dry-run] [--output-dir data/imports]

    # Or using the sources manifest:
    python -m src.cli.import_url_domains --from-manifest data/imports/domain_sources.yaml \\
        --schedule manual

    # Promote staged imports directly into TOON seed files:
    python -m src.cli.import_url_domains --from-manifest data/imports/domain_sources.yaml \\
        --schedule manual --promote-to-toon
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import socket
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from urllib.parse import urlparse

import yaml

try:
    from bs4 import BeautifulSoup
except ImportError:  # pragma: no cover
    print(
        "Error: beautifulsoup4 is required. Install with: pip install beautifulsoup4",
        file=sys.stderr,
    )
    sys.exit(1)

# ---------------------------------------------------------------------------
# Government domain heuristics
# ---------------------------------------------------------------------------

# TLD/domain patterns considered likely government domains
GOV_TLD_PATTERNS: List[re.Pattern[str]] = [
    re.compile(r"\.gov(\.[a-z]{2})?$"),           # .gov, .gov.be, .gov.uk, …
    re.compile(r"\.gouv\.[a-z]{2}$"),             # .gouv.fr, .gouv.be, …
    re.compile(r"\.gv\.[a-z]{2}$"),               # .gv.at
    re.compile(r"\.gc\.ca$"),                      # .gc.ca (Canada)
    re.compile(r"\.europa\.eu$"),                  # EU institutions
    re.compile(r"\.vlaanderen\.be$"),              # Flemish government
    re.compile(r"\.brussels$"),                    # Brussels region
    re.compile(r"\.wallonie\.be$"),                # Wallonia
    re.compile(r"\.fgov\.be$"),                    # Belgian federal
    re.compile(r"\.belgium\.be$"),                 # Belgian federal portal
    re.compile(r"\.public\.lu$"),                  # Luxembourg public bodies
    re.compile(r"\.admin\.ch$"),                   # Swiss administration
    re.compile(r"\.bund\.de$"),                    # German federal
    re.compile(r"\.service\.gov\.uk$"),            # UK gov services
    re.compile(r"\.judiciary\.gov\.uk$"),
    re.compile(r"\.parliament\.uk$"),
    re.compile(r"\.police\.uk$"),
    re.compile(r"\.nhs\.uk$"),
    re.compile(r"\.ac\.uk$"),                      # UK academic (commonly public)
    re.compile(r"\.edu$"),
]

# Country-code TLDs that are predominantly government when combined with path hints
# Keys: ccTLD suffix, Values: ISO-3 country code
CCTLD_TO_ISO3: Dict[str, str] = {
    ".be": "BEL",
    ".fr": "FRA",
    ".de": "DEU",
    ".nl": "NLD",
    ".lu": "LUX",
    ".at": "AUT",
    ".ch": "CHE",
    ".uk": "GBR",
    ".ie": "IRL",
    ".it": "ITA",
    ".es": "ESP",
    ".pt": "PRT",
    ".se": "SWE",
    ".no": "NOR",
    ".dk": "DNK",
    ".fi": "FIN",
    ".pl": "POL",
    ".cz": "CZE",
    ".sk": "SVK",
    ".hu": "HUN",
    ".ro": "ROU",
    ".bg": "BGR",
    ".hr": "HRV",
    ".si": "SVN",
    ".ee": "EST",
    ".lv": "LVA",
    ".lt": "LTU",
    ".mt": "MLT",
    ".cy": "CYP",
    ".gr": "GRC",
    ".is": "ISL",
    ".ca": "CAN",
}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def fetch_page(url: str, timeout: int = 30) -> Optional[str]:
    """Fetch a web page and return its HTML content.

    Returns None on failure (non-fatal — caller should log and continue).
    """
    print(f"Fetching {url}...")
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "eu-plus-government-scans/import-url-domains (+https://github.com/mgifford/eu-plus-government-scans)"},
        )
        with urllib.request.urlopen(req, timeout=timeout) as response:
            return response.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:
        print(f"  Warning: HTTP {exc.code} fetching {url}: {exc.reason}", file=sys.stderr)
        return None
    except urllib.error.URLError as exc:
        print(f"  Warning: Network error fetching {url}: {exc.reason}", file=sys.stderr)
        return None
    except Exception as exc:  # noqa: BLE001
        print(f"  Warning: Unexpected error fetching {url}: {exc}", file=sys.stderr)
        return None


def extract_links(html: str, base_url: str) -> List[str]:
    """Extract all href links from HTML, returning absolute URLs."""
    soup = BeautifulSoup(html, "html.parser")
    links: List[str] = []
    base_parts = urlparse(base_url)
    base_origin = f"{base_parts.scheme}://{base_parts.netloc}"

    for tag in soup.find_all("a", href=True):
        href = tag["href"].strip()
        if not href or href.startswith("#") or href.startswith("mailto:"):
            continue
        if href.startswith("//"):
            href = base_parts.scheme + ":" + href
        elif href.startswith("/"):
            href = base_origin + href
        elif not href.startswith("http"):
            continue  # skip relative paths without enough context
        links.append(href)

    return links


def extract_domain(url: str) -> Optional[str]:
    """Extract the bare domain (host) from a URL, stripping www. prefix."""
    try:
        host = urlparse(url).netloc.lower()
        if not host:
            return None
        # Remove port
        host = host.split(":")[0]
        # Strip www.
        if host.startswith("www."):
            host = host[4:]
        return host if host else None
    except Exception:  # noqa: BLE001
        return None


def is_likely_gov_domain(domain: str) -> bool:
    """Return True if the domain looks like a government domain."""
    for pattern in GOV_TLD_PATTERNS:
        if pattern.search(domain):
            return True
    return False


def domain_resolves(domain: str, timeout: float = 5.0) -> bool:
    """Return True if the domain resolves via DNS."""
    try:
        socket.setdefaulttimeout(timeout)
        socket.getaddrinfo(domain, None)
        return True
    except (socket.gaierror, socket.timeout, OSError):
        return False


def scrape_domains(
    source_url: str,
    gov_only: bool = True,
    check_dns: bool = True,
) -> Tuple[List[str], List[str]]:
    """Scrape a source URL and return (resolved_domains, unresolved_domains).

    Args:
        source_url: The page to scrape.
        gov_only: If True, only return domains matching government TLD patterns.
        check_dns: If True, validate each domain resolves via DNS.

    Returns:
        Tuple of (valid_domains, failed_dns_domains).
    """
    html = fetch_page(source_url)
    if html is None:
        return [], []

    links = extract_links(html, source_url)
    print(f"  Found {len(links)} links on page")

    # Collect unique domains (excluding the source domain itself)
    source_domain = extract_domain(source_url) or ""
    seen: Set[str] = set()
    candidates: List[str] = []
    for link in links:
        domain = extract_domain(link)
        if not domain or domain == source_domain or domain in seen:
            continue
        seen.add(domain)
        if gov_only and not is_likely_gov_domain(domain):
            continue
        candidates.append(domain)

    print(f"  {len(candidates)} candidate government domains after filtering")

    if not check_dns:
        return candidates, []

    valid: List[str] = []
    failed: List[str] = []
    for domain in candidates:
        if domain_resolves(domain):
            valid.append(domain)
        else:
            failed.append(domain)
            print(f"  DNS failed: {domain}")

    print(f"  {len(valid)} domains resolve; {len(failed)} do not")
    return valid, failed


def load_existing_domains(toon_dir: Path) -> Dict[str, Set[str]]:
    """Load existing domains from TOON seed files (mirrors import_swh_gov_domains)."""
    existing: Dict[str, Set[str]] = {}
    index_path = toon_dir / "index.json"
    if not index_path.exists():
        print(f"Warning: {index_path} not found", file=sys.stderr)
        return existing

    with open(index_path) as f:
        index = json.load(f)

    for country_info in index["countries"]:
        country_name = country_info["country"]
        toon_file = toon_dir / country_info["file"].replace("data/toon-seeds/", "")
        if not toon_file.exists():
            continue
        domains: Set[str] = set()
        try:
            with open(toon_file) as f:
                toon_data = json.load(f)
                for entry in toon_data.get("domains", []):
                    canonical = entry.get("canonical_domain", "")
                    if canonical:
                        domains.add(canonical.lower())
        except json.JSONDecodeError:
            continue
        existing[country_name] = domains

    return existing


def save_results(
    results: Dict[str, Dict[str, List[str]]],
    output_dir: Path,
    dry_run: bool = False,
) -> None:
    """Save import results to per-source CSV files and a JSON summary.

    Each CSV row carries a ``status`` value:

    - ``new``        – domain not previously seen in any TOON seed file.
    - ``dns_failed`` – domain did not resolve during DNS validation.
    - ``duplicate``  – domain already present in an existing TOON seed file
                       (recorded for auditability; not re-added).

    Args:
        results: Mapping of source_url → {"new": [...], "unresolved": [...],
            "duplicates": [...]}.
        output_dir: Directory to write output files into.
        dry_run: If True, print what would be saved without writing.
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    summary: Dict[str, object] = {
        "sources": {},
        "total_new_domains": 0,
    }
    total_new = 0

    for source_url, data in results.items():
        new_domains = data.get("new", [])
        unresolved = data.get("unresolved", [])
        duplicates = data.get("duplicates", [])
        total_new += len(new_domains)

        # Derive a slug for output filenames
        parsed = urlparse(source_url)
        slug = re.sub(r"[^a-z0-9]+", "_", parsed.netloc.lower()).strip("_")
        slug = slug[:60]  # keep filenames manageable

        summary["sources"][source_url] = {  # type: ignore[index]
            "new_domain_count": len(new_domains),
            "unresolved_count": len(unresolved),
            "duplicate_count": len(duplicates),
            "new_domains": sorted(new_domains),
            "unresolved_domains": sorted(unresolved),
            "skipped_duplicates": sorted(duplicates),
        }

        if not dry_run:
            csv_path = output_dir / f"url_import_{slug}.csv"
            with open(csv_path, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["domain", "source", "status"])
                for domain in sorted(new_domains):
                    writer.writerow([domain, source_url, "new"])
                for domain in sorted(unresolved):
                    writer.writerow([domain, source_url, "dns_failed"])
                for domain in sorted(duplicates):
                    writer.writerow([domain, source_url, "duplicate"])
            print(
                f"  Saved {len(new_domains)} new, {len(duplicates)} duplicate, "
                f"{len(unresolved)} unresolved domains to {csv_path}"
            )
        else:
            print(
                f"  [DRY RUN] Would save {len(new_domains)} new, "
                f"{len(duplicates)} duplicate domains from {source_url}"
            )

    summary["total_new_domains"] = total_new

    if not dry_run:
        summary_path = output_dir / "url_import_summary.json"
        with open(summary_path, "w") as f:
            json.dump(summary, f, indent=2)
        print(f"\nSaved summary to {summary_path}")

    print(f"\nTotal new domains across all sources: {total_new}")


def promote_to_toon(
    results: Dict[str, Dict[str, List[str]]],
    toon_dir: Path,
    existing_by_country: Dict[str, Set[str]],
    dry_run: bool = False,
) -> Dict[str, List[str]]:
    """Write newly discovered domains into the matching TOON seed files.

    For each ``new`` domain in *results*, the function:

    1. Determines the target country by matching the domain's ccTLD against
       ``CCTLD_TO_ISO3``.  Domains with unrecognised TLDs are skipped (logged).
    2. Finds the TOON file for that country from *toon_dir*/index.json.
    3. Appends a minimal domain entry (``canonical_domain``, ``source``,
       ``source_url``, ``pages: []``, ``subnational: []``) and re-serialises
       the file with a 2-space indent.
    4. Updates ``domain_count`` in the top-level metadata.

    The function is idempotent: a domain already present (from any source) is
    silently skipped even if ``results`` lists it as ``new``.

    Args:
        results: Mapping of source_url → {"new": [...], ...}.
        toon_dir: Root of the TOON seed tree (contains index.json and countries/).
        existing_by_country: Pre-loaded domain sets keyed by country name —
            used to skip domains that arrived via a second source in the same
            run before this function was called.
        dry_run: If True, log what would change without writing files.

    Returns:
        Mapping of country_name → list of domain strings that were added
        (or would be added in dry-run mode).
    """
    index_path = toon_dir / "index.json"
    if not index_path.exists():
        print(f"Warning: {index_path} not found — cannot promote to TOON", file=sys.stderr)
        return {}

    with open(index_path) as f:
        index = json.load(f)

    # Build lookup: country_name → toon file path
    country_file: Dict[str, Path] = {}
    for entry in index.get("countries", []):
        country_name = entry["country"]
        rel_path = entry["file"].replace("data/toon-seeds/", "")
        toon_file = toon_dir / rel_path
        country_file[country_name] = toon_file

    # Static mapping from ISO-3 to the country name used in index.json
    KNOWN_ISO3_COUNTRY: Dict[str, str] = {
        "BEL": "Belgium",
        "FRA": "France",
        "DEU": "Germany",
        "NLD": "Netherlands",
        "LUX": "Luxembourg",
        "AUT": "Austria",
        "CHE": "Switzerland",
        "GBR": "United Kingdom",
        "IRL": "Ireland",
        "ITA": "Italy",
        "ESP": "Spain",
        "PRT": "Portugal",
        "SWE": "Sweden",
        "NOR": "Norway",
        "DNK": "Denmark",
        "FIN": "Finland",
        "POL": "Poland",
        "CZE": "Czechia",
        "SVK": "Slovakia",
        "HUN": "Hungary",
        "ROU": "Romania",
        "BGR": "Bulgaria",
        "HRV": "Croatia",
        "SVN": "Slovenia",
        "EST": "Estonia",
        "LVA": "Latvia",
        "LTU": "Lithuania",
        "MLT": "Malta",
        "CYP": "Republic of Cyprus",
        "GRC": "Greece",
        "ISL": "Iceland",
        "CAN": "Canada",
    }

    added: Dict[str, List[str]] = {}

    for source_url, data in results.items():
        for domain in sorted(data.get("new", [])):
            # Determine ccTLD
            parts = domain.rsplit(".", 1)
            tld = f".{parts[-1]}" if len(parts) == 2 else ""
            iso3 = CCTLD_TO_ISO3.get(tld)
            if iso3 is None:
                # Try two-part TLD (e.g. .gov.be → .be)
                parts2 = domain.rsplit(".", 2)
                if len(parts2) == 3:
                    tld2 = f".{parts2[-1]}"
                    iso3 = CCTLD_TO_ISO3.get(tld2)
            if iso3 is None:
                print(f"  Skipping {domain}: unrecognised TLD '{tld}'")
                continue

            country_name = KNOWN_ISO3_COUNTRY.get(iso3)
            if country_name is None or country_name not in country_file:
                print(f"  Skipping {domain}: no TOON file for ISO3 '{iso3}'")
                continue

            toon_file = country_file[country_name]
            already = existing_by_country.get(country_name, set())
            if domain.lower() in already:
                continue  # already present — skip silently

            if dry_run:
                print(f"  [DRY RUN] Would add {domain} → {toon_file.name} ({country_name})")
                added.setdefault(country_name, []).append(domain)
                continue

            if not toon_file.exists():
                print(f"  Warning: {toon_file} not found — skipping {domain}", file=sys.stderr)
                continue

            with open(toon_file) as f:
                toon_data = json.load(f)

            new_entry: Dict[str, object] = {
                "canonical_domain": domain,
                "subnational": [],
                "source": "url_import",
                "source_url": source_url,
                "pages": [],
            }
            toon_data.setdefault("domains", []).append(new_entry)
            toon_data["domain_count"] = len(toon_data["domains"])

            with open(toon_file, "w") as f:
                json.dump(toon_data, f, indent=2, ensure_ascii=False)
                f.write("\n")

            # Update in-memory set so the same domain is not added twice
            existing_by_country.setdefault(country_name, set()).add(domain.lower())
            added.setdefault(country_name, []).append(domain)
            print(f"  Added {domain} → {toon_file.name}")

    if added:
        total = sum(len(v) for v in added.values())
        print(f"\nPromoted {total} domain(s) to TOON seed files across {len(added)} country/countries.")
    else:
        print("\nNo new domains to promote to TOON seed files.")

    return added


def load_manifest_urls(manifest_path: Path, schedule_filter: Optional[str]) -> List[str]:
    """Load html_scrape source URLs from domain_sources.yaml.

    Args:
        manifest_path: Path to domain_sources.yaml.
        schedule_filter: If given, only include sources with this schedule value.

    Returns:
        List of source URLs.
    """
    with open(manifest_path) as f:
        data = yaml.safe_load(f)

    urls: List[str] = []
    for source in data.get("sources", []):
        if source.get("type") != "html_scrape":
            continue
        if schedule_filter and source.get("schedule") != schedule_filter:
            continue
        url = source.get("url")
        if url:
            urls.append(url)
    return urls


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def parse_args(args: list[str] | None = None) -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description=(
            "Scrape government domain lists from web pages and import new domains."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scrape two Belgian audit-list pages
  python -m src.cli.import_url_domains \\
      --url https://accessibility.belgium.be/fr/actualites/liste-des-sites... \\
      --url https://www.vlaanderen.be/inter/...

  # Use all manual html_scrape entries from the manifest
  python -m src.cli.import_url_domains \\
      --from-manifest data/imports/domain_sources.yaml --schedule manual
""",
    )
    parser.add_argument(
        "--url",
        dest="urls",
        action="append",
        default=[],
        metavar="URL",
        help="Source URL to scrape (can be specified multiple times)",
    )
    parser.add_argument(
        "--from-manifest",
        metavar="PATH",
        help="Load html_scrape source URLs from domain_sources.yaml",
    )
    parser.add_argument(
        "--schedule",
        metavar="SCHEDULE",
        help=(
            "When using --from-manifest, only include sources with this schedule "
            "(e.g. 'manual', 'monthly')"
        ),
    )
    parser.add_argument(
        "--all-domains",
        action="store_true",
        help=(
            "Include all external domains, not just those matching government TLD "
            "patterns (default: government domains only)"
        ),
    )
    parser.add_argument(
        "--skip-dns",
        action="store_true",
        help="Skip DNS validation (faster but may include non-resolving domains)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be imported without saving",
    )
    parser.add_argument(
        "--promote-to-toon",
        action="store_true",
        help=(
            "After scraping, write newly discovered domains directly into the "
            "matching TOON seed files (determined by ccTLD). Implies the CSV "
            "staging files are still written. Cannot be combined with --dry-run."
        ),
    )
    parser.add_argument(
        "--output-dir",
        default="data/imports",
        help="Output directory for import files (default: data/imports)",
    )
    return parser.parse_args(args)


def main(args: list[str] | None = None) -> int:
    """Main entry point."""
    parsed = parse_args(args)

    # Collect source URLs
    urls: List[str] = list(parsed.urls)

    if parsed.from_manifest:
        manifest_path = Path(parsed.from_manifest)
        if not manifest_path.exists():
            print(f"Error: manifest not found: {manifest_path}", file=sys.stderr)
            return 1
        manifest_urls = load_manifest_urls(manifest_path, parsed.schedule)
        print(f"Loaded {len(manifest_urls)} URL(s) from manifest: {manifest_path}")
        urls.extend(manifest_urls)

    if not urls:
        print(
            "Error: no source URLs provided. Use --url URL or --from-manifest PATH.",
            file=sys.stderr,
        )
        return 1

    # Load existing domains for deduplication
    toon_dir = Path("data/toon-seeds")
    print("Loading existing domains from TOON seeds...")
    existing_domains = load_existing_domains(toon_dir)
    all_existing: Set[str] = set()
    for domains in existing_domains.values():
        all_existing.update(domains)
    print(f"Found {len(all_existing)} existing domains across {len(existing_domains)} countries\n")

    gov_only = not parsed.all_domains
    check_dns = not parsed.skip_dns

    results: Dict[str, Dict[str, List[str]]] = {}

    for url in urls:
        print(f"\n--- Scraping: {url} ---")
        valid, failed = scrape_domains(url, gov_only=gov_only, check_dns=check_dns)

        # Separate new domains from duplicates
        new_domains = sorted(d for d in valid if d not in all_existing)
        duplicates = sorted(d for d in valid if d in all_existing)
        print(f"  {len(new_domains)} domains not yet in TOON seeds")
        if duplicates:
            print(f"  {len(duplicates)} domains already in TOON seeds (will be marked as duplicate)")

        results[url] = {"new": new_domains, "unresolved": failed, "duplicates": duplicates}

    # Save staged CSV/JSON output
    output_dir = Path(parsed.output_dir)
    save_results(results, output_dir, dry_run=parsed.dry_run)

    # Optionally promote new domains directly into TOON seed files
    if parsed.promote_to_toon and not parsed.dry_run:
        print("\n--- Promoting new domains to TOON seed files ---")
        promote_to_toon(results, toon_dir, existing_domains, dry_run=False)
    elif parsed.promote_to_toon and parsed.dry_run:
        print("\n--- [DRY RUN] Would promote new domains to TOON seed files ---")
        promote_to_toon(results, toon_dir, existing_domains, dry_run=True)

    return 0


if __name__ == "__main__":
    sys.exit(main())
