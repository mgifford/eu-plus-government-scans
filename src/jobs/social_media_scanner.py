"""Social media scanner job for processing TOON files."""

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
from src.services.social_media_scanner import SocialMediaScanResult, SocialMediaScanner
from src.storage.schema import initialize_schema


class SocialMediaScannerJob:
    """Scanner job for detecting social media links from TOON file URLs."""

    def __init__(self, settings: Settings):
        self.settings = settings
        self.scanner = SocialMediaScanner(
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

    def _save_social_media_results(
        self,
        results: List[SocialMediaScanResult],
        country_code: str,
        scan_id: str,
    ) -> None:
        """Persist social media scan results to the database."""
        conn = sqlite3.connect(self.db_path)
        try:
            for result in results:
                conn.execute(
                    """
                    INSERT INTO url_social_media_results
                    (url, country_code, scan_id, is_reachable,
                     twitter_links, x_links, bluesky_links, mastodon_links,
                     social_tier, error_message, scanned_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        result.url,
                        country_code,
                        scan_id,
                        1 if result.is_reachable else 0,
                        json.dumps(result.twitter_links),
                        json.dumps(result.x_links),
                        json.dumps(result.bluesky_links),
                        json.dumps(result.mastodon_links),
                        result.social_tier,
                        result.error_message,
                        result.scanned_at,
                    ),
                )
            conn.commit()
        finally:
            conn.close()

    def _update_toon_with_social_media(
        self,
        toon_data: dict,
        scan_results: Dict[str, SocialMediaScanResult],
    ) -> dict:
        """
        Annotate TOON pages with detected social media links.

        Each page entry gains a ``social_media`` field (dict) and an optional
        ``social_media_error`` field when scanning failed for that URL.
        """
        for domain_entry in toon_data.get("domains", []):
            for page in domain_entry.get("pages", []):
                url = page.get("url")
                if url not in scan_results:
                    continue

                result = scan_results[url]
                if result.error_message and not result.is_reachable:
                    page["social_media_error"] = result.error_message
                else:
                    page["social_media"] = {
                        "tier": result.social_tier,
                        "twitter": result.twitter_links,
                        "x": result.x_links,
                        "bluesky": result.bluesky_links,
                        "mastodon": result.mastodon_links,
                    }

        return toon_data

    async def scan_country(
        self,
        country_code: str,
        toon_path: Path,
        rate_limit_per_second: float = 2.0,
    ) -> Dict[str, Any]:
        """
        Scan all URLs in a country's TOON file for social media links.

        Args:
            country_code: Country code (e.g. FRANCE).
            toon_path: Path to the TOON seed file.
            rate_limit_per_second: Maximum HTTP requests per second.

        Returns:
            Scan statistics dictionary.
        """
        scan_id = (
            f"social-{country_code}-"
            f"{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S%f')}-"
            f"{uuid4().hex[:8]}"
        )

        print(f"Starting social media scan {scan_id} for {country_code}")
        print(f"Loading TOON file: {toon_path}")

        toon_data = self._load_toon_file(toon_path)
        urls = self._extract_urls_from_toon(toon_data)

        print(f"Found {len(urls)} URLs to scan")

        scan_results = await self.scanner.scan_urls_batch(
            urls,
            rate_limit_per_second=rate_limit_per_second,
        )

        self._save_social_media_results(
            list(scan_results.values()), country_code, scan_id
        )

        updated_toon = self._update_toon_with_social_media(toon_data, scan_results)

        output_path = (
            toon_path.parent / f"{toon_path.stem}_social{toon_path.suffix}"
        )
        with output_path.open("w", encoding="utf-8") as f:
            json.dump(updated_toon, f, indent=2, ensure_ascii=False)

        print(f"Saved social-media-annotated TOON to: {output_path}")

        reachable_count = sum(1 for r in scan_results.values() if r.is_reachable)
        unreachable_count = len(scan_results) - reachable_count
        twitter_count = sum(1 for r in scan_results.values() if r.twitter_links)
        x_count = sum(1 for r in scan_results.values() if r.x_links)
        bluesky_count = sum(1 for r in scan_results.values() if r.bluesky_links)
        mastodon_count = sum(1 for r in scan_results.values() if r.mastodon_links)

        tier_counts: Dict[str, int] = {}
        for r in scan_results.values():
            tier_counts[r.social_tier] = tier_counts.get(r.social_tier, 0) + 1

        stats = {
            "scan_id": scan_id,
            "country_code": country_code,
            "total_urls": len(urls),
            "reachable_count": reachable_count,
            "unreachable_count": unreachable_count,
            "twitter_count": twitter_count,
            "x_count": x_count,
            "bluesky_count": bluesky_count,
            "mastodon_count": mastodon_count,
            "tier_counts": tier_counts,
            "output_path": str(output_path),
        }

        print(f"\nSocial media scan complete:")
        print(f"  Scanned:     {len(urls)}")
        print(f"  Reachable:   {reachable_count}")
        print(f"  Unreachable: {unreachable_count}")
        print(f"  Twitter:     {twitter_count}")
        print(f"  X:           {x_count}")
        print(f"  Bluesky:     {bluesky_count}")
        print(f"  Mastodon:    {mastodon_count}")
        for tier, count in sorted(tier_counts.items()):
            print(f"  [{tier}]: {count}")

        return stats

    async def scan_all_countries(
        self,
        toon_seeds_dir: Path,
        rate_limit_per_second: float = 2.0,
    ) -> List[Dict[str, Any]]:
        """
        Scan all TOON files in a directory for social media links.

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
