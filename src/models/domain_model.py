"""Models for the Canonical Domain and Relationship extraction dataset."""

from __future__ import annotations

from typing import Dict, List, Literal, Optional, Set
from pydantic import BaseModel, Field


class SourceEvidence(BaseModel):
    """Evidence for a classification or domain assertion."""
    name: str = Field(description="Name of the source (e.g. existing_country_seed, software_heritage)")
    source_url: str = Field(description="URL or reference to the source")
    retrieved_at: str = Field(description="ISO date when this data was ingested")
    confidence: Optional[int] = Field(None, description="Source-provided confidence score (e.g., from Software Heritage)")


GovernmentLevel = Literal[
    "supranational",
    "national",
    "regional",
    "state_or_province",
    "local",
    "municipal",
    "independent_public_body",
    "unknown"
]

OrganizationType = Literal[
    "head_of_government",
    "executive_office",
    "ministry",
    "department",
    "executive_agency",
    "shared_service",
    "legislature",
    "judiciary",
    "independent_regulator",
    "central_bank",
    "audit_body",
    "ombuds_body",
    "regional_government",
    "state_or_province",
    "territorial_government",
    "municipality",
    "public_health",
    "public_education",
    "public_university",
    "public_broadcaster",
    "state_owned_enterprise",
    "public_utility",
    "unknown"
]

ClassificationStatus = Literal[
    "confirmed",
    "probable",
    "candidate",
    "disputed",
    "retired",
    "unknown"
]

ClassificationBasis = Literal[
    "authoritative_registry",
    "curated_source",
    "institutional_source",
    "structured_source",
    "software_heritage",
    "domain_pattern",
    "network_signal",
    "explicit_exception",
    "country_rule",
    "unknown"
]

ReviewStatus = Literal[
    "pending",
    "reviewed",
    "approved",
    "rejected",
    "unknown"
]


class Conflict(BaseModel):
    """A conflict between classification sources."""
    source: str = Field(description="Name of the source making the assertion")
    assertion: str = Field(description="The assertion made by the source")
    url: Optional[str] = Field(None, description="URL of the source")


class CanonicalDomain(BaseModel):
    """A canonical record for a normalized government domain."""
    id: str = Field(description="Unique identifier for the organization or domain (e.g., gb-hackney-council)")
    domain: str = Field(description="The normalized registrable domain (e.g. hackney.gov.uk)")
    country: Optional[str] = Field(None, description="ISO-3166-1 alpha-2 country code if known")
    organization_name: Optional[str] = Field(None, description="Name of the organization")
    government_level: GovernmentLevel = Field(default="unknown")
    organization_type: OrganizationType = Field(default="unknown")

    # Central administration classification
    central_administration: Optional[bool] = Field(
        None,
        description="Whether the domain belongs to central administration. "
        "True for national executive ministries/departments, False for non-central bodies, "
        "null for unknown or unresolved cases."
    )

    # Classification metadata
    classification_status: ClassificationStatus = Field(default="unknown")
    classification_basis: List[str] = Field(
        default_factory=list,
        description="List of evidence sources used for classification"
    )
    classification_rule: Optional[str] = Field(
        None,
        description="The classification rule that was applied (e.g., CA-EXPLICIT-INCLUDE)"
    )

    # Review tracking
    review_status: ReviewStatus = Field(
        default="unknown",
        description="Whether the classification has been reviewed by a maintainer"
    )
    reviewed_at: Optional[str] = Field(
        None,
        description="ISO date when the classification was last reviewed"
    )
    reviewed_by: Optional[str] = Field(
        None,
        description="Who reviewed the classification (e.g., maintainer username)"
    )

    # Conflict tracking
    conflicts: List[Conflict] = Field(
        default_factory=list,
        description="List of conflicting source assertions"
    )

    # Applied rules tracking
    applied_rules: List[str] = Field(
        default_factory=list,
        description="List of classification rules that were applied"
    )

    # Source tracking
    sources: List[SourceEvidence] = Field(default_factory=list)

    # Descriptive graph metrics (must not be called institutional confidence scores)
    in_degree: int = Field(default=0)
    out_degree: int = Field(default=0)
    weighted_in_degree: int = Field(default=0)
    weighted_out_degree: int = Field(default=0)
    unique_source_organizations: int = Field(default=0)
    unique_source_pages: int = Field(default=0)


class RelationshipEdgeMetrics(BaseModel):
    """Metrics for an edge between two domains."""
    source: str
    target: str
    relationship_type: str
    source_pages: int = Field(default=0)
    observations: int = Field(default=0)
    page_regions: Dict[str, int] = Field(default_factory=dict)
    first_seen: str
    last_seen: str


class GlobalSummary(BaseModel):
    """Aggregate summaries for the global manifest."""
    total_domains: int
    total_edges: int
    domains_by_country: Dict[str, int]
    edges_by_type: Dict[str, int]
    generated_at: str
    schema_version: str = "1.0.0"


class CountrySummary(BaseModel):
    """Aggregate summary for a specific country."""
    country_code: str
    total_domains: int
    total_edges: int
    generated_at: str
    schema_version: str = "1.0.0"
