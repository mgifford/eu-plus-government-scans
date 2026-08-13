"""Unit tests for dated corpus snapshots."""

from __future__ import annotations

import json
from pathlib import Path

from src.cli.generate_snapshot import (
    INDEX_FILENAME,
    build_snapshot,
    count_seed_domains,
    write_snapshot,
)


INDEX = {"a.gov.uk": "UNITED_KINGDOM_UK", "b.gov.uk": "UNITED_KINGDOM_UK", "c.gov.pl": "POLAND"}
SEEDS = {"UNITED_KINGDOM_UK": 10, "POLAND": 5}


def _row(source, target, rel_type="script_dependency", category="cdn", **extra):
    """Build a relationship row."""
    row = {
        "source_domain": source,
        "target_domain": target,
        "target_hostname": f"www.{target}",
        "relationship_type": rel_type,
        "target_category": category,
    }
    row.update(extra)
    return row


def _snapshot(rows, date="2026-08-12", **kwargs):
    """Build a snapshot from *rows* with the shared fixtures."""
    return build_snapshot(rows, INDEX, SEEDS, date, **kwargs)


class TestSeedCounts:
    """Inventory size comes from the seeds, not from what was scanned."""

    def test_counts_domains_per_country(self, tmp_path: Path) -> None:
        (tmp_path / "iceland.toon").write_text(
            json.dumps({"domains": [{"canonical_domain": "a.is"},
                                    {"canonical_domain": "b.is"}]}),
            encoding="utf-8",
        )
        assert count_seed_domains(tmp_path) == {"ICELAND": 2}

    def test_derived_files_are_not_counted(self, tmp_path: Path) -> None:
        """Scanner output beside the seeds would double-count the inventory."""
        (tmp_path / "iceland.toon").write_text(
            json.dumps({"domains": [{"canonical_domain": "a.is"}]}), encoding="utf-8"
        )
        (tmp_path / "iceland_validated.toon").write_text(
            json.dumps({"domains": [{"canonical_domain": "a.is"}]}), encoding="utf-8"
        )
        assert count_seed_domains(tmp_path) == {"ICELAND": 1}

    def test_malformed_seed_is_skipped(self, tmp_path: Path) -> None:
        (tmp_path / "broken.toon").write_text("{ not json", encoding="utf-8")
        (tmp_path / "iceland.toon").write_text(
            json.dumps({"domains": [{"canonical_domain": "a.is"}]}), encoding="utf-8"
        )
        assert count_seed_domains(tmp_path) == {"ICELAND": 1}


class TestSnapshotContent:
    """A snapshot has to describe the corpus on its date."""

    def test_records_inventory_and_scanned_counts(self) -> None:
        snap = _snapshot([_row("a.gov.uk", "googleapis.com")])
        uk = snap["countries"].index("UNITED_KINGDOM_UK")

        assert snap["seed_domains"][uk] == 10
        assert snap["scanned_domains"][uk] == 1

    def test_countries_with_seeds_but_no_scans_are_present(self) -> None:
        """A country must not vanish from the series just because a cycle
        happened not to reach it."""
        snap = _snapshot([_row("a.gov.uk", "googleapis.com")])

        assert "POLAND" in snap["countries"]
        pl = snap["countries"].index("POLAND")
        assert snap["seed_domains"][pl] == 5
        assert snap["scanned_domains"][pl] == 0

    def test_cells_count_distinct_domains(self) -> None:
        snap = _snapshot([
            _row("a.gov.uk", "googleapis.com"),
            _row("a.gov.uk", "googleapis.com", rel_type="stylesheet_dependency"),
            _row("b.gov.uk", "googleapis.com"),
        ])
        uk = snap["countries"].index("UNITED_KINGDOM_UK")
        gapi = snap["providers"].index("googleapis.com")

        assert [c for c in snap["cells"] if c[0] == uk and c[1] == gapi] == [[uk, gapi, 2]]

    def test_gov_to_gov_links_are_counted_separately(self) -> None:
        """The two views are different questions and must not be conflated."""
        snap = _snapshot([
            _row("a.gov.uk", "b.gov.uk", rel_type="editorial_link",
                 category="known_government"),
            _row("a.gov.uk", "googleapis.com"),
        ])
        uk = snap["countries"].index("UNITED_KINGDOM_UK")

        assert snap["gov_to_gov_links"][uk] == 1
        assert snap["providers"] == ["googleapis.com"]

    def test_self_links_are_not_counted(self) -> None:
        snap = _snapshot([
            _row("a.gov.uk", "a.gov.uk", rel_type="editorial_link",
                 category="known_government"),
        ])
        uk = snap["countries"].index("UNITED_KINGDOM_UK")
        assert snap["gov_to_gov_links"][uk] == 0

    def test_providers_beyond_the_cap_roll_into_other(self) -> None:
        """Per-country totals must still reconcile once the tail is dropped."""
        rows = [_row("a.gov.uk", "big.com"), _row("b.gov.uk", "big.com"),
                _row("a.gov.uk", "tail.com")]
        snap = _snapshot(rows, top_providers=1)
        uk = snap["countries"].index("UNITED_KINGDOM_UK")

        assert snap["providers"] == ["big.com"]
        assert snap["other_domains"][uk] == 1

    def test_inactive_edges_are_excluded(self) -> None:
        """A dependency that has been retired is not part of today's corpus."""
        snap = _snapshot([
            _row("a.gov.uk", "googleapis.com", active=False),
            _row("b.gov.uk", "other.com"),
        ])

        assert snap["providers"] == ["other.com"]

    def test_unresolvable_source_is_skipped(self) -> None:
        snap = _snapshot([_row("someone-elses.com", "googleapis.com"),
                          _row("a.gov.uk", "googleapis.com")])
        uk = snap["countries"].index("UNITED_KINGDOM_UK")
        assert snap["scanned_domains"][uk] == 1

    def test_cells_are_deterministically_ordered(self) -> None:
        """Stable ordering keeps the daily git delta small."""
        rows = [_row("b.gov.uk", "z.com"), _row("a.gov.uk", "y.com"),
                _row("c.gov.pl", "z.com")]
        assert _snapshot(rows)["cells"] == sorted(_snapshot(rows)["cells"])

    def test_snapshot_carries_its_date(self) -> None:
        assert _snapshot([_row("a.gov.uk", "x.com")], date="2026-01-31")["date"] == "2026-01-31"


class TestWriting:
    """One file per day, plus an index of what exists."""

    def test_writes_one_file_per_date(self, tmp_path: Path) -> None:
        write_snapshot(_snapshot([_row("a.gov.uk", "x.com")], date="2026-08-12"), tmp_path)
        write_snapshot(_snapshot([_row("a.gov.uk", "x.com")], date="2026-08-13"), tmp_path)

        assert {p.name for p in tmp_path.glob("2*.json")} == {
            "2026-08-12.json", "2026-08-13.json",
        }

    def test_same_day_rerun_replaces_rather_than_accumulates(self, tmp_path: Path) -> None:
        """Four scan cycles a day must collapse to one daily point."""
        write_snapshot(_snapshot([_row("a.gov.uk", "x.com")], date="2026-08-12"), tmp_path)
        write_snapshot(
            _snapshot([_row("a.gov.uk", "x.com"), _row("b.gov.uk", "x.com")],
                      date="2026-08-12"),
            tmp_path,
        )

        assert len(list(tmp_path.glob("2*.json"))) == 1
        written = json.loads((tmp_path / "2026-08-12.json").read_text(encoding="utf-8"))
        uk = written["countries"].index("UNITED_KINGDOM_UK")
        assert written["scanned_domains"][uk] == 2

    def test_index_lists_every_snapshot(self, tmp_path: Path) -> None:
        for day in ("2026-08-12", "2026-08-13", "2026-08-14"):
            write_snapshot(_snapshot([_row("a.gov.uk", "x.com")], date=day), tmp_path)

        index = json.loads((tmp_path / INDEX_FILENAME).read_text(encoding="utf-8"))
        assert index["count"] == 3
        assert index["first"] == "2026-08-12"
        assert index["latest"] == "2026-08-14"
        assert index["dates"] == ["2026-08-12", "2026-08-13", "2026-08-14"]

    def test_index_is_not_mistaken_for_a_snapshot(self, tmp_path: Path) -> None:
        write_snapshot(_snapshot([_row("a.gov.uk", "x.com")], date="2026-08-12"), tmp_path)
        index = json.loads((tmp_path / INDEX_FILENAME).read_text(encoding="utf-8"))
        assert INDEX_FILENAME.removesuffix(".json") not in index["dates"]


class TestTrend:
    """The point of the exercise: two snapshots make a change measurable."""

    def test_dropping_a_provider_is_visible_between_snapshots(self) -> None:
        before = _snapshot([_row("a.gov.uk", "googleapis.com"),
                            _row("b.gov.uk", "googleapis.com")], date="2026-08-12")
        after = _snapshot([_row("a.gov.uk", "googleapis.com"),
                           _row("b.gov.uk", "googleapis.com", active=False)],
                          date="2026-09-12")

        def depending(snap):
            uk = snap["countries"].index("UNITED_KINGDOM_UK")
            p = snap["providers"].index("googleapis.com")
            return next(c[2] for c in snap["cells"] if c[0] == uk and c[1] == p)

        assert depending(before) == 2
        assert depending(after) == 1

    def test_new_domains_are_visible_between_snapshots(self) -> None:
        first = build_snapshot([_row("a.gov.uk", "x.com")], INDEX,
                               {"UNITED_KINGDOM_UK": 10}, "2026-08-12")
        later = build_snapshot([_row("a.gov.uk", "x.com")], INDEX,
                               {"UNITED_KINGDOM_UK": 14}, "2026-09-12")
        uk = first["countries"].index("UNITED_KINGDOM_UK")

        assert later["seed_domains"][uk] - first["seed_domains"][uk] == 4
