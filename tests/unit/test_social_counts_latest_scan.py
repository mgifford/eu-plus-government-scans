"""Tests that social figures describe each page's latest successful scan.

Counting every scan a page ever had meant an agency that removed its Twitter
link stayed counted as a Twitter page forever, hiding exactly the change the
reports exist to show.  Only successful scans count, so an outage or an error
page never looks like a page dropping its links.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

import pytest

from src.cli.generate_scan_progress import _query_social_media
from src.cli.generate_social_media_report import (
    _query_by_country,
    _query_metric_drilldowns_by_country,
    _query_platform_drilldowns_by_country,
    _query_summary,
)
from src.services.social_media_scanner import SocialMediaScanner
from src.storage.schema import initialize_schema

_TWITTER = ["https://twitter.com/agency"]


def _insert(
    conn: sqlite3.Connection,
    url: str,
    scan_id: str,
    scanned_at: str,
    tier: str,
    twitter: list[str] | None = None,
    reachable: bool = True,
    error: str | None = None,
) -> None:
    """Insert one scan row for an Iceland page."""
    conn.execute(
        """
        INSERT INTO url_social_media_results
        (url, country_code, scan_id, is_reachable, twitter_links,
         social_tier, error_message, scanned_at, platforms_version)
        VALUES (?, 'ICELAND', ?, ?, ?, ?, ?, ?, 3)
        """,
        (url, scan_id, int(reachable), json.dumps(twitter or []), tier, error, scanned_at),
    )


@pytest.fixture
def history_db(tmp_path: Path) -> Path:
    """Pages whose scans changed over time."""
    db_path = tmp_path / "metadata.db"
    initialize_schema(f"sqlite:///{db_path}")
    conn = sqlite3.connect(db_path)
    try:
        # Dropped Twitter in its newer scan.
        _insert(conn, "https://a.is/", "s1", "2026-10-01T00:00:00", "twitter_only", _TWITTER)
        _insert(conn, "https://a.is/", "s2", "2026-11-01T00:00:00", "no_social")
        # Still has Twitter; the newer fetch failed, which is not evidence.
        _insert(conn, "https://b.is/", "s1", "2026-10-01T00:00:00", "twitter_only", _TWITTER)
        _insert(
            conn, "https://b.is/", "s2", "2026-11-01T00:00:00", "unreachable",
            reachable=False, error="Timeout: read timed out",
        )
        # Newer scan reached the page but could not parse it.
        _insert(conn, "https://c.is/", "s1", "2026-10-01T00:00:00", "twitter_only", _TWITTER)
        _insert(
            conn, "https://c.is/", "s2", "2026-11-01T00:00:00", "no_social",
            error="Parse error: bad markup",
        )
        # Never reached at all.
        _insert(
            conn, "https://d.is/", "s1", "2026-10-01T00:00:00", "unreachable",
            reachable=False, error="Connection error: refused",
        )
        conn.commit()
    finally:
        conn.close()
    return db_path


def _connect(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def test_summary_counts_latest_successful_scan(history_db: Path):
    """A removed link stops counting; failed or unparsed scans change nothing."""
    with _connect(history_db) as conn:
        summary = _query_summary(conn)
    assert summary["total_scanned"] == 4
    assert summary["total_reachable"] == 3
    assert summary["twitter_pages"] == 2  # b and c, not a
    assert summary["total_batches"] == 2
    assert summary["first_scan"] == "2026-10-01T00:00:00"
    assert summary["last_scan"] == "2026-11-01T00:00:00"


def test_by_country_tiers_use_latest_successful_scan(history_db: Path):
    """Each reachable page lands in exactly one tier, from its latest good scan."""
    with _connect(history_db) as conn:
        (iceland,) = _query_by_country(conn)
    assert iceland["total_scanned"] == 4
    assert iceland["reachable"] == 3
    assert iceland["no_social"] == 1
    assert iceland["twitter_only"] == 2
    assert iceland["twitter_pages"] == 2
    assert iceland["has_any_legacy"] == 2
    tiers = ("no_social", "twitter_only", "modern_only", "mixed")
    assert sum(iceland[t] for t in tiers) == iceland["reachable"]


def test_country_with_no_successful_scan_reports_zeros(tmp_path: Path):
    """A country whose pages were never reached still appears, with zeros."""
    db_path = tmp_path / "metadata.db"
    initialize_schema(f"sqlite:///{db_path}")
    with _connect(db_path) as conn:
        _insert(
            conn, "https://d.is/", "s1", "2026-10-01T00:00:00", "unreachable",
            reachable=False, error="Timeout",
        )
        (iceland,) = _query_by_country(conn)
    assert iceland["total_scanned"] == 1
    assert iceland["reachable"] == 0
    assert iceland["twitter_pages"] == 0


def test_ties_on_scanned_at_pick_one_row_stably(tmp_path: Path):
    """Two scans with the same timestamp count once, by the later scan_id."""
    db_path = tmp_path / "metadata.db"
    initialize_schema(f"sqlite:///{db_path}")
    with _connect(db_path) as conn:
        _insert(conn, "https://a.is/", "s1", "2026-11-01T00:00:00", "twitter_only", _TWITTER)
        _insert(conn, "https://a.is/", "s2", "2026-11-01T00:00:00", "no_social")
        summary = _query_summary(conn)
        (iceland,) = _query_by_country(conn)
    assert summary["total_reachable"] == 1
    assert summary["twitter_pages"] == 0
    assert iceland["no_social"] == 1


def test_platform_drilldowns_list_only_current_links(history_db: Path):
    """The Twitter drilldown matches the Twitter count."""
    with _connect(history_db) as conn:
        drilldowns = _query_platform_drilldowns_by_country(conn)
    pages = [item["page_url"] for item in drilldowns["ICELAND"]["twitter"]]
    assert pages == ["https://b.is/", "https://c.is/"]


def test_metric_drilldowns_match_counts(history_db: Path):
    """Scanned lists every page; reachable and tiers use latest good scans."""
    with _connect(history_db) as conn:
        drilldowns = _query_metric_drilldowns_by_country(conn)["ICELAND"]
    assert [r["page_url"] for r in drilldowns["scanned"]] == [
        "https://a.is/", "https://b.is/", "https://c.is/", "https://d.is/",
    ]
    assert [r["page_url"] for r in drilldowns["reachable"]] == [
        "https://a.is/", "https://b.is/", "https://c.is/",
    ]
    assert [r["page_url"] for r in drilldowns["no_social"]] == ["https://a.is/"]
    assert [r["page_url"] for r in drilldowns["legacy_only"]] == [
        "https://b.is/", "https://c.is/",
    ]
    # The scanned record shows the most recent attempt, even a failed one.
    scanned_b = next(r for r in drilldowns["scanned"] if r["page_url"] == "https://b.is/")
    assert scanned_b["is_reachable"] is False


def test_progress_page_uses_the_same_rule(history_db: Path):
    """The progress page agrees with the social media page."""
    with _connect(history_db) as conn:
        iceland = _query_social_media(conn)["ICELAND"]
    assert iceland["total"] == 4
    assert iceland["reachable"] == 3
    assert iceland["has_twitter"] == 2
    assert iceland["twitter_only"] == 2
    assert iceland["no_social"] == 1
    assert iceland["unreachable"] == 1
    tiers = ("twitter_only", "modern_only", "mixed", "no_social", "unreachable")
    assert sum(iceland[t] for t in tiers) == iceland["total"]


@pytest.mark.asyncio
@pytest.mark.parametrize("status", [404, 500, 503])
async def test_scan_url_treats_error_status_as_unreachable(status: int):
    """An error page must not be recorded as a reachable page with no links."""
    response = Mock()
    response.status_code = status
    response.text = '<a href="https://twitter.com/notfound">x</a>'
    with patch("httpx.AsyncClient") as client:
        client.return_value.__aenter__.return_value.get = AsyncMock(return_value=response)
        result = await SocialMediaScanner(timeout_seconds=5).scan_url("https://a.is/")
    assert result.is_reachable is False
    assert result.error_message == f"HTTP {status}"
    assert result.social_tier == "unreachable"
    assert result.twitter_links == []
