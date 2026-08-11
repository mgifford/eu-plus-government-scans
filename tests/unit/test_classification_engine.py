"""Unit tests for the classification engine and report generator."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path


from src.services.classification_engine import (
    ClassificationEngine,
    ClassificationResult,
)
from src.services.classification_report_generator import ClassificationReportGenerator


class TestCountryRule:
    """Tests for the CountryRule model."""

    def test_country_rule_from_yaml(self) -> None:
        """Test loading a CountryRule from YAML file."""
        engine = ClassificationEngine()
        rule = engine.get_country_rule("CA")

        assert rule is not None
        assert rule.country_code == "CA"
        assert rule.rule_version == 1
        assert "federal" in rule.administrative_context.lower()

    def test_country_rule_with_exceptions(self) -> None:
        """Test loading a CountryRule with exceptions."""
        engine = ClassificationEngine()
        rule = engine.get_country_rule("CA")

        assert rule is not None
        assert "exclude" in rule.exceptions
        exclude_exceptions = rule.exceptions["exclude"]
        # Check that there's at least one exclude exception
        assert len(exclude_exceptions) > 0


class TestClassificationResult:
    """Tests for the ClassificationResult model."""

    def test_classification_result_creation(self) -> None:
        """Test creating a ClassificationResult."""
        result = ClassificationResult(
            domain="example.gov.ca",
            country="CA",
            central_administration=True,
            classification_status="confirmed",
            classification_basis=["authoritative_registry", "country_rule"],
            classification_rule="CA-INCLUDE-MINISTRY",
            review_required=False,
            applied_rules=["CA-INCLUDE-MINISTRY"],
            conflicts=[],
        )

        assert result.central_administration is True
        assert result.classification_status == "confirmed"
        assert len(result.classification_basis) == 2
        assert len(result.applied_rules) == 1

    def test_classification_result_with_conflicts(self) -> None:
        """Test creating a ClassificationResult with conflicts."""
        conflicts = [
            {"source": "Wikipedia", "assertion": "Central government", "url": "https://en.wikipedia.org/wiki/Example"}
        ]

        result = ClassificationResult(
            domain="example.gov.xx",
            country="XX",
            central_administration=None,
            classification_status="disputed",
            classification_basis=["network_signal"],
            classification_rule=None,
            review_required=True,
            applied_rules=[],
            conflicts=conflicts,
        )

        assert result.central_administration is None
        assert result.classification_status == "disputed"
        assert len(result.conflicts) == 1

    def test_classification_result_to_dict(self) -> None:
        """Test converting ClassificationResult to dictionary."""
        result = ClassificationResult(
            domain="example.gov.ca",
            country="CA",
            central_administration=True,
            classification_status="confirmed",
            classification_basis=["authoritative_registry"],
            classification_rule="CA-INCLUDE-MINISTRY",
            review_required=False,
            applied_rules=["CA-INCLUDE-MINISTRY"],
            conflicts=[],
        )

        result_dict = result.to_dict()
        assert result_dict["domain"] == "example.gov.ca"
        assert result_dict["central_administration"] is True
        assert result_dict["classification_status"] == "confirmed"


class TestClassificationEngine:
    """Tests for the ClassificationEngine."""

    def test_engine_initialization(self) -> None:
        """Test initializing the ClassificationEngine."""
        engine = ClassificationEngine()
        assert engine.classification_dir.exists()
        assert engine.global_baseline is not None
        assert len(engine.country_rules) >= 5

    def test_load_country_rules(self) -> None:
        """Test loading country rules."""
        engine = ClassificationEngine()
        # Should load at least the 5 countries we created
        assert len(engine.country_rules) >= 5
        assert "CA" in engine.country_rules
        assert "FR" in engine.country_rules
        assert "DE" in engine.country_rules
        assert "ES" in engine.country_rules
        assert "GB" in engine.country_rules

    def test_load_country_rule(self) -> None:
        """Test loading a specific country rule."""
        engine = ClassificationEngine()
        rule = engine.get_country_rule("CA")

        assert rule is not None
        assert rule.country_code == "CA"
        assert rule.rule_version == 1
        assert "ministry" in rule.include.get("organization_types", [])

    def test_classify_domain_ministry(self) -> None:
        """Test classifying a ministry domain."""
        engine = ClassificationEngine()

        result = engine.classify_domain(
            domain="sct-ftb.canada.ca",
            country_code="CA",
            organization_type="ministry",
            government_level="national",
        )

        # Ministry should be classified as central administration
        assert result.central_administration is True
        assert result.classification_status in ["confirmed", "probable"]
        assert len(result.applied_rules) > 0

    def test_classify_domain_crown_corporation(self) -> None:
        """Test classifying a crown corporation domain."""
        engine = ClassificationEngine()

        result = engine.classify_domain(
            domain="cbc.ca",
            country_code="CA",
            organization_type="public_broadcaster",
            government_level="national",
        )

        # Crown corporation should be classified as non-central
        assert result.central_administration is False
        assert "organization_type_excluded" in result.applied_rules

    def test_classify_domain_explicit_exception(self) -> None:
        """Test classifying a domain with an explicit exception."""
        engine = ClassificationEngine()

        # www.parl.ca is in the exclude exceptions list for Canada
        result = engine.classify_domain(
            domain="www.parl.ca",
            country_code="CA",
            organization_type="parliament",
            government_level="national",
        )

        # Should be explicitly excluded
        assert result.central_administration is False
        assert "explicit_exclude_exception" in result.applied_rules

    def test_classify_domain_uk_executive_agency(self) -> None:
        """Test classifying a UK executive agency domain."""
        engine = ClassificationEngine()

        result = engine.classify_domain(
            domain="metoffice.gov.uk",
            country_code="GB",
            organization_type="executive_agency",
            government_level="national",
        )

        # Executive agency is included in UK rules, so should be central
        assert result.central_administration is True
        assert "organization_type_included" in result.applied_rules

    def test_classify_domain_uk_health_service(self) -> None:
        """Test classifying a UK health service domain."""
        engine = ClassificationEngine()

        result = engine.classify_domain(
            domain="nhs.uk",
            country_code="GB",
            organization_type="public_health",
            government_level="national",
        )

        # public_health is not in either included or excluded list for UK
        # So it should remain unresolved
        assert result.central_administration is None
        assert result.classification_status == "candidate"

    def test_deterministic_output(self) -> None:
        """Test that classification is deterministic."""
        engine = ClassificationEngine()

        result1 = engine.classify_domain(
            domain="sct-ftb.canada.ca",
            country_code="CA",
            organization_type="ministry",
            government_level="national",
        )
        result2 = engine.classify_domain(
            domain="sct-ftb.canada.ca",
            country_code="CA",
            organization_type="ministry",
            government_level="national",
        )

        # Results should be identical
        assert result1.central_administration == result2.central_administration
        assert result1.classification_status == result2.classification_status
        assert result1.applied_rules == result2.applied_rules


class TestClassificationReportGenerator:
    """Tests for the ClassificationReportGenerator."""

    def test_generator_initialization(self) -> None:
        """Test initializing the ClassificationReportGenerator."""
        engine = ClassificationEngine()
        generator = ClassificationReportGenerator(engine)
        assert generator.engine is not None

    def test_generate_country_report(self) -> None:
        """Test generating a country report."""
        engine = ClassificationEngine()
        generator = ClassificationReportGenerator(engine)

        report = generator.generate_country_report("CA")

        assert report["country_code"] == "CA"
        assert "generated_at" in report
        assert "statistics" in report
        assert "domains" in report

    def test_generate_global_report(self) -> None:
        """Test generating a global report."""
        engine = ClassificationEngine()
        generator = ClassificationReportGenerator(engine)

        report = generator.generate_global_report()

        assert "generated_at" in report
        assert "statistics" in report
        assert "countries" in report
        assert report["statistics"]["total_countries"] >= 5

    def test_save_country_report(self) -> None:
        """Test saving a country report."""
        engine = ClassificationEngine()
        generator = ClassificationReportGenerator(engine)

        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)
            generator.save_country_report("CA", output_dir)

            # Check that files were created
            json_path = output_dir / "ca.json"
            md_path = output_dir / "ca.md"

            assert json_path.exists()
            assert md_path.exists()

            # Verify JSON content
            with open(json_path) as f:
                report = json.load(f)
                assert report["country_code"] == "CA"

            # Verify Markdown content
            with open(md_path) as f:
                content = f.read()
                assert "# Classification Report: CA" in content

    def test_save_global_report(self) -> None:
        """Test saving the global report."""
        engine = ClassificationEngine()
        generator = ClassificationReportGenerator(engine)

        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)
            generator.save_global_report(output_dir)

            # Check that files were created
            json_path = output_dir / "global.json"
            md_path = output_dir / "global.md"

            assert json_path.exists()
            assert md_path.exists()

            # Verify JSON content
            with open(json_path) as f:
                report = json.load(f)
                assert "statistics" in report
                assert "countries" in report


class TestClassificationPrinciples:
    """Tests for the classification principles."""

    def test_institutional_evidence_required(self) -> None:
        """Test that institutional evidence is required for central-administration status."""
        engine = ClassificationEngine()

        # Domain without institutional evidence
        result = engine.classify_domain(
            domain="example.gov.xx",
            country_code="XX",
            organization_type="unknown",
            government_level="unknown",
        )

        # Should not be classified as central administration
        assert result.central_administration is not True
        # With unknown government level, it should be classified as non-national
        assert result.classification_status in ["candidate", "probable", "unknown"]

    def test_country_rules_override_global(self) -> None:
        """Test that country-specific rules override global baseline."""
        engine = ClassificationEngine()

        # Canadian ministry
        result_ca = engine.classify_domain(
            domain="canada.ca",
            country_code="CA",
            organization_type="ministry",
            government_level="national",
        )

        # Should be classified using country-specific rules
        assert result_ca.central_administration is True
        assert "organization_type_included" in result_ca.applied_rules

    def test_unresolved_preferred_over_uncertainty(self) -> None:
        """Test that unresolved classifications are preferred over uncertainty."""
        engine = ClassificationEngine()

        # Domain with uncertain classification
        result = engine.classify_domain(
            domain="example.gov.xx",
            country_code="XX",
            organization_type="unknown",
            government_level="national",
        )

        # Should be unresolved (null) rather than uncertain (True/False)
        assert result.central_administration is None
        assert result.classification_status in ["candidate", "unknown"]

    def test_deterministic_output_multiple_runs(self) -> None:
        """Test that classification is deterministic across multiple runs."""
        engine = ClassificationEngine()

        results = []
        for _ in range(5):
            result = engine.classify_domain(
                domain="example.gov.xx",
                country_code="XX",
                organization_type="ministry",
                government_level="national",
            )
            results.append(result)

        # All results should be identical
        for result in results[1:]:
            assert result.central_administration == results[0].central_administration
            assert result.classification_status == results[0].classification_status
            assert result.applied_rules == results[0].applied_rules
