"""Unit tests for the sharded relationship dataset."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.lib import relationship_shards


def _row(source: str, target: str = "t.com", rel: str = "editorial_link") -> dict:
    """Build a minimal relationship row."""
    return {
        "source_domain": source,
        "target_domain": target,
        "target_hostname": f"www.{target}",
        "relationship_type": rel,
        "target_category": "unknown_external",
        "source_pages": 1,
        "observations": 1,
        "page_regions": ["main"],
        "first_seen": "2026-01-01T00:00:00+00:00",
        "last_seen": "2026-01-01T00:00:00+00:00",
    }


class TestShardGroup:
    """Grouping of source domains into shard names."""

    @pytest.mark.parametrize(
        ("domain", "expected"),
        [
            ("varna.bg", "bg"),
            ("GOV.UK", "uk"),
            ("example.co.uk", "uk"),
            ("bund.de", "de"),
        ],
    )
    def test_uses_top_level_domain(self, domain: str, expected: str) -> None:
        assert relationship_shards.shard_group_for_domain(domain) == expected

    @pytest.mark.parametrize("domain", ["", "localhost", "192.168.0.1"])
    def test_falls_back_when_no_usable_tld(self, domain: str) -> None:
        """Values without a country-bearing TLD land in the catch-all group."""
        assert relationship_shards.shard_group_for_domain(domain) == "other"

    def test_group_name_is_filename_safe(self) -> None:
        """Hostile input cannot escape the shard directory."""
        group = relationship_shards.shard_group_for_domain("evil.../../../etc")
        assert "/" not in group and "." not in group


class TestRoundTrip:
    """Writing then reading the dataset preserves every row."""

    def test_all_rows_survive(self, tmp_path: Path) -> None:
        rows = [_row("a.uk"), _row("b.bg"), _row("c.de"), _row("localhost")]
        relationship_shards.write_rows(rows, tmp_path)

        loaded = list(relationship_shards.iter_rows(tmp_path))
        assert len(loaded) == len(rows)
        assert {r["source_domain"] for r in loaded} == {
            "a.uk", "b.bg", "c.de", "localhost",
        }

    def test_rows_are_grouped_by_tld(self, tmp_path: Path) -> None:
        relationship_shards.write_rows([_row("a.uk"), _row("b.bg")], tmp_path)
        names = {p.name for p in relationship_shards.shard_files(tmp_path)}
        assert names == {"uk.001.jsonl", "bg.001.jsonl"}

    def test_index_totals_match_contents(self, tmp_path: Path) -> None:
        rows = [_row("a.uk"), _row("b.uk"), _row("c.bg")]
        index = relationship_shards.write_rows(rows, tmp_path)

        assert index["total_rows"] == 3
        assert index["total_bytes"] == sum(
            p.stat().st_size for p in relationship_shards.shard_files(tmp_path)
        )


class TestDeterminism:
    """Stable output keeps git deltas small between scan cycles."""

    def test_input_order_does_not_change_output(self, tmp_path: Path) -> None:
        rows = [_row("b.uk"), _row("a.uk"), _row("c.bg")]

        relationship_shards.write_rows(rows, tmp_path)
        first = {p.name: p.read_bytes() for p in relationship_shards.shard_files(tmp_path)}

        relationship_shards.write_rows(list(reversed(rows)), tmp_path)
        second = {p.name: p.read_bytes() for p in relationship_shards.shard_files(tmp_path)}

        assert first == second


class TestSplitting:
    """Oversized groups are split rather than written as one huge file."""

    def test_group_splits_into_numbered_parts(self, tmp_path: Path) -> None:
        rows = [_row(f"site{i}.uk", target=f"t{i}.com") for i in range(20)]
        index = relationship_shards.write_rows(rows, tmp_path, max_bytes=512)

        uk_shards = [e for e in index["shards"] if e["group"] == "uk"]
        assert len(uk_shards) > 1, "expected the uk group to be split"
        assert [e["file"] for e in uk_shards] == sorted(e["file"] for e in uk_shards)

    def test_no_rows_lost_when_splitting(self, tmp_path: Path) -> None:
        rows = [_row(f"site{i}.uk", target=f"t{i}.com") for i in range(20)]
        relationship_shards.write_rows(rows, tmp_path, max_bytes=512)

        loaded = list(relationship_shards.iter_rows(tmp_path))
        assert len(loaded) == 20

    def test_every_shard_stays_under_github_limit(self, tmp_path: Path) -> None:
        rows = [_row(f"site{i}.uk", target=f"t{i}.com") for i in range(50)]
        index = relationship_shards.write_rows(rows, tmp_path, max_bytes=1024)

        for entry in index["shards"]:
            assert entry["bytes"] <= relationship_shards.GITHUB_FILE_LIMIT_BYTES

    def test_oversized_single_row_still_written(self, tmp_path: Path) -> None:
        """A row larger than the cap gets its own shard instead of vanishing."""
        rows = [_row("a.uk", target="x" * 5000)]
        relationship_shards.write_rows(rows, tmp_path, max_bytes=100)

        assert len(list(relationship_shards.iter_rows(tmp_path))) == 1


class TestStaleCleanup:
    """A shrinking dataset does not strand rows from a previous run."""

    def test_shards_no_longer_needed_are_removed(self, tmp_path: Path) -> None:
        relationship_shards.write_rows(
            [_row("a.uk"), _row("b.bg"), _row("c.de")], tmp_path
        )
        relationship_shards.write_rows([_row("a.uk")], tmp_path)

        loaded = list(relationship_shards.iter_rows(tmp_path))
        assert len(loaded) == 1
        assert {p.name for p in relationship_shards.shard_files(tmp_path)} == {
            "uk.001.jsonl"
        }

    def test_no_temp_files_left_behind(self, tmp_path: Path) -> None:
        relationship_shards.write_rows([_row("a.uk"), _row("b.bg")], tmp_path)
        assert list(tmp_path.glob("*.tmp")) == []


class TestReadFallbacks:
    """Reading tolerates a missing directory, damaged index, or legacy layout."""

    def test_missing_directory_yields_nothing(self, tmp_path: Path) -> None:
        assert list(relationship_shards.iter_rows(tmp_path / "absent")) == []

    def test_legacy_single_file_is_read(self, tmp_path: Path) -> None:
        legacy = tmp_path / "relationships.jsonl"
        legacy.write_text(
            "".join(json.dumps(_row(d)) + "\n" for d in ("a.uk", "b.bg")),
            encoding="utf-8",
        )

        loaded = list(
            relationship_shards.iter_rows(tmp_path / "shards", legacy_path=legacy)
        )
        assert len(loaded) == 2

    def test_shards_take_precedence_over_legacy(self, tmp_path: Path) -> None:
        shard_dir = tmp_path / "shards"
        relationship_shards.write_rows([_row("a.uk")], shard_dir)

        legacy = tmp_path / "relationships.jsonl"
        legacy.write_text(json.dumps(_row("stale.bg")) + "\n", encoding="utf-8")

        loaded = list(
            relationship_shards.iter_rows(shard_dir, legacy_path=legacy)
        )
        assert [r["source_domain"] for r in loaded] == ["a.uk"]

    def test_damaged_index_falls_back_to_glob(self, tmp_path: Path) -> None:
        relationship_shards.write_rows([_row("a.uk"), _row("b.bg")], tmp_path)
        (tmp_path / relationship_shards.INDEX_FILENAME).write_text(
            "not json", encoding="utf-8"
        )

        assert len(list(relationship_shards.iter_rows(tmp_path))) == 2

    def test_malformed_lines_are_skipped(self, tmp_path: Path) -> None:
        relationship_shards.write_rows([_row("a.uk")], tmp_path)
        shard = relationship_shards.shard_files(tmp_path)[0]
        with shard.open("a", encoding="utf-8") as handle:
            handle.write("{ not valid json\n\n")

        assert len(list(relationship_shards.iter_rows(tmp_path))) == 1


class TestPublishedDataset:
    """Guards on the dataset actually committed to the repository."""

    def test_committed_shards_stay_clear_of_github_limit(self) -> None:
        """Regression guard: the single-file dataset reached 100.00 MiB.

        GitHub refuses a push containing any file over 100 MiB, which would
        break the scan workflow's auto-commit with no obvious signal.
        """
        shard_dir = Path("docs/data/relationships")
        if not shard_dir.is_dir():
            pytest.skip("relationship dataset not present in this checkout")

        oversized = [
            (path.name, path.stat().st_size)
            for path in shard_dir.glob("*.jsonl")
            if path.stat().st_size > relationship_shards.GITHUB_FILE_LIMIT_BYTES
        ]
        assert not oversized, f"shards over GitHub's file limit: {oversized}"

    def test_legacy_single_file_is_gone(self) -> None:
        """The pre-split file must not come back; it is what hit the limit."""
        assert not Path("docs/data/relationships.jsonl").exists()
