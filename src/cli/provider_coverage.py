"""Report how much of the dependency data the provider table explains.

Curating provider jurisdictions is open-ended -- there are thousands of observed
hosts and a long tail nobody will ever classify.  This reports two things that
make the work finite:

* what share of observed dependencies the table currently covers, so any figure
  derived from it can be published with its coverage stated rather than implying
  completeness;
* which unclassified hosts would add the most coverage, so the next hour of
  curation goes to the entries that matter.

Coverage is measured in distinct government domains, not requests, so a single
heavily-crawled site cannot make the table look better than it is.
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

from src.cli.generate_dependency_matrix import DEPENDENCY_TYPES, build_country_index
from src.lib.provider_registry import DEFAULT_REGISTRY_PATH, ProviderRegistry
from src.lib.relationship_shards import iter_rows

DEFAULT_TOON_DIR = Path("data/toon-seeds/countries")
DEFAULT_SHARD_DIR = Path("docs/data/relationships")


def measure_coverage(
    rows,
    country_index: dict[str, str],
    registry: ProviderRegistry,
) -> dict:
    """Measure provider-table coverage over the dependency data.

    Args:
        rows: Relationship rows.
        country_index: Registrable domain to country code.
        registry: The curated provider table.

    Returns:
        Coverage totals, a jurisdiction breakdown, and the unclassified hosts
        ranked by how many government domains depend on them.
    """
    scanned: set[str] = set()
    classified: dict[str, set[str]] = defaultdict(set)
    unclassified: dict[str, set[str]] = defaultdict(set)
    by_jurisdiction: dict[str, set[str]] = defaultdict(set)
    needs_review: dict[str, set[str]] = defaultdict(set)
    government_hosts: dict[str, set[str]] = defaultdict(set)

    for row in rows:
        if row.get("active") is False:
            continue
        source = row.get("source_domain", "")
        if country_index.get(source.lower()) is None:
            continue
        scanned.add(source)
        if row.get("relationship_type") not in DEPENDENCY_TYPES:
            continue
        if row.get("target_category") == "known_government":
            continue

        host = row.get("target_domain", "")
        if not host:
            continue

        provider = registry.get(host)
        if provider is None:
            unclassified[host].add(source)
            continue

        classified[host].add(source)
        if provider.needs_review:
            needs_review[host].add(source)
        if provider.is_government:
            government_hosts[host].add(source)
        else:
            by_jurisdiction[provider.jurisdiction or "unknown"].add(source)

    covered = sum(len(v) for v in classified.values())
    missing = sum(len(v) for v in unclassified.values())
    total = covered + missing

    return {
        "providers_in_table": len(registry),
        "scanned_domains": len(scanned),
        "hosts_observed": len(classified) + len(unclassified),
        "hosts_classified": len(classified),
        "dependencies_total": total,
        "dependencies_classified": covered,
        "coverage_percent": round(covered / total * 100, 1) if total else 0.0,
        "dependencies_needing_review": sum(len(v) for v in needs_review.values()),
        "dependencies_on_public_bodies": sum(len(v) for v in government_hosts.values()),
        # Distinct government domains depending on at least one provider from
        # each jurisdiction.  A domain using both Google and Cloudflare counts
        # once for US, so these do not sum to the dependency-pair total and are
        # reported against the scanned-domain denominator instead.
        "domains_by_jurisdiction": {
            j: len(d) for j, d in
            sorted(by_jurisdiction.items(), key=lambda kv: -len(kv[1]))
        },
        "top_unclassified": [
            {"host": h, "domains": len(d)}
            for h, d in sorted(unclassified.items(), key=lambda kv: (-len(kv[1]), kv[0]))
        ],
    }


def parse_args(args: list[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--toon-dir", type=Path, default=DEFAULT_TOON_DIR)
    parser.add_argument("--shard-dir", type=Path, default=DEFAULT_SHARD_DIR)
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY_PATH)
    parser.add_argument(
        "--top", type=int, default=25,
        help="How many unclassified hosts to list (default: 25).",
    )
    parser.add_argument(
        "--json", action="store_true",
        help="Emit the report as JSON instead of text.",
    )
    return parser.parse_args(args)


def main(args: list[str] | None = None) -> int:
    """Entry point."""
    parsed = parse_args(args)

    report = measure_coverage(
        iter_rows(parsed.shard_dir),
        build_country_index(parsed.toon_dir),
        ProviderRegistry(parsed.registry),
    )

    if parsed.json:
        report["top_unclassified"] = report["top_unclassified"][: parsed.top]
        print(json.dumps(report, indent=2))
        return 0

    print(f"Provider table: {report['providers_in_table']} entries")
    print(
        f"Coverage: {report['coverage_percent']}% of "
        f"{report['dependencies_total']:,} domain-provider dependencies "
        f"({report['hosts_classified']} of {report['hosts_observed']:,} hosts)"
    )
    if report["dependencies_needing_review"]:
        print(
            f"  {report['dependencies_needing_review']:,} rest on entries marked "
            "needs_review — verify before publishing"
        )
    if report["dependencies_on_public_bodies"]:
        print(
            f"  {report['dependencies_on_public_bodies']:,} are on public bodies "
            "missing from the government registry, not real third parties"
        )

    total_domains = report["scanned_domains"]
    print(
        f"\nGovernment domains depending on at least one provider from "
        f"(of {total_domains:,} scanned):"
    )
    for jurisdiction, count in report["domains_by_jurisdiction"].items():
        share = count / total_domains * 100 if total_domains else 0
        print(f"  {jurisdiction:<8} {count:>6,}  {share:>5.1f}%")

    print(f"\nHighest-impact unclassified hosts (top {parsed.top}):")
    for entry in report["top_unclassified"][: parsed.top]:
        print(f"  {entry['domains']:>5}  {entry['host']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
