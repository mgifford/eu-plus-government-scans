"""Deterministic classification rule engine for government domains.

Implements a rule-based classifier that loads global baseline rules and
country-specific governance models to determine central administration status
and other classification fields.

Classification Principle:
    Central-administration status must be based on institutional evidence,
    not graph patterns, TLD matching, or Software Heritage presence.
"""

from __future__ import annotations

import fnmatch
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

import yaml


@dataclass
class CountryRule:
    """Country-specific governance classification rule."""

    country_code: str
    country_name: str
    rule_version: int
    last_reviewed: str
    administrative_context: str
    central_administration_definition: str
    include: Dict[str, List[str]]
    exclude: Dict[str, List[str]]
    domain_patterns: Dict[str, List[str]]
    exceptions: Dict[str, List[Dict[str, str]]]
    authoritative_sources: List[Dict[str, str]]
    known_ambiguities: List[str]
    classification_notes: str = ""

    @classmethod
    def from_yaml(cls, path: Path) -> CountryRule:
        """Load a country rule from a YAML file."""
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        return cls(
            country_code=data["country"]["code"],
            country_name=data["country"]["name"],
            rule_version=data["rule_version"],
            last_reviewed=data["last_reviewed"],
            administrative_context=data["administrative_context"],
            central_administration_definition=data["central_administration_definition"],
            include=data["include"],
            exclude=data["exclude"],
            domain_patterns=data["domain_patterns"],
            exceptions=data["exceptions"],
            authoritative_sources=data["authoritative_sources"],
            known_ambiguities=data["known_ambiguities"],
            classification_notes=data.get("classification_notes", ""),
        )


@dataclass
class ClassificationResult:
    """Result of domain classification."""

    domain: str
    country: Optional[str]
    central_administration: Optional[bool]
    classification_status: str
    classification_basis: List[str]
    classification_rule: Optional[str]
    review_required: bool
    conflicts: List[Dict[str, Any]] = field(default_factory=list)
    applied_rules: List[str] = field(default_factory=list)
    sources: List[Dict[str, Any]] = field(default_factory=list)
    government_level: Optional[str] = None
    organization_type: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result = {
            "domain": self.domain,
            "country": self.country,
            "central_administration": self.central_administration,
            "classification_status": self.classification_status,
            "classification_basis": self.classification_basis,
            "classification_rule": self.classification_rule,
            "review_required": self.review_required,
            "conflicts": self.conflicts,
            "applied_rules": self.applied_rules,
            "sources": self.sources,
        }
        if self.government_level:
            result["government_level"] = self.government_level
        if self.organization_type:
            result["organization_type"] = self.organization_type
        return result


class ClassificationEngine:
    """Deterministic classifier for government domains.

    Loads global baseline rules and country-specific governance models
    to classify domains according to institutional evidence.
    """

    def __init__(
        self,
        classification_dir: Path = Path("data/classification"),
    ):
        """Initialize the classification engine.

        Args:
            classification_dir: Path to the classification directory
                containing global-baseline.yml and countries/ subdirectory.
        """
        self.classification_dir = classification_dir
        self.global_baseline: Optional[Dict[str, Any]] = None
        self.country_rules: Dict[str, CountryRule] = {}
        self._load_rules()

    def _load_rules(self) -> None:
        """Load all classification rules from disk."""
        baseline_path = self.classification_dir / "global-baseline.yml"
        if baseline_path.exists():
            with open(baseline_path, "r", encoding="utf-8") as f:
                self.global_baseline = yaml.safe_load(f)

        countries_dir = self.classification_dir / "countries"
        if countries_dir.exists():
            for yaml_file in countries_dir.glob("*.yml"):
                try:
                    rule = CountryRule.from_yaml(yaml_file)
                    self.country_rules[rule.country_code] = rule
                except Exception as e:
                    print(f"Warning: Failed to load rule {yaml_file}: {e}")

    def get_country_rule(self, country_code: str) -> Optional[CountryRule]:
        """Get the country-specific rule for a given country code."""
        return self.country_rules.get(country_code.upper())

    def classify_domain(
        self,
        domain: str,
        country_code: Optional[str] = None,
        organization_type: Optional[str] = None,
        government_level: Optional[str] = None,
        existing_classification: Optional[Dict[str, Any]] = None,
        evidence_sources: Optional[List[Dict[str, Any]]] = None,
    ) -> ClassificationResult:
        """Classify a domain according to the rule engine.

        Args:
            domain: The domain to classify.
            country_code: ISO-3166-1 alpha-2 country code.
            organization_type: Detected organization type.
            government_level: Detected government level.
            existing_classification: Existing classification data if available.
            evidence_sources: Additional evidence sources.

        Returns:
            ClassificationResult with all classification details.
        """
        # Initialize result
        result = ClassificationResult(
            domain=domain,
            country=country_code,
            central_administration=None,
            classification_status="candidate",
            classification_basis=[],
            classification_rule=None,
            review_required=True,
        )

        # Get country rule (or use global baseline)
        country_rule = self.get_country_rule(country_code) if country_code else None
        rule_source = country_rule or self.global_baseline

        if not rule_source:
            result.classification_status = "candidate"
            result.classification_basis.append("No classification rules available")
            return result

        # Step 1: Apply explicit domain exceptions first
        if country_rule:
            self._apply_explicit_exceptions(result, country_rule)

        # Step 2: Apply organization type inclusion/exclusion rules
        if organization_type:
            self._apply_organization_type_rules(
                result, country_rule, organization_type
            )

        # Step 3: Apply authoritative source assertions
        if evidence_sources:
            self._apply_authoritative_assertions(result, country_rule, evidence_sources)

        # Step 4: Apply domain pattern matching (supporting evidence only)
        if country_rule:
            self._apply_domain_patterns(result, country_rule)

        # Step 5: Apply government level rules
        if government_level:
            self._apply_government_level_rules(
                result, country_rule, government_level
            )

        # Step 6: Check for conflicts
        if result.conflicts:
            result.classification_status = "disputed"
            result.review_required = True

        # Step 7: Set review requirements based on classification status
        if result.classification_status == "confirmed":
            result.review_required = True  # Confirmed requires maintainer approval
        elif result.classification_status == "disputed":
            result.review_required = True

        return result

    def _apply_explicit_exceptions(
        self, result: ClassificationResult, country_rule: CountryRule
    ) -> None:
        """Apply explicit domain exceptions from the country rule."""
        include_exceptions = country_rule.exceptions.get("include", [])
        exclude_exceptions = country_rule.exceptions.get("exclude", [])

        for exc in include_exceptions:
            if exc["domain"] == result.domain:
                result.central_administration = True
                result.classification_status = "confirmed"
                result.classification_basis.append(
                    f"Explicit include exception: {exc.get('reason', 'No reason provided')}"
                )
                result.classification_rule = f"{country_rule.country_code}-EXPLICIT-INCLUDE"
                result.review_required = False
                if "source" in exc:
                    result.sources.append(
                        {"name": "Explicit Exception", "url": exc["source"]}
                    )
                result.applied_rules.append("explicit_include_exception")
                return

        for exc in exclude_exceptions:
            if exc["domain"] == result.domain:
                result.central_administration = False
                result.classification_status = "confirmed"
                result.classification_basis.append(
                    f"Explicit exclude exception: {exc.get('reason', 'No reason provided')}"
                )
                result.classification_rule = f"{country_rule.country_code}-EXPLICIT-EXCLUDE"
                result.review_required = False
                if "source" in exc:
                    result.sources.append(
                        {"name": "Explicit Exception", "url": exc["source"]}
                    )
                result.applied_rules.append("explicit_exclude_exception")
                return

    def _apply_organization_type_rules(
        self,
        result: ClassificationResult,
        country_rule: Optional[CountryRule],
        organization_type: str,
    ) -> None:
        """Apply organization type inclusion/exclusion rules."""
        if result.central_administration is not None:
            return  # Already classified by explicit exception

        if country_rule:
            # Use country-specific rule
            included_types = country_rule.include.get("organization_types", [])
            excluded_types = country_rule.exclude.get("organization_types", [])
        elif self.global_baseline:
            # Use global baseline
            included_types = self.global_baseline.get("include", {}).get("organization_types", [])
            excluded_types = self.global_baseline.get("exclude", {}).get("organization_types", [])
        else:
            return

        if organization_type in included_types:
            result.central_administration = True
            result.classification_status = "probable"
            result.classification_basis.append(
                f"Organization type '{organization_type}' is included in classification rules"
            )
            result.organization_type = organization_type
            result.review_required = True
            result.applied_rules.append("organization_type_included")

        elif organization_type in excluded_types:
            result.central_administration = False
            result.classification_status = "probable"
            result.classification_basis.append(
                f"Organization type '{organization_type}' is excluded from classification rules"
            )
            result.organization_type = organization_type
            result.review_required = True
            result.applied_rules.append("organization_type_excluded")

    def _apply_authoritative_assertions(
        self,
        result: ClassificationResult,
        country_rule: Optional[CountryRule],
        evidence_sources: List[Dict[str, Any]],
    ) -> None:
        """Apply authoritative source assertions."""
        if result.central_administration is not None and result.classification_status == "confirmed":
            return  # Already classified by explicit exception

        for source in evidence_sources:
            if source.get("assertion") == "central":
                result.central_administration = True
                result.classification_status = "probable"
                result.classification_basis.append(
                    f"Authoritative assertion: {source.get('name', 'Unknown source')}"
                )
                result.sources.append(source)
                result.review_required = True
                result.applied_rules.append("authoritative_assertion")
            elif source.get("assertion") == "non-central":
                result.central_administration = False
                result.classification_status = "probable"
                result.classification_basis.append(
                    f"Authoritative assertion (non-central): {source.get('name', 'Unknown source')}"
                )
                result.sources.append(source)
                result.review_required = True
                result.applied_rules.append("authoritative_assertion_non_central")

    def _apply_domain_patterns(
        self, result: ClassificationResult, country_rule: CountryRule
    ) -> None:
        """Apply domain pattern matching as supporting evidence only."""
        if result.central_administration is not None:
            return  # Already classified

        high_confidence_patterns = country_rule.domain_patterns.get("high_confidence", [])
        supporting_patterns = country_rule.domain_patterns.get("supporting", [])

        for pattern in high_confidence_patterns:
            if fnmatch.fnmatch(result.domain, pattern):
                result.classification_basis.append(
                    f"Domain matches high-confidence pattern: {pattern}"
                )
                result.applied_rules.append("high_confidence_pattern")
                break

        for pattern in supporting_patterns:
            if fnmatch.fnmatch(result.domain, pattern):
                result.classification_basis.append(
                    f"Domain matches supporting pattern: {pattern}"
                )
                result.applied_rules.append("supporting_pattern")
                break

    def _apply_government_level_rules(
        self,
        result: ClassificationResult,
        country_rule: Optional[CountryRule],
        government_level: str,
    ) -> None:
        """Apply government level rules."""
        if result.central_administration is not None:
            return  # Already classified

        # National level is a prerequisite for central administration
        if government_level != "national":
            result.central_administration = False
            result.classification_status = "probable"
            result.classification_basis.append(
                f"Government level '{government_level}' is not national"
            )
            result.government_level = government_level
            result.review_required = True
            result.applied_rules.append("non_national_level")
        else:
            result.government_level = government_level

    def generate_review_report(
        self, domains: List[Dict[str, Any]], country_code: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate a review report for a set of domains.

        Args:
            domains: List of domain records to review.
            country_code: Optional country code to filter by.

        Returns:
            Review report dictionary.
        """
        report = {
            "country_code": country_code or "GLOBAL",
            "total_domains": len(domains),
            "unclassified": [],
            "conflicting": [],
            "pattern_only": [],
            "software_heritage_only": [],
            "high_link_unknown": [],
            "explicit_exceptions": [],
            "not_reviewed": [],
        }

        for domain in domains:
            # Check if classification is missing or needs review
            if domain.get("central_administration") is None:
                report["unclassified"].append(domain.get("domain", "unknown"))
            elif domain.get("conflicts"):
                report["conflicting"].append(domain.get("domain", "unknown"))
            elif "supporting_pattern" in domain.get("applied_rules", []):
                report["pattern_only"].append(domain.get("domain", "unknown"))

        return report
