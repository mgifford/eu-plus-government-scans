"""Tests for technology license enrichment helpers."""

from __future__ import annotations

from pathlib import Path

from src.services.technology_license_enrichment import (
    EnrichedTechnology,
    LicenseOverride,
    enrich_all,
    enrich_technology,
    is_spdx_osi_approved,
    load_overrides,
    to_dict,
)


def test_osi_approved_mit() -> None:
    """MIT should be classified as OSI-approved."""
    assert is_spdx_osi_approved("MIT") is True


def test_osi_approved_gpl2() -> None:
    """GPL-2.0-or-later should be classified as OSI-approved."""
    assert is_spdx_osi_approved("GPL-2.0-or-later") is True


def test_osi_not_approved_proprietary() -> None:
    """Unknown proprietary identifiers should not be treated as OSI-approved."""
    assert is_spdx_osi_approved("LicenseRef-Proprietary") is False


def test_compound_spdx_all_osi() -> None:
    """Compound SPDX expressions should pass when all IDs are approved."""
    assert is_spdx_osi_approved("MIT AND Apache-2.0") is True


def test_compound_spdx_mixed() -> None:
    """Compound SPDX expressions should fail conservatively on mixed IDs."""
    assert is_spdx_osi_approved("MIT AND LicenseRef-custom") is False


def test_enrich_known_osi() -> None:
    """Known open source technologies should use the curated override."""
    overrides = {
        "jQuery": LicenseOverride(
            spdx_expression="MIT",
            license_status="osi_approved",
            osi_approved=True,
            notes="jQuery is released under the MIT License.",
            confidence="high",
        )
    }

    enriched = enrich_technology(
        name="jQuery",
        categories=["JavaScript libraries"],
        detected_count=10,
        by_country={"ICELAND": 10},
        overrides=overrides,
    )

    assert enriched.license_status == "osi_approved"
    assert enriched.osi_approved is True
    assert enriched.requires_manual_review is False
    assert enriched.license_source == "override"


def test_enrich_proprietary_service() -> None:
    """Service-oriented technologies should keep the service classification."""
    overrides = {
        "Google Analytics": LicenseOverride(
            spdx_expression=None,
            license_status="not_applicable_service",
            osi_approved=None,
            notes="Google Analytics is a hosted proprietary service.",
            confidence="high",
        )
    }

    enriched = enrich_technology(
        name="Google Analytics",
        categories=["Analytics"],
        detected_count=4,
        by_country={"FRANCE": 4},
        overrides=overrides,
    )

    assert enriched.license_status == "not_applicable_service"
    assert enriched.requires_manual_review is False
    assert enriched.osi_approved is None


def test_enrich_unknown() -> None:
    """Unknown technologies should be flagged for manual review."""
    enriched = enrich_technology(
        name="SomeUnknownTech12345",
        categories=["Miscellaneous"],
        detected_count=1,
        by_country={"ICELAND": 1},
        overrides={},
    )

    assert enriched.license_status == "unknown"
    assert enriched.requires_manual_review is True
    assert enriched.license_source == "unknown"


def test_enrich_all_sorting() -> None:
    """enrich_all should sort by detected count descending then name."""
    technology_index = {
        "by_technology": {
            "Zulu": {"pages": 2, "categories": [], "by_country": {}},
            "Alpha": {"pages": 5, "categories": [], "by_country": {}},
            "Beta": {"pages": 5, "categories": [], "by_country": {}},
        }
    }

    enriched = enrich_all(technology_index, overrides={})

    assert [tech.name for tech in enriched] == ["Alpha", "Beta", "Zulu"]


def test_to_dict_fields() -> None:
    """to_dict should expose every required output field."""
    tech = EnrichedTechnology(
        name="Leaflet",
        categories=["Maps"],
        detected_count=7,
        license_status="osi_approved",
        spdx_license_expression="BSD-2-Clause",
        osi_approved=True,
        license_source="override",
        confidence="high",
        requires_manual_review=False,
        notes="Leaflet uses BSD-2-Clause.",
        by_country={"ICELAND": 7},
    )

    payload = to_dict(tech)

    assert set(payload) == {
        "name",
        "categories",
        "detected_count",
        "license_status",
        "spdx_license_expression",
        "osi_approved",
        "license_source",
        "confidence",
        "requires_manual_review",
        "notes",
        "by_country",
    }
    assert payload["name"] == "Leaflet"
    assert payload["by_country"] == {"ICELAND": 7}


def test_load_overrides() -> None:
    """load_overrides should parse the real curated override file."""
    repo_root = Path(__file__).resolve().parents[2]
    overrides = load_overrides(
        repo_root / "data" / "technology-license-overrides.json"
    )

    assert overrides["jQuery"].spdx_expression == "MIT"
    assert overrides["Drupal"].license_status == "osi_approved"
    assert overrides["Font Awesome"].osi_approved is None
    assert overrides["Google Analytics"].license_status == (
        "not_applicable_service"
    )
