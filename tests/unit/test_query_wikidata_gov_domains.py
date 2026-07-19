"""Tests for the Wikidata government-domain query script.

These tests exercise the pure logic (label filtering, hostname
normalization, deduplication, dry-run/report behavior) using recorded-style
fixture data rather than live SPARQL calls -- run_sparql() itself is not
tested here since it's a thin network wrapper.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.cli.query_wikidata_gov_domains import (
    _hostname_from_url,
    _looks_like_government,
    _looks_like_non_government,
    build_report,
    load_existing_domains,
    parse_args,
    save_report,
)


# ---------------------------------------------------------------------------
# label filtering
# ---------------------------------------------------------------------------

def test_looks_like_government_matches_expected_patterns():
    assert _looks_like_government("Government of Catalonia")
    assert _looks_like_government("Parliament of Andalusia")
    assert _looks_like_government("President of the Generalitat of Catalonia")
    assert _looks_like_government("Regional Government of Castilla-La Mancha")


def test_looks_like_government_rejects_unrelated_labels():
    assert not _looks_like_government("Doñana National Park")
    assert not _looks_like_government("High Court of Justice of Galicia")


def test_looks_like_government_rejects_party_leadership_false_positive():
    """Caught during manual review of Spain's results (2026-07-19): party
    leadership titles can match a naive 'President of X' pattern."""
    assert not _looks_like_government(
        "President of Democratic Convergence of Catalonia"
    )
    assert not _looks_like_government(
        "President of the Catalan European Democratic Party"
    )


def test_looks_like_non_government_catches_diplomatic_missions():
    assert _looks_like_non_government("Apostolic Nunciature to Spain")
    assert _looks_like_non_government("Embassy of Argentina in Spain")


def test_looks_like_non_government_does_not_reject_real_ministries():
    assert not _looks_like_non_government("Ministry of Justice of Spain")


# ---------------------------------------------------------------------------
# hostname normalization
# ---------------------------------------------------------------------------

def test_hostname_from_url_strips_scheme_and_path():
    assert _hostname_from_url("https://web.gencat.cat/ca/inici") == "web.gencat.cat"


def test_hostname_from_url_strips_www():
    assert _hostname_from_url("http://www.govern.cat") == "govern.cat"


def test_hostname_from_url_handles_bare_domain():
    assert _hostname_from_url("consejo-estado.es") == "consejo-estado.es"


# ---------------------------------------------------------------------------
# existing-domain loading
# ---------------------------------------------------------------------------

def test_load_existing_domains_from_toon(tmp_path: Path):
    toon_path = tmp_path / "spain.toon"
    toon_path.write_text(
        json.dumps(
            {
                "domains": [
                    {"canonical_domain": "web.gencat.cat"},
                    {"canonical_domain": "012.comunidad.madrid"},
                ]
            }
        ),
        encoding="utf-8",
    )
    result = load_existing_domains(toon_path)
    assert result == {"web.gencat.cat", "012.comunidad.madrid"}


def test_load_existing_domains_missing_file_returns_empty_set(tmp_path: Path):
    result = load_existing_domains(tmp_path / "does-not-exist.toon")
    assert result == set()


# ---------------------------------------------------------------------------
# build_report (mocks the two SPARQL calls)
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_national_results(monkeypatch):
    """Patch query_national_domains to return fixture data instead of a live call."""
    def fake(country_qid):
        return [
            {
                "label": "Council of State",
                "website": "https://www.consejo-estado.es/",
                "dissolved": None,
            },
            {
                "label": "Ministry of Labour of Spain",
                "website": "http://www.mitramiss.gob.es/",
                "dissolved": None,
            },
        ]

    monkeypatch.setattr(
        "src.cli.query_wikidata_gov_domains.query_national_domains", fake
    )


@pytest.fixture
def mock_regional_results(monkeypatch):
    """Patch query_regional_domains to return fixture data instead of a live call."""
    def fake(country_qid):
        return {
            "Catalonia": {
                "iso_code": "ES-CT",
                "place_website": "https://web.gencat.cat/",
                "institutions": [
                    {
                        "label": "Government of Catalonia",
                        "website": "http://www.govern.cat",
                        "dissolved": None,
                    },
                ],
            }
        }

    monkeypatch.setattr(
        "src.cli.query_wikidata_gov_domains.query_regional_domains", fake
    )


def test_build_report_flags_new_vs_already_seeded(
    mock_national_results, mock_regional_results
):
    existing = {"web.gencat.cat", "mitramiss.gob.es"}
    report = build_report("Spain", "Q29", existing)

    national_by_host = {e["hostname"]: e for e in report["national"]}
    assert national_by_host["consejo-estado.es"]["already_seeded"] is False
    assert national_by_host["mitramiss.gob.es"]["already_seeded"] is True

    catalonia = report["regional"]["Catalonia"]
    assert catalonia["place_website_new"] is False  # web.gencat.cat is seeded
    assert catalonia["institutions"][0]["hostname"] == "govern.cat"
    assert catalonia["institutions"][0]["already_seeded"] is False


def test_build_report_includes_review_note(
    mock_national_results, mock_regional_results
):
    report = build_report("Spain", "Q29", set())
    assert "not merged" in report["note"].lower()


# ---------------------------------------------------------------------------
# save_report
# ---------------------------------------------------------------------------

def test_save_report_dry_run_does_not_write_file(tmp_path: Path):
    report = {"country": "Spain", "national": [], "regional": {}}
    path = save_report(report, tmp_path, dry_run=True)
    assert not path.exists()


def test_save_report_writes_expected_filename(tmp_path: Path):
    report = {"country": "Republic of Cyprus", "national": [], "regional": {}}
    path = save_report(report, tmp_path, dry_run=False)
    assert path.name == "wikidata_republic_of_cyprus.json"
    assert path.exists()
    with path.open() as f:
        saved = json.load(f)
    assert saved["country"] == "Republic of Cyprus"


# ---------------------------------------------------------------------------
# CLI argument parsing
# ---------------------------------------------------------------------------

def test_parse_args_requires_country():
    with pytest.raises(SystemExit):
        parse_args([])


def test_parse_args_defaults():
    args = parse_args(["--country", "Spain"])
    assert args.country == "Spain"
    assert args.output_dir == "data/imports"
    assert args.dry_run is False


def test_parse_args_dry_run_flag():
    args = parse_args(["--country", "Spain", "--dry-run"])
    assert args.dry_run is True
