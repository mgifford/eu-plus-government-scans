"""Tests for the Lighthouse scan results report generator."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pytest

from src.cli.generate_lighthouse_report import (
    _build_stats_block,
    _query_by_country,
    _query_summary,
    generate_lighthouse_report,
)
from src.storage.schema import initialize_schema


_LIGHTHOUSE_PAGE_TEMPLATE = """\
---
title: Lighthouse Scan Results
layout: page
---

<!-- LIGHTHOUSE_STATS_START -->

_No scan data yet._

<!-- LIGHTHOUSE_STATS_END -->

## Overview

Some content.
"""


@pytest.fixture
def empty_db(tmp_path: Path) -> Path:
    """Return path to a freshly initialised empty database."""
    db_path = tmp_path / "test.db"
    initialize_schema(f"sqlite:///{db_path}")
    return db_path


@pytest.fixture
def populated_db(tmp_path: Path) -> Path:
    """Return a database with representative Lighthouse scan data."""
    db_path = tmp_path / "test.db"
    initialize_schema(f"sqlite:///{db_path}")

    conn = sqlite3.connect(db_path)
    try:
        rows = [
            # (url, country_code, scan_id, perf, a11y, bp, seo, error, scanned_at)
            (
                "https://example.is/page1",
                "ICELAND",
                "lh-ICELAND-001",
                0.9,
                0.8,
                1.0,
                0.95,
                None,
                None,
                "2026-03-01T10:00:00+00:00",
            ),
            (
                "https://example.is/page2",
                "ICELAND",
                "lh-ICELAND-001",
                0.7,
                0.6,
                0.8,
                0.85,
                None,
                None,
                "2026-03-01T10:05:00+00:00",
            ),
            (
                "https://example.is/page3",
                "ICELAND",
                "lh-ICELAND-001",
                None,
                None,
                None,
                None,
                None,
                "Lighthouse timed out after 120s",
                "2026-03-01T10:10:00+00:00",
            ),
            (
                "https://gov.example.fr/home",
                "FRANCE",
                "lh-FRANCE-001",
                0.5,
                0.75,
                0.9,
                0.6,
                None,
                None,
                "2026-03-02T09:00:00+00:00",
            ),
        ]
        for row in rows:
            conn.execute(
                """
                INSERT INTO url_lighthouse_results
                (url, country_code, scan_id,
                 performance_score, accessibility_score,
                 best_practices_score, seo_score, pwa_score,
                 error_message, scanned_at)
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

def test_query_summary_empty_db(empty_db: Path) -> None:
    """Should return zero/null values from an empty database."""
    conn = sqlite3.connect(empty_db)
    conn.row_factory = sqlite3.Row
    try:
        result = _query_summary(conn)
    finally:
        conn.close()

    assert result.get("total_batches", 0) == 0
    assert result.get("total_scanned", 0) == 0


def test_query_summary_populated_db(populated_db: Path) -> None:
    """Should aggregate stats correctly across countries."""
    conn = sqlite3.connect(populated_db)
    conn.row_factory = sqlite3.Row
    try:
        result = _query_summary(conn)
    finally:
        conn.close()

    assert result["total_batches"] == 2   # 2 distinct scan_ids
    assert result["total_scanned"] == 4   # 4 distinct URLs
    assert result["total_success"] == 3   # page3 has an error
    assert result["avg_accessibility"] is not None
    # avg of 0.8, 0.6, 0.75 = 0.717 (page3 excluded)
    assert abs(result["avg_accessibility"] - (0.8 + 0.6 + 0.75) / 3) < 0.01


# ---------------------------------------------------------------------------
# _query_by_country tests
# ---------------------------------------------------------------------------

def test_query_by_country_empty_db(empty_db: Path) -> None:
    """Should return empty list from an empty database."""
    conn = sqlite3.connect(empty_db)
    conn.row_factory = sqlite3.Row
    try:
        rows = _query_by_country(conn)
    finally:
        conn.close()

    assert rows == []


def test_query_by_country_groups_by_country(populated_db: Path) -> None:
    """Should return one row per country with correct aggregates."""
    conn = sqlite3.connect(populated_db)
    conn.row_factory = sqlite3.Row
    try:
        rows = _query_by_country(conn)
    finally:
        conn.close()

    assert len(rows) == 2
    country_map = {r["country_code"]: r for r in rows}

    iceland = country_map["ICELAND"]
    assert iceland["total_scanned"] == 3
    assert iceland["total_success"] == 2  # page3 is an error
    assert iceland["avg_accessibility"] is not None
    assert abs(iceland["avg_accessibility"] - (0.8 + 0.6) / 2) < 0.01

    france = country_map["FRANCE"]
    assert france["total_scanned"] == 1
    assert france["total_success"] == 1
    assert france["avg_accessibility"] == pytest.approx(0.75)


# ---------------------------------------------------------------------------
# _build_stats_block tests
# ---------------------------------------------------------------------------

def test_build_stats_block_empty_returns_placeholder() -> None:
    """Should return a no-data placeholder when summary is empty."""
    block = _build_stats_block({}, [], "2026-04-01 10:00 UTC")
    assert "No Lighthouse scan data yet" in block
    assert "<!-- LIGHTHOUSE_STATS_START -->" in block
    assert "<!-- LIGHTHOUSE_STATS_END -->" in block


def test_build_stats_block_populated_includes_scores(populated_db: Path) -> None:
    """Should include country names and score columns when data is present."""
    conn = sqlite3.connect(populated_db)
    conn.row_factory = sqlite3.Row
    try:
        summary = _query_summary(conn)
        by_country = _query_by_country(conn)
    finally:
        conn.close()

    block = _build_stats_block(summary, by_country, "2026-04-01 10:00 UTC")
    assert "<!-- LIGHTHOUSE_STATS_START -->" in block
    assert "<!-- LIGHTHOUSE_STATS_END -->" in block
    assert "Iceland" in block
    assert "France" in block
    assert "Perf" in block
    assert "A11y" in block
    assert "Best Practices" in block
    assert "SEO" in block
    assert "lighthouse-data.json" in block


def test_build_stats_block_includes_coverage_when_available(populated_db: Path) -> None:
    """Should include X of Y available pages when seed_counts are supplied."""
    conn = sqlite3.connect(populated_db)
    conn.row_factory = sqlite3.Row
    try:
        summary = _query_summary(conn)
        by_country = _query_by_country(conn)
    finally:
        conn.close()

    seed_counts = {"ICELAND": 100, "FRANCE": 500}
    block = _build_stats_block(
        summary, by_country, "2026-04-01", total_available=600, seed_counts=seed_counts
    )
    assert "600" in block


# ---------------------------------------------------------------------------
# generate_lighthouse_report integration tests
# ---------------------------------------------------------------------------

def test_generate_lighthouse_report_no_db(tmp_path: Path) -> None:
    """Should write a placeholder stats block when no database exists."""
    page_path = tmp_path / "lighthouse-results.md"
    page_path.write_text(_LIGHTHOUSE_PAGE_TEMPLATE, encoding="utf-8")
    data_path = tmp_path / "lighthouse-data.json"

    ok = generate_lighthouse_report(tmp_path / "nonexistent.db", page_path, data_path)

    assert ok
    content = page_path.read_text(encoding="utf-8")
    assert "No Lighthouse scan data yet" in content
    assert data_path.exists()
    data = json.loads(data_path.read_text())
    assert data["summary"]["total_scanned"] == 0


def test_generate_lighthouse_report_missing_markers(tmp_path: Path, empty_db: Path) -> None:
    """Should return False and leave the page unchanged when markers are absent."""
    page_path = tmp_path / "lighthouse-results.md"
    page_path.write_text("No markers here.\n", encoding="utf-8")
    data_path = tmp_path / "lighthouse-data.json"

    ok = generate_lighthouse_report(empty_db, page_path, data_path)

    assert not ok
    assert page_path.read_text() == "No markers here.\n"


def test_generate_lighthouse_report_writes_stats(tmp_path: Path, populated_db: Path) -> None:
    """Should replace the stats block with real data."""
    page_path = tmp_path / "lighthouse-results.md"
    page_path.write_text(_LIGHTHOUSE_PAGE_TEMPLATE, encoding="utf-8")
    data_path = tmp_path / "lighthouse-data.json"

    ok = generate_lighthouse_report(populated_db, page_path, data_path)

    assert ok
    content = page_path.read_text(encoding="utf-8")
    assert "Iceland" in content
    assert "France" in content
    assert "_No scan data yet._" not in content

    data = json.loads(data_path.read_text())
    assert data["summary"]["total_scanned"] == 4
    assert data["summary"]["total_success"] == 3
    assert len(data["by_country"]) == 2
