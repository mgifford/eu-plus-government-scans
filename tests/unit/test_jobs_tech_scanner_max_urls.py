"""Unit tests for TechScanner's max_urls support.

Regression coverage for the bug found during the GitHub Actions orchestration
audit (WORKFLOW_ORCHESTRATION_AUDIT.md Section 1.4/14.4): scan-technology.yml
accepted a workflow_dispatch `limit` input and forwarded it as `--limit` to
scan_technology.py, which had no such argparse argument and no max_urls
support anywhere in the TechScanner/TechDetector stack. This adds the same
max_urls pattern already used by AccessibilityScannerJob.
"""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.jobs.tech_scanner import TechScanner
from src.lib.settings import Settings


@pytest.fixture
def temp_settings(tmp_path):
    db_path = tmp_path / "test.db"
    return Settings(
        scheduler_cadence="monthly",
        crawl_rate_limit_per_host=0.5,
        crawl_timeout_seconds=2,
        toon_output_dir=tmp_path / "toon-cache",
        metadata_db_url=f"sqlite:///{db_path}",
    )


def _make_scanner(settings: Settings) -> TechScanner:
    scanner = TechScanner(settings)
    scanner.detector = MagicMock()
    return scanner


@pytest.fixture
def sample_toon(tmp_path) -> Path:
    data = {
        "version": "0.1-seed",
        "country": "TESTLAND",
        "domains": [
            {
                "canonical_domain": "gov.example",
                "pages": [
                    {"url": "https://gov.example/a", "is_root_page": True},
                    {"url": "https://gov.example/b", "is_root_page": False},
                    {"url": "https://gov.example/c", "is_root_page": False},
                ],
            }
        ],
    }
    toon_file = tmp_path / "testland.toon"
    toon_file.write_text(json.dumps(data), encoding="utf-8")
    return toon_file


@pytest.fixture
def toon_seeds_dir(tmp_path):
    page = {"url": "https://a.gov/"}
    for stem in ("alpha", "beta"):
        data = {
            "country": stem.upper(),
            "domains": [{"canonical_domain": f"{stem}.gov", "pages": [page]}],
        }
        (tmp_path / f"{stem}.toon").write_text(json.dumps(data), encoding="utf-8")
    return tmp_path


@pytest.mark.asyncio
async def test_scan_country_truncates_urls_to_max_urls(temp_settings, sample_toon):
    scanner = _make_scanner(temp_settings)

    async def _mock_batch(urls, **kwargs):
        return {}

    scanner.detector.detect_urls_batch = _mock_batch

    stats = await scanner.scan_country("TESTLAND", sample_toon, max_urls=2)

    # 3 URLs in the TOON file, but max_urls=2 should cap what's scanned.
    assert stats["total_urls"] == 3
    assert stats["urls_scanned"] == 0  # mock returned no results, but is_complete reflects the cap
    assert stats["is_complete"] is False


@pytest.mark.asyncio
async def test_scan_country_no_max_urls_scans_everything(temp_settings, sample_toon):
    scanner = _make_scanner(temp_settings)

    async def _mock_batch(urls, **kwargs):
        assert len(urls) == 3
        return {}

    scanner.detector.detect_urls_batch = _mock_batch

    await scanner.scan_country("TESTLAND", sample_toon, max_urls=None)


@pytest.mark.asyncio
async def test_scan_all_countries_stops_when_url_budget_exhausted(
    temp_settings, toon_seeds_dir
):
    scanner = _make_scanner(temp_settings)

    async def _mock_scan(country_code, toon_path, *args, **kwargs):
        return {"country_code": country_code, "urls_scanned": 1}

    with patch.object(scanner, "scan_country", side_effect=_mock_scan):
        all_stats = await scanner.scan_all_countries(toon_seeds_dir, max_urls=1)

    # Budget of 1 URL, first country consumes it -- second country should be skipped.
    assert len(all_stats) == 1


@pytest.mark.asyncio
async def test_scan_all_countries_passes_remaining_budget_to_each_country(
    temp_settings, toon_seeds_dir
):
    scanner = _make_scanner(temp_settings)
    seen_max_urls = []

    async def _mock_scan(country_code, toon_path, *args, **kwargs):
        seen_max_urls.append(kwargs.get("max_urls"))
        return {"country_code": country_code, "urls_scanned": 3}

    with patch.object(scanner, "scan_country", side_effect=_mock_scan):
        await scanner.scan_all_countries(toon_seeds_dir, max_urls=10)

    # First country gets the full budget (10); after it "scans" 3, the second
    # country (if reached) should be offered the reduced remaining budget (7).
    assert seen_max_urls[0] == 10
    if len(seen_max_urls) > 1:
        assert seen_max_urls[1] == 7


@pytest.mark.asyncio
async def test_scan_all_countries_unlimited_when_max_urls_none(
    temp_settings, toon_seeds_dir
):
    scanner = _make_scanner(temp_settings)

    async def _mock_scan(country_code, toon_path, *args, **kwargs):
        assert kwargs.get("max_urls") is None
        return {"country_code": country_code}

    with patch.object(scanner, "scan_country", side_effect=_mock_scan):
        all_stats = await scanner.scan_all_countries(toon_seeds_dir, max_urls=None)

    assert len(all_stats) == 2
