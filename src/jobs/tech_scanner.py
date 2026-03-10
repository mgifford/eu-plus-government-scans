"""Technology scanner job for processing TOON files."""

from __future__ import annotations

import asyncio
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List
from uuid import uuid4

from src.lib.country_utils import country_filename_to_code
from src.lib.settings import Settings
from src.services.tech_detector import TechDetectionResult, TechDetector
from src.storage.schema import initialize_schema


class TechScanner:
    """Scanner for detecting technologies from TOON file URLs."""

    def __init__(self, settings: Settings):
        self.settings = settings
        self.detector = TechDetector(
            timeout_seconds=settings.crawl_timeout_seconds,
        )
        self.db_path = initialize_schema(settings.metadata_db_url)

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

    def _save_tech_results(
        self,
        results: List[TechDetectionResult],
        country_code: str,
        scan_id: str,
    ) -> None:
        """Persist technology detection results to the database."""
        conn = sqlite3.connect(self.db_path)
        try:
            for result in results:
                conn.execute(
                    """
                    INSERT INTO url_tech_results
                    (url, country_code, scan_id, technologies, error_message, scanned_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        result.url,
                        country_code,
                        scan_id,
                        json.dumps(result.technologies),
                        result.error_message,
                        result.scanned_at,
                    ),
                )
            conn.commit()
        finally:
            conn.close()

    def _update_toon_with_tech(
        self,
        toon_data: dict,
        tech_results: Dict[str, TechDetectionResult],
    ) -> dict:
        """
        Annotate TOON pages with detected technologies.

        Each page entry gains a ``technologies`` field (dict) and an optional
        ``tech_error`` field when detection failed for that URL.
        """
        for domain_entry in toon_data.get("domains", []):
            for page in domain_entry.get("pages", []):
                url = page.get("url")
                if url not in tech_results:
                    continue

                result = tech_results[url]
                if result.error_message:
                    page["tech_error"] = result.error_message
                else:
                    page["technologies"] = result.technologies

        return toon_data

    async def scan_country(
        self,
        country_code: str,
        toon_path: Path,
        rate_limit_per_second: float = 2.0,
    ) -> Dict[str, Any]:
        """
        Detect technologies for all URLs in a country's TOON file.

        Args:
            country_code: Country code (e.g. FRANCE).
            toon_path: Path to the TOON seed file.
            rate_limit_per_second: Maximum HTTP requests per second.

        Returns:
            Scan statistics dictionary.
        """
        scan_id = (
            f"tech-{country_code}-"
            f"{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S%f')}-"
            f"{uuid4().hex[:8]}"
        )

        print(f"Starting tech scan {scan_id} for {country_code}")
        print(f"Loading TOON file: {toon_path}")

        toon_data = self._load_toon_file(toon_path)
        urls = self._extract_urls_from_toon(toon_data)

        print(f"Found {len(urls)} URLs to scan")

        tech_results = await self.detector.detect_urls_batch(
            urls,
            rate_limit_per_second=rate_limit_per_second,
        )

        self._save_tech_results(list(tech_results.values()), country_code, scan_id)

        updated_toon = self._update_toon_with_tech(toon_data, tech_results)

        output_path = (
            toon_path.parent / f"{toon_path.stem}_tech{toon_path.suffix}"
        )
        with output_path.open("w", encoding="utf-8") as f:
            json.dump(updated_toon, f, indent=2, ensure_ascii=False)

        print(f"Saved tech-annotated TOON to: {output_path}")

        success_count = sum(
            1 for r in tech_results.values() if not r.error_message
        )
        error_count = len(tech_results) - success_count
        tech_detected_count = sum(
            1 for r in tech_results.values() if r.technologies
        )

        stats = {
            "scan_id": scan_id,
            "country_code": country_code,
            "total_urls": len(urls),
            "success_count": success_count,
            "error_count": error_count,
            "tech_detected_count": tech_detected_count,
            "output_path": str(output_path),
        }

        print(f"\nTech scan complete:")
        print(f"  Scanned:  {len(urls)}")
        print(f"  Success:  {success_count}")
        print(f"  Errors:   {error_count}")
        print(f"  With tech: {tech_detected_count}")

        return stats

    async def scan_all_countries(
        self,
        toon_seeds_dir: Path,
        rate_limit_per_second: float = 2.0,
    ) -> List[Dict[str, Any]]:
        """
        Scan all TOON files in a directory for technologies.

        Args:
            toon_seeds_dir: Directory containing TOON seed files.
            rate_limit_per_second: Maximum requests per second per country.

        Returns:
            List of scan statistics for each country.
        """
        all_stats = []
        toon_files = sorted(toon_seeds_dir.glob("*.toon"))

        print(f"Found {len(toon_files)} TOON files to process")

        for toon_path in toon_files:
            country_code = country_filename_to_code(toon_path.stem)
            try:
                stats = await self.scan_country(
                    country_code,
                    toon_path,
                    rate_limit_per_second,
                )
                all_stats.append(stats)
            except Exception as exc:
                print(f"Error scanning {toon_path}: {exc}")
                all_stats.append({"country_code": country_code, "error": str(exc)})

        return all_stats
