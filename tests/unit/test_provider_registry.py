"""Unit tests for the curated provider jurisdiction table."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from src.cli.provider_coverage import measure_coverage
from src.lib.provider_registry import (
    DEFAULT_REGISTRY_PATH,
    EU_EEA,
    ProviderRegistry,
)

VALID_KINDS = {"commercial", "government", "nonprofit", "community"}
VALID_CONFIDENCE = {"high", "medium", "low"}


def _write(tmp_path: Path, providers: dict) -> Path:
    """Write a registry file and return its path."""
    path = tmp_path / "jurisdictions.yaml"
    path.write_text(yaml.safe_dump({"version": 1, "providers": providers}),
                    encoding="utf-8")
    return path


class TestLookup:
    """Resolving a scanned host to its operator."""

    def test_exact_match(self, tmp_path: Path) -> None:
        reg = ProviderRegistry(_write(tmp_path, {
            "googleapis.com": {"operator": "Google LLC", "jurisdiction": "US",
                               "kind": "commercial", "confidence": "high"},
        }))
        provider = reg.get("googleapis.com")

        assert provider is not None
        assert provider.operator == "Google LLC"
        assert provider.jurisdiction == "US"

    def test_subdomain_falls_back_to_registrable_domain(self, tmp_path: Path) -> None:
        """One row per company, not one per subdomain."""
        reg = ProviderRegistry(_write(tmp_path, {
            "cloudflare.com": {"operator": "Cloudflare, Inc.", "jurisdiction": "US",
                               "kind": "commercial", "confidence": "high"},
        }))

        assert reg.get("cdnjs.cloudflare.com").operator == "Cloudflare, Inc."

    def test_lookup_is_case_and_dot_insensitive(self, tmp_path: Path) -> None:
        reg = ProviderRegistry(_write(tmp_path, {
            "example.com": {"operator": "Example", "jurisdiction": "US",
                            "kind": "commercial", "confidence": "high"},
        }))

        assert reg.get("EXAMPLE.COM.") is not None

    def test_unknown_host_returns_none(self, tmp_path: Path) -> None:
        """Unclassified must stay unclassified rather than defaulting."""
        reg = ProviderRegistry(_write(tmp_path, {}))
        assert reg.get("mystery-host.example") is None

    def test_unrelated_suffix_does_not_match(self, tmp_path: Path) -> None:
        """notgoogleapis.com must not resolve to Google."""
        reg = ProviderRegistry(_write(tmp_path, {
            "googleapis.com": {"operator": "Google LLC", "jurisdiction": "US",
                               "kind": "commercial", "confidence": "high"},
        }))

        assert reg.get("notgoogleapis.com") is None

    def test_bare_tld_is_never_matched(self, tmp_path: Path) -> None:
        """Walking up the labels must stop before matching a bare TLD."""
        reg = ProviderRegistry(_write(tmp_path, {
            "com": {"operator": "Nonsense", "jurisdiction": "US",
                    "kind": "commercial", "confidence": "high"},
        }))

        assert reg.get("sub.anything.com") is None

    def test_empty_host_returns_none(self, tmp_path: Path) -> None:
        assert ProviderRegistry(_write(tmp_path, {})).get("") is None


class TestResilience:
    """A missing or broken table must not stop a scan."""

    def test_missing_file_yields_empty_registry(self, tmp_path: Path) -> None:
        assert len(ProviderRegistry(tmp_path / "absent.yaml")) == 0

    def test_malformed_yaml_yields_empty_registry(self, tmp_path: Path) -> None:
        path = tmp_path / "bad.yaml"
        path.write_text("providers: [unclosed", encoding="utf-8")
        assert len(ProviderRegistry(path)) == 0

    def test_non_mapping_entry_is_skipped(self, tmp_path: Path) -> None:
        path = tmp_path / "j.yaml"
        path.write_text(
            yaml.safe_dump({"version": 1, "providers": {"a.com": "not a mapping",
                                                        "b.com": {"operator": "B",
                                                                  "jurisdiction": "US",
                                                                  "kind": "commercial",
                                                                  "confidence": "high"}}}),
            encoding="utf-8",
        )
        reg = ProviderRegistry(path)
        assert len(reg) == 1 and reg.get("b.com") is not None


class TestClassification:
    """Derived flags used by the sovereignty reporting."""

    def test_eu_jurisdiction_is_recognised(self, tmp_path: Path) -> None:
        reg = ProviderRegistry(_write(tmp_path, {
            "plausible.io": {"operator": "Plausible Insights OU", "jurisdiction": "EE",
                             "kind": "commercial", "confidence": "high"},
        }))
        assert reg.get("plausible.io").is_eu_eea is True

    def test_non_eu_jurisdiction_is_not(self, tmp_path: Path) -> None:
        reg = ProviderRegistry(_write(tmp_path, {
            "google.com": {"operator": "Google LLC", "jurisdiction": "US",
                           "kind": "commercial", "confidence": "high"},
        }))
        assert reg.get("google.com").is_eu_eea is False

    def test_absent_jurisdiction_is_not_eu(self, tmp_path: Path) -> None:
        """A community project with no jurisdiction must not count as European."""
        reg = ProviderRegistry(_write(tmp_path, {
            "jsdelivr.net": {"operator": "jsDelivr", "jurisdiction": None,
                             "kind": "community", "confidence": "medium"},
        }))
        provider = reg.get("jsdelivr.net")
        assert provider.jurisdiction is None
        assert provider.is_eu_eea is False

    def test_public_bodies_are_flagged(self, tmp_path: Path) -> None:
        """Counting a public body as a third party overstates exposure."""
        reg = ProviderRegistry(_write(tmp_path, {
            "cqc.org.uk": {"operator": "Care Quality Commission", "jurisdiction": "GB",
                           "kind": "government", "confidence": "high"},
        }))
        assert reg.get("cqc.org.uk").is_government is True


class TestCuratedTable:
    """Guards on the table that actually ships."""

    @pytest.fixture
    def entries(self) -> dict:
        if not DEFAULT_REGISTRY_PATH.is_file():
            pytest.skip("provider table not present in this checkout")
        data = yaml.safe_load(DEFAULT_REGISTRY_PATH.read_text(encoding="utf-8"))
        return data["providers"]

    def test_every_entry_has_the_required_fields(self, entries: dict) -> None:
        for domain, entry in entries.items():
            assert entry.get("operator"), f"{domain} has no operator"
            assert entry.get("kind") in VALID_KINDS, f"{domain} has kind {entry.get('kind')!r}"
            assert entry.get("confidence") in VALID_CONFIDENCE, f"{domain} confidence"

    def test_jurisdictions_are_two_letter_codes_or_null(self, entries: dict) -> None:
        """A malformed code would silently fall out of the EU/EEA comparison."""
        for domain, entry in entries.items():
            jurisdiction = entry.get("jurisdiction")
            if jurisdiction is None:
                continue
            assert isinstance(jurisdiction, str), domain
            assert len(jurisdiction) == 2 and jurisdiction.isupper(), (
                f"{domain} has jurisdiction {jurisdiction!r}, expected an ISO-3166 alpha-2 code"
            )

    def test_uncertain_entries_are_marked_for_review(self, entries: dict) -> None:
        """Anything short of high confidence must announce itself.

        A wrong nationality claim in a sovereignty report is worse than an
        absent one, so medium-confidence rows carry needs_review and the
        coverage report counts what rests on them.
        """
        for domain, entry in entries.items():
            if entry.get("confidence") != "high":
                assert entry.get("needs_review") is True, (
                    f"{domain} is {entry.get('confidence')} confidence but not flagged"
                )

    def test_domains_are_lowercase_and_bare(self, entries: dict) -> None:
        for domain in entries:
            assert domain == domain.lower(), domain
            assert not domain.startswith(("http", "www.")), domain
            assert "/" not in domain, domain

    def test_eu_codes_used_are_real(self, entries: dict) -> None:
        """Catch a typo that would quietly drop a country out of the EU bucket."""
        european = {"GB", "CH", "UA", "RS", "TR", "MD", "AL", "MK", "BA", "ME", "XK"}
        for domain, entry in entries.items():
            j = entry.get("jurisdiction")
            if j and len(j) == 2 and j not in EU_EEA and j not in european:
                # Non-European codes are fine; this only asserts the value is
                # plausible rather than a mangled EU code.
                assert j.isalpha(), f"{domain} jurisdiction {j!r}"


class TestCoverageReport:
    """The report has to make the remaining curation finite and honest."""

    @staticmethod
    def _rows(pairs):
        return [
            {
                "source_domain": s, "target_domain": t,
                "relationship_type": "script_dependency",
                "target_category": "cdn",
            }
            for s, t in pairs
        ]

    def test_counts_classified_and_unclassified(self, tmp_path: Path) -> None:
        registry = ProviderRegistry(_write(tmp_path, {
            "known.com": {"operator": "Known", "jurisdiction": "US",
                          "kind": "commercial", "confidence": "high"},
        }))
        report = measure_coverage(
            self._rows([("a.gov.uk", "known.com"), ("b.gov.uk", "mystery.com")]),
            {"a.gov.uk": "UK", "b.gov.uk": "UK"},
            registry,
        )

        assert report["dependencies_total"] == 2
        assert report["dependencies_classified"] == 1
        assert report["coverage_percent"] == 50.0

    def test_ranks_unclassified_by_impact(self, tmp_path: Path) -> None:
        """Curation effort should go where it buys the most coverage."""
        registry = ProviderRegistry(_write(tmp_path, {}))
        report = measure_coverage(
            self._rows([("a.gov.uk", "big.com"), ("b.gov.uk", "big.com"),
                        ("a.gov.uk", "small.com")]),
            {"a.gov.uk": "UK", "b.gov.uk": "UK"},
            registry,
        )

        assert [e["host"] for e in report["top_unclassified"]] == ["big.com", "small.com"]

    def test_public_bodies_are_reported_separately(self, tmp_path: Path) -> None:
        registry = ProviderRegistry(_write(tmp_path, {
            "cqc.org.uk": {"operator": "CQC", "jurisdiction": "GB",
                           "kind": "government", "confidence": "high"},
        }))
        report = measure_coverage(
            self._rows([("a.gov.uk", "cqc.org.uk")]), {"a.gov.uk": "UK"}, registry,
        )

        assert report["dependencies_on_public_bodies"] == 1
        assert "GB" not in report["domains_by_jurisdiction"]

    def test_jurisdiction_counts_each_domain_once(self, tmp_path: Path) -> None:
        """A domain using two US providers is one US-dependent domain."""
        registry = ProviderRegistry(_write(tmp_path, {
            "one.com": {"operator": "One", "jurisdiction": "US",
                        "kind": "commercial", "confidence": "high"},
            "two.com": {"operator": "Two", "jurisdiction": "US",
                        "kind": "commercial", "confidence": "high"},
        }))
        report = measure_coverage(
            self._rows([("a.gov.uk", "one.com"), ("a.gov.uk", "two.com")]),
            {"a.gov.uk": "UK"}, registry,
        )

        assert report["domains_by_jurisdiction"]["US"] == 1
        assert report["scanned_domains"] == 1

    def test_needs_review_dependencies_are_counted(self, tmp_path: Path) -> None:
        registry = ProviderRegistry(_write(tmp_path, {
            "shaky.com": {"operator": "Shaky", "jurisdiction": "US", "kind": "commercial",
                          "confidence": "medium", "needs_review": True},
        }))
        report = measure_coverage(
            self._rows([("a.gov.uk", "shaky.com")]), {"a.gov.uk": "UK"}, registry,
        )

        assert report["dependencies_needing_review"] == 1

    def test_retired_edges_are_excluded(self, tmp_path: Path) -> None:
        registry = ProviderRegistry(_write(tmp_path, {
            "known.com": {"operator": "Known", "jurisdiction": "US",
                          "kind": "commercial", "confidence": "high"},
        }))
        rows = self._rows([("a.gov.uk", "known.com")])
        rows[0]["active"] = False

        report = measure_coverage(rows, {"a.gov.uk": "UK"}, registry)

        assert report["dependencies_total"] == 0
