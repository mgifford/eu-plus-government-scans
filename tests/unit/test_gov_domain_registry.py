"""Tests for the shared government-domain registry."""

from __future__ import annotations

import json
from pathlib import Path

from src.lib.gov_domain_registry import GovernmentDomainRegistry


def _write_toon(path: Path, domains: list[str]) -> None:
    data = {
        "version": "0.1-seed",
        "country": path.stem.title(),
        "domain_count": len(domains),
        "page_count": 0,
        "domains": [
            {"canonical_domain": d, "subnational": [], "source_tabs": [], "pages": []}
            for d in domains
        ],
    }
    path.write_text(json.dumps(data), encoding="utf-8")


def test_loads_domains_from_toon_dir(tmp_path: Path):
    _write_toon(tmp_path / "spain.toon", ["gob.es", "gencat.cat"])
    _write_toon(tmp_path / "canada.toon", ["canada.ca"])

    registry = GovernmentDomainRegistry(tmp_path)

    assert len(registry) == 3
    assert registry.is_government_domain("gob.es")
    assert registry.is_government_domain("canada.ca")


def test_is_government_domain_case_insensitive(tmp_path: Path):
    _write_toon(tmp_path / "spain.toon", ["gob.es"])
    registry = GovernmentDomainRegistry(tmp_path)
    assert registry.is_government_domain("GOB.ES")


def test_unknown_domain_is_not_government(tmp_path: Path):
    _write_toon(tmp_path / "spain.toon", ["gob.es"])
    registry = GovernmentDomainRegistry(tmp_path)
    assert not registry.is_government_domain("facebook.com")


def test_country_for_domain(tmp_path: Path):
    _write_toon(tmp_path / "spain.toon", ["gob.es"])
    _write_toon(tmp_path / "canada.toon", ["canada.ca"])
    registry = GovernmentDomainRegistry(tmp_path)

    assert registry.country_for_domain("gob.es") == "SPAIN"
    assert registry.country_for_domain("canada.ca") == "CANADA"


def test_country_for_domain_unknown_returns_none(tmp_path: Path):
    _write_toon(tmp_path / "spain.toon", ["gob.es"])
    registry = GovernmentDomainRegistry(tmp_path)
    assert registry.country_for_domain("facebook.com") is None


def test_country_filename_with_hyphens_maps_to_underscored_code(tmp_path: Path):
    _write_toon(tmp_path / "united-kingdom-uk.toon", ["gov.uk"])
    registry = GovernmentDomainRegistry(tmp_path)
    assert registry.country_for_domain("gov.uk") == "UNITED_KINGDOM_UK"


def test_all_domains_returns_full_mapping(tmp_path: Path):
    _write_toon(tmp_path / "spain.toon", ["gob.es", "gencat.cat"])
    _write_toon(tmp_path / "canada.toon", ["canada.ca"])
    registry = GovernmentDomainRegistry(tmp_path)

    assert registry.all_domains() == {
        "gob.es": "SPAIN",
        "gencat.cat": "SPAIN",
        "canada.ca": "CANADA",
    }


def test_all_domains_returns_copy_not_internal_reference(tmp_path: Path):
    _write_toon(tmp_path / "spain.toon", ["gob.es"])
    registry = GovernmentDomainRegistry(tmp_path)
    snapshot = registry.all_domains()
    snapshot["injected.com"] = "NOWHERE"
    assert not registry.is_government_domain("injected.com")


def test_missing_toon_dir_yields_empty_registry(tmp_path: Path):
    registry = GovernmentDomainRegistry(tmp_path / "does-not-exist")
    assert len(registry) == 0
    assert not registry.is_government_domain("gob.es")


def test_malformed_toon_file_is_skipped(tmp_path: Path):
    (tmp_path / "broken.toon").write_text("not valid json", encoding="utf-8")
    _write_toon(tmp_path / "spain.toon", ["gob.es"])
    registry = GovernmentDomainRegistry(tmp_path)
    assert registry.is_government_domain("gob.es")
    assert len(registry) == 1
