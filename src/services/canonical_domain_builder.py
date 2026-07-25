"""Service for canonicalizing domain metadata based on evidence precedence."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

from src.models.domain_model import (
    CanonicalDomain,
    ClassificationBasis,
    ClassificationStatus,
    GovernmentLevel,
    OrganizationType,
    SourceEvidence,
)
from src.services.domain_normalizer import normalize_domain
from src.services.software_heritage_fetcher import SoftwareHeritageFetcher


class CanonicalDomainBuilder:
    """Builds and resolves canonical domain records from diverse sources."""

    # Higher integer = higher precedence for classification.
    # We map ClassificationBasis to precedence.
    PRECEDENCE_MAP: Dict[ClassificationBasis, int] = {
        "authoritative_registry": 70,
        "curated_source": 60,
        "institutional_source": 50,
        "structured_source": 40,
        "software_heritage": 30,
        "domain_pattern": 20,
        "network_signal": 10,
        "unknown": 0,
    }

    def __init__(self):
        self.domains: Dict[str, CanonicalDomain] = {}

    def _get_precedence(self, basis: ClassificationBasis | List[str]) -> int:
        if isinstance(basis, list):
            if not basis:
                return 0
            return max(self.PRECEDENCE_MAP.get(b, 0) for b in basis)
        return self.PRECEDENCE_MAP.get(basis, 0)

    def get_or_create(self, domain: str) -> CanonicalDomain:
        normalized = normalize_domain(domain).canonical_hostname
        if not normalized:
            normalized = domain.lower().strip()

        if normalized not in self.domains:
            self.domains[normalized] = CanonicalDomain(
                id=normalized.replace(".", "-"),
                domain=normalized,
            )
        return self.domains[normalized]

    def add_evidence(
        self,
        domain: str,
        evidence: SourceEvidence,
        basis: ClassificationBasis,
        country: Optional[str] = None,
        government_level: Optional[str] = None,
        organization_type: Optional[str] = None,
        organization_name: Optional[str] = None,
        classification_status: Optional[str] = None,
    ) -> None:
        """Add evidence to a domain, updating classifications if precedence is higher."""
        record = self.get_or_create(domain)
        record.sources.append(evidence)

        # Country assignment
        if country and not record.country:
            record.country = country.upper()

        # Classification precedence check
        current_precedence = self._get_precedence(record.classification_basis)
        new_precedence = self._get_precedence(basis)

        if new_precedence >= current_precedence and basis != "unknown":
            if basis not in record.classification_basis:
                record.classification_basis.append(basis)
            if government_level and government_level != "unknown":
                record.government_level = government_level  # type: ignore
            if organization_type and organization_type != "unknown":
                record.organization_type = organization_type  # type: ignore
            if organization_name:
                record.organization_name = organization_name
            if classification_status:
                record.classification_status = classification_status  # type: ignore

    def ingest_toon_directory(self, toon_dir: Path) -> None:
        """Ingest all curated TOON files as high-precedence evidence."""
        import datetime
        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
        
        for toon_file in toon_dir.glob("*.toon"):
            try:
                with toon_file.open("r", encoding="utf-8") as f:
                    data = json.load(f)
            except Exception as e:
                print(f"Warning: Failed to parse TOON {toon_file}: {e}")
                continue
                
            country_name = data.get("country", "")
            # Determine ISO code from filename or rely on metadata
            iso_code = self._country_from_filename(toon_file.name)

            for domain_obj in data.get("domains", []):
                domain = domain_obj.get("canonical_domain")
                if not domain:
                    continue

                evidence = SourceEvidence(
                    name="existing_country_seed",
                    source_url=f"local:toon:{toon_file.name}",
                    retrieved_at=now_iso,
                )

                self.add_evidence(
                    domain=domain,
                    evidence=evidence,
                    basis="curated_source",
                    country=iso_code,
                    classification_status="confirmed",
                    # TOON files don't strictly enforce level/type yet, but they are confirmed gov domains
                )

    def _country_from_filename(self, filename: str) -> str:
        """Helper to extract country code from our TOON filename patterns."""
        from src.lib.country_utils import country_filename_to_code
        try:
            return country_filename_to_code(filename.replace(".toon", ""))
        except Exception:
            return ""

    def ingest_software_heritage(self, sh_data: Dict[str, Dict[str, str]]) -> None:
        """Ingest parsed Software Heritage dataset."""
        for domain, meta in sh_data.items():
            evidence = meta.get("evidence")
            if not isinstance(evidence, SourceEvidence):
                continue
            
            self.add_evidence(
                domain=domain,
                evidence=evidence,
                basis="software_heritage",
                country=meta.get("country"),
                government_level=meta.get("government_level"),
                organization_type=meta.get("organization_type"),
                classification_status="candidate",
            )

    def fallback_tld_country_assignment(self) -> None:
        """Fallback for unassigned countries using ccTLDs."""
        generic_tlds = {"org", "com", "net", "edu", "int", "gov", "mil", "info"}
        
        for record in self.domains.values():
            if not record.country:
                parts = record.domain.split(".")
                if len(parts) > 1:
                    tld = parts[-1].lower()
                    if tld not in generic_tlds:
                        # Basic assignment, could be more sophisticated
                        record.country = tld.upper()
