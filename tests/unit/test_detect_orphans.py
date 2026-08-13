"""Unit tests for orphan detection over the relationship dataset."""

from __future__ import annotations

import json
from pathlib import Path

from src.cli.detect_orphans import load_relationship_targets


def _row(source: str, target: str, active: bool | None = None) -> dict:
    """Build a minimal government-to-government relationship row."""
    row = {
        "source_domain": source,
        "target_domain": target,
        "target_hostname": f"www.{target}",
        "relationship_type": "editorial_link",
        "target_category": "known_government",
        "source_pages": 1,
        "observations": 1,
        "page_regions": ["body"],
        "first_seen": "2026-01-01T00:00:00+00:00",
        "last_seen": "2026-01-01T00:00:00+00:00",
    }
    if active is not None:
        row["active"] = active
    return row


def _write(shard_dir: Path, rows: list[dict]) -> None:
    """Write *rows* as a single shard."""
    shard_dir.mkdir(parents=True, exist_ok=True)
    (shard_dir / "uk.001.jsonl").write_text(
        "".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8"
    )


class TestLoadRelationshipTargets:
    """Which inbound links count as evidence a domain is referenced."""

    def test_government_targets_are_collected(self, tmp_path: Path) -> None:
        _write(tmp_path, [_row("a.gov.uk", "target.gov.uk")])

        assert load_relationship_targets(tmp_path) == {
            "target.gov.uk": {"a.gov.uk"}
        }

    def test_non_government_targets_are_ignored(self, tmp_path: Path) -> None:
        row = _row("a.gov.uk", "cdn.example")
        row["target_category"] = "cdn"
        _write(tmp_path, [row])

        assert load_relationship_targets(tmp_path) == {}

    def test_retired_links_do_not_count_as_references(self, tmp_path: Path) -> None:
        """A link that has since been removed must not mask an orphan.

        Retired edges stay in the shards for 180 days so a drop is auditable.
        Counting them here would keep a domain out of the orphan report on the
        strength of a link that no longer exists.
        """
        _write(tmp_path, [_row("a.gov.uk", "target.gov.uk", active=False)])

        assert load_relationship_targets(tmp_path) == {}

    def test_a_live_link_still_counts_alongside_a_retired_one(
        self, tmp_path: Path
    ) -> None:
        _write(tmp_path, [
            _row("a.gov.uk", "target.gov.uk", active=False),
            _row("b.gov.uk", "target.gov.uk", active=True),
        ])

        assert load_relationship_targets(tmp_path) == {
            "target.gov.uk": {"b.gov.uk"}
        }

    def test_rows_predating_the_active_flag_are_kept(self, tmp_path: Path) -> None:
        """Absent means never evaluated, not retired."""
        _write(tmp_path, [_row("a.gov.uk", "target.gov.uk")])

        assert "target.gov.uk" in load_relationship_targets(tmp_path)
