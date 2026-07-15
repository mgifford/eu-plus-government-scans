"""Relationship scanner job for batch processing TOON files and aggregating output."""

from __future__ import annotations

import json
import time
from collections import defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4

from src.lib.country_utils import country_filename_to_code
from src.lib.settings import Settings
from src.services.multi_scanner import MultiScanner, MultiScanResult
from src.services.relationship_scanner import RelationshipEdge


@dataclass
class AggregatedRelationship:
    source_domain: str
    target_domain: str
    target_hostname: str
    relationship_type: str
    target_category: str
    source_pages: set[str]
    observations: int
    page_regions: set[str]
    first_seen: str
    last_seen: str

    def to_dict(self) -> dict:
        return {
            "source_domain": self.source_domain,
            "target_domain": self.target_domain,
            "target_hostname": self.target_hostname,
            "relationship_type": self.relationship_type,
            "target_category": self.target_category,
            "source_pages": len(self.source_pages),
            "observations": self.observations,
            "page_regions": sorted(list(self.page_regions)),
            "first_seen": self.first_seen,
            "last_seen": self.last_seen,
        }


class RelationshipScannerJob:
    """Scanner job for extracting and aggregating relationships."""

    def __init__(self, settings: Settings):
        self.settings = settings
        self.scanner = MultiScanner(
            timeout_seconds=settings.crawl_timeout_seconds,
            run_accessibility=False,
            run_social_media=False,
            run_tech=False,
            run_third_party_js=False,
            run_relationships=True,
        )

    def _load_toon_file(self, toon_path: Path) -> dict:
        """Load and parse a TOON file."""
        with toon_path.open("r", encoding="utf-8") as f:
            return json.load(f)

    def _extract_urls_from_toon(self, toon_data: dict) -> List[str]:
        """Extract all page URLs from TOON data structure."""
        urls = []
        for domain_entry in toon_data.get("domains", []):
            for page in domain_entry.get("pages", []):
                url = page.get("url")
                if url:
                    urls.append(url)
        return urls

    async def scan_country(
        self,
        country_code: str,
        toon_path: Path,
        rate_limit_per_second: float = 2.0,
        max_runtime_seconds: Optional[float] = None,
        start_time: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Scan a country's URLs and write aggregated relationships.
        """
        scan_id = (
            f"rels-{country_code}-"
            f"{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}-"
            f"{uuid4().hex[:8]}"
        )
        batch_id = f"batch-{uuid4().hex[:8]}"

        print(f"Starting relationship scan {scan_id} for {country_code}")
        
        toon_data = self._load_toon_file(toon_path)
        urls = self._extract_urls_from_toon(toon_data)
        
        # Deduplicate URLs
        urls = list(set(urls))
        print(f"Found {len(urls)} unique URLs to scan")

        _start = start_time if start_time is not None else time.monotonic()
        
        # Aggregation state
        aggregated: dict[tuple[str, str, str, str], AggregatedRelationship] = {}

        def _on_result(result: MultiScanResult) -> None:
            if not result.relationships or not result.relationships.relationships:
                return
                
            scanned_at = result.scanned_at or datetime.now(timezone.utc).isoformat()
            
            for edge in result.relationships.relationships:
                key = (
                    edge.source_domain,
                    edge.target_domain,
                    edge.target_hostname,
                    edge.relationship_type
                )
                
                if key not in aggregated:
                    aggregated[key] = AggregatedRelationship(
                        source_domain=edge.source_domain,
                        target_domain=edge.target_domain,
                        target_hostname=edge.target_hostname,
                        relationship_type=edge.relationship_type,
                        target_category=edge.target_category,
                        source_pages={result.url},
                        observations=1,
                        page_regions={edge.page_region},
                        first_seen=scanned_at,
                        last_seen=scanned_at,
                    )
                else:
                    agg = aggregated[key]
                    agg.source_pages.add(result.url)
                    agg.observations += 1
                    agg.page_regions.add(edge.page_region)
                    if scanned_at < agg.first_seen:
                        agg.first_seen = scanned_at
                    if scanned_at > agg.last_seen:
                        agg.last_seen = scanned_at

        scan_results = await self.scanner.scan_urls_batch(
            urls,
            rate_limit_per_second=rate_limit_per_second,
            max_runtime_seconds=max_runtime_seconds,
            start_time=_start,
            on_result=_on_result,
        )

        scanned_count = len(scan_results)
        is_complete = scanned_count == len(urls)

        # Write output to JSONL
        out_dir = Path("data/work/relationships") / scan_id
        out_dir.mkdir(parents=True, exist_ok=True)
        out_file = out_dir / f"{batch_id}.jsonl"

        with out_file.open("w", encoding="utf-8") as f:
            for agg in aggregated.values():
                f.write(json.dumps(agg.to_dict()) + "\n")

        print(f"Saved aggregated relationships to: {out_file}")

        stats = {
            "scan_id": scan_id,
            "country_code": country_code,
            "total_urls": len(urls),
            "urls_scanned": scanned_count,
            "is_complete": is_complete,
            "relationships_extracted": sum(agg.observations for agg in aggregated.values()),
            "unique_edges": len(aggregated),
            "output_path": str(out_file),
        }
        
        return stats
