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
            # url, country, scan_id, is_reachable, twitter, x, bluesky, mastodon, tier
            (
                "https://example.is/page1",
                "ICELAND",
                "social-ICELAND-20240601-001",
                1, '["https://twitter.com/gov_is"]', '[]', '[]', '[]',
                "twitter_only", "2024-06-01T10:00:00+00:00",
            ),
            (
                "https://example.is/page2",
                "ICELAND",
                "social-ICELAND-20240601-001",
                0, '[]', '[]', '[]', '[]',
                "unreachable", "2024-06-01T10:01:00+00:00",
            ),
            (
                "https://example.is/page3",
                "ICELAND",
                "social-ICELAND-20240601-001",
                1, '[]', '[]',
                '["https://bsky.app/profile/gov.is"]',
                '["https://mastodon.social/@gov_is"]',
                "modern_only", "2024-06-01T10:02:00+00:00",
            ),
            (
                "https://example.fr/page1",
                "FRANCE",
                "social-FRANCE-20240602-001",
                1, '[]', '["https://x.com/france_gov"]',
                '[]', '[]',
                "twitter_only", "2024-06-02T08:00:00+00:00",
            ),
            (
                "https://example.fr/page2",
                "FRANCE",
                "social-FRANCE-20240602-001",
                1, '[]', '[]', '[]', '[]',
                "no_social", "2024-06-02T08:01:00+00:00",
            ),
        ]
        for row in rows:
            conn.execute(
                """
                INSERT INTO url_social_media_results
                (url, country_code, scan_id, is_reachable,
                 twitter_links, x_links, bluesky_links, mastodon_links,
                 social_tier, scanned_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                "twitter_pages", "x_pages", "bluesky_pages", "mastodon_pages"):
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
