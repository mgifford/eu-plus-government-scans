"""Unit tests for helpers shared by the report generators."""

from __future__ import annotations

import json
from pathlib import Path

from src.cli._report_common import count_toon_seed_urls


def test_missing_dir_returns_empty(tmp_path: Path):
    """A missing seed directory yields no counts rather than raising."""
    assert count_toon_seed_urls(tmp_path / "nonexistent") == {}


def test_empty_dir_returns_empty(tmp_path: Path):
    """A directory with no seed files yields no counts."""
    seeds_dir = tmp_path / "seeds"
    seeds_dir.mkdir()
    assert count_toon_seed_urls(seeds_dir) == {}


def test_reads_page_count(tmp_path: Path):
    """Each seed contributes its declared page_count, keyed by country code."""
    seeds_dir = tmp_path / "seeds"
    seeds_dir.mkdir()
    for name, count in [("iceland", 139), ("norway", 239)]:
        (seeds_dir / f"{name}.toon").write_text(
            json.dumps({"page_count": count, "domains": []}), encoding="utf-8"
        )

    assert count_toon_seed_urls(seeds_dir) == {"ICELAND": 139, "NORWAY": 239}


def test_scanner_output_is_not_counted(tmp_path: Path):
    """Derived .toon files must not inflate the seed totals reports divide by."""
    seeds_dir = tmp_path / "seeds"
    seeds_dir.mkdir()
    (seeds_dir / "iceland.toon").write_text(
        json.dumps({"page_count": 139, "domains": []}), encoding="utf-8"
    )
    for suffix in ("_validated", "_tech", "_social"):
        (seeds_dir / f"iceland{suffix}.toon").write_text(
            json.dumps({"page_count": 999, "domains": []}), encoding="utf-8"
        )

    assert count_toon_seed_urls(seeds_dir) == {"ICELAND": 139}


def test_unreadable_seed_is_skipped(tmp_path: Path):
    """One malformed seed must not fail the whole report."""
    seeds_dir = tmp_path / "seeds"
    seeds_dir.mkdir()
    (seeds_dir / "broken.toon").write_text("{ not json", encoding="utf-8")
    (seeds_dir / "norway.toon").write_text(
        json.dumps({"page_count": 12, "domains": []}), encoding="utf-8"
    )

    assert count_toon_seed_urls(seeds_dir) == {"NORWAY": 12}


def test_missing_page_count_is_zero(tmp_path: Path):
    """A seed without page_count counts as zero, not as an error."""
    seeds_dir = tmp_path / "seeds"
    seeds_dir.mkdir()
    (seeds_dir / "iceland.toon").write_text(
        json.dumps({"domains": []}), encoding="utf-8"
    )

    assert count_toon_seed_urls(seeds_dir) == {"ICELAND": 0}
