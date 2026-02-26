"""URL validation scanner job for processing TOON files."""

from __future__ import annotations

import asyncio
import json
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Set
from uuid import uuid4

from src.lib.country_utils import country_filename_to_code
from src.lib.settings import Settings
from src.services.url_validator import UrlValidator, ValidationResult
from src.storage.schema import initialize_schema


@dataclass(slots=True)
class ScanSession:
    """Tracks state for a single validation scan session."""
    scan_id: str
    country_code: str
    failed_urls: Set[str]
    processed_urls: Set[str]
    

class UrlValidationScanner:
    """Scanner for validating URLs from TOON files."""

    def __init__(self, settings: Settings):
        self.settings = settings
        self.validator = UrlValidator(
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

    def _get_previous_failures(self, country_code: str) -> Dict[str, int]:
        """
        Get failure counts for URLs from previous scans.
        
        Returns:
            Dictionary mapping URL to failure count
        """
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.execute(
                """
                SELECT url, MAX(failure_count) as max_failures
                FROM url_validation_results
                WHERE country_code = ?
                GROUP BY url
                """,
                (country_code,)
            )
            return {row[0]: row[1] for row in cursor.fetchall()}
        finally:
            conn.close()

    def _save_validation_results(
        self,
        results: List[ValidationResult],
        country_code: str,
        scan_id: str,
        previous_failures: Dict[str, int],
    ):
        """Save validation results to database."""
        conn = sqlite3.connect(self.db_path)
        try:
            for result in results:
                # Calculate new failure count
                prev_failures = previous_failures.get(result.url, 0)
                new_failure_count = prev_failures + 1 if not result.is_valid else 0
                
                # Build redirect chain as JSON string
                redirect_chain_json = None
                if result.redirect_chain:
                    redirect_chain_json = json.dumps(result.redirect_chain)
                
                conn.execute(
                    """
                    INSERT INTO url_validation_results
                    (url, country_code, scan_id, status_code, error_message,
                     redirected_to, redirect_chain, is_valid, failure_count, validated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        result.url,
                        country_code,
                        scan_id,
                        result.status_code,
                        result.error_message,
                        result.redirected_to,
                        redirect_chain_json,
                        1 if result.is_valid else 0,
                        new_failure_count,
                        result.validated_at,
                    ),
                )
            conn.commit()
        finally:
            conn.close()

    def _update_toon_with_validation(
        self,
        toon_data: dict,
        validation_results: Dict[str, ValidationResult],
        urls_to_remove: Set[str],
    ) -> dict:
        """
        Update TOON data with validation results and remove failed URLs.
        
        Args:
            toon_data: Original TOON data
            validation_results: Validation results by URL
            urls_to_remove: URLs that failed twice and should be removed
            
        Returns:
            Updated TOON data
        """
        updated_domains = []
        
        for domain_entry in toon_data.get("domains", []):
            updated_pages = []
            
            for page in domain_entry.get("pages", []):
                url = page.get("url")
                
                # Skip URLs that should be removed (failed twice)
                if url in urls_to_remove:
                    continue
                
                # Add validation metadata
                if url in validation_results:
                    result = validation_results[url]
                    page["validation_status"] = "valid" if result.is_valid else "invalid"
                    
                    if result.status_code is not None:
                        page["status_code"] = result.status_code
                    
                    if result.error_message:
                        page["error_message"] = result.error_message
                    
                    if result.redirected_to:
                        page["redirected_to"] = result.redirected_to
                        # Update the URL to the redirect target for future scans
                        page["original_url"] = url
                        page["url"] = result.redirected_to
                
                updated_pages.append(page)
            
            # Only keep domain if it has pages left
            if updated_pages:
                domain_entry["pages"] = updated_pages
                updated_domains.append(domain_entry)
        
        # Update domain and page counts
        toon_data["domains"] = updated_domains
        toon_data["domain_count"] = len(updated_domains)
        toon_data["page_count"] = sum(len(d.get("pages", [])) for d in updated_domains)
        
        return toon_data

    async def scan_country(
        self,
        country_code: str,
        toon_path: Path,
        rate_limit_per_second: float = 2.0,
    ) -> Dict[str, Any]:
        """
        Scan all URLs in a country's TOON file.
        
        Args:
            country_code: ISO country code
            toon_path: Path to TOON file
            rate_limit_per_second: Max requests per second
            
        Returns:
            Scan statistics and results
        """
        scan_id = f"{country_code}-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}-{uuid4().hex[:8]}"
        
        print(f"Starting scan {scan_id} for {country_code}")
        print(f"Loading TOON file: {toon_path}")
        
        # Load TOON data
        toon_data = self._load_toon_file(toon_path)
        urls = self._extract_urls_from_toon(toon_data)
        
        print(f"Found {len(urls)} URLs to validate")
        
        # Get previous failure counts
        previous_failures = self._get_previous_failures(country_code)
        
        # Filter out URLs that already failed twice (skip them)
        urls_to_skip = {url for url, count in previous_failures.items() if count >= 2}
        urls_to_validate = [url for url in urls if url not in urls_to_skip]
        
        print(f"Skipping {len(urls_to_skip)} URLs that previously failed twice")
        print(f"Validating {len(urls_to_validate)} URLs")
        
        # Validate URLs
        validation_results = await self.validator.validate_urls_batch(
            urls_to_validate,
            rate_limit_per_second=rate_limit_per_second,
        )
        
        # Save results
        self._save_validation_results(
            list(validation_results.values()),
            country_code,
            scan_id,
            previous_failures,
        )
        
        # Identify newly failed URLs (failed twice total)
        newly_failed_twice = set()
        for url, result in validation_results.items():
            if not result.is_valid:
                prev_count = previous_failures.get(url, 0)
                if prev_count + 1 >= 2:
                    newly_failed_twice.add(url)
        
        # Combine with already failed URLs
        urls_to_remove = urls_to_skip | newly_failed_twice
        
        # Update TOON file with validation results
        updated_toon = self._update_toon_with_validation(
            toon_data,
            validation_results,
            urls_to_remove,
        )
        
        # Save updated TOON file
        output_path = toon_path.parent / f"{toon_path.stem}_validated{toon_path.suffix}"
        with output_path.open("w", encoding="utf-8") as f:
            json.dump(updated_toon, f, indent=2, ensure_ascii=False)
        
        print(f"Saved updated TOON to: {output_path}")
        
        # Calculate statistics
        valid_count = sum(1 for r in validation_results.values() if r.is_valid)
        invalid_count = len(validation_results) - valid_count
        redirect_count = sum(1 for r in validation_results.values() if r.redirected_to)
        
        stats = {
            "scan_id": scan_id,
            "country_code": country_code,
            "total_urls": len(urls),
            "urls_validated": len(urls_to_validate),
            "urls_skipped": len(urls_to_skip),
            "valid_urls": valid_count,
            "invalid_urls": invalid_count,
            "redirected_urls": redirect_count,
            "urls_removed": len(urls_to_remove),
            "output_path": str(output_path),
        }
        
        print(f"\nScan complete:")
        print(f"  Valid: {valid_count}")
        print(f"  Invalid: {invalid_count}")
        print(f"  Redirected: {redirect_count}")
        print(f"  Removed (failed 2x): {len(urls_to_remove)}")
        
        return stats

    async def scan_all_countries(
        self,
        toon_seeds_dir: Path,
        rate_limit_per_second: float = 2.0,
    ) -> List[Dict[str, Any]]:
        """
        Scan all TOON files in a directory.
        
        Args:
            toon_seeds_dir: Directory containing TOON files
            rate_limit_per_second: Max requests per second per country
            
        Returns:
            List of scan statistics for each country
        """
        all_stats = []
        
        # Find all .toon files
        toon_files = list(toon_seeds_dir.glob("*.toon"))
        
        print(f"Found {len(toon_files)} TOON files to process")
        
        for toon_path in sorted(toon_files):
            # Extract country code from filename using utility function
            country_code = country_filename_to_code(toon_path.stem)
            
            try:
                stats = await self.scan_country(
                    country_code,
                    toon_path,
                    rate_limit_per_second,
                )
                all_stats.append(stats)
            except Exception as e:
                print(f"Error scanning {toon_path}: {e}")
                all_stats.append({
                    "country_code": country_code,
                    "error": str(e),
                })
        
        return all_stats
