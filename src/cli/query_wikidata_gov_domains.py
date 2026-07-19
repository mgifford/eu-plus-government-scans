#!/usr/bin/env python3
"""Query Wikidata for regional/subnational government domains, for one country at a time.

Complements src/cli/import_swh_gov_domains.py (national-level government
domains from Software Heritage) with a source that also covers regional
government entities -- e.g. a country's autonomous communities, states, or
provinces and their own government/parliament/president institutions, which
the SWH dataset does not include.

Two queries are made per country:

  1. National: government agencies whose jurisdiction (P1001) is the country
     itself, with an official website (P856) set.
  2. Regional: every first-level administrative division of the country
     (P31 = Q10742), plus (a) the division's own direct official website if
     set, and (b) government/parliament/president institutions linked to it
     via P1001, filtered by label to exclude non-government matches (courts,
     agencies, political parties) that a broad class query would otherwise
     include.

Every result also carries Wikidata's "dissolved, abolished or demolished
date" (P576) when present, so a caller can see when an entity is known to be
historical -- but this is not a complete signal by itself (an entity can be
defunct in practice without ever being marked dissolved in Wikidata), so
output here is always a candidate list for manual review, matching how the
existing SWH import is meant to be reviewed before merging into any TOON
seed file. This script does not write to data/toon-seeds/ directly.

Usage:
    python -m src.cli.query_wikidata_gov_domains --country Spain
    python -m src.cli.query_wikidata_gov_domains --country Spain --dry-run
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

SPARQL_ENDPOINT = "https://query.wikidata.org/sparql"
USER_AGENT = "eu-plus-government-scans/0.1 (data quality research)"

# Wikidata Q-IDs for the countries currently tracked in data/toon-seeds/index.json.
# Verified via a single batch SPARQL query (instance-of-country + continent-Europe)
# rather than transcribed individually, to avoid entering a wrong ID by hand.
COUNTRY_QIDS: dict[str, str] = {
    "Austria": "Q40",
    "Belgium": "Q31",
    "Bulgaria": "Q219",
    "Croatia": "Q224",
    "Czechia": "Q213",
    "Denmark": "Q35",
    "Estonia": "Q191",
    "Finland": "Q33",
    "France": "Q142",
    "Germany": "Q183",
    "Greece": "Q41",
    "Hungary": "Q28",
    "Iceland": "Q189",
    "Ireland": "Q27",
    "Italy": "Q38",
    "Latvia": "Q211",
    "Lithuania": "Q37",
    "Luxembourg": "Q32",
    "Malta": "Q233",
    "Netherlands": "Q55",
    "Norway": "Q20",
    "Poland": "Q36",
    "Portugal": "Q45",
    "Republic of Cyprus": "Q229",
    "Romania": "Q218",
    "Slovakia": "Q214",
    "Slovenia": "Q215",
    "Spain": "Q29",
    "Sweden": "Q34",
    "Switzerland": "Q39",
    "United Kingdom (UK)": "Q145",
}

# Q327333 = "government agency" (broad class, includes courts/agencies/etc).
GOV_AGENCY_CLASS = "Q327333"

# Q10742 = "first-level administrative country subdivision".
SUBDIVISION_CLASS = "Q10742"

# Q213283 = "diplomatic mission" (embassies, consulates, nunciatures, high
# commissions). A P1001-to-country query otherwise pulls in every foreign
# country's mission accredited TO that country -- P17 (country) on a mission
# entity means the host country, not the operator, so P17 cannot be used to
# exclude these (confirmed by inspecting "embassy of Argentina in Spain",
# which has P17=Spain). The class exclusion is the structurally correct
# filter; caught during manual review of Spain's results (2026-07-19).
DIPLOMATIC_MISSION_CLASS = "Q213283"

NATIONAL_QUERY_TEMPLATE = """
SELECT ?govBodyLabel ?website ?dissolved WHERE {{
  ?govBody wdt:P1001 wd:{qid}.
  ?govBody wdt:P31/wdt:P279* wd:%(agency)s.
  ?govBody wdt:P856 ?website.
  MINUS {{ ?govBody wdt:P31/wdt:P279* wd:%(mission)s. }}
  OPTIONAL {{ ?govBody wdt:P576 ?dissolved. }}
  SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
}}
""" % {"agency": GOV_AGENCY_CLASS, "mission": DIPLOMATIC_MISSION_CLASS}

REGIONAL_QUERY_TEMPLATE = """
SELECT ?subdivisionLabel ?isoCode ?placeWebsite ?govBodyLabel ?govWebsite ?dissolved WHERE {{
  ?subdivision wdt:P17 wd:{qid}.
  ?subdivision wdt:P31 wd:%s.
  OPTIONAL {{ ?subdivision wdt:P300 ?isoCode. }}
  OPTIONAL {{ ?subdivision wdt:P856 ?placeWebsite. }}
  OPTIONAL {{
    ?subdivision wdt:P1365|^wdt:P1001 ?govBody.
    ?govBody wdt:P856 ?govWebsite.
    OPTIONAL {{ ?govBody wdt:P576 ?dissolved. }}
  }}
  SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
}}
ORDER BY ?subdivisionLabel
""" % SUBDIVISION_CLASS

# Entities that legitimately match a government-institution label pattern
# (see GOV_LABEL_PATTERNS) but are not government bodies -- caught by manual
# review of Spain's results (2026-07-19): party leadership titles that happen
# to be phrased "President of the X Party".
EXCLUDE_LABEL_PATTERNS = [
    r"\bParty\b",
    r"\bConvergence\b",
]

GOV_LABEL_PATTERNS = [
    r"^Government of ",
    r"^Regional Government of ",
    r"^Parliament of ",
    r"^President of the (?:Generalitat|Community|Xunta|Junta) of ",
    r"^President of ",
    r"^Presidency of ",
]

# Diplomatic missions accredited to a country are not part of that country's
# own government, but can match a broad "government agency + P1001" query.
# Caught during manual review of Spain's national results (2026-07-19).
NON_GOVERNMENT_LABEL_PATTERNS = [
    r"^Apostolic Nunciature",
    r"^Embassy of",
    r"^Consulate",
]


def _looks_like_government(label: str) -> bool:
    """Return True if a Wikidata label matches a government-institution pattern."""
    if any(re.search(p, label) for p in EXCLUDE_LABEL_PATTERNS):
        return False
    return any(re.search(p, label) for p in GOV_LABEL_PATTERNS)


def _looks_like_non_government(label: str) -> bool:
    """Return True if a label matches a known non-government false-positive pattern."""
    return any(re.search(p, label) for p in NON_GOVERNMENT_LABEL_PATTERNS)


def run_sparql(query: str, timeout: int = 40) -> dict[str, Any]:
    """Execute a SPARQL query against the Wikidata Query Service and return the parsed JSON."""
    params = urllib.parse.urlencode({"query": query, "format": "json"})
    url = f"{SPARQL_ENDPOINT}?{params}"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def query_national_domains(country_qid: str) -> list[dict[str, Any]]:
    """Query national-level government domains for a country.

    Returns:
        List of {label, website, dissolved} dicts. `dissolved` is None for
        entities with no P576 value set (which does not guarantee the entity
        is still active -- see module docstring).
    """
    query = NATIONAL_QUERY_TEMPLATE.format(qid=country_qid)
    result = run_sparql(query)

    seen: set[tuple[str, str]] = set()
    entries = []
    for row in result["results"]["bindings"]:
        label = row.get("govBodyLabel", {}).get("value", "")
        website = row.get("website", {}).get("value", "")
        if not label or not website:
            continue
        if re.fullmatch(r"Q\d+", label):
            # No English label available -- not usable in a human-reviewed report.
            continue
        if _looks_like_non_government(label):
            continue
        key = (label, website)
        if key in seen:
            continue
        seen.add(key)
        entries.append(
            {
                "label": label,
                "website": website,
                "dissolved": row.get("dissolved", {}).get("value"),
            }
        )
    return entries


def query_regional_domains(country_qid: str) -> dict[str, dict[str, Any]]:
    """Query regional/subnational government domains for a country.

    Returns:
        Dict keyed by subdivision name, each value containing:
          - iso_code: ISO 3166-2 code if Wikidata has it (P300)
          - place_website: the subdivision's own direct P856, if set
          - institutions: list of {label, website, dissolved} for
            government-labelled institutions linked via P1001
    """
    query = REGIONAL_QUERY_TEMPLATE.format(qid=country_qid)
    result = run_sparql(query)

    regions: dict[str, dict[str, Any]] = {}
    for row in result["results"]["bindings"]:
        sub = row.get("subdivisionLabel", {}).get("value", "")
        if not sub:
            continue
        region = regions.setdefault(
            sub,
            {"iso_code": None, "place_website": None, "institutions": []},
        )

        iso_code = row.get("isoCode", {}).get("value")
        if iso_code:
            region["iso_code"] = iso_code

        place_website = row.get("placeWebsite", {}).get("value")
        if place_website:
            region["place_website"] = place_website

        gov_label = row.get("govBodyLabel", {}).get("value", "")
        gov_website = row.get("govWebsite", {}).get("value", "")
        if gov_label and gov_website and _looks_like_government(gov_label):
            entry = {
                "label": gov_label,
                "website": gov_website,
                "dissolved": row.get("dissolved", {}).get("value"),
            }
            if entry not in region["institutions"]:
                region["institutions"].append(entry)

    return regions


def load_existing_domains(toon_path: Path) -> set[str]:
    """Load the set of canonical domains already present in a country's TOON seed."""
    if not toon_path.exists():
        return set()
    with toon_path.open(encoding="utf-8") as f:
        data = json.load(f)
    return {d["canonical_domain"] for d in data.get("domains", [])}


def _hostname_from_url(url: str) -> str:
    """Extract a bare hostname from a URL for comparison against canonical_domain."""
    parsed = urllib.parse.urlparse(url if "//" in url else f"//{url}")
    host = (parsed.hostname or "").lower()
    if host.startswith("www."):
        host = host[4:]
    return host


def build_report(country: str, country_qid: str, existing_domains: set[str]) -> dict[str, Any]:
    """Query Wikidata and build a structured candidate report for one country."""
    print(f"Querying national-level government domains for {country}...")
    national = query_national_domains(country_qid)
    print(f"  {len(national)} candidates")

    print(f"Querying regional government domains for {country}...")
    regional = query_regional_domains(country_qid)
    print(f"  {len(regional)} subdivisions")

    def is_new(website: str) -> bool:
        host = _hostname_from_url(website)
        return bool(host) and host not in existing_domains and not any(
            existing.endswith("." + host) or host.endswith("." + existing)
            for existing in existing_domains
        )

    national_out = [
        {**entry, "hostname": _hostname_from_url(entry["website"]), "already_seeded": not is_new(entry["website"])}
        for entry in national
    ]

    regional_out = {}
    for name, info in sorted(regional.items()):
        place_new = info["place_website"] and is_new(info["place_website"])
        institutions_out = [
            {**inst, "hostname": _hostname_from_url(inst["website"]), "already_seeded": not is_new(inst["website"])}
            for inst in info["institutions"]
        ]
        regional_out[name] = {
            "iso_code": info["iso_code"],
            "place_website": info["place_website"],
            "place_website_new": bool(place_new),
            "institutions": institutions_out,
        }

    return {
        "country": country,
        "wikidata_qid": country_qid,
        "national": national_out,
        "regional": regional_out,
        "note": (
            "Candidate list only -- not merged into any TOON seed. "
            "Verify liveness (DNS/HTTP) and currency before adding any "
            "domain; 'dissolved' being empty does not guarantee an entity "
            "is still active, and 'already_seeded' is a hostname-suffix "
            "match, not a guarantee of exact equivalence."
        ),
    }


def save_report(report: dict[str, Any], output_dir: Path, dry_run: bool = False) -> Path:
    """Write the report to data/imports/wikidata_<country>.json."""
    output_dir.mkdir(parents=True, exist_ok=True)
    slug = report["country"].lower().replace(" ", "_").replace("(", "").replace(")", "")
    path = output_dir / f"wikidata_{slug}.json"

    if dry_run:
        print(f"\n[DRY RUN] Would save report to {path}")
        return path

    with path.open("w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(f"\nSaved report to {path}")
    return path


def print_summary(report: dict[str, Any]) -> None:
    """Print a human-readable summary of new candidates found."""
    new_national = [e for e in report["national"] if not e["already_seeded"]]
    print(f"\nNational candidates not already seeded: {len(new_national)}")
    for entry in new_national:
        flag = f" (dissolved {entry['dissolved'][:10]})" if entry["dissolved"] else ""
        print(f"  {entry['hostname']:35s} {entry['label']}{flag}")

    print("\nRegional candidates not already seeded:")
    for name, info in report["regional"].items():
        new_items = []
        if info["place_website_new"]:
            new_items.append((_hostname_from_url(info["place_website"]), "(place entity)", None))
        for inst in info["institutions"]:
            if not inst["already_seeded"]:
                new_items.append((inst["hostname"], inst["label"], inst["dissolved"]))
        if not new_items:
            continue
        iso = f" [{info['iso_code']}]" if info["iso_code"] else ""
        print(f"  {name}{iso}:")
        for hostname, label, dissolved in new_items:
            flag = f" (dissolved {dissolved[:10]})" if dissolved else ""
            print(f"    {hostname:35s} {label}{flag}")


def main(args: list[str] | None = None) -> int:
    """Main CLI entry point."""
    parsed = parse_args(args)

    if parsed.country not in COUNTRY_QIDS:
        print(f"Error: unknown country {parsed.country!r}.", file=sys.stderr)
        print(f"Known countries: {', '.join(sorted(COUNTRY_QIDS))}", file=sys.stderr)
        return 1

    country_qid = COUNTRY_QIDS[parsed.country]
    toon_slug = parsed.country.lower().replace(" ", "-").replace("(", "").replace(")", "")
    toon_path = Path("data/toon-seeds/countries") / f"{toon_slug}.toon"

    print(f"Loading existing seed domains from {toon_path}...")
    existing_domains = load_existing_domains(toon_path)
    print(f"  {len(existing_domains)} existing domains\n")

    try:
        report = build_report(parsed.country, country_qid, existing_domains)
    except Exception as exc:
        print(f"Error querying Wikidata: {exc}", file=sys.stderr)
        return 1

    output_dir = Path(parsed.output_dir)
    save_report(report, output_dir, dry_run=parsed.dry_run)
    print_summary(report)

    return 0


def parse_args(args: list[str] | None = None) -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description=(
            "Query Wikidata for national and regional government domain "
            "candidates for one country, cross-referenced against the "
            "existing TOON seed. Produces a review report only -- does not "
            "modify any seed file."
        )
    )
    parser.add_argument(
        "--country",
        required=True,
        help="Country name exactly as used in data/toon-seeds/index.json (e.g. 'Spain').",
    )
    parser.add_argument(
        "--output-dir",
        default="data/imports",
        help="Directory to write the report to (default: data/imports)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Query and print results without saving the report file",
    )
    return parser.parse_args(args)


if __name__ == "__main__":
    sys.exit(main())
