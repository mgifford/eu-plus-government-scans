"""CLI tool to generate a static government-domain manifest for network.html.

Reads all country TOON seed files (via GovernmentDomainRegistry) and writes a
single JSON file mapping every known government domain to its country. This
lets docs/network.html check domain membership against the same curated,
per-domain dataset the rest of the pipeline uses, instead of an independent
regex/suffix heuristic.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from src.lib.gov_domain_registry import GovernmentDomainRegistry


def build_manifest(toon_dir: Path) -> dict:
    registry = GovernmentDomainRegistry(toon_dir)
    domains = dict(sorted(registry.all_domains().items()))
    return {"domain_count": len(domains), "domains": domains}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate a static government-domain manifest from TOON seed files."
    )
    parser.add_argument(
        "--toon-dir",
        type=Path,
        default=Path("data/toon-seeds/countries"),
        help="Directory of country TOON seed files (default: data/toon-seeds/countries)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("docs/data/gov-domains.json"),
        help="Output path for the manifest (default: docs/data/gov-domains.json)",
    )
    args = parser.parse_args(argv)

    manifest = build_manifest(args.toon_dir)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2, separators=(",", ":"))
        f.write("\n")

    print(f"Wrote {args.output}: {manifest['domain_count']} government domains")
    return 0


if __name__ == "__main__":
    sys.exit(main())
