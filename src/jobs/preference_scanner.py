"""User-preference signal scanner job for processing TOON files."""

from __future__ import annotations

import json
import sqlite3
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
from uuid import uuid4

from src.lib.country_utils import country_filename_to_code, iter_seed_toon_files
from src.lib.settings import Settings
from src.services.preference_scanner import PreferenceScanResult, PreferenceScanner
from src.storage.schema import initialize_schema


class PreferenceScannerJob:
    """Scanner job for user-preference signals and design-system adoption."""

    def __init__(self, settings: Settings):
        self.settings = settings
        self.scanner = PreferenceScanner(
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

    def _get_recently_scanned_urls(
        self, country_code: str, within_days: int
    ) -> Set[str]:
        """Return URLs already scanned within the last ``within_days`` days.

        Args:
            country_code: Country to look up.
            within_days: Consider results from the last N days.

        Returns:
            Set of URL strings that do not need re-scanning.
        """
        cutoff = (
            datetime.now(timezone.utc) - timedelta(days=within_days)
        ).isoformat()

        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.execute(
                """
                SELECT DISTINCT url
                FROM url_preference_results
                WHERE country_code = ?
                  AND scanned_at >= ?
                """,
                (country_code, cutoff),
            )
            return {row[0] for row in cursor.fetchall()}
        finally:
            conn.close()

    def _save_results(
        self,
        results: List[PreferenceScanResult],
        country_code: str,
        scan_id: str,
    ) -> None:
        """Persist preference scan results to the database."""
        conn = sqlite3.connect(self.db_path)
        try:
            for result in results:
                conn.execute(
                    """
                    INSERT INTO url_preference_results
                    (url, country_code, scan_id, is_reachable,
                     meta_color_scheme, features, feature_sources,
                     theme_toggle_hints, override_signals, design_systems,
                     stylesheets_checked, stylesheets_total,
                     error_message, scanned_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        result.url,
                        country_code,
                        scan_id,
                        1 if result.is_reachable else 0,
                        result.meta_color_scheme,
                        json.dumps(result.features),
                        json.dumps(result.feature_sources, sort_keys=True),
                        json.dumps(result.theme_toggle_hints),
                        json.dumps(result.override_signals),
                        json.dumps(result.design_systems),
                        result.stylesheets_checked,
                        result.stylesheets_total,
                        result.error_message,
                        result.scanned_at,
                    ),
                )
            conn.commit()
        finally:
            conn.close()

    def _update_toon_with_preferences(
        self,
        toon_data: dict,
        scan_results: Dict[str, PreferenceScanResult],
    ) -> dict:
        """Annotate TOON pages with detected preference signals.

        Each scanned page gains a compact ``preferences`` object with the
        detected features, override risks, and matched design systems; failed
        URLs gain ``preferences_error`` instead.

        Args:
            toon_data: Parsed TOON JSON dict (mutated in place).
            scan_results: Mapping of URL to :class:`PreferenceScanResult`.

        Returns:
            The updated *toon_data* dict.
        """
        for domain_entry in toon_data.get("domains", []):
            for page in domain_entry.get("pages", []):
                url = page.get("url")
                if url not in scan_results:
                    continue

                result = scan_results[url]
                if result.error_message and not result.is_reachable:
                    page["preferences_error"] = result.error_message
                else:
                    page["preferences"] = {
                        "features": result.features,
                        "meta_color_scheme": result.meta_color_scheme,
                        "theme_toggle_hints": result.theme_toggle_hints,
                        "override_signals": result.override_signals,
                        "design_systems": result.design_systems,
                        "stylesheets_checked": result.stylesheets_checked,
                        "stylesheets_total": result.stylesheets_total,
                    }

        return toon_data

    async def scan_country(
        self,
        country_code: str,
        toon_path: Path,
        rate_limit_per_second: float = 1.0,
        max_runtime_seconds: Optional[float] = None,
        start_time: Optional[float] = None,
        skip_recently_scanned_days: int = 0,
        max_urls: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Scan a country's TOON URLs for user-preference signals.

        Results are persisted incrementally as each URL is scanned, so
        partial results survive an early stop.

        Args:
            country_code: Country code (e.g. ICELAND).
            toon_path: Path to the TOON seed file.
            rate_limit_per_second: Maximum HTTP requests per second.
            max_runtime_seconds: Shared runtime budget in seconds measured
                from *start_time*; scanning stops with a 60-second buffer.
                ``None`` = no limit.
            start_time: ``time.monotonic()`` value from the start of the
                overall job.  ``None`` starts a fresh clock for this country.
            skip_recently_scanned_days: Skip URLs already scanned by this
                scanner within the last N days.  ``0`` disables skipping.
            max_urls: Optional cap on URLs scanned for this country.

        Returns:
            Scan statistics dictionary.
        """
        scan_id = (
            f"preference-{country_code}-"
            f"{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S%f')}-"
            f"{uuid4().hex[:8]}"
        )

        print(f"Starting preference scan {scan_id} for {country_code}")
        print(f"Loading TOON file: {toon_path}")

        toon_data = self._load_toon_file(toon_path)
        urls = self._extract_urls_from_toon(toon_data)
        total_urls = len(urls)

        skipped_count = 0
        if skip_recently_scanned_days > 0:
            recently_scanned = self._get_recently_scanned_urls(
                country_code, within_days=skip_recently_scanned_days
            )
            before = len(urls)
            urls = [u for u in urls if u not in recently_scanned]
            skipped_count = before - len(urls)
            if skipped_count:
                print(
                    f"  Skipping {skipped_count} URL(s) already scanned "
                    f"within the last {skip_recently_scanned_days} day(s)"
                )

        if max_urls is not None:
            urls = urls[:max_urls]

        print(f"Found {len(urls)} URLs to scan ({total_urls} total)")

        _start = start_time if start_time is not None else time.monotonic()

        def _save_result(result: PreferenceScanResult) -> None:
            """Persist a single scan result immediately after it is computed."""
            self._save_results([result], country_code, scan_id)

        scan_results = await self.scanner.scan_urls_batch(
            urls,
            rate_limit_per_second=rate_limit_per_second,
            max_runtime_seconds=max_runtime_seconds,
            start_time=_start,
            on_result=_save_result,
        )

        updated_toon = self._update_toon_with_preferences(toon_data, scan_results)

        output_path = (
            toon_path.parent / f"{toon_path.stem}_preferences{toon_path.suffix}"
        )
        with output_path.open("w", encoding="utf-8") as f:
            json.dump(updated_toon, f, indent=2, ensure_ascii=False)

        scanned_count = len(scan_results)
        is_complete = scanned_count == len(urls)
        if is_complete:
            print(f"Saved preference-annotated TOON to: {output_path}")
        else:
            print(
                f"Saved partial preference-annotated TOON to: {output_path} "
                f"({scanned_count}/{len(urls)} URLs scanned)"
            )

        reachable_count = sum(1 for r in scan_results.values() if r.is_reachable)
        with_signals = sum(
            1 for r in scan_results.values() if r.has_preference_support
        )
        with_css = sum(1 for r in scan_results.values() if r.css_scanned)
        with_override_risk = sum(
            1 for r in scan_results.values() if r.has_override_risk
        )

        feature_counts: Dict[str, int] = {}
        adoption_counts: Dict[str, int] = {}
        for result in scan_results.values():
            for feature in result.features:
                feature_counts[feature] = feature_counts.get(feature, 0) + 1
            for system in result.design_systems:
                adoption_counts[system] = adoption_counts.get(system, 0) + 1

        stats = {
            "scan_id": scan_id,
            "country_code": country_code,
            "total_urls": total_urls,
            "urls_scanned": scanned_count,
            "urls_skipped_recent": skipped_count,
            "is_complete": is_complete,
            "reachable_count": reachable_count,
            "urls_with_signals": with_signals,
            "urls_with_css_checked": with_css,
            "urls_with_override_risk": with_override_risk,
            "feature_counts": feature_counts,
            "adoption_counts": adoption_counts,
            "output_path": str(output_path),
        }

        print(f"\nPreference scan {'complete' if is_complete else 'partial'}:")
        print(f"  Scanned:                 {scanned_count}/{len(urls)}")
        print(f"  Reachable:               {reachable_count}")
        print(f"  With preference signals: {with_signals}")
        print(f"  With CSS tier checked:   {with_css}")
        print(f"  With override risk:      {with_override_risk}")
        if feature_counts:
            print("  Features:")
            for feature, count in sorted(
                feature_counts.items(), key=lambda x: -x[1]
            ):
                print(f"    {feature}: {count}")
        if adoption_counts:
            print("  Design-system adoption:")
            for system, count in sorted(adoption_counts.items(), key=lambda x: -x[1]):
                print(f"    {system}: {count}")

        return stats

    async def scan_all_countries(
        self,
        toon_seeds_dir: Path,
        rate_limit_per_second: float = 1.0,
        max_runtime_seconds: Optional[float] = None,
        skip_recently_scanned_days: int = 90,
        max_urls: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """Scan all TOON files in a directory for user-preference signals.

        Stops gracefully before *max_runtime_seconds* elapses so partial
        results are saved and the workflow is not hard-cancelled.

        Args:
            toon_seeds_dir: Directory containing TOON seed files.
            rate_limit_per_second: Maximum HTTP requests per second per country.
            max_runtime_seconds: Shared runtime budget in seconds.  No new
                country is started when fewer than 5 minutes remain.
                ``None`` means no limit.
            skip_recently_scanned_days: Skip URLs scanned within this many
                days so repeat runs make progress through the corpus.
            max_urls: Optional per-country cap on URLs scanned.

        Returns:
            List of scan statistics for each country processed.
        """
        all_stats: List[Dict[str, Any]] = []
        toon_files = iter_seed_toon_files(toon_seeds_dir)

        print(f"Found {len(toon_files)} TOON files to process")

        start_time = time.monotonic()
        _country_start_buffer = 5 * 60  # 5 minutes

        for toon_path in toon_files:
            country_code = country_filename_to_code(toon_path.stem)

            if max_runtime_seconds is not None:
                elapsed = time.monotonic() - start_time
                remaining = max_runtime_seconds - elapsed
                if remaining < _country_start_buffer:
                    print(
                        f"⏱️  Time budget near limit "
                        f"({elapsed / 60:.1f}m elapsed, "
                        f"{remaining / 60:.1f}m remaining) "
                        f"— skipping remaining countries starting with {country_code}"
                    )
                    break

            try:
                stats = await self.scan_country(
                    country_code,
                    toon_path,
                    rate_limit_per_second,
                    max_runtime_seconds=max_runtime_seconds,
                    start_time=start_time,
                    skip_recently_scanned_days=skip_recently_scanned_days,
                    max_urls=max_urls,
                )
                all_stats.append(stats)
            except Exception as exc:  # noqa: BLE001
                print(f"Error scanning {toon_path}: {exc}")
                all_stats.append({"country_code": country_code, "error": str(exc)})

        return all_stats
