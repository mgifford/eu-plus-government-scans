"""Aggregates relationships into graph metrics and structured outputs."""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Set, Tuple

from src.models.domain_model import (
    CanonicalDomain,
    RelationshipEdgeMetrics,
)


class RelationshipAggregator:
    """Computes descriptive network metrics from observed relationships."""

    def __init__(self, canonical_domains: Dict[str, CanonicalDomain]):
        self.domains = canonical_domains
        # (source, target, relationship_type) -> RelationshipEdgeMetrics
        self.edges: Dict[Tuple[str, str, str], RelationshipEdgeMetrics] = {}

    def ingest_jsonl_relationships(self, jsonl_dir: Path) -> None:
        """Parse all relationship output files and merge them."""
        for jsonl_file in jsonl_dir.rglob("*.jsonl"):
            with jsonl_file.open("r", encoding="utf-8") as f:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                        source_domain = data.get("source_domain")
                        target_domain = data.get("target_domain")
                        rel_type = data.get("relationship_type")
                        if not source_domain or not target_domain or not rel_type:
                            continue

                        key = (source_domain, target_domain, rel_type)
                        
                        # We merge observations if they span multiple scans
                        if key not in self.edges:
                            self.edges[key] = RelationshipEdgeMetrics(
                                source=source_domain,
                                target=target_domain,
                                relationship_type=rel_type,
                                source_pages=data.get("source_pages", 0),
                                observations=data.get("observations", 0),
                                page_regions={},
                                first_seen=data.get("first_seen", ""),
                                last_seen=data.get("last_seen", ""),
                            )
                            # Handle page regions from array format (from previous scanner)
                            regions_list = data.get("page_regions", [])
                            if isinstance(regions_list, list):
                                for r in regions_list:
                                    self.edges[key].page_regions[r] = data.get("observations", 1) // max(1, len(regions_list))
                            
                        else:
                            edge = self.edges[key]
                            edge.source_pages += data.get("source_pages", 0)
                            edge.observations += data.get("observations", 0)
                            
                            # Merge dates
                            if data.get("first_seen") < edge.first_seen:
                                edge.first_seen = data.get("first_seen")
                            if data.get("last_seen") > edge.last_seen:
                                edge.last_seen = data.get("last_seen")
                                
                            regions_list = data.get("page_regions", [])
                            if isinstance(regions_list, list):
                                share = data.get("observations", 1) // max(1, len(regions_list))
                                for r in regions_list:
                                    edge.page_regions[r] = edge.page_regions.get(r, 0) + share

                    except json.JSONDecodeError:
                        continue

    def compute_graph_metrics(self) -> None:
        """Calculate in/out degrees for canonical domains based on editorial links."""
        
        # Track unique sources for in-degree unique orgs
        # domain -> set of unique source domains
        in_sources: Dict[str, Set[str]] = defaultdict(set)
        
        for (source, target, rel_type), edge in self.edges.items():
            # Apply metrics mainly to editorial links for gov structure,
            # though we could count others if wanted. The requirements imply
            # not to call them confidence scores, but graph metrics are fine.
            # Let's count all relationships for degree, but maybe distinguish.
            
            s_domain = self.domains.get(source)
            t_domain = self.domains.get(target)

            if s_domain:
                s_domain.out_degree += 1
                s_domain.weighted_out_degree += edge.observations

            if t_domain:
                t_domain.in_degree += 1
                t_domain.weighted_in_degree += edge.observations
                t_domain.unique_source_pages += edge.source_pages
                
                in_sources[target].add(source)

        for target, sources_set in in_sources.items():
            t_domain = self.domains.get(target)
            if t_domain:
                t_domain.unique_source_organizations = len(sources_set)
