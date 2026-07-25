"""CLI entry point to generate the static provenance-aware dataset."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from src.models.domain_model import GlobalSummary, CountrySummary
from src.services.canonical_domain_builder import CanonicalDomainBuilder
from src.services.relationship_aggregator import RelationshipAggregator
from src.services.software_heritage_fetcher import SoftwareHeritageFetcher


def write_json(path: Path, data: Any, minify: bool = True) -> None:
    """Write deterministic JSON to file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        if minify:
            # separators=(',', ':') removes whitespace
            json.dump(data, f, separators=(",", ":"), sort_keys=True)
        else:
            json.dump(data, f, indent=2, sort_keys=True)


def main():
    parser = argparse.ArgumentParser(
        description="Generate the provenance-aware government web relationship dataset."
    )
    parser.add_argument(
        "--toon-dir",
        type=Path,
        default=Path("data/toon-seeds/countries"),
        help="Directory containing TOON files.",
    )
    parser.add_argument(
        "--relationships-dir",
        type=Path,
        default=Path("data/work/relationships"),
        help="Directory containing JSONL relationship outputs.",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("docs/data"),
        help="Output directory for static JSONs.",
    )
    parser.add_argument(
        "--sh-commit",
        type=str,
        default="HEAD",
        help="Commit SHA for Software Heritage dataset.",
    )
    parser.add_argument(
        "--minify",
        action="store_true",
        default=True,
        help="Minify JSON output.",
    )
    args = parser.parse_args()

    # 1. Ingest Evidence
    builder = CanonicalDomainBuilder()
    
    print("Ingesting TOON files...")
    builder.ingest_toon_directory(args.toon_dir)

    print("Fetching and ingesting Software Heritage dataset...")
    try:
        # Note: in an async context we would await, but we can run it synchronously
        # via asyncio.run if needed, or if we mock it for tests.
        import asyncio
        fetcher = SoftwareHeritageFetcher()
        sh_path = asyncio.run(fetcher.fetch_and_cache(commit_sha=args.sh_commit))
        sh_data = fetcher.parse_dataset(sh_path)
        builder.ingest_software_heritage(sh_data)
    except Exception as e:
        print(f"Warning: Failed to fetch Software Heritage data: {e}")

    builder.fallback_tld_country_assignment()

    # 2. Aggregate Relationships
    print("Aggregating relationships...")
    aggregator = RelationshipAggregator(builder.domains)
    if args.relationships_dir.exists():
        aggregator.ingest_jsonl_relationships(args.relationships_dir)
    aggregator.compute_graph_metrics()

    # 3. Output Generation
    print("Generating static dataset...")
    out_dir = args.out_dir
    
    # Prepare directory
    if out_dir.exists():
        # Clean up existing country dirs if needed, but we don't want to wipe docs/data entirely
        # Let's just create/overwrite within it
        pass
    out_dir.mkdir(parents=True, exist_ok=True)

    now_iso = datetime.now(timezone.utc).isoformat()
    
    # Group by country
    country_nodes: Dict[str, List[dict]] = {}
    country_editorial_edges: Dict[str, List[dict]] = {}
    country_dependency_edges: Dict[str, List[dict]] = {}

    for domain_id, domain_record in builder.domains.items():
        cc = domain_record.country or "UNKNOWN"
        country_nodes.setdefault(cc, []).append(domain_record.model_dump())

    for key, edge in aggregator.edges.items():
        # Edge source country
        s_domain = builder.domains.get(edge.source)
        cc = s_domain.country if s_domain and s_domain.country else "UNKNOWN"
        
        edge_data = edge.model_dump()
        
        if edge.relationship_type in {"editorial_link", "form_destination"}:
            country_editorial_edges.setdefault(cc, []).append(edge_data)
        else:
            country_dependency_edges.setdefault(cc, []).append(edge_data)

    # Write countries
    domains_by_country = {}
    for cc in country_nodes.keys():
        cc_dir = out_dir / "countries" / cc
        
        nodes = sorted(country_nodes.get(cc, []), key=lambda x: x["domain"])
        e_edges = sorted(country_editorial_edges.get(cc, []), key=lambda x: (x["source"], x["target"]))
        d_edges = sorted(country_dependency_edges.get(cc, []), key=lambda x: (x["source"], x["target"]))
        
        write_json(cc_dir / "nodes.json", nodes, args.minify)
        write_json(cc_dir / "editorial-edges.json", e_edges, args.minify)
        write_json(cc_dir / "dependency-edges.json", d_edges, args.minify)
        
        c_summary = CountrySummary(
            country_code=cc,
            total_domains=len(nodes),
            total_edges=len(e_edges) + len(d_edges),
            generated_at=now_iso,
        )
        write_json(cc_dir / "summary.json", c_summary.model_dump(), args.minify)
        
        domains_by_country[cc] = len(nodes)

    # Global summaries
    edges_by_type = {}
    for key, edge in aggregator.edges.items():
        edges_by_type[edge.relationship_type] = edges_by_type.get(edge.relationship_type, 0) + 1

    g_summary = GlobalSummary(
        total_domains=len(builder.domains),
        total_edges=len(aggregator.edges),
        domains_by_country=domains_by_country,
        edges_by_type=edges_by_type,
        generated_at=now_iso,
    )
    
    global_dir = out_dir / "global"
    write_json(global_dir / "summary.json", g_summary.model_dump(), args.minify)
    
    # Top domains based on in_degree
    top_domains = sorted(
        [d.model_dump() for d in builder.domains.values()],
        key=lambda x: x["in_degree"],
        reverse=True
    )[:100]
    write_json(global_dir / "top-domains.json", top_domains, args.minify)

    # Manifest
    manifest = {
        "schema_version": "1.0.0",
        "generated_at": now_iso,
        "total_countries": len(domains_by_country),
        "total_domains": len(builder.domains),
        "total_edges": len(aggregator.edges),
    }
    write_json(out_dir / "manifest.json", manifest, args.minify)

    print(f"Dataset generated in {out_dir}")


if __name__ == "__main__":
    main()
