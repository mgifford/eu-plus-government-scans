"""Service for building canonical domain records."""

from __future__ import annotations

import tldextract
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime, timezone

from src.models.domain_model import (
    CanonicalDomain,
    SourceEvidence,
    GovernmentLevel,
    OrganizationType,
    ClassificationStatus,
    ClassificationBasis,
)


class CanonicalDomainBuilder:
    """Builds canonical domain records from various sources."""

    def __init__(self, domains_dir: Optional[Path] = None):
        self.domains_dir = domains_dir
        self.tld_extract = tldextract.TLDExtract()

    def build_canonical_domain(
        self,
        domain: str,
        target_category: str = "unknown_external",
        curation_source_url: Optional[str] = None,
        institutional_source_url: Optional[str] = None,
        structured_source_url: Optional[str] = None,
        country_code: Optional[str] = None,
        organization_name: Optional[str] = None,
        government_level: Optional[str] = None,
        organization_type: Optional[str] = None,
        classification_status: str = "unknown",
        confidence_score: Optional[int] = None,
        from_network: bool = False,
    ) -> Optional[CanonicalDomain]:
        """
        Build a canonical domain record following precedence rules:

        1. Authoritative government registry
        2. Existing curated source
        3. Official institutional source
        4. High-quality structured source (Wikidata, etc.)
        5. Software Heritage classification with preserved confidence
        6. Domain-pattern evidence
        7. Network structure only as a weak discovery signal
        """
        # Normalize domain
        domain = domain.lower().strip()

        # Determine registrable domain
        extracted = self.tld_extract(domain)
        if extracted.registered_domain:
            registrable_domain = extracted.registered_domain
        else:
            registrable_domain = domain

        # Determine country
        country = self._determine_country(
            registrable_domain, country_code, target_category
        )

        # Create unique ID
        id = f"{country or 'unknown'}-{registrable_domain.replace('.', '-')}"

        # Build sources list
        sources = self._build_sources(
            country or country_code,
            curation_source_url,
            institutional_source_url,
            structured_source_url,
            target_category,
            confidence_score,
            from_network,
        )

        # Determine government level and organization type based on precedence
        gov_level, org_type = self._determine_classification(
            country,
            government_level,
            organization_type,
            target_category,
            from_network,
            sources,
        )

        # Determine classification status and basis
        if classification_status == "unknown":
            classification_status = self._determine_classification_status(sources)

        if classification_status == "unknown":
            classification_basis = ClassificationBasis.UNKNOWN
        elif from_network:
            classification_basis = ClassificationBasis.NETWORK_SIGNAL
        elif confidence_score is not None and confidence_score >= 7:
            classification_basis = ClassificationBasis.SOFTWARE_HERITAGE
        else:
            classification_basis = ClassificationBasis.DOMAIN_PATTERN

        # Calculate graph metrics
        in_degree = 0
        out_degree = 0
        weighted_in_degree = 0
        weighted_out_degree = 0
        unique_source_organizations = 0
        unique_source_pages = 0

        return CanonicalDomain(
            id=id,
            domain=registrable_domain,
            country=country,
            organization_name=organization_name,
            government_level=gov_level,
            organization_type=org_type,
            classification_status=classification_status,
            classification_basis=classification_basis,
            sources=sources,
            in_degree=in_degree,
            out_degree=out_degree,
            weighted_in_degree=weighted_in_degree,
            weighted_out_degree=weighted_out_degree,
            unique_source_organizations=unique_source_organizations,
            unique_source_pages=unique_source_pages,
        )

    def _determine_country(
        self,
        domain: str,
        country_code: Optional[str],
        target_category: str,
    ) -> Optional[str]:
        """Determine country from various sources."""
        if country_code and len(country_code) == 2:
            return country_code.upper()

        if target_category == "known_government":
            if ".gov." in domain:
                if domain.endswith(".gov.uk"):
                    return "GB"
                elif domain.endswith(".gov.au"):
                    return "AU"
                elif domain.endswith(".gov.fr"):
                    return "FR"
                elif domain.endswith(".gov.de"):
                    return "DE"
                elif ".gov." in domain:
                    tld = domain.split(".")[-2]
                    if len(tld) == 2:
                        return tld.upper()

        if target_category == "shared_government_service" or domain.endswith(".gouv.fr"):
            return "FR"

        if target_category == "shared_government_service" and domain.endswith(".gov.sg"):
            return "SG"

        tld = tldextract.extract(domain).tld
        if len(tld) == 2:
            return tld.upper()

        return None

    def _build_sources(
        self,
        country_code: Optional[str],
        curation_source_url: Optional[str],
        institutional_source_url: Optional[str],
        structured_source_url: Optional[str],
        target_category: str,
        confidence_score: Optional[int],
        from_network: bool,
    ) -> list[SourceEvidence]:
        """Build source evidence list."""
        sources: list[SourceEvidence] = []
        retrieved_at = datetime.now(timezone.utc).isoformat()

        if country_code and target_category == "known_government":
            source = SourceEvidence(
                name="curated_source",
                source_url=curation_source_url or "",
                retrieved_at=retrieved_at,
            )
            sources.append(source)

        if institutional_source_url:
            source = SourceEvidence(
                name="institutional_source",
                source_url=institutional_source_url,
                retrieved_at=retrieved_at,
                confidence=confidence_score,
            )
            sources.append(source)

        if structured_source_url and (
            target_category == "shared_government_service"
            or target_category == "cdn"
        ):
            source = SourceEvidence(
                name="structured_source",
                source_url=structured_source_url,
                retrieved_at=retrieved_at,
            )
            sources.append(source)

        if from_network:
            source = SourceEvidence(
                name="network_signal",
                source_url="network_observation",
                retrieved_at=retrieved_at,
            )
            sources.append(source)

        if not sources:
            source = SourceEvidence(
                name="domain_pattern",
                source_url="",
                retrieved_at=retrieved_at,
            )
            sources.append(source)

        return sources

    def _determine_classification(
        self,
        country: Optional[str],
        government_level: Optional[str],
        organization_type: Optional[str],
        target_category: str,
        from_network: bool,
        sources: list[SourceEvidence],
    ) -> tuple[str, str]:
        """Determine government level and organization type."""
        gov_level = GovernmentLevel.UNKNOWN
        org_type = OrganizationType.UNKNOWN

        if from_network:
            gov_level = GovernmentLevel.LOCAL
            org_type = OrganizationType.MUNICIPALITY
            return gov_level, org_type

        if government_level:
            if government_level in [e.value for e in GovernmentLevel]:
                gov_level = GovernmentLevel(government_level)

        if organization_type:
            if organization_type in [e.value for e in OrganizationType]:
                org_type = OrganizationType(organization_type)

        if not gov_level or gov_level == GovernmentLevel.UNKNOWN:
            if country:
                if country in ["GB", "FR", "DE", "IT", "ES", "NL", "AT", "BE", "CH"]:
                    gov_level = GovernmentLevel.NATIONAL
                elif country in ["CA", "AU", "NZ"]:
                    gov_level = GovernmentLevel.NATIONAL
                elif country in ["US"]:
                    gov_level = GovernmentLevel.NATIONAL
                elif country in ["IE", "PT", "SE", "NO", "DK", "FI"]:
                    gov_level = GovernmentLevel.NATIONAL
                else:
                    gov_level = GovernmentLevel.LOCAL
            else:
                gov_level = GovernmentLevel.UNKNOWN

        if not org_type or org_type == OrganizationType.UNKNOWN:
            if target_category == "known_government":
                org_type = OrganizationType.EXECUTIVE
            elif target_category == "cdn":
                org_type = OrganizationType.SHARED_SERVICE
            elif target_category == "analytics":
                org_type = OrganizationType.EXECUTIVE
            elif target_category == "social_platform":
                org_type = OrganizationType.EXECUTIVE
            elif target_category == "identity":
                org_type = OrganizationType.EXECUTIVE
            elif target_category == "commercial_service":
                org_type = OrganizationType.EXECUTIVE
            elif target_category == "document_host":
                org_type = OrganizationType.EXECUTIVE

        return gov_level, org_type

    def _determine_classification_status(
        self, sources: list[SourceEvidence]
    ) -> str:
        """Determine classification status based on sources."""
        has_confirmed_source = any(
            source.name == "curated_source"
            or (source.name == "software_heritage" and source.confidence and source.confidence >= 7)
            for source in sources
        )

        has_probable_source = any(
            source.name == "institutional_source"
            or (source.name == "structured_source" and source.confidence and source.confidence >= 5)
            for source in sources
        )

        has_candidate_source = any(source.name == "network_signal" for source in sources)

        if has_confirmed_source:
            return ClassificationStatus.CONFIRMED
        elif has_probable_source:
            return ClassificationStatus.PROBABLE
        elif has_candidate_source:
            return ClassificationStatus.CANDIDATE
        else:
            return ClassificationStatus.UNKNOWN
