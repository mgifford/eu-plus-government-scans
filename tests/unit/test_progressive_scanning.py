"""Tests for progressive relationship scanning features.

Covers: eligibility, backoff, deterministic ordering, incremental merge,
fairness, and coverage reporting.
"""

from __future__ import annotations

import json
import sqlite3
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import MagicMock

from src.jobs.relationship_scanner_job import (
    RelationshipScannerJob,
    _backoff_days,
    _rel_key,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_edge(
    source_domain: str = "source.gov",
    target_domain: str = "target.com",
    target_hostname: str = "www.target.com",
    relationship_type: str = "editorial_link",
    target_category: str = "unknown_external",
    page_region: str = "body",
) -> MagicMock:
    """Create a mock RelationshipEdge."""
    edge = MagicMock()
    edge.source_domain = source_domain
    edge.target_domain = target_domain
    edge.target_hostname = target_hostname
    edge.relationship_type = relationship_type
    edge.target_category = target_category
    edge.page_region = page_region
    return edge


def _setup_db(db_path: Path) -> None:
    """Initialize the schema in a temp DB."""
    from src.storage.schema import initialize_schema

    initialize_schema(f"sqlite:///{db_path}")


def _insert_state(
    conn: sqlite3.Connection,
    url: str,
    country_code: str = "ICELAND",
    last_attempted: str | None = None,
    last_successful: str | None = None,
    status: str = "completed",
    failure_count: int = 0,
) -> None:
    """Insert a row into relationship_scan_state."""
    conn.execute(
        """
        INSERT OR REPLACE INTO relationship_scan_state
        (url, country_code, source_domain, last_attempted_at,
         last_successful_at, status, failure_count, scan_duration_ms, last_scan_id)
        VALUES (?, ?, '', ?, ?, ?, ?, 0, '')
        """,
        (url, country_code, last_attempted, last_successful, status, failure_count),
    )
    conn.commit()


# ---------------------------------------------------------------------------
# Unit tests: helpers
# ---------------------------------------------------------------------------

class TestBackoffDays:
    def test_zero_failures(self) -> None:
        assert _backoff_days(0) == 0

    def test_one_failure(self) -> None:
        assert _backoff_days(1) == 1

    def test_two_failures(self) -> None:
        assert _backoff_days(2) == 2

    def test_three_failures(self) -> None:
        assert _backoff_days(3) == 4

    def test_four_failures(self) -> None:
        assert _backoff_days(4) == 8

    def test_five_failures(self) -> None:
        assert _backoff_days(5) == 16

    def test_six_failures_capped(self) -> None:
        assert _backoff_days(6) == 28  # capped

    def test_large_failures_capped(self) -> None:
        assert _backoff_days(100) == 28


class TestRelKey:
    def test_deterministic(self) -> None:
        e1 = _make_edge("a.com", "b.com", "www.b.com", "editorial_link")
        e2 = _make_edge("a.com", "b.com", "www.b.com", "editorial_link")
        assert _rel_key(e1) == _rel_key(e2)

    def test_different_types(self) -> None:
        e1 = _make_edge("a.com", "b.com", "www.b.com", "editorial_link")
        e2 = _make_edge("a.com", "b.com", "www.b.com", "script")
        assert _rel_key(e1) != _rel_key(e2)

    def test_different_domains(self) -> None:
        e1 = _make_edge("a.com", "b.com", "www.b.com", "editorial_link")
        e2 = _make_edge("a.com", "c.com", "www.c.com", "editorial_link")
        assert _rel_key(e1) != _rel_key(e2)


# ---------------------------------------------------------------------------
# Eligibility tests
# ---------------------------------------------------------------------------

class TestEligibility:
    def test_never_scanned_gets_highest_priority(self) -> None:
        """URLs that were never scanned should be priority 0."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            _setup_db(db_path)

            from src.lib.settings import Settings

            settings = Settings()
            settings.metadata_db_url = f"sqlite:///{db_path}"
            job = RelationshipScannerJob(settings)

            urls = ["https://a.is/page1", "https://b.is/page2"]
            eligible = job._get_eligible_urls("ICELAND", urls)

            assert len(eligible) == 2
            assert all(e.priority == 0 for e in eligible)

    def test_recently_scanned_urls_are_skipped(self) -> None:
        """URLs scanned within skip_recently_scanned_days should be excluded."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            _setup_db(db_path)

            now = datetime.now(timezone.utc).isoformat()
            conn = sqlite3.connect(db_path)
            _insert_state(conn, "https://a.is/p1", "ICELAND", now, now, "completed", 0)
            _insert_state(conn, "https://b.is/p2", "ICELAND", now, now, "completed", 0)
            conn.close()

            from src.lib.settings import Settings

            settings = Settings()
            settings.metadata_db_url = f"sqlite:///{db_path}"
            job = RelationshipScannerJob(settings)

            urls = ["https://a.is/p1", "https://b.is/p2"]
            eligible = job._get_eligible_urls(
                "ICELAND", urls, skip_recently_scanned_days=28
            )
            assert len(eligible) == 0

    def test_failed_urls_get_priority_1(self) -> None:
        """Failed URLs should be prioritized after never-scanned."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            _setup_db(db_path)

            # Use old attempt time so backoff has expired (1 failure = 1 day backoff)
            old = (datetime.now(timezone.utc) - timedelta(days=5)).isoformat()
            now = datetime.now(timezone.utc).isoformat()
            conn = sqlite3.connect(db_path)
            _insert_state(
                conn, "https://a.is/p1", "ICELAND", old, None, "failed", 1
            )
            _insert_state(
                conn, "https://b.is/p2", "ICELAND", now, now, "completed", 0
            )
            conn.close()

            from src.lib.settings import Settings

            settings = Settings()
            settings.metadata_db_url = f"sqlite:///{db_path}"
            job = RelationshipScannerJob(settings)

            urls = ["https://a.is/p1", "https://b.is/p2"]
            eligible = job._get_eligible_urls(
                "ICELAND", urls, skip_recently_scanned_days=28
            )

            # a.is is failed (priority 1), b.is is recently scanned (skipped)
            assert len(eligible) == 1
            assert eligible[0].url == "https://a.is/p1"
            assert eligible[0].priority == 1

    def test_stale_successful_urls_get_priority_2(self) -> None:
        """Successful but old URLs should get priority 2."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            _setup_db(db_path)

            old_time = (
                datetime.now(timezone.utc) - timedelta(days=60)
            ).isoformat()
            conn = sqlite3.connect(db_path)
            _insert_state(
                conn, "https://a.is/p1", "ICELAND", old_time, old_time,
                "completed", 0,
            )
            conn.close()

            from src.lib.settings import Settings

            settings = Settings()
            settings.metadata_db_url = f"sqlite:///{db_path}"
            job = RelationshipScannerJob(settings)

            urls = ["https://a.is/p1"]
            eligible = job._get_eligible_urls(
                "ICELAND", urls, skip_recently_scanned_days=28
            )

            assert len(eligible) == 1
            assert eligible[0].priority == 2

    def test_backoff_respected(self) -> None:
        """Failed URLs in backoff window should be skipped."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            _setup_db(db_path)

            recent = datetime.now(timezone.utc).isoformat()
            conn = sqlite3.connect(db_path)
            # 2 failures = 2-day backoff, attempted recently
            _insert_state(
                conn, "https://a.is/p1", "ICELAND", recent, None, "failed", 2
            )
            conn.close()

            from src.lib.settings import Settings

            settings = Settings()
            settings.metadata_db_url = f"sqlite:///{db_path}"
            job = RelationshipScannerJob(settings)

            urls = ["https://a.is/p1"]
            eligible = job._get_eligible_urls(
                "ICELAND", urls, skip_recently_scanned_days=0
            )
            # Should be skipped due to backoff
            assert len(eligible) == 0

    def test_priority_ordering(self) -> None:
        """Never-scanned should come before failed, which comes before stale."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            _setup_db(db_path)

            old = (datetime.now(timezone.utc) - timedelta(days=60)).isoformat()
            conn = sqlite3.connect(db_path)
            _insert_state(conn, "https://a.is/stale", "ICELAND", old, old, "completed", 0)
            _insert_state(conn, "https://b.is/failed", "ICELAND", old, None, "failed", 1)
            conn.close()

            from src.lib.settings import Settings

            settings = Settings()
            settings.metadata_db_url = f"sqlite:///{db_path}"
            job = RelationshipScannerJob(settings)

            urls = ["https://a.is/stale", "https://b.is/failed", "https://c.is/new"]
            eligible = job._get_eligible_urls("ICELAND", urls)

            priorities = [e.priority for e in eligible]
            # c.is (never scanned) = 0, b.is (failed) = 1, a.is (stale) = 2
            assert priorities == sorted(priorities)
            assert eligible[0].url == "https://c.is/new"
            assert eligible[1].url == "https://b.is/failed"
            assert eligible[2].url == "https://a.is/stale"


# ---------------------------------------------------------------------------
# Deterministic ordering tests
# ---------------------------------------------------------------------------

class TestDeterministicOrdering:
    def test_urls_are_sorted(self) -> None:
        """scan_country should use sorted(set()) for deterministic ordering."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            _setup_db(db_path)

            from src.lib.settings import Settings

            settings = Settings()
            settings.metadata_db_url = f"sqlite:///{db_path}"
            job = RelationshipScannerJob(settings)

            # The _get_eligible_urls method should sort results
            urls = [
                "https://c.is/page",
                "https://a.is/page",
                "https://b.is/page",
                "https://a.is/page",  # duplicate
            ]
            eligible = job._get_eligible_urls("ICELAND", urls)

            eligible_urls = [e.url for e in eligible]
            assert eligible_urls == sorted(set(urls))


# ---------------------------------------------------------------------------
# Merge tests
# ---------------------------------------------------------------------------

class TestIncrementalMerge:
    def test_merge_new_relationships(self) -> None:
        """New edges should be added to the existing map."""
        from src.jobs.relationship_scanner_job import (
            AggregatedRelationship,
            RelationshipScannerJob,
        )

        existing: dict[tuple, AggregatedRelationship] = {}
        edge = _make_edge("source.gov", "target.com", "www.target.com", "editorial_link")

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            _setup_db(db_path)

            from src.lib.settings import Settings

            settings = Settings()
            settings.metadata_db_url = f"sqlite:///{db_path}"
            job = RelationshipScannerJob(settings)

            merged = job._merge_new_relationships(existing, [(edge, "https://source.gov")])
            assert len(merged) == 1
            key = _rel_key(edge)
            assert key in merged
            assert merged[key].observations == 1

    def test_merge_increments_observations(self) -> None:
        """Duplicate edges should increment observation count."""
        from src.jobs.relationship_scanner_job import (
            AggregatedRelationship,
            RelationshipScannerJob,
        )

        edge = _make_edge("source.gov", "target.com", "www.target.com", "editorial_link")
        key = _rel_key(edge)
        existing = {
            key: AggregatedRelationship(
                source_domain="source.gov",
                target_domain="target.com",
                target_hostname="www.target.com",
                relationship_type="editorial_link",
                target_category="unknown_external",
                source_pages={"https://other.gov"},
                observations=5,
                page_regions={"body"},
                first_seen="2024-01-01T00:00:00",
                last_seen="2024-06-01T00:00:00",
            )
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            _setup_db(db_path)

            from src.lib.settings import Settings

            settings = Settings()
            settings.metadata_db_url = f"sqlite:///{db_path}"
            job = RelationshipScannerJob(settings)

            merged = job._merge_new_relationships(
                existing, [(edge, "https://source.gov")]
            )
            assert len(merged) == 1
            assert merged[key].observations == 6
            assert "https://source.gov" in merged[key].source_pages
            assert "https://other.gov" in merged[key].source_pages

    def test_merge_preserves_existing_metadata(self) -> None:
        """Merge should preserve first_seen from existing data."""
        from src.jobs.relationship_scanner_job import (
            AggregatedRelationship,
            RelationshipScannerJob,
        )

        edge = _make_edge("source.gov", "target.com", "www.target.com", "editorial_link")
        key = _rel_key(edge)
        existing = {
            key: AggregatedRelationship(
                source_domain="source.gov",
                target_domain="target.com",
                target_hostname="www.target.com",
                relationship_type="editorial_link",
                target_category="unknown_external",
                source_pages=set(),
                observations=1,
                page_regions=set(),
                first_seen="2020-01-01T00:00:00",
                last_seen="2020-06-01T00:00:00",
            )
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            _setup_db(db_path)

            from src.lib.settings import Settings

            settings = Settings()
            settings.metadata_db_url = f"sqlite:///{db_path}"
            job = RelationshipScannerJob(settings)

            merged = job._merge_new_relationships(
                existing, [(edge, "https://source.gov")]
            )
            assert merged[key].first_seen == "2020-01-01T00:00:00"

    def test_merge_multiple_edges(self) -> None:
        """Multiple edges from the same URL should all be merged."""
        from src.jobs.relationship_scanner_job import RelationshipScannerJob

        e1 = _make_edge("src.gov", "a.com", "www.a.com", "editorial_link")
        e2 = _make_edge("src.gov", "b.com", "www.b.com", "script")
        e3 = _make_edge("src.gov", "a.com", "www.a.com", "script")

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            _setup_db(db_path)

            from src.lib.settings import Settings

            settings = Settings()
            settings.metadata_db_url = f"sqlite:///{db_path}"
            job = RelationshipScannerJob(settings)

            merged = job._merge_new_relationships(
                {},
                [(e1, "https://src.gov"), (e2, "https://src.gov"), (e3, "https://src.gov")],
            )
            # e1 and e3 both have src.gov->a.com but different types
            # So we get 3 unique edges
            assert len(merged) == 3


# ---------------------------------------------------------------------------
# JSONL write/read round-trip
# ---------------------------------------------------------------------------

class TestJsonlRoundTrip:
    def test_write_and_reload(self) -> None:
        """Written JSONL should be reloadable with correct data."""
        from src.jobs.relationship_scanner_job import (
            AggregatedRelationship,
            RelationshipScannerJob,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            _setup_db(db_path)
            jsonl_path = Path(tmpdir) / "test.jsonl"

            from src.lib.settings import Settings

            settings = Settings()
            settings.metadata_db_url = f"sqlite:///{db_path}"
            job = RelationshipScannerJob(settings)

            relationships = {
                ("src.gov", "tgt.com", "www.tgt.com", "editorial_link"):
                    AggregatedRelationship(
                        source_domain="src.gov",
                        target_domain="tgt.com",
                        target_hostname="www.tgt.com",
                        relationship_type="editorial_link",
                        target_category="unknown_external",
                        source_pages={"https://src.gov"},
                        observations=3,
                        page_regions={"body", "nav"},
                        first_seen="2024-01-01T00:00:00",
                        last_seen="2024-06-01T00:00:00",
                    ),
            }

            job._write_jsonl(relationships, jsonl_path)
            assert jsonl_path.exists()

            loaded = job._load_existing_relationships(jsonl_path)
            assert len(loaded) == 1
            key = ("src.gov", "tgt.com", "www.tgt.com", "editorial_link")
            assert loaded[key].observations == 3
            # source_pages is stored as count in JSONL; set is empty on reload
            assert loaded[key].source_pages == set()


# ---------------------------------------------------------------------------
# Fairness ordering
# ---------------------------------------------------------------------------

class TestFairnessOrdering:
    def test_build_balanced_country_order(self) -> None:
        """Countries should be interleaved by size."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            _setup_db(db_path)

            from src.lib.settings import Settings

            settings = Settings()
            settings.metadata_db_url = f"sqlite:///{db_path}"
            job = RelationshipScannerJob(settings)

            # Create fake TOON files with varying sizes
            toon_dir = Path(tmpdir) / "toons"
            toon_dir.mkdir()

            for name, page_count in [
                ("iceland.toon", 10),
                ("france.toon", 500),
                ("germany.toon", 1000),
                ("ireland.toon", 50),
                ("denmark.toon", 200),
            ]:
                toon_data = {
                    "domains": [
                        {"pages": [{"url": f"https://{name}/{i}"} for i in range(page_count)]}
                    ]
                }
                (toon_dir / name).write_text(json.dumps(toon_data))

            toon_files = sorted(toon_dir.glob("*.toon"))
            balanced = job._build_balanced_country_order(toon_files)

            # Should have all files
            assert len(balanced) == len(toon_files)

            # Small countries should not all be at the end
            names = [p.stem for p in balanced]
            # Iceland (small) should not be last
            assert names[-1] != "iceland"
