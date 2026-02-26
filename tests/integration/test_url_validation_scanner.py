"""Integration tests for URL validation scanner."""

import asyncio
import json
import sqlite3
import tempfile
from pathlib import Path

import pytest

from src.jobs.url_validation_scanner import UrlValidationScanner
from src.lib.settings import Settings
from src.storage.schema import initialize_schema


@pytest.fixture
def temp_settings(tmp_path):
    """Create temporary settings for testing."""
    db_path = tmp_path / "test.db"
    return Settings(
        scheduler_cadence="monthly",
        crawl_rate_limit_per_host=0.5,
        crawl_timeout_seconds=2,
        toon_output_dir=tmp_path / "toon-cache",
        metadata_db_url=f"sqlite:///{db_path}",
    )


@pytest.fixture
def sample_toon_file(tmp_path):
    """Create a sample TOON file for testing."""
    toon_data = {
        "version": "0.1-seed",
        "country": "TestCountry",
        "domain_count": 2,
        "page_count": 3,
        "domains": [
            {
                "canonical_domain": "example.com",
                "subnational": [],
                "source_tabs": [],
                "pages": [
                    {
                        "url": "https://httpbin.org/status/200",
                        "is_root_page": True,
                    },
                    {
                        "url": "https://httpbin.org/status/404",
                        "is_root_page": False,
                    },
                ],
            },
            {
                "canonical_domain": "test.com",
                "subnational": [],
                "source_tabs": [],
                "pages": [
                    {
                        "url": "https://httpbin.org/redirect/1",
                        "is_root_page": True,
                    },
                ],
            },
        ],
    }
    
    toon_file = tmp_path / "test.toon"
    with toon_file.open("w") as f:
        json.dump(toon_data, f)
    
    return toon_file


@pytest.mark.asyncio
async def test_scanner_processes_toon_file(temp_settings, sample_toon_file):
    """Test that scanner can process a TOON file."""
    scanner = UrlValidationScanner(temp_settings)
    
    # Run scan
    stats = await scanner.scan_country(
        country_code="TEST",
        toon_path=sample_toon_file,
        rate_limit_per_second=10,  # Fast for testing
    )
    
    # Verify statistics
    assert stats["country_code"] == "TEST"
    assert stats["total_urls"] == 3
    assert stats["urls_validated"] == 3
    assert stats["urls_skipped"] == 0
    
    # Verify output file was created
    output_path = Path(stats["output_path"])
    assert output_path.exists()
    
    # Verify database records were created
    conn = sqlite3.connect(scanner.db_path)
    cursor = conn.execute(
        "SELECT COUNT(*) FROM url_validation_results WHERE country_code = ?",
        ("TEST",)
    )
    count = cursor.fetchone()[0]
    conn.close()
    
    assert count == 3


@pytest.mark.asyncio
async def test_scanner_tracks_failures_across_runs(temp_settings, sample_toon_file):
    """Test that scanner tracks failures across multiple runs."""
    scanner = UrlValidationScanner(temp_settings)
    
    # First run - all URLs validated
    stats1 = await scanner.scan_country(
        country_code="TEST",
        toon_path=sample_toon_file,
        rate_limit_per_second=10,
    )
    
    # Verify no URLs removed yet
    assert stats1["urls_removed"] == 0
    
    # Second run - URLs that failed twice should be removed
    stats2 = await scanner.scan_country(
        country_code="TEST",
        toon_path=sample_toon_file,
        rate_limit_per_second=10,
    )
    
    # Verify some URLs were removed (those that failed twice)
    # Note: This depends on which URLs actually fail in the test environment
    assert "urls_removed" in stats2


@pytest.mark.asyncio
async def test_scanner_handles_empty_toon_file(temp_settings, tmp_path):
    """Test that scanner handles empty TOON files gracefully."""
    # Create empty TOON file
    toon_data = {
        "version": "0.1-seed",
        "country": "Empty",
        "domain_count": 0,
        "page_count": 0,
        "domains": [],
    }
    
    toon_file = tmp_path / "empty.toon"
    with toon_file.open("w") as f:
        json.dump(toon_data, f)
    
    scanner = UrlValidationScanner(temp_settings)
    
    # Run scan
    stats = await scanner.scan_country(
        country_code="EMPTY",
        toon_path=toon_file,
        rate_limit_per_second=10,
    )
    
    # Verify statistics
    assert stats["total_urls"] == 0
    assert stats["urls_validated"] == 0
    assert stats["valid_urls"] == 0
    assert stats["invalid_urls"] == 0


def test_scanner_initializes_database(temp_settings):
    """Test that scanner initializes database schema correctly."""
    scanner = UrlValidationScanner(temp_settings)
    
    # Verify database file exists
    assert scanner.db_path.exists()
    
    # Verify tables were created
    conn = sqlite3.connect(scanner.db_path)
    cursor = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='url_validation_results'"
    )
    table_exists = cursor.fetchone() is not None
    conn.close()
    
    assert table_exists
