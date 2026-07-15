"""Service for aggregating relationship JSONL files into canonical datasets."""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Dict, Any, List

from src.models.domain_model import (
    CanonicalDomain,
    SourceEvidence,
    RelationshipEdgeMetrics,
    GlobalSummary,
    GovernmentLevel,
    OrganizationType,
    ClassificationStatus,
    ClassificationBasis,
)
from src.services.canonical_domain_builder import CanonicalDomainBuilder


class RelationshipAggregator:
    """Aggregates relationship observations from JSONL files into canonical datasets."""

    def __init__(self, domains_dir: Path = Path("src/domains")):
        self.domains_dir = domains_dir
        self.domain_builder = CanonicalDomainBuilder(domains_dir)

    def load_relationship_jsonl(self, jsonl_path: Path) -> List[Dict[str, Any]]:
        """Load relationship observations from a JSONL file."""
        observations = []
        try:
            with jsonl_path.open("r", encoding="utf-8") as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        observation = json.loads(line)
                        observations.append(observation)
                    except json.JSONDecodeError as e:
                        print(
                            f"Warning: Skipping invalid JSON on line {line_num} "
                            f"in {jsonl_path}: {e}"
                        )
        except Exception as e:
            print(f"Warning: Failed to load {jsonl_path}: {e}")
        return observations

    def aggregate_relationships(
        self, work_relationships_dir: Path
    ) -> Dict[str, Any]:
        """
        Aggregate relationships from all scan batches and build canonical domains.

        Args:
            work_relationships_dir: Directory containing relationship JSONL files
                                    (data/work/relationships/<scan-id>/*.jsonl)

        Returns:
            Dict with canonical_domains and relationship_metrics
        """
        if not work_relationships_dir.exists():
            print(f"Warning: {work_relationships_dir} does not exist")
            return {"canonical_domains": {}, "relationship_metrics": []}

        all_observations = []
        for jsonl_file in work_relationships_dir.glob("*.jsonl"):
            all_observations.extend(self.load_relationship_jsonl(jsonl_file))

        if not all_observations:
            print("Warning: No relationship observations found")
            return {"canonical_domains": {}, "relationship_metrics": []}

        domain_builder = CanonicalDomainBuilder(self.domains_dir)
        canonical_domains = self._build_canonical_domains(
            all_observations, domain_builder
        )

        relationship_metrics = self._build_relationship_metrics(all_observations)

        return {
            "canonical_domains": canonical_domains,
            "relationship_metrics": relationship_metrics,
        }

    def _build_canonical_domains(
        self,
        observations: List[Dict[str, Any]],
        domain_builder: CanonicalDomainBuilder,
    ) -> Dict[str, CanonicalDomain]:
        """Build canonical domain records from relationship observations."""
        canonical_domains: Dict[str, CanonicalDomain] = {}

        for obs in observations:
            source_domain = obs.get("source_domain")
            target_domain = obs.get("target_domain")
            target_category = obs.get("target_category", "unknown_external")

            for domain in [source_domain, target_domain]:
                if domain not in canonical_domains:
                    canonical_domain = domain_builder.build_canonical_domain(
                        domain, target_category
                    )
                    if canonical_domain:
                        canonical_domains[domain] = canonical_domain

        return canonical_domains

    def _build_relationship_metrics(
        self, observations: List[Dict[str, Any]]
    ) -> List[RelationshipEdgeMetrics]:
        """Build relationship edge metrics from aggregated observations."""
        edge_metrics: Dict[str, RelationshipEdgeMetrics] = {}

        for obs in observations:
            key = (
                obs.get("source_domain"),
                obs.get("target_domain"),
                obs.get("relationship_type"),
            )

            if key not in edge_metrics:
                edge_metrics[key] = RelationshipEdgeMetrics(
                    source=obs.get("source_domain"),
                    target=obs.get("target_domain"),
                    relationship_type=obs.get("relationship_type"),
                    source_pages=int(obs.get("source_pages", 0)),
                    observations=int(obs.get("observations", 0)),
                    page_regions=self._parse_page_regions(obs.get("page_regions", [])),
                    first_seen=obs.get("first_seen", ""),
                    last_seen=obs.get("last_seen", ""),
                )
            else:
                edge = edge_metrics[key]
                edge.source_pages += int(obs.get("source_pages", 0))
                edge.observations += int(obs.get("observations", 0))
                edge.page_regions.update(self._parse_page_regions(obs.get("page_regions", [])))
                if obs.get("first_seen", "") < edge.first_seen:
                    edge.first_seen = obs.get("first_seen", "")
                if obs.get("last_seen", "") > edge.last_seen:
                    edge.last_seen = obs.get("last_seen", "")

        return list(edge_metrics.values())

    def _parse_page_regions(self, regions: List[str]) -> Dict[str, int]:
        """Parse page regions into a frequency dictionary."""
        region_counts: Dict[str, int] = defaultdict(int)
        for region in regions:
            region_counts[region] += 1
        return dict(region_counts)
