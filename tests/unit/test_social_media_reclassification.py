"""Tests for platforms version 3: schema migration and stored-row reclassification.

Before version 3 the ``/@name`` Mastodon heuristic matched TikTok and YouTube
profiles.  Those links sit in ``mastodon_links`` of older rows, and the report
counts a page under every platform any of its scans found, so the stored rows
must be corrected rather than left to age out.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pytest

from src.cli.generate_social_media_report import (
    _build_stats_block,
    _query_by_country,
    _query_summary,
)
from src.jobs.social_media_scanner import reclassify_stored_links
from src.services.social_media_scanner import SOCIAL_PLATFORMS_VERSION
from src.storage.schema import initialize_schema

_NEW_COLUMNS = ("tiktok_links", "youtube_links", "blacksky_links", "gander_links")


def _insert(
    conn: sqlite3.Connection,
    url: str,
    mastodon: list[str],
    tier: str,
    version: int,
    scan_id: str = "social-ICELAND-20261001-001",
) -> None:
    """Insert one social media result row with only Mastodon links set."""
    conn.execute(
        """
        INSERT INTO url_social_media_results
        (url, country_code, scan_id, is_reachable, mastodon_links,
         social_tier, scanned_at, platforms_version)
        VALUES (?, 'ICELAND', ?, 1, ?, ?, '2026-10-01T10:00:00+00:00', ?)
        """,
        (url, scan_id, json.dumps(mastodon), tier, version),
    )


def _row(db_path: Path, url: str) -> sqlite3.Row:
    """Fetch the single stored row for *url*."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        return conn.execute(
            "SELECT * FROM url_social_media_results WHERE url = ?", (url,)
        ).fetchone()
    finally:
        conn.close()


@pytest.fixture
def v2_db(tmp_path: Path) -> Path:
    """Database holding rows written by the version 2 scanner."""
    db_path = tmp_path / "metadata.db"
    initialize_schema(f"sqlite:///{db_path}")
    conn = sqlite3.connect(db_path)
    try:
        _insert(
            conn,
            "https://example.is/mixed",
            [
                "https://social.example.is/@agency",
                "@agency@mastodon.social",
                "https://www.youtube.com/@agency",
                "https://www.threads.net/@agency",
            ],
            "modern_only",
            2,
        )
        _insert(
            conn,
            "https://example.is/youtube-only",
            ["https://www.youtube.com/@agency"],
            "modern_only",
            2,
        )
        _insert(
            conn,
            "https://example.is/real-mastodon",
            ["https://social.example.is/@agency"],
            "modern_only",
            2,
        )
        conn.commit()
    finally:
        conn.close()
    return db_path


def test_initialize_schema_adds_new_columns_to_old_table(tmp_path: Path):
    """A database created before version 3 gains the new link columns."""
    db_path = tmp_path / "old.db"
    conn = sqlite3.connect(db_path)
    conn.execute(
        """
        CREATE TABLE url_social_media_results (
            url TEXT NOT NULL, country_code TEXT NOT NULL, scan_id TEXT NOT NULL,
            is_reachable INTEGER NOT NULL DEFAULT 1,
            twitter_links TEXT NOT NULL DEFAULT '[]',
            x_links TEXT NOT NULL DEFAULT '[]',
            bluesky_links TEXT NOT NULL DEFAULT '[]',
            mastodon_links TEXT NOT NULL DEFAULT '[]',
            social_tier TEXT NOT NULL DEFAULT 'no_social',
            error_message TEXT, scanned_at TEXT,
            PRIMARY KEY (url, scan_id)
        )
        """
    )
    conn.commit()
    conn.close()

    initialize_schema(f"sqlite:///{db_path}")

    conn = sqlite3.connect(db_path)
    try:
        columns = {
            row[1]
            for row in conn.execute("PRAGMA table_info(url_social_media_results)")
        }
    finally:
        conn.close()
    assert set(_NEW_COLUMNS) <= columns


def test_reclassify_moves_corporate_links_and_recomputes_tier(v2_db: Path):
    """YouTube moves out of Mastodon, Threads is dropped, the tier is recomputed."""
    assert reclassify_stored_links(v2_db) == 2

    mixed = _row(v2_db, "https://example.is/mixed")
    assert json.loads(mixed["mastodon_links"]) == [
        "https://social.example.is/@agency",
        "@agency@mastodon.social",
    ]
    assert json.loads(mixed["youtube_links"]) == ["https://www.youtube.com/@agency"]
    assert mixed["social_tier"] == "mixed"

    youtube_only = _row(v2_db, "https://example.is/youtube-only")
    assert json.loads(youtube_only["mastodon_links"]) == []
    assert youtube_only["social_tier"] == "twitter_only"


def test_reclassify_leaves_genuine_mastodon_rows_alone(v2_db: Path):
    """A row whose Mastodon links are all genuine is not rewritten."""
    reclassify_stored_links(v2_db)
    row = _row(v2_db, "https://example.is/real-mastodon")
    assert json.loads(row["mastodon_links"]) == ["https://social.example.is/@agency"]
    assert row["social_tier"] == "modern_only"


def test_reclassify_keeps_platforms_version_so_pages_are_rescanned(v2_db: Path):
    """Old rows keep their version: a v2 scan never stored most YouTube links."""
    reclassify_stored_links(v2_db)
    assert _row(v2_db, "https://example.is/mixed")["platforms_version"] == 2


def test_reclassify_is_idempotent(v2_db: Path):
    """A second run finds nothing left to move."""
    reclassify_stored_links(v2_db)
    assert reclassify_stored_links(v2_db) == 0


def test_reclassify_skips_current_version_rows(tmp_path: Path):
    """Rows written by the current scanner are never touched."""
    db_path = tmp_path / "metadata.db"
    initialize_schema(f"sqlite:///{db_path}")
    conn = sqlite3.connect(db_path)
    try:
        # Not something the current scanner would write; proves the filter.
        _insert(
            conn,
            "https://example.is/current",
            ["https://www.youtube.com/@agency"],
            "modern_only",
            SOCIAL_PLATFORMS_VERSION,
        )
        conn.commit()
    finally:
        conn.close()

    assert reclassify_stored_links(db_path) == 0


def test_report_counts_reclassified_youtube_as_legacy(v2_db: Path):
    """After reclassification the report shows YouTube, not Mastodon, exposure."""
    reclassify_stored_links(v2_db)
    conn = sqlite3.connect(v2_db)
    conn.row_factory = sqlite3.Row
    try:
        summary = _query_summary(conn)
        by_country = _query_by_country(conn)
    finally:
        conn.close()

    assert summary["mastodon_pages"] == 2
    assert summary["youtube_pages"] == 2
    iceland = by_country[0]
    assert iceland["has_any_legacy"] == 2
    assert iceland["twitter_only"] == 1

    block = _build_stats_block(summary, "2026-11-08 12:00 UTC", by_country=by_country)
    header = next(line for line in block.splitlines() if "Scan Period" in line)
    for label in ("TikTok", "YouTube", "Blacksky", "Gander"):
        assert f"| {label} |" in header
