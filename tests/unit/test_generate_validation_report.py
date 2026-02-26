"""Tests for validation report generation."""

import sqlite3
from pathlib import Path

import pytest

from src.cli.generate_validation_report import generate_report
from src.storage.schema import initialize_schema


@pytest.fixture
def test_db(tmp_path):
    """Create a test database with sample data."""
    db_path = tmp_path / "test.db"
    initialize_schema(f"sqlite:///{db_path}")
    
    conn = sqlite3.connect(db_path)
    try:
        # Insert sample validation results
        conn.execute(
            """
            INSERT INTO url_validation_results
            (url, country_code, scan_id, status_code, error_message,
             redirected_to, redirect_chain, is_valid, failure_count, validated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "https://example.com/page1",
                "ICELAND",
                "ICELAND-20240101-000000000000-test1234",
                200,
                None,
                None,
                None,
                1,
                0,
                "2024-01-01T00:00:00+00:00",
            ),
        )
        
        conn.execute(
            """
            INSERT INTO url_validation_results
            (url, country_code, scan_id, status_code, error_message,
             redirected_to, redirect_chain, is_valid, failure_count, validated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "https://example.com/broken",
                "ICELAND",
                "ICELAND-20240101-000000000000-test1234",
                404,
                "Not Found",
                None,
                None,
                0,
                1,
                "2024-01-01T00:00:00+00:00",
            ),
        )
        
        conn.execute(
            """
            INSERT INTO url_validation_results
            (url, country_code, scan_id, status_code, error_message,
             redirected_to, redirect_chain, is_valid, failure_count, validated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "https://example.com/removed",
                "ICELAND",
                "ICELAND-20240101-000000000000-test1234",
                None,
                "Connection timeout",
                None,
                None,
                0,
                2,
                "2024-01-01T00:00:00+00:00",
            ),
        )
        
        conn.commit()
    finally:
        conn.close()
    
    return db_path


def test_generate_report_creates_file(test_db, tmp_path):
    """Test that report generation creates a markdown file."""
    output_path = tmp_path / "report.md"
    
    generate_report(test_db, output_path)
    
    assert output_path.exists()
    content = output_path.read_text()
    assert "# URL Validation Report" in content
    assert "ICELAND" in content


def test_generate_report_includes_statistics(test_db, tmp_path):
    """Test that report includes correct statistics."""
    output_path = tmp_path / "report.md"
    
    generate_report(test_db, output_path)
    
    content = output_path.read_text()
    # Should show: 3 total, 1 valid, 2 invalid
    assert "| ICELAND | 3 | 1 | 2 |" in content


def test_generate_report_shows_errors(test_db, tmp_path):
    """Test that report shows error details."""
    output_path = tmp_path / "report.md"
    
    generate_report(test_db, output_path)
    
    content = output_path.read_text()
    assert "https://example.com/broken" in content
    assert "https://example.com/removed" in content
    assert "⚠️ **REMOVED**" in content  # URL that failed twice


def test_generate_report_handles_empty_database(tmp_path):
    """Test that report handles empty database gracefully."""
    db_path = tmp_path / "empty.db"
    initialize_schema(f"sqlite:///{db_path}")
    
    output_path = tmp_path / "report.md"
    
    generate_report(db_path, output_path)
    
    assert output_path.exists()
    content = output_path.read_text()
    assert "No validation data available" in content


def test_generate_report_handles_missing_database(tmp_path):
    """Test that report handles missing database gracefully."""
    db_path = tmp_path / "nonexistent.db"
    output_path = tmp_path / "report.md"
    
    # Should not raise an exception
    generate_report(db_path, output_path)
