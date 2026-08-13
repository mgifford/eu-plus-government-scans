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
    _page_confirmed,
    _rel_key,
)
from src.services.multi_scanner import MultiScanResult
from src.services.relationship_scanner import RelationshipScanResult


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
            # The page set survives the round-trip, so the next cycle resumes
            # the tally rather than restarting it at zero.
            assert loaded[key].source_pages == {"https://src.gov"}


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


class TestSourcePagePersistence:
    """The published source-page count must survive progressive scan cycles.

    Regression tests for a defect that published ``source_pages: 0`` on every
    row of the dataset: ``to_dict`` wrote the set's length while the loader
    restored an empty set, so an edge's tally was discarded on every reload and
    only ever reflected pages seen in the run that happened to touch it.
    """

    @staticmethod
    def _job(tmpdir: str):
        """Build a scanner job backed by a throwaway database."""
        from src.lib.settings import Settings
        from src.jobs.relationship_scanner_job import RelationshipScannerJob

        db_path = Path(tmpdir) / "test.db"
        _setup_db(db_path)
        settings = Settings()
        settings.metadata_db_url = f"sqlite:///{db_path}"
        return RelationshipScannerJob(settings)

    def test_count_accumulates_across_cycles(self) -> None:
        """Each cycle's pages add to the tally instead of replacing it."""
        from src.jobs.relationship_scanner_job import _rel_key

        edge = _make_edge("source.gov", "target.com", "www.target.com", "editorial_link")
        key = _rel_key(edge)

        with tempfile.TemporaryDirectory() as tmpdir:
            job = self._job(tmpdir)
            shard_dir = Path(tmpdir) / "relationships"

            # Three cycles, each scanning a different page of the same domain.
            for page in ("https://source.gov/a", "https://source.gov/b", "https://source.gov/c"):
                existing = job._load_existing_relationships(shard_dir)
                merged = job._merge_new_relationships(existing, [(edge, page)])
                job._write_jsonl(merged, shard_dir)

            final = job._load_existing_relationships(shard_dir)
            assert final[key].source_pages == {
                "https://source.gov/a",
                "https://source.gov/b",
                "https://source.gov/c",
            }

    def test_published_count_is_not_zero(self) -> None:
        """The value actually written to disk reflects the pages seen."""
        import json

        from src.lib.relationship_shards import iter_rows

        edge = _make_edge("source.gov", "target.com", "www.target.com", "editorial_link")

        with tempfile.TemporaryDirectory() as tmpdir:
            job = self._job(tmpdir)
            shard_dir = Path(tmpdir) / "relationships"

            merged = job._merge_new_relationships(
                {}, [(edge, "https://source.gov/a"), (edge, "https://source.gov/b")]
            )
            job._write_jsonl(merged, shard_dir)

            # A second cycle that re-observes one page must not reset the count.
            existing = job._load_existing_relationships(shard_dir)
            merged = job._merge_new_relationships(existing, [(edge, "https://source.gov/a")])
            job._write_jsonl(merged, shard_dir)

            rows = list(iter_rows(shard_dir))
            assert len(rows) == 1
            assert rows[0]["source_pages"] == 2
            assert json.dumps(rows[0])  # row stays JSON-serialisable

    def test_count_matches_published_url_list(self) -> None:
        """The count is reproducible from the data published beside it."""
        from src.lib.relationship_shards import iter_rows

        edge = _make_edge("source.gov", "target.com", "www.target.com", "editorial_link")

        with tempfile.TemporaryDirectory() as tmpdir:
            job = self._job(tmpdir)
            shard_dir = Path(tmpdir) / "relationships"

            merged = job._merge_new_relationships(
                {}, [(edge, f"https://source.gov/{n}") for n in range(5)]
            )
            job._write_jsonl(merged, shard_dir)

            for row in iter_rows(shard_dir):
                assert row["source_pages"] == len(row["source_page_urls"])
                assert row["source_page_urls"] == sorted(row["source_page_urls"])

    def test_repeated_page_counted_once(self) -> None:
        """Re-scanning the same page does not inflate the distinct-page count."""
        from src.jobs.relationship_scanner_job import _rel_key

        edge = _make_edge("source.gov", "target.com", "www.target.com", "editorial_link")
        key = _rel_key(edge)

        with tempfile.TemporaryDirectory() as tmpdir:
            job = self._job(tmpdir)
            shard_dir = Path(tmpdir) / "relationships"

            for _ in range(4):
                existing = job._load_existing_relationships(shard_dir)
                merged = job._merge_new_relationships(
                    existing, [(edge, "https://source.gov/a")]
                )
                job._write_jsonl(merged, shard_dir)

            final = job._load_existing_relationships(shard_dir)
            assert len(final[key].source_pages) == 1
            # observations still counts every sighting, unlike the page set.
            assert final[key].observations == 4

    def test_legacy_row_without_url_list_is_tolerated(self) -> None:
        """A row predating source_page_urls loads without raising."""
        import json

        from src.jobs.relationship_scanner_job import _rel_key

        edge = _make_edge("source.gov", "target.com", "www.target.com", "editorial_link")
        key = _rel_key(edge)

        with tempfile.TemporaryDirectory() as tmpdir:
            job = self._job(tmpdir)
            shard_dir = Path(tmpdir) / "relationships"
            shard_dir.mkdir(parents=True)
            (shard_dir / "gov.001.jsonl").write_text(
                json.dumps(
                    {
                        "source_domain": "source.gov",
                        "target_domain": "target.com",
                        "target_hostname": "www.target.com",
                        "relationship_type": "editorial_link",
                        "target_category": "unknown_external",
                        "source_pages": 7,
                        "observations": 7,
                        "page_regions": ["body"],
                        "first_seen": "2026-01-01T00:00:00+00:00",
                        "last_seen": "2026-01-01T00:00:00+00:00",
                    }
                )
                + "\n",
                encoding="utf-8",
            )

            loaded = job._load_existing_relationships(shard_dir)
            assert loaded[key].source_pages == set()
            assert loaded[key].observations == 7


class TestPageConfirmation:
    """What counts as evidence that a page no longer serves a dependency.

    ``is_reachable`` only says a response arrived.  An error page or a WAF
    challenge parses as HTML with no scripts on it, so accepting either would
    retire every edge the page really serves and publish a migration that never
    happened -- the exact false result edge expiry exists to avoid.
    """

    @staticmethod
    def _result(status=200, sub_error=None, relationships=True):
        sub = None
        if relationships:
            sub = RelationshipScanResult(
                url="https://source.gov/a",
                is_reachable=True,
                relationships=[],
                error_message=sub_error,
            )
        return MultiScanResult(
            url="https://source.gov/a",
            is_reachable=status is not None,
            status_code=status,
            relationships=sub,
        )

    def test_ok_response_is_confirmed(self) -> None:
        assert _page_confirmed(self._result(status=200)) is True

    def test_204_is_confirmed(self) -> None:
        assert _page_confirmed(self._result(status=204)) is True

    def test_server_error_page_is_not_confirmed(self) -> None:
        """A 503 renders as HTML with no dependencies on it."""
        assert _page_confirmed(self._result(status=503)) is False

    def test_not_found_page_is_not_confirmed(self) -> None:
        assert _page_confirmed(self._result(status=404)) is False

    def test_waf_challenge_is_not_confirmed(self) -> None:
        """A 403 interstitial is a block, not a page that dropped its scripts."""
        assert _page_confirmed(self._result(status=403)) is False

    def test_parser_error_is_not_confirmed(self) -> None:
        """The sub-scanner returns a non-None result carrying the error."""
        assert _page_confirmed(self._result(sub_error="Unexpected error: boom")) is False

    def test_unreachable_page_is_not_confirmed(self) -> None:
        assert _page_confirmed(self._result(status=None, relationships=False)) is False

    def test_missing_status_is_not_confirmed(self) -> None:
        """Absent evidence is not evidence of removal."""
        result = self._result(status=200)
        result.status_code = None
        assert _page_confirmed(result) is False


class TestEdgeExpiry:
    """A dependency that is dropped has to become visible as a drop.

    Nothing previously removed an edge, so the dataset only grew and a
    government migrating away from a provider looked identical to no change.
    """

    @staticmethod
    def _agg(source="source.gov", target="target.com", pages=("https://source.gov/a",),
             active=True):
        from src.jobs.relationship_scanner_job import AggregatedRelationship

        return AggregatedRelationship(
            source_domain=source,
            target_domain=target,
            target_hostname=f"www.{target}",
            relationship_type="editorial_link",
            target_category="unknown_external",
            source_pages=set(pages),
            observations=1,
            page_regions={"body"},
            first_seen="2026-01-01T00:00:00+00:00",
            last_seen="2026-01-01T00:00:00+00:00",
            active=active,
        )

    @staticmethod
    def _key(agg):
        return (agg.source_domain, agg.target_domain, agg.target_hostname,
                agg.relationship_type)

    def _expire(self, existing, confirmed, observed):
        from src.jobs.relationship_scanner_job import RelationshipScannerJob

        return RelationshipScannerJob._expire_missing_edges(
            existing, set(confirmed), observed, "2026-06-01T00:00:00+00:00"
        )

    def test_edge_absent_from_a_rescanned_page_is_retired(self) -> None:
        agg = self._agg()
        key = self._key(agg)
        existing = {key: agg}

        retired = self._expire(existing, {"https://source.gov/a"}, {"https://source.gov/a": set()})

        assert retired == 1
        assert existing[key].active is False
        assert existing[key].inactive_since == "2026-06-01T00:00:00+00:00"

    def test_edge_still_served_is_kept(self) -> None:
        agg = self._agg()
        key = self._key(agg)
        existing = {key: agg}

        retired = self._expire(existing, {"https://source.gov/a"},
                               {"https://source.gov/a": {key}})

        assert retired == 0
        assert existing[key].active is True

    def test_failed_page_is_not_evidence_of_removal(self) -> None:
        """Treating an outage as removal would fake a sovereignty win."""
        agg = self._agg()
        key = self._key(agg)
        existing = {key: agg}

        # The page was attempted but not confirmed, so it is absent from both
        # confirmed_urls and observed_by_url.
        retired = self._expire(existing, set(), {})

        assert retired == 0
        assert existing[key].active is True

    def test_edge_survives_while_any_page_still_serves_it(self) -> None:
        agg = self._agg(pages=("https://source.gov/a", "https://source.gov/b"))
        key = self._key(agg)
        existing = {key: agg}

        retired = self._expire(
            existing,
            {"https://source.gov/a"},
            {"https://source.gov/a": set()},
        )

        assert retired == 0
        assert existing[key].active is True
        assert existing[key].source_pages == {"https://source.gov/b"}

    def test_unscanned_pages_do_not_retire_an_edge(self) -> None:
        """Progressive scanning visits a slice per run; the rest is unknown."""
        agg = self._agg(pages=("https://source.gov/a",))
        key = self._key(agg)
        existing = {key: agg}

        retired = self._expire(existing, {"https://source.gov/other"},
                               {"https://source.gov/other": set()})

        assert retired == 0
        assert existing[key].source_pages == {"https://source.gov/a"}

    def test_legacy_edge_without_page_attribution_is_left_alone(self) -> None:
        """Rows predating source_page_urls cannot be checked, so are not guessed at."""
        agg = self._agg(pages=())
        key = self._key(agg)
        existing = {key: agg}

        retired = self._expire(existing, {"https://source.gov/a"},
                               {"https://source.gov/a": set()})

        assert retired == 0
        assert existing[key].active is True

    def test_already_inactive_edge_is_not_retired_twice(self) -> None:
        agg = self._agg(active=False)
        agg.inactive_since = "2026-05-01T00:00:00+00:00"
        key = self._key(agg)
        existing = {key: agg}

        retired = self._expire(existing, {"https://source.gov/a"},
                               {"https://source.gov/a": set()})

        assert retired == 0
        assert existing[key].inactive_since == "2026-05-01T00:00:00+00:00"

    def test_reobserving_a_retired_edge_revives_it(self) -> None:
        """A provider can be dropped and later readopted."""
        import tempfile
        from pathlib import Path

        from src.jobs.relationship_scanner_job import _rel_key

        edge = _make_edge("source.gov", "target.com", "www.target.com", "editorial_link")
        key = _rel_key(edge)
        agg = self._agg(target="target.com", active=False)
        agg.inactive_since = "2026-05-01T00:00:00+00:00"

        with tempfile.TemporaryDirectory() as tmpdir:
            from src.lib.settings import Settings
            from src.jobs.relationship_scanner_job import RelationshipScannerJob

            db_path = Path(tmpdir) / "test.db"
            _setup_db(db_path)
            settings = Settings()
            settings.metadata_db_url = f"sqlite:///{db_path}"
            job = RelationshipScannerJob(settings)

            merged = job._merge_new_relationships(
                {key: agg}, [(edge, "https://source.gov/a")]
            )

        assert merged[key].active is True
        assert merged[key].inactive_since is None

    def test_active_flag_round_trips_through_the_dataset(self) -> None:
        """Liveness must survive the JSONL, or every cycle would resurrect it."""
        import tempfile
        from pathlib import Path

        from src.lib.settings import Settings
        from src.jobs.relationship_scanner_job import RelationshipScannerJob

        agg = self._agg(active=False)
        agg.inactive_since = "2026-05-01T00:00:00+00:00"
        key = self._key(agg)

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            _setup_db(db_path)
            settings = Settings()
            settings.metadata_db_url = f"sqlite:///{db_path}"
            job = RelationshipScannerJob(settings)

            shard_dir = Path(tmpdir) / "relationships"
            job._write_jsonl({key: agg}, shard_dir)
            loaded = job._load_existing_relationships(shard_dir)

        assert loaded[key].active is False
        assert loaded[key].inactive_since == "2026-05-01T00:00:00+00:00"

    def test_rows_predating_the_field_load_as_active(self) -> None:
        """Existing published data has no `active` key and must not vanish."""
        import json
        import tempfile
        from pathlib import Path

        from src.lib.settings import Settings
        from src.jobs.relationship_scanner_job import RelationshipScannerJob

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            _setup_db(db_path)
            settings = Settings()
            settings.metadata_db_url = f"sqlite:///{db_path}"
            job = RelationshipScannerJob(settings)

            shard_dir = Path(tmpdir) / "relationships"
            shard_dir.mkdir(parents=True)
            (shard_dir / "gov.001.jsonl").write_text(
                json.dumps({
                    "source_domain": "source.gov", "target_domain": "target.com",
                    "target_hostname": "www.target.com",
                    "relationship_type": "editorial_link",
                    "target_category": "unknown_external",
                    "source_pages": 1, "observations": 1, "page_regions": ["body"],
                    "first_seen": "2026-01-01T00:00:00+00:00",
                    "last_seen": "2026-01-01T00:00:00+00:00",
                }) + "\n",
                encoding="utf-8",
            )
            loaded = job._load_existing_relationships(shard_dir)

        assert all(a.active is True for a in loaded.values())


class TestSummaryExcludesRetiredEdges:
    """The summaries feed the country pages and the network graph.

    Retired edges stay in the shards so a drop stays auditable, but the matrix
    and the snapshots filter them out.  If the summaries did not, two published
    views of the same data would disagree for the 180 days a retired edge is
    retained.
    """

    @staticmethod
    def _agg(target="target.com", active=True):
        from src.jobs.relationship_scanner_job import AggregatedRelationship

        return AggregatedRelationship(
            source_domain="agency.gov.uk",
            target_domain=target,
            target_hostname=f"www.{target}",
            relationship_type="script_dependency",
            target_category="cdn",
            source_pages={"https://agency.gov.uk/a"},
            observations=3,
            page_regions={"head"},
            first_seen="2026-01-01T00:00:00+00:00",
            last_seen="2026-01-01T00:00:00+00:00",
            active=active,
        )

    def _summary(self, aggs):
        relationships = {_rel_key(a): a for a in aggs}
        return RelationshipScannerJob._build_country_summary(
            object(), "UNITED_KINGDOM", relationships
        )

    def test_active_edge_is_counted(self) -> None:
        summary = self._summary([self._agg()])

        assert summary["total_relationships"] == 1
        assert summary["top_target_domains"][0]["domain"] == "target.com"

    def test_retired_edge_is_not_counted(self) -> None:
        summary = self._summary([self._agg(active=False)])

        assert summary["total_relationships"] == 0
        assert summary["top_target_domains"] == []
        assert summary["total_source_domains"] == 0

    def test_retired_edge_does_not_inflate_a_live_one(self) -> None:
        summary = self._summary([
            self._agg(target="live.com"),
            self._agg(target="dropped.com", active=False),
        ])

        assert [t["domain"] for t in summary["top_target_domains"]] == ["live.com"]
        assert summary["relationship_types"] == {"script_dependency": 1}
