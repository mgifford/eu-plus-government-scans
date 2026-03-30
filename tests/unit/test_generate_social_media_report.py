"""Tests for the social media stats report generator."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pytest

from src.cli.generate_social_media_report import (
    _build_stats_block,
    _query_by_country,
    _query_summary,
    generate_social_media_report,
)
from src.storage.schema import initialize_schema


# ---------------------------------------------------------------------------
# fixtures
# ---------------------------------------------------------------------------

_STATS_MARKER_START = "<!-- SOCIAL_MEDIA_STATS_START -->"
_STATS_MARKER_END = "<!-- SOCIAL_MEDIA_STATS_END -->"

_SOCIAL_MEDIA_PAGE_TEMPLATE = """\
---
title: Social Media Scanning
layout: page
---

# Social Media Scanning

## Current Stats

<!-- SOCIAL_MEDIA_STATS_START -->

_No scan data yet._

<!-- SOCIAL_MEDIA_STATS_END -->

## Overview

Some content.
"""


@pytest.fixture
def empty_db(tmp_path: Path) -> Path:
    """Return path to a freshly initialised, empty database."""
    db_path = tmp_path / "test.db"
    initialize_schema(f"sqlite:///{db_path}")
    return db_path


@pytest.fixture
def populated_db(tmp_path: Path) -> Path:
    """Return path to a database with sample social media scan data."""
    db_path = tmp_path / "test.db"
    initialize_schema(f"sqlite:///{db_path}")

    conn = sqlite3.connect(db_path)
    try:
        rows = [
            # url, country, scan_id, is_reachable, twitter, x, bluesky, mastodon,
            # facebook, linkedin, tier
            (
                "https://example.is/page1",
                "ICELAND",
                "social-ICELAND-20240601-001",
                1, '["https://twitter.com/gov_is"]', '[]', '[]', '[]',
                '[]', '[]',
                "twitter_only", "2024-06-01T10:00:00+00:00",
            ),
            (
                "https://example.is/page2",
                "ICELAND",
                "social-ICELAND-20240601-001",
                0, '[]', '[]', '[]', '[]',
                '[]', '[]',
                "unreachable", "2024-06-01T10:01:00+00:00",
            ),
            (
                "https://example.is/page3",
                "ICELAND",
                "social-ICELAND-20240601-001",
                1, '[]', '[]',
                '["https://bsky.app/profile/gov.is"]',
                '["https://mastodon.social/@gov_is"]',
                '[]', '[]',
                "modern_only", "2024-06-01T10:02:00+00:00",
            ),
            (
                "https://example.fr/page1",
                "FRANCE",
                "social-FRANCE-20240602-001",
                1, '[]', '["https://x.com/france_gov"]',
                '[]', '[]',
                '["https://www.facebook.com/francegov"]', '[]',
                "twitter_only", "2024-06-02T08:00:00+00:00",
            ),
            (
                "https://example.fr/page2",
                "FRANCE",
                "social-FRANCE-20240602-001",
                1, '[]', '[]', '[]', '[]',
                '[]', '[]',
                "no_social", "2024-06-02T08:01:00+00:00",
            ),
        ]
        for row in rows:
            conn.execute(
                """
                INSERT INTO url_social_media_results
                (url, country_code, scan_id, is_reachable,
                 twitter_links, x_links, bluesky_links, mastodon_links,
                 facebook_links, linkedin_links,
                 social_tier, scanned_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                row,
            )
        conn.commit()
    finally:
        conn.close()

    return db_path


# ---------------------------------------------------------------------------
# _query_summary tests
# ---------------------------------------------------------------------------

def test_query_summary_empty_db(empty_db: Path):
    """Should return zero/null values from an empty database."""
    conn = sqlite3.connect(empty_db)
    conn.row_factory = sqlite3.Row
    try:
        result = _query_summary(conn)
    finally:
        conn.close()

    assert result.get("total_batches", 0) == 0
    assert result.get("total_scanned", 0) == 0


def test_query_summary_populated_db(populated_db: Path):
    """Should aggregate stats correctly across countries."""
    conn = sqlite3.connect(populated_db)
    conn.row_factory = sqlite3.Row
    try:
        result = _query_summary(conn)
    finally:
        conn.close()

    assert result["total_batches"] == 2   # 2 distinct scan_ids
    assert result["total_scanned"] == 5   # 5 distinct URLs
    assert result["total_reachable"] == 4  # 4 reachable
    assert result["twitter_pages"] == 1    # 1 page with twitter links
    assert result["x_pages"] == 1          # 1 page with x links
    assert result["bluesky_pages"] == 1    # 1 page with bluesky links
    assert result["mastodon_pages"] == 1   # 1 page with mastodon links
    assert result["facebook_pages"] == 1   # 1 page with facebook links
    assert result["linkedin_pages"] == 0   # no pages with linkedin links


# ---------------------------------------------------------------------------
# _query_by_country tests
# ---------------------------------------------------------------------------

def test_query_by_country_populated_db(populated_db: Path):
    """Should return per-country rows sorted alphabetically."""
    conn = sqlite3.connect(populated_db)
    conn.row_factory = sqlite3.Row
    try:
        rows = _query_by_country(conn)
    finally:
        conn.close()

    assert len(rows) == 2
    countries = [r["country_code"] for r in rows]
    assert countries == ["FRANCE", "ICELAND"]

    iceland = next(r for r in rows if r["country_code"] == "ICELAND")
    assert iceland["total_scanned"] == 3
    assert iceland["reachable"] == 2


# ---------------------------------------------------------------------------
# _build_stats_block tests
# ---------------------------------------------------------------------------

def test_build_stats_block_empty_summary():
    """Should return a placeholder block when no summary data is available."""
    block = _build_stats_block({}, "2024-06-01 12:00 UTC")
    assert _STATS_MARKER_START in block
    assert _STATS_MARKER_END in block
    assert "No scan data yet" in block


def test_build_stats_block_with_data():
    """Should produce a block containing the key stat figures."""
    summary = {
        "total_batches": 10,
        "total_scanned": 500,
        "total_reachable": 450,
        "twitter_pages": 30,
        "x_pages": 20,
        "bluesky_pages": 15,
        "mastodon_pages": 12,
        "facebook_pages": 40,
        "linkedin_pages": 25,
        "last_scan": "2024-06-01T12:00:00",
    }
    block = _build_stats_block(summary, "2024-06-01 12:00 UTC")
    assert _STATS_MARKER_START in block
    assert _STATS_MARKER_END in block
    assert "10" in block          # batches
    assert "500" in block         # scanned
    assert "450" in block         # reachable
    assert "30" in block          # twitter
    assert "15" in block          # bluesky
    assert "12" in block          # mastodon
    assert "40" in block          # facebook
    assert "25" in block          # linkedin
    assert "social-media-data.json" in block


# ---------------------------------------------------------------------------
# generate_social_media_report tests
# ---------------------------------------------------------------------------

def test_generate_social_media_report_missing_db(tmp_path: Path):
    """Should write an empty-data JSON file and a placeholder stats block."""
    page_path = tmp_path / "social-media.md"
    page_path.write_text(_SOCIAL_MEDIA_PAGE_TEMPLATE)
    data_path = tmp_path / "social-media-data.json"
    db_path = tmp_path / "nonexistent.db"

    result = generate_social_media_report(db_path, page_path, data_path)

    assert result is True
    assert data_path.exists()
    data = json.loads(data_path.read_text())
    assert data["summary"]["total_scanned"] == 0

    content = page_path.read_text()
    assert _STATS_MARKER_START in content
    assert _STATS_MARKER_END in content
    assert "No scan data yet" in content
    assert "## Overview" in content  # rest of page preserved


def test_generate_social_media_report_with_data(populated_db: Path, tmp_path: Path):
    """Should inject real stats and write accurate JSON data."""
    page_path = tmp_path / "social-media.md"
    page_path.write_text(_SOCIAL_MEDIA_PAGE_TEMPLATE)
    data_path = tmp_path / "social-media-data.json"

    result = generate_social_media_report(populated_db, page_path, data_path)

    assert result is True

    # Check JSON data file
    assert data_path.exists()
    data = json.loads(data_path.read_text())
    assert data["summary"]["total_batches"] == 2
    assert data["summary"]["total_scanned"] == 5
    assert data["summary"]["total_reachable"] == 4
    assert data["summary"]["twitter_pages"] == 1
    assert data["summary"]["x_pages"] == 1
    assert data["summary"]["bluesky_pages"] == 1
    assert data["summary"]["mastodon_pages"] == 1
    assert len(data["by_country"]) == 2

    # Check Markdown page was updated
    content = page_path.read_text()
    assert _STATS_MARKER_START in content
    assert _STATS_MARKER_END in content
    assert "5" in content       # total scanned
    assert "4" in content       # reachable
    assert "social-media-data.json" in content
    # Rest of the page must still be present
    assert "## Overview" in content


def test_generate_social_media_report_missing_markers(populated_db: Path, tmp_path: Path):
    """Should return False without modifying the page when markers are absent."""
    page_path = tmp_path / "social-media.md"
    original = "# Social Media\n\nNo markers here.\n"
    page_path.write_text(original)
    data_path = tmp_path / "social-media-data.json"

    result = generate_social_media_report(populated_db, page_path, data_path)

    assert result is False
    assert page_path.read_text() == original
    # JSON data file is still written even when the page update fails
    assert data_path.exists()


def test_generate_social_media_report_missing_page(populated_db: Path, tmp_path: Path):
    """Should return False when the social-media.md page does not exist."""
    page_path = tmp_path / "nonexistent.md"
    data_path = tmp_path / "social-media-data.json"

    result = generate_social_media_report(populated_db, page_path, data_path)

    assert result is False
    # JSON data file is still written
    assert data_path.exists()


def test_generate_social_media_report_json_structure(populated_db: Path, tmp_path: Path):
    """JSON data file should have the expected top-level keys."""
    page_path = tmp_path / "social-media.md"
    page_path.write_text(_SOCIAL_MEDIA_PAGE_TEMPLATE)
    data_path = tmp_path / "social-media-data.json"

    generate_social_media_report(populated_db, page_path, data_path)

    data = json.loads(data_path.read_text())
    assert "generated_at" in data
    assert "summary" in data
    assert "by_country" in data

    summary = data["summary"]
    for key in ("total_batches", "total_scanned", "total_reachable",
                "twitter_pages", "x_pages", "bluesky_pages", "mastodon_pages",
                "facebook_pages", "linkedin_pages"):
        assert key in summary, f"Missing key: {key}"


def test_generate_social_media_report_preserves_page_structure(
    populated_db: Path, tmp_path: Path
):
    """Content outside the markers must be preserved after an update."""
    page_path = tmp_path / "social-media.md"
    page_path.write_text(_SOCIAL_MEDIA_PAGE_TEMPLATE)
    data_path = tmp_path / "social-media-data.json"

    generate_social_media_report(populated_db, page_path, data_path)

    content = page_path.read_text()
    # Front matter and heading
    assert "title: Social Media Scanning" in content
    assert "# Social Media Scanning" in content
    # Section after the markers
    assert "## Overview" in content
    assert "Some content." in content


# ---------------------------------------------------------------------------
# Tests for duplicate URL handling (inflated counts bug)
# ---------------------------------------------------------------------------

@pytest.fixture
def duplicate_scan_db(tmp_path: Path) -> Path:
    """DB where the same URL appears in two different scan batches."""
    db_path = tmp_path / "test.db"
    initialize_schema(f"sqlite:///{db_path}")
    conn = sqlite3.connect(db_path)
    try:
        # Same URL scanned twice in different batches
        rows = [
            (
                "https://example.is/page1", "ICELAND",
                "social-ICELAND-scan-001", 1,
                '["https://twitter.com/gov_is"]', '[]', '[]', '[]',
                '[]', '[]',
                "twitter_only", "2024-06-01T10:00:00+00:00",
            ),
            # Same URL in a second batch - should NOT be double-counted
            (
                "https://example.is/page1", "ICELAND",
                "social-ICELAND-scan-002", 1,
                '["https://twitter.com/gov_is"]', '[]', '[]', '[]',
                '[]', '[]',
                "twitter_only", "2024-06-02T10:00:00+00:00",
            ),
            (
                "https://example.is/page2", "ICELAND",
                "social-ICELAND-scan-001", 0,
                '[]', '[]', '[]', '[]',
                '[]', '[]',
                "unreachable", "2024-06-01T10:01:00+00:00",
            ),
        ]
        for row in rows:
            conn.execute(
                """
                INSERT INTO url_social_media_results
                (url, country_code, scan_id, is_reachable,
                 twitter_links, x_links, bluesky_links, mastodon_links,
                 facebook_links, linkedin_links,
                 social_tier, scanned_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                row,
            )
        conn.commit()
    finally:
        conn.close()
    return db_path


def test_query_summary_no_double_counting(duplicate_scan_db: Path):
    """URL that appears in multiple scan batches should be counted only once."""
    conn = sqlite3.connect(duplicate_scan_db)
    conn.row_factory = sqlite3.Row
    try:
        result = _query_summary(conn)
    finally:
        conn.close()

    assert result["total_batches"] == 2     # 2 distinct scan_ids
    assert result["total_scanned"] == 2     # only 2 distinct URLs
    assert result["total_reachable"] == 1   # page1 is reachable (counted once)
    assert result["twitter_pages"] == 1     # page1 has twitter (counted once)


def test_query_by_country_no_double_counting(duplicate_scan_db: Path):
    """Per-country query must not inflate counts for multi-batch URLs."""
    conn = sqlite3.connect(duplicate_scan_db)
    conn.row_factory = sqlite3.Row
    try:
        rows = _query_by_country(conn)
    finally:
        conn.close()

    assert len(rows) == 1
    iceland = rows[0]
    assert iceland["total_scanned"] == 2   # 2 distinct URLs
    assert iceland["reachable"] == 1       # only page1 is reachable
    assert iceland["twitter_pages"] == 1   # only page1 has twitter


def test_build_stats_block_with_total_available():
    """Stats block should include coverage line when total_available > 0."""
    summary = {
        "total_batches": 5,
        "total_scanned": 100,
        "total_reachable": 80,
        "twitter_pages": 20,
        "x_pages": 10,
        "bluesky_pages": 5,
        "mastodon_pages": 15,
        "facebook_pages": 30,
        "linkedin_pages": 8,
        "last_scan": "2024-06-01T12:00:00",
    }
    block = _build_stats_block(summary, "2024-06-01 12:00 UTC", total_available=1000)
    assert "100" in block                          # scanned
    assert "1,000" in block                        # available
    assert "10.0%" in block                        # 100/1000 coverage


def test_generate_social_media_report_json_includes_total_available(
    populated_db: Path, tmp_path: Path
):
    """JSON data file should include total_available when seeds_dir is provided."""
    # Create a minimal toon seed directory with one file
    seeds_dir = tmp_path / "seeds"
    seeds_dir.mkdir()
    seed_data = {"version": "0.1-seed", "country": "Iceland", "page_count": 50, "domains": []}
    (seeds_dir / "iceland.toon").write_text(json.dumps(seed_data), encoding="utf-8")

    page_path = tmp_path / "social-media.md"
    page_path.write_text(_SOCIAL_MEDIA_PAGE_TEMPLATE)
    data_path = tmp_path / "social-media-data.json"

    generate_social_media_report(populated_db, page_path, data_path, seeds_dir)

    data = json.loads(data_path.read_text())
    assert data["summary"]["total_available"] == 50


# ---------------------------------------------------------------------------
# Tests for _count_toon_seed_urls
# ---------------------------------------------------------------------------

def test_count_toon_seed_urls_missing_dir(tmp_path: Path):
    """Should return empty dict when the directory does not exist."""
    from src.cli.generate_social_media_report import _count_toon_seed_urls
    result = _count_toon_seed_urls(tmp_path / "nonexistent")
    assert result == {}


def test_count_toon_seed_urls_empty_dir(tmp_path: Path):
    """Should return empty dict when the directory contains no .toon files."""
    from src.cli.generate_social_media_report import _count_toon_seed_urls
    seeds_dir = tmp_path / "seeds"
    seeds_dir.mkdir()
    result = _count_toon_seed_urls(seeds_dir)
    assert result == {}


def test_count_toon_seed_urls_reads_page_count(tmp_path: Path):
    """Should correctly read page_count from toon seed files."""
    from src.cli.generate_social_media_report import _count_toon_seed_urls
    seeds_dir = tmp_path / "seeds"
    seeds_dir.mkdir()
    for name, count in [("iceland", 139), ("norway", 239)]:
        data = {"page_count": count, "domains": []}
        (seeds_dir / f"{name}.toon").write_text(json.dumps(data), encoding="utf-8")
    result = _count_toon_seed_urls(seeds_dir)
    assert result == {"ICELAND": 139, "NORWAY": 239}


# ---------------------------------------------------------------------------
# Tests for new platform columns (Facebook, LinkedIn) and column ordering
# ---------------------------------------------------------------------------

def test_build_stats_block_includes_facebook_linkedin():
    """Platform overview table must include Facebook and LinkedIn rows."""
    summary = {
        "total_batches": 3,
        "total_scanned": 200,
        "total_reachable": 180,
        "twitter_pages": 10,
        "x_pages": 5,
        "bluesky_pages": 8,
        "mastodon_pages": 12,
        "facebook_pages": 25,
        "linkedin_pages": 15,
        "last_scan": "2024-06-01T12:00:00",
    }
    block = _build_stats_block(summary, "2024-06-01 12:00 UTC")
    assert "Facebook" in block
    assert "LinkedIn" in block
    assert "Legacy social media" in block
    assert "Modern" in block or "modern" in block


def test_build_stats_block_country_table_column_order(populated_db: Path):
    """Country table must place No Social and Legacy-only before platform columns."""
    conn = sqlite3.connect(populated_db)
    conn.row_factory = sqlite3.Row
    try:
        summary = _query_summary(conn)
        by_country = _query_by_country(conn)
    finally:
        conn.close()

    block = _build_stats_block(summary, "2024-06-01 12:00 UTC", by_country=by_country)

    # Find the header row of the country table
    header_line = None
    for line in block.splitlines():
        if "No Social" in line and "Legacy-only" in line and "Scan Period" in line:
            header_line = line
            break

    assert header_line is not None, "Country table header not found"
    # No Social must come before Legacy-only, which must come before Twitter column
    ns_pos = header_line.index("No Social")
    lo_pos = header_line.index("Legacy-only")
    # Find " Twitter |" to avoid matching "Legacy-only" or "Twitter-only"
    tw_pos = header_line.index("| Twitter |")
    assert ns_pos < lo_pos < tw_pos, (
        f"Column order wrong: No Social={ns_pos}, Legacy-only={lo_pos}, Twitter={tw_pos}"
    )


def test_build_stats_block_sortable_table_uses_scan_period_identifier(populated_db: Path):
    """JS _findCountryTable should look for 'Scan Period', not 'Non-X Score'."""
    conn = sqlite3.connect(populated_db)
    conn.row_factory = sqlite3.Row
    try:
        summary = _query_summary(conn)
        by_country = _query_by_country(conn)
    finally:
        conn.close()

    block = _build_stats_block(summary, "2024-06-01 12:00 UTC", by_country=by_country)

    # The JS should use "Scan Period" as the identifier, NOT "Non-X Score"
    assert '"Scan Period"' in block
    assert '"Non-X Score"' not in block


def test_build_stats_block_available_reachable_clarification(populated_db: Path):
    """Stats block must explain Available and Reachable in the country table section."""
    conn = sqlite3.connect(populated_db)
    conn.row_factory = sqlite3.Row
    try:
        summary = _query_summary(conn)
        by_country = _query_by_country(conn)
    finally:
        conn.close()

    block = _build_stats_block(summary, "2024-06-01 12:00 UTC", by_country=by_country)

    assert "Available" in block
    assert "Reachable" in block
    # The introductory sentence should explain both terms
    assert "valid HTTP response" in block or "tracked in our domain list" in block


def test_generate_social_media_report_json_includes_facebook_linkedin(
    populated_db: Path, tmp_path: Path
):
    """JSON data file should include facebook_pages and linkedin_pages."""
    page_path = tmp_path / "social-media.md"
    page_path.write_text(_SOCIAL_MEDIA_PAGE_TEMPLATE)
    data_path = tmp_path / "social-media-data.json"

    generate_social_media_report(populated_db, page_path, data_path)

    data = json.loads(data_path.read_text())
    assert "facebook_pages" in data["summary"]
    assert "linkedin_pages" in data["summary"]
    assert data["summary"]["facebook_pages"] == 1   # one France page has Facebook
    assert data["summary"]["linkedin_pages"] == 0

