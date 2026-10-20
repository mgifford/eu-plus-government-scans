"""Unit tests for the curated design-system registry."""

from __future__ import annotations

from pathlib import Path

import yaml

from src.lib.design_system_registry import (
    DEFAULT_REGISTRY_PATH,
    MIN_SIGNATURE_LENGTH,
    DESIGN_SYSTEM_TYPES,
    DesignSystemRegistry,
)

VALID_CONFIDENCE = {"high", "medium", "low"}


def _write(tmp_path: Path, entries: list[dict]) -> Path:
    """Write a registry file and return its path."""
    path = tmp_path / "design-systems.yaml"
    path.write_text(yaml.safe_dump({"design_systems": entries}), encoding="utf-8")
    return path


def _entry(**overrides) -> dict:
    """Return a minimal valid registry entry, with optional overrides."""
    entry = {
        "name": "Example Design System",
        "country_code": "ESTONIA",
        "type": "design_system",
        "scope": "national",
        "url": "https://example.gov/design",
        "adoption_signatures": ["example-ds"],
        "confidence": "high",
        "needs_review": False,
        "notes": "",
    }
    entry.update(overrides)
    return entry


class TestCurationRules:
    """The shipped registry must follow its own doctrine."""

    def test_default_registry_loads_with_entries(self) -> None:
        reg = DesignSystemRegistry()
        assert len(reg) > 0

    def test_default_registry_has_known_system_with_signatures(self) -> None:
        reg = DesignSystemRegistry()
        uk = next(
            (s for s in reg.all_systems() if s.country_code == "UNITED_KINGDOM_UK"),
            None,
        )
        assert uk is not None
        assert uk.has_signatures

    def test_entries_obey_confidence_rule(self) -> None:
        """Anything below confidence: high must carry needs_review: true."""
        reg = DesignSystemRegistry()
        for system in reg.all_systems():
            if system.confidence != "high":
                assert system.needs_review, system.name

    def test_types_and_confidence_are_valid(self) -> None:
        reg = DesignSystemRegistry()
        for system in reg.all_systems():
            assert system.type in DESIGN_SYSTEM_TYPES, system.name
            assert system.confidence in VALID_CONFIDENCE, system.name

    def test_country_codes_are_upper_snake_when_present(self) -> None:
        reg = DesignSystemRegistry()
        for system in reg.all_systems():
            if system.country_code:
                assert system.country_code == system.country_code.upper()
                assert " " not in system.country_code

    def test_registry_file_exists(self) -> None:
        assert DEFAULT_REGISTRY_PATH.is_file()


class TestLookup:
    """Matching and grouping behaviour."""

    def test_missing_file_is_tolerated(self, tmp_path: Path) -> None:
        reg = DesignSystemRegistry(tmp_path / "absent.yaml")
        assert len(reg) == 0
        assert reg.matched_systems("<html></html>") == []

    def test_signature_match_is_case_insensitive(self, tmp_path: Path) -> None:
        reg = DesignSystemRegistry(_write(tmp_path, [
            _entry(adoption_signatures=["Example-DS"]),
        ]))
        assert reg.matched_systems('<link href="/example-ds.min.css">') == [
            "Example Design System"
        ]

    def test_entry_without_signatures_never_matches(self, tmp_path: Path) -> None:
        reg = DesignSystemRegistry(_write(tmp_path, [
            _entry(adoption_signatures=[]),
        ]))
        assert reg.matched_systems("<body class='example-ds'>") == []

    def test_short_signatures_are_dropped(self, tmp_path: Path) -> None:
        """A 2-character signature would collide with unrelated markup."""
        reg = DesignSystemRegistry(_write(tmp_path, [
            _entry(adoption_signatures=["ab"]),
        ]))
        assert reg.all_systems()[0].adoption_signatures == ()
        assert len("ab") < MIN_SIGNATURE_LENGTH

    def test_entry_without_name_is_skipped(self, tmp_path: Path) -> None:
        reg = DesignSystemRegistry(_write(tmp_path, [_entry(name="")]))
        assert len(reg) == 0

    def test_unknown_type_falls_back_to_design_system(self, tmp_path: Path) -> None:
        reg = DesignSystemRegistry(_write(tmp_path, [_entry(type="mystery")]))
        assert reg.all_systems()[0].type == "design_system"

    def test_by_country_groups_supranational_under_empty_key(self, tmp_path: Path) -> None:
        reg = DesignSystemRegistry(_write(tmp_path, [
            _entry(),
            _entry(name="EU Thing", country_code=""),
        ]))
        grouped = reg.by_country()
        assert "ESTONIA" in grouped
        assert "" in grouped

    def test_contains_by_name(self, tmp_path: Path) -> None:
        reg = DesignSystemRegistry(_write(tmp_path, [_entry()]))
        assert "Example Design System" in reg
        assert "Other" not in reg


class TestCoverage:
    """Coverage counts must expose how much of the table is unmeasurable."""

    def test_coverage_counts_signature_gaps(self, tmp_path: Path) -> None:
        reg = DesignSystemRegistry(_write(tmp_path, [
            _entry(),
            _entry(name="No Sigs", adoption_signatures=[], needs_review=True,
                   confidence="medium"),
        ]))
        coverage = reg.coverage()
        assert coverage["total"] == 2
        assert coverage["with_adoption_signatures"] == 1
        assert coverage["without_adoption_signatures"] == 1
        assert coverage["needs_review"] == 1
        assert coverage["with_country_code"] == 2

    def test_empty_registry_coverage_is_zeroed(self, tmp_path: Path) -> None:
        reg = DesignSystemRegistry(tmp_path / "absent.yaml")
        assert reg.coverage()["total"] == 0
