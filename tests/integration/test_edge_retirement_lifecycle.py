"""End-to-end retirement: a dependency appears, is dropped, and comes back.

The unit tests cover ``_expire_missing_edges`` in isolation.  They cannot show
that a real scan cycle wires it up correctly -- that a page scanned twice, with
a dependency present the first time and gone the second, actually ends with a
retired edge on disk.

This matters more than usual because of the timing.  Every published row
predates ``source_page_urls`` and so is unretirable until re-observed, and the
28-day skip window means a page is not normally visited twice inside a month.
A wiring defect here would therefore not surface in production for weeks, and
would surface as *nothing happening* -- indistinguishable from a corpus that
genuinely did not change.  So the cycle is driven here instead, against the
real job, with the network stubbed.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.jobs import relationship_scanner_job as job_module
from src.jobs.relationship_scanner_job import RelationshipScannerJob
from src.lib import relationship_shards
from src.lib.settings import Settings
from src.services.multi_scanner import MultiScanResult
from src.services.relationship_scanner import RelationshipEdge, RelationshipScanResult

PAGE = "https://agency.test/index.html"
SOURCE = "agency.test"


def _edge(target: str) -> RelationshipEdge:
    """A script dependency from the scanned page to *target*."""
    return RelationshipEdge(
        source_domain=SOURCE,
        target_domain=target,
        target_hostname=f"cdn.{target}",
        relationship_type="script_dependency",
        target_category="cdn",
        is_external=True,
        html_element="script",
        page_region="head",
        target_url=f"https://cdn.{target}/lib.js",
    )


class ScriptedScanner:
    """Stands in for MultiScanner, replaying one scripted result per pass."""

    def __init__(self) -> None:
        self.passes: list[MultiScanResult] = []
        self.calls = 0

    def queue(self, targets, status=200, sub_error=None, reachable=True) -> None:
        """Queue a pass in which the page serves exactly *targets*."""
        relationships = None
        if reachable:
            relationships = RelationshipScanResult(
                url=PAGE,
                is_reachable=True,
                relationships=[_edge(t) for t in targets],
                error_message=sub_error,
            )
        self.passes.append(
            MultiScanResult(
                url=PAGE,
                is_reachable=reachable,
                status_code=status,
                relationships=relationships,
            )
        )

    async def scan_urls_batch(self, urls, on_result=None, **kwargs):
        """Replay the next queued pass through the job's result callback."""
        result = self.passes[self.calls]
        self.calls += 1
        if on_result is not None:
            on_result(result)
        return {result.url: result}


@pytest.fixture
def toon_file(tmp_path: Path) -> Path:
    """A seed naming the single page this cycle scans."""
    path = tmp_path / "testland.toon"
    path.write_text(
        json.dumps({
            "version": "0.1-seed",
            "country": "TestLand",
            "domains": [{"canonical_domain": SOURCE, "pages": [{"url": PAGE}]}],
        }),
        encoding="utf-8",
    )
    return path


@pytest.fixture
def scan(tmp_path: Path, toon_file: Path, monkeypatch):
    """Return a callable running one scan pass against a temporary dataset."""
    shard_dir = tmp_path / "relationships"
    monkeypatch.setattr(job_module, "RELATIONSHIP_SHARD_DIR", shard_dir)

    settings = Settings(
        crawl_timeout_seconds=2,
        toon_output_dir=tmp_path / "toon-cache",
        metadata_db_url=f"sqlite:///{tmp_path / 'meta.db'}",
    )
    job = RelationshipScannerJob(settings)
    scanner = ScriptedScanner()
    job.scanner = scanner

    async def run(targets, **kwargs):
        scanner.queue(targets, **kwargs)
        # skip_recently_scanned_days=0 so each pass revisits the same page,
        # standing in for the 28-day window elapsing between real runs.
        return await job.scan_country(
            "TESTLAND", toon_file, skip_recently_scanned_days=0,
        )

    run.shard_dir = shard_dir
    return run


def _rows(shard_dir: Path) -> dict[str, dict]:
    """Published rows keyed by target domain."""
    return {r["target_domain"]: r for r in relationship_shards.iter_rows(shard_dir)}


class TestRetirementLifecycle:
    """The full appear / drop / return cycle through the real scan path."""

    @pytest.mark.asyncio
    async def test_first_pass_publishes_both_edges_as_active(self, scan) -> None:
        await scan(["analytics.example", "maps.example"])
        rows = _rows(scan.shard_dir)

        assert set(rows) == {"analytics.example", "maps.example"}
        assert all(r["active"] is True for r in rows.values())
        # Without a page set the edge could never be retired later.
        assert all(r["source_page_urls"] == [PAGE] for r in rows.values())

    @pytest.mark.asyncio
    async def test_dropped_dependency_is_retired(self, scan) -> None:
        """The signal the sovereignty view depends on."""
        await scan(["analytics.example", "maps.example"])
        result = await scan(["analytics.example"])

        rows = _rows(scan.shard_dir)
        assert result["edges_retired"] == 1
        assert rows["maps.example"]["active"] is False
        assert rows["maps.example"]["inactive_since"]
        # The retired row stays published so the drop itself is auditable.
        assert rows["analytics.example"]["active"] is True

    @pytest.mark.asyncio
    async def test_readopted_dependency_is_revived(self, scan) -> None:
        """A provider can be dropped and taken up again."""
        await scan(["analytics.example", "maps.example"])
        await scan(["analytics.example"])
        await scan(["analytics.example", "maps.example"])

        row = _rows(scan.shard_dir)["maps.example"]
        assert row["active"] is True
        assert row["inactive_since"] is None

    @pytest.mark.asyncio
    async def test_error_page_retires_nothing(self, scan) -> None:
        """A 503 serves no scripts; treating that as a drop fakes a migration."""
        await scan(["analytics.example", "maps.example"])
        result = await scan([], status=503)

        rows = _rows(scan.shard_dir)
        assert result["pages_confirmed"] == 0
        assert result["edges_retired"] == 0
        assert all(r["active"] is True for r in rows.values())

    @pytest.mark.asyncio
    async def test_unreachable_page_retires_nothing(self, scan) -> None:
        await scan(["analytics.example", "maps.example"])
        result = await scan([], reachable=False, status=None)

        assert result["edges_retired"] == 0
        assert all(r["active"] is True for r in _rows(scan.shard_dir).values())

    @pytest.mark.asyncio
    async def test_parser_failure_retires_nothing(self, scan) -> None:
        await scan(["analytics.example", "maps.example"])
        result = await scan([], sub_error="Unexpected error: boom")

        assert result["edges_retired"] == 0
        assert all(r["active"] is True for r in _rows(scan.shard_dir).values())

    @pytest.mark.asyncio
    async def test_confirmation_is_reported_for_monitoring(self, scan) -> None:
        """The counts that make a silent retirement failure visible."""
        result = await scan(["analytics.example"])

        assert result["pages_confirmed"] == 1
        assert result["edges_checkable"] == 1
        assert result["edges_inactive"] == 0
