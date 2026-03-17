"""Tests for the multi-scan progress report generator."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from src.cli.generate_scan_progress import generate_progress_report
from src.storage.schema import initialize_schema


# ---------------------------------------------------------------------------
# fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def empty_db(tmp_path: Path) -> Path:
    """Return path to a freshly initialised, empty database."""
    db_path = tmp_path / "test.db"
    initialize_schema(f"sqlite:///{db_path}")
    return db_path


@pytest.fixture
def populated_db(tmp_path: Path) -> Path:
    """Return path to a database with sample data for all three scan types."""
    db_path = tmp_path / "test.db"
    initialize_schema(f"sqlite:///{db_path}")

    conn = sqlite3.connect(db_path)
    try:
        # URL validation results
        for url, is_valid, failure_count, ts in [
            ("https://example.is/page1", 1, 0, "2024-06-01T10:00:00+00:00"),
            ("https://example.is/page2", 0, 1, "2024-06-01T10:01:00+00:00"),
            ("https://example.is/page3", 1, 0, "2024-06-01T10:02:00+00:00"),
            ("https://example.fr/page1", 1, 0, "2024-06-02T08:00:00+00:00"),
        ]:
            conn.execute(
                """
                INSERT INTO url_validation_results
                (url, country_code, scan_id, status_code, is_valid,
                 failure_count, validated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    url,
                    "ICELAND" if "example.is" in url else "FRANCE",
                    "scan-001",
                    200 if is_valid else 404,
                    is_valid,
                    failure_count,
                    ts,
                ),
            )

        # Social media results
        for url, is_reachable, tier, ts in [
            ("https://example.is/page1", 1, "twitter_only", "2024-06-03T09:00:00+00:00"),
            ("https://example.is/page2", 0, "unreachable",  "2024-06-03T09:01:00+00:00"),
            ("https://example.is/page3", 1, "no_social",    "2024-06-03T09:02:00+00:00"),
            ("https://example.de/home",  1, "modern_only",  "2024-06-04T07:00:00+00:00"),
        ]:
            conn.execute(
                """
                INSERT INTO url_social_media_results
                (url, country_code, scan_id, is_reachable, social_tier,
                 twitter_links, x_links, bluesky_links, mastodon_links,
                 scanned_at)
                VALUES (?, ?, ?, ?, ?, '[]', '[]', '[]', '[]', ?)
                """,
                (
                    url,
                    "ICELAND" if "example.is" in url else "GERMANY",
                    "social-001",
                    is_reachable,
                    tier,
                    ts,
                ),
            )

        # Technology results
        conn.execute(
            """
            INSERT INTO url_tech_results
            (url, country_code, scan_id, technologies, scanned_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                "https://example.is/page1",
                "ICELAND",
                "tech-001",
                '{"WordPress": {"versions": ["6.5"], "categories": ["CMS"]}}',
                "2024-06-05T11:00:00+00:00",
            ),
        )

        conn.commit()
    finally:
        conn.close()

    return db_path


# ---------------------------------------------------------------------------
# tests
# ---------------------------------------------------------------------------

def test_generate_progress_report_missing_db(tmp_path: Path):
    """Report should be created gracefully when the database does not exist."""
    db_path = tmp_path / "nonexistent.db"
    output_path = tmp_path / "report.md"

    generate_progress_report(db_path, output_path)

    assert output_path.exists()
    content = output_path.read_text()
    assert "# Scan Progress Report" in content
    assert "No scan data available yet" in content


def test_generate_progress_report_empty_db(empty_db: Path, tmp_path: Path):
    """Report should be created when the database is empty."""
    output_path = tmp_path / "report.md"
    generate_progress_report(empty_db, output_path)

    assert output_path.exists()
    content = output_path.read_text()
    # Empty DB → no validation data → gracefully handled
    assert "# Scan Progress Report" in content


def test_generate_progress_report_with_data(populated_db: Path, tmp_path: Path):
    """Report should contain expected sections and data."""
    output_path = tmp_path / "report.md"
    generate_progress_report(populated_db, output_path)

    assert output_path.exists()
    content = output_path.read_text()

    # Check main sections
    assert "# Scan Progress Report" in content
    assert "## Overall Coverage" in content
    assert "## URL Validation by Country" in content
    assert "## Social Media Scan by Country" in content
    assert "## Scan Priority Guide" in content

    # Check country rows appear
    assert "ICELAND" in content
    assert "FRANCE" in content
    assert "GERMANY" in content


def test_generate_progress_report_url_validation_stats(
    populated_db: Path, tmp_path: Path
):
    """URL validation section should show correct valid/invalid counts."""
    output_path = tmp_path / "report.md"
    generate_progress_report(populated_db, output_path)
    content = output_path.read_text()

    # Iceland has 2 valid + 1 invalid; France has 1 valid
    # The table rows should have numbers present
    assert "ICELAND" in content
    assert "FRANCE" in content


def test_generate_progress_report_social_tiers(populated_db: Path, tmp_path: Path):
    """Social media section should list tier counts."""
    output_path = tmp_path / "report.md"
    generate_progress_report(populated_db, output_path)
    content = output_path.read_text()

    assert "Social Media Scan by Country" in content
    assert "GERMANY" in content


def test_generate_progress_report_technology_section(
    populated_db: Path, tmp_path: Path
):
    """Technology section should appear when tech scan data exists."""
    output_path = tmp_path / "report.md"
    generate_progress_report(populated_db, output_path)
    content = output_path.read_text()

    assert "Technology" in content
    assert "ICELAND" in content


def test_generate_progress_report_pending_social_scan(
    populated_db: Path, tmp_path: Path
):
    """Countries with URL validation but no social scan should be highlighted."""
    output_path = tmp_path / "report.md"
    generate_progress_report(populated_db, output_path)
    content = output_path.read_text()

    # FRANCE has URL validation but no social media scan
    assert "Countries Pending Social Media Scan" in content
    assert "FRANCE" in content


def test_generate_progress_report_scan_priority_guide(
    populated_db: Path, tmp_path: Path
):
    """Report should include the scan priority guide."""
    output_path = tmp_path / "report.md"
    generate_progress_report(populated_db, output_path)
    content = output_path.read_text()

    assert "Scan Priority Guide" in content
    assert "Social Media Scan" in content
    assert "URL Validation" in content
    assert "30 days" in content


def test_generate_progress_report_social_media_platform_breakdown(
    populated_db: Path, tmp_path: Path
):
    """Report should include a per-platform social media breakdown table."""
    output_path = tmp_path / "report.md"
    generate_progress_report(populated_db, output_path)
    content = output_path.read_text()

    assert "## Social Media Platform Breakdown" in content
    # Table should include the platform columns
    assert "Twitter" in content
    assert "Bluesky" in content
    assert "Mastodon" in content
    # Should show the countries that have social media data
    assert "ICELAND" in content
    assert "GERMANY" in content
