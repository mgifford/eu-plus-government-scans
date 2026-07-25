import pytest
from src.services.canonical_domain_builder import CanonicalDomainBuilder
from src.models.domain_model import SourceEvidence


def test_precedence_logic():
    builder = CanonicalDomainBuilder()
    
    # 1. Add low precedence evidence
    ev1 = SourceEvidence(name="network_signal", source_url="...", retrieved_at="2026-07-15")
    builder.add_evidence(
        domain="example.gov",
        evidence=ev1,
        basis="network_signal",
        government_level="local",
        organization_type="municipality",
        classification_status="candidate"
    )
    
    rec = builder.get_or_create("example.gov")
    assert rec.government_level == "local"
    assert "network_signal" in rec.classification_basis
    assert rec.classification_status == "candidate"

    # 2. Add higher precedence evidence (curated_source)
    ev2 = SourceEvidence(name="curated_source", source_url="...", retrieved_at="2026-07-15")
    builder.add_evidence(
        domain="example.gov",
        evidence=ev2,
        basis="curated_source",
        government_level="national",
        organization_type="ministry",
        classification_status="confirmed"
    )

    assert rec.government_level == "national"
    assert "curated_source" in rec.classification_basis
    assert rec.classification_status == "confirmed"

    # 3. Add lower precedence evidence again (software_heritage) - should not overwrite gov level
    ev3 = SourceEvidence(name="software_heritage", source_url="...", retrieved_at="2026-07-15", confidence=8)
    builder.add_evidence(
        domain="example.gov",
        evidence=ev3,
        basis="software_heritage",
        government_level="regional",
        organization_type="agency",
        classification_status="probable"
    )

    assert rec.government_level == "national" # Stays national
    assert "curated_source" in rec.classification_basis
    assert len(rec.sources) == 3


def test_fallback_tld():
    builder = CanonicalDomainBuilder()
    ev = SourceEvidence(name="network_signal", source_url="...", retrieved_at="2026-07-15")
    
    builder.add_evidence("city.gov.fr", ev, "network_signal")
    builder.add_evidence("service.org", ev, "network_signal")
    
    builder.fallback_tld_country_assignment()
    
    assert builder.get_or_create("city.gov.fr").country == "FR"
    assert builder.get_or_create("service.org").country is None  # .org is generic
