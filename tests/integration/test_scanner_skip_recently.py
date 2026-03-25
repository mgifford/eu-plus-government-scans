"""Integration tests for skip-recently-scanned-days in social media and tech scanner jobs."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

from src.jobs.social_media_scanner import SocialMediaScannerJob
from src.jobs.tech_scanner import TechScanner
from src.lib.settings import Settings
from src.services.social_media_scanner import SocialMediaScanResult
from src.services.tech_detector import TechDetectionResult
from src.storage.schema import initialize_schema


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def temp_settings(tmp_path: Path) -> Settings:
    """Settings backed by a temporary database."""
    db_path = tmp_path / "test.db"
    return Settings(
        scheduler_cadence="monthly",
        crawl_rate_limit_per_host=0.5,
        crawl_timeout_seconds=2,
        toon_output_dir=tmp_path / "toon-cache",
        metadata_db_url=f"sqlite:///{db_path}",
    )


@pytest.fixture
def sample_toon_file(tmp_path: Path) -> Path:
    """Minimal TOON file with three page URLs."""
    toon_data = {
        "version": "0.1-seed",
        "country": "TestLand",
        "domains": [
            {
                "canonical_domain": "example.test",
                "pages": [
                    {"url": "https://example.test/page1"},
                    {"url": "https://example.test/page2"},
                    {"url": "https://example.test/page3"},
                ],
            }
        ],
    }
    toon_path = tmp_path / "testland.toon"
    toon_path.write_text(json.dumps(toon_data), encoding="utf-8")
    return toon_path


# ---------------------------------------------------------------------------
# SocialMediaScannerJob._get_recently_scanned_urls
# ---------------------------------------------------------------------------

def test_social_get_recently_scanned_empty_db(temp_settings):
    """Returns empty set when the database has no records."""
    job = SocialMediaScannerJob(temp_settings)
    result = job._get_recently_scanned_urls("TESTLAND", within_days=7)
    assert result == set()


def test_social_get_recently_scanned_returns_recent_urls(temp_settings):
    """URLs scanned within the window are returned."""
    job = SocialMediaScannerJob(temp_settings)
    now = datetime.now(timezone.utc).isoformat()

    conn = sqlite3.connect(job.db_path)
    try:
        conn.execute(
            """
            INSERT INTO url_social_media_results
            (url, country_code, scan_id, is_reachable, social_tier,
             twitter_links, x_links, bluesky_links, mastodon_links, scanned_at)
            VALUES (?, ?, ?, ?, ?, '[]', '[]', '[]', '[]', ?)
            """,
            ("https://example.test/page1", "TESTLAND", "s-001", 1, "no_social", now),
        )
        conn.commit()
    finally:
        conn.close()

    result = job._get_recently_scanned_urls("TESTLAND", within_days=7)
    assert "https://example.test/page1" in result


def test_social_get_recently_scanned_excludes_old_results(temp_settings):
    """URLs scanned outside the window are not returned."""
    job = SocialMediaScannerJob(temp_settings)
    old_ts = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()

    conn = sqlite3.connect(job.db_path)
    try:
        conn.execute(
            """
            INSERT INTO url_social_media_results
            (url, country_code, scan_id, is_reachable, social_tier,
             twitter_links, x_links, bluesky_links, mastodon_links, scanned_at)
            VALUES (?, ?, ?, ?, ?, '[]', '[]', '[]', '[]', ?)
            """,
            ("https://example.test/old", "TESTLAND", "s-old", 1, "no_social", old_ts),
        )
        conn.commit()
    finally:
        conn.close()

    result = job._get_recently_scanned_urls("TESTLAND", within_days=7)
    assert "https://example.test/old" not in result


def test_social_get_recently_scanned_excludes_other_countries(temp_settings):
    """URLs for a different country are not returned."""
    job = SocialMediaScannerJob(temp_settings)
    now = datetime.now(timezone.utc).isoformat()

    conn = sqlite3.connect(job.db_path)
    try:
        conn.execute(
            """
            INSERT INTO url_social_media_results
            (url, country_code, scan_id, is_reachable, social_tier,
             twitter_links, x_links, bluesky_links, mastodon_links, scanned_at)
            VALUES (?, ?, ?, ?, ?, '[]', '[]', '[]', '[]', ?)
            """,
            ("https://example.fr/page1", "FRANCE", "s-001", 1, "no_social", now),
        )
        conn.commit()
    finally:
        conn.close()

    result = job._get_recently_scanned_urls("TESTLAND", within_days=7)
    assert result == set()


@pytest.mark.asyncio
async def test_social_scan_country_skips_recently_scanned_urls(
    temp_settings, sample_toon_file
):
    """scan_country skips URLs already in the recent-scan window."""
    job = SocialMediaScannerJob(temp_settings)
    now = datetime.now(timezone.utc).isoformat()

    # Pre-populate page1 and page2 as recently scanned
    conn = sqlite3.connect(job.db_path)
    try:
        for url in ["https://example.test/page1", "https://example.test/page2"]:
            conn.execute(
                """
                INSERT INTO url_social_media_results
                (url, country_code, scan_id, is_reachable, social_tier,
                 twitter_links, x_links, bluesky_links, mastodon_links, scanned_at)
                VALUES (?, ?, ?, ?, ?, '[]', '[]', '[]', '[]', ?)
                """,
                (url, "TESTLAND", "s-prev", 1, "no_social", now),
            )
        conn.commit()
    finally:
        conn.close()

    scan_results: list[str] = []

    mock_result = SocialMediaScanResult(
        url="https://example.test/page3",
        is_reachable=True,
        social_tier="no_social",
    )

    async def _fake_scan_batch(urls, **kwargs):
        scan_results.extend(urls)
        on_result = kwargs.get("on_result")
        for url in urls:
            r = SocialMediaScanResult(url=url, is_reachable=True, social_tier="no_social")
            if on_result:
                on_result(r)
        return {u: SocialMediaScanResult(url=u, is_reachable=True, social_tier="no_social") for u in urls}

    with patch.object(job.scanner, "scan_urls_batch", side_effect=_fake_scan_batch):
        stats = await job.scan_country(
            "TESTLAND",
            sample_toon_file,
            skip_recently_scanned_days=7,
        )

    # Only page3 should have been submitted to the scanner
    assert scan_results == ["https://example.test/page3"]
    assert stats["urls_scanned"] == 1
    assert stats["urls_skipped_recently_scanned"] == 2
    assert stats["total_urls"] == 3


@pytest.mark.asyncio
async def test_social_scan_country_all_recently_scanned_skips_scan(
    temp_settings, sample_toon_file
):
    """When all URLs are recently scanned scan_country returns immediately."""
    job = SocialMediaScannerJob(temp_settings)
    now = datetime.now(timezone.utc).isoformat()

    conn = sqlite3.connect(job.db_path)
    try:
        for url in [
            "https://example.test/page1",
            "https://example.test/page2",
            "https://example.test/page3",
        ]:
            conn.execute(
                """
                INSERT INTO url_social_media_results
                (url, country_code, scan_id, is_reachable, social_tier,
                 twitter_links, x_links, bluesky_links, mastodon_links, scanned_at)
                VALUES (?, ?, ?, ?, ?, '[]', '[]', '[]', '[]', ?)
                """,
                (url, "TESTLAND", "s-prev", 1, "no_social", now),
            )
        conn.commit()
    finally:
        conn.close()

    with patch.object(job.scanner, "scan_urls_batch", new_callable=AsyncMock) as mock_scan:
        stats = await job.scan_country(
            "TESTLAND",
            sample_toon_file,
            skip_recently_scanned_days=7,
        )

    mock_scan.assert_not_called()
    assert stats["urls_scanned"] == 0
    assert stats["urls_skipped_recently_scanned"] == 3
    assert stats["is_complete"] is True


# ---------------------------------------------------------------------------
# TechScanner._get_recently_scanned_urls
# ---------------------------------------------------------------------------

def test_tech_get_recently_scanned_empty_db(temp_settings):
    """Returns empty set when the database has no records."""
    scanner = TechScanner(temp_settings)
    result = scanner._get_recently_scanned_urls("TESTLAND", within_days=7)
    assert result == set()


def test_tech_get_recently_scanned_returns_recent_urls(temp_settings):
    """URLs scanned within the window are returned."""
    scanner = TechScanner(temp_settings)
    now = datetime.now(timezone.utc).isoformat()

    conn = sqlite3.connect(scanner.db_path)
    try:
        conn.execute(
            """
            INSERT INTO url_tech_results
            (url, country_code, scan_id, technologies, scanned_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            ("https://example.test/page1", "TESTLAND", "t-001", "{}", now),
        )
        conn.commit()
    finally:
        conn.close()

    result = scanner._get_recently_scanned_urls("TESTLAND", within_days=7)
    assert "https://example.test/page1" in result


def test_tech_get_recently_scanned_excludes_old_results(temp_settings):
    """URLs scanned outside the window are not returned."""
    scanner = TechScanner(temp_settings)
    old_ts = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()

    conn = sqlite3.connect(scanner.db_path)
    try:
        conn.execute(
            """
            INSERT INTO url_tech_results
            (url, country_code, scan_id, technologies, scanned_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            ("https://example.test/old", "TESTLAND", "t-old", "{}", old_ts),
        )
        conn.commit()
    finally:
        conn.close()

    result = scanner._get_recently_scanned_urls("TESTLAND", within_days=7)
    assert "https://example.test/old" not in result


@pytest.mark.asyncio
async def test_tech_scan_country_skips_recently_scanned_urls(
    temp_settings, sample_toon_file
):
    """scan_country skips URLs already in the recent-scan window."""
    scanner = TechScanner(temp_settings)
    now = datetime.now(timezone.utc).isoformat()

    # Pre-populate page1 and page2 as recently scanned
    conn = sqlite3.connect(scanner.db_path)
    try:
        for url in ["https://example.test/page1", "https://example.test/page2"]:
            conn.execute(
                """
                INSERT INTO url_tech_results
                (url, country_code, scan_id, technologies, scanned_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (url, "TESTLAND", "t-prev", "{}", now),
            )
        conn.commit()
    finally:
        conn.close()

    scan_results: list[str] = []

    async def _fake_detect_batch(urls, **kwargs):
        scan_results.extend(urls)
        on_result = kwargs.get("on_result")
        for url in urls:
            r = TechDetectionResult(url=url, technologies={})
            if on_result:
                on_result(r)
        return {u: TechDetectionResult(url=u, technologies={}) for u in urls}

    with patch.object(scanner.detector, "detect_urls_batch", side_effect=_fake_detect_batch):
        stats = await scanner.scan_country(
            "TESTLAND",
            sample_toon_file,
            skip_recently_scanned_days=7,
        )

    # Only page3 should have been submitted to the detector
    assert scan_results == ["https://example.test/page3"]
    assert stats["urls_scanned"] == 1
    assert stats["urls_skipped_recently_scanned"] == 2
    assert stats["total_urls"] == 3


@pytest.mark.asyncio
async def test_tech_scan_country_all_recently_scanned_skips_scan(
    temp_settings, sample_toon_file
):
    """When all URLs are recently scanned scan_country returns immediately."""
    scanner = TechScanner(temp_settings)
    now = datetime.now(timezone.utc).isoformat()

    conn = sqlite3.connect(scanner.db_path)
    try:
        for url in [
            "https://example.test/page1",
            "https://example.test/page2",
            "https://example.test/page3",
        ]:
            conn.execute(
                """
                INSERT INTO url_tech_results
                (url, country_code, scan_id, technologies, scanned_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (url, "TESTLAND", "t-prev", "{}", now),
            )
        conn.commit()
    finally:
        conn.close()

    with patch.object(scanner.detector, "detect_urls_batch", new_callable=AsyncMock) as mock_detect:
        stats = await scanner.scan_country(
            "TESTLAND",
            sample_toon_file,
            skip_recently_scanned_days=7,
        )

    mock_detect.assert_not_called()
    assert stats["urls_scanned"] == 0
    assert stats["urls_skipped_recently_scanned"] == 3
    assert stats["is_complete"] is True
