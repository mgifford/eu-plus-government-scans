"""Best-effort enrichment for upstream technology license metadata.

This module classifies the likely upstream license of detected technologies,
not whether a particular government deployment complies with that license.
SaaS and cloud services are not OSI-licensed simply because they may rely on
open source internally. Confidence levels matter, and any public or policy
claim should be manually reviewed against the upstream project first.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

_VALID_LICENSE_STATUSES: frozenset[str] = frozenset(
    {
        "osi_approved",
        "proprietary",
        "source_available",
        "not_applicable_service",
        "unknown",
    }
)
_VALID_CONFIDENCE_LEVELS: frozenset[str] = frozenset({"high", "medium", "low"})
_SCOPE_NOTE = (
    "Best-effort classification of upstream technology licenses, not "
    "deployment compliance. SaaS and cloud services are not OSI-licensed "
    "just because they use open source internally. Confidence levels "
    "matter, and manual review is required before making public claims."
)
_SPDX_SPLIT_PATTERN = re.compile(r"\s+(?:AND|OR)\s+")

_OSI_APPROVED_SPDX_IDS: frozenset[str] = frozenset(
    {
        "AFL-3.0",
        "AGPL-3.0-only",
        "AGPL-3.0-or-later",
        "Apache-2.0",
        "Artistic-2.0",
        "BSD-2-Clause",
        "BSD-3-Clause",
        "CDDL-1.0",
        "CPAL-1.0",
        "EPL-1.0",
        "EPL-2.0",
        "EUPL-1.1",
        "EUPL-1.2",
        "GPL-2.0-only",
        "GPL-2.0-or-later",
        "GPL-3.0-only",
        "GPL-3.0-or-later",
        "ISC",
        "LGPL-2.0-only",
        "LGPL-2.0-or-later",
        "LGPL-2.1-only",
        "LGPL-2.1-or-later",
        "LGPL-3.0-only",
        "LGPL-3.0-or-later",
        "MIT",
        "MPL-2.0",
        "OSL-3.0",
        "PHP-3.01",
        "Python-2.0",
    }
)


@dataclass(slots=True)
class LicenseOverride:
    """Curated license metadata for a detected technology name."""

    spdx_expression: str | None
    license_status: str
    osi_approved: bool | None
    notes: str
    confidence: str


@dataclass(slots=True)
class EnrichedTechnology:
    """Detected technology record with license enrichment metadata."""

    name: str
    categories: list[str]
    detected_count: int
    license_status: str
    spdx_license_expression: str | None
    osi_approved: bool | None
    license_source: str
    confidence: str
    requires_manual_review: bool
    notes: str
    by_country: dict[str, int]


def _parse_override(tech_name: str, raw_override: object) -> LicenseOverride:
    """Validate and convert one override record from JSON data.

    Args:
        tech_name: Technology name used as the mapping key.
        raw_override: Parsed JSON value for that technology.

    Returns:
        A validated :class:`LicenseOverride` instance.

    Raises:
        ValueError: If the override payload is malformed.
    """
    if not isinstance(raw_override, dict):
        raise ValueError(f"Override for {tech_name} must be an object.")

    spdx_expression = raw_override.get("spdx_expression")
    if spdx_expression is not None and not isinstance(spdx_expression, str):
        raise ValueError(
            f"Override for {tech_name} has a non-string spdx_expression."
        )

    license_status = raw_override.get("license_status")
    if license_status not in _VALID_LICENSE_STATUSES:
        raise ValueError(
            f"Override for {tech_name} has invalid license_status: "
            f"{license_status}"
        )

    osi_approved = raw_override.get("osi_approved")
    if osi_approved is not None and not isinstance(osi_approved, bool):
        raise ValueError(
            f"Override for {tech_name} has a non-boolean osi_approved value."
        )

    notes = raw_override.get("notes")
    if not isinstance(notes, str) or not notes.strip():
        raise ValueError(f"Override for {tech_name} must include notes.")

    confidence = raw_override.get("confidence")
    if confidence not in _VALID_CONFIDENCE_LEVELS:
        raise ValueError(
            f"Override for {tech_name} has invalid confidence: {confidence}"
        )

    return LicenseOverride(
        spdx_expression=spdx_expression,
        license_status=license_status,
        osi_approved=osi_approved,
        notes=notes,
        confidence=confidence,
    )


def load_overrides(overrides_path: Path) -> dict[str, LicenseOverride]:
    """Load technology-license-overrides.json and return dict keyed by name.

    Args:
        overrides_path: Path to the curated override JSON file.

    Returns:
        Mapping of technology name to validated override metadata.

    Raises:
        ValueError: If the JSON structure is invalid.
        OSError: If the file cannot be read.
    """
    raw_text = overrides_path.read_text(encoding="utf-8")
    raw_data = json.loads(raw_text)
    overrides_data = raw_data.get("overrides")
    if not isinstance(overrides_data, dict):
        raise ValueError("Override file must contain an 'overrides' object.")

    return {
        tech_name: _parse_override(tech_name, raw_override)
        for tech_name, raw_override in sorted(overrides_data.items())
    }


def is_spdx_osi_approved(spdx_expression: str) -> bool:
    """Return True when every SPDX identifier in the expression is OSI-approved.

    Handles simple identifiers and flat ``X AND Y`` / ``X OR Y`` compound
    expressions. Parentheses, the ``WITH`` operator, and other complex SPDX
    syntax are treated as unsupported and return ``False`` conservatively.

    Args:
        spdx_expression: SPDX identifier or simple compound expression.

    Returns:
        ``True`` when every parsed identifier is in the OSI-approved allow
        list, otherwise ``False``.
    """
    expression = spdx_expression.strip()
    if not expression:
        return False
    if "WITH" in expression or "(" in expression or ")" in expression:
        return False

    identifiers = [item.strip() for item in _SPDX_SPLIT_PATTERN.split(expression)]
    if not identifiers or any(not item for item in identifiers):
        return False
    return all(identifier in _OSI_APPROVED_SPDX_IDS for identifier in identifiers)


def _normalize_by_country(raw_by_country: object) -> dict[str, int]:
    """Return a deterministic country-count mapping from raw JSON data."""
    if not isinstance(raw_by_country, dict):
        return {}
    return {
        str(country_code): int(count or 0)
        for country_code, count in sorted(raw_by_country.items())
    }


def enrich_technology(
    name: str,
    categories: list[str],
    detected_count: int,
    by_country: dict[str, int],
    overrides: dict[str, LicenseOverride],
) -> EnrichedTechnology:
    """Enrich a single technology entry with license metadata.

    Resolution order:
    1. Check curated overrides dict (exact name match, case-sensitive)
    2. Mark as unknown with ``requires_manual_review=True``

    Args:
        name: Detected technology name.
        categories: Technology categories from ``technology-index.json``.
        detected_count: Number of detected pages.
        by_country: Per-country detection counts.
        overrides: Curated override mapping keyed by technology name.

    Returns:
        A populated :class:`EnrichedTechnology` record.
    """
    override = overrides.get(name)
    normalized_categories = sorted(categories)
    normalized_by_country = _normalize_by_country(by_country)

    if override is None:
        return EnrichedTechnology(
            name=name,
            categories=normalized_categories,
            detected_count=detected_count,
            license_status="unknown",
            spdx_license_expression=None,
            osi_approved=None,
            license_source="unknown",
            confidence="low",
            requires_manual_review=True,
            notes="No curated override found; manual review required.",
            by_country=normalized_by_country,
        )

    requires_manual_review = (
        override.license_status == "unknown" or override.confidence != "high"
    )
    return EnrichedTechnology(
        name=name,
        categories=normalized_categories,
        detected_count=detected_count,
        license_status=override.license_status,
        spdx_license_expression=override.spdx_expression,
        osi_approved=override.osi_approved,
        license_source="override",
        confidence=override.confidence,
        requires_manual_review=requires_manual_review,
        notes=override.notes,
        by_country=normalized_by_country,
    )


def enrich_all(
    technology_index: dict,
    overrides: dict[str, LicenseOverride],
) -> list[EnrichedTechnology]:
    """Enrich all technologies from the technology-index.json structure.

    Args:
        technology_index: Parsed JSON payload from
            ``docs/technology-index.json``.
        overrides: Curated override mapping keyed by technology name.

    Returns:
        Enriched technology records sorted by detected count descending, then
        by name ascending.
    """
    raw_by_technology = technology_index.get("by_technology")
    if not isinstance(raw_by_technology, dict):
        return []

    enriched = []
    for name, raw_record in raw_by_technology.items():
        if not isinstance(raw_record, dict):
            raw_record = {}
        categories = raw_record.get("categories")
        category_list = categories if isinstance(categories, list) else []
        detected_count = int(raw_record.get("pages") or 0)
        by_country = raw_record.get("by_country")
        enriched.append(
            enrich_technology(
                name=name,
                categories=category_list,
                detected_count=detected_count,
                by_country=by_country if isinstance(by_country, dict) else {},
                overrides=overrides,
            )
        )

    return sorted(enriched, key=lambda tech: (-tech.detected_count, tech.name))


def to_dict(tech: EnrichedTechnology) -> dict:
    """Serialize an EnrichedTechnology to a JSON-compatible dict.

    Args:
        tech: Enriched technology record.

    Returns:
        JSON-compatible dictionary with deterministic category ordering.
    """
    return {
        "name": tech.name,
        "categories": list(tech.categories),
        "detected_count": tech.detected_count,
        "license_status": tech.license_status,
        "spdx_license_expression": tech.spdx_license_expression,
        "osi_approved": tech.osi_approved,
        "license_source": tech.license_source,
        "confidence": tech.confidence,
        "requires_manual_review": tech.requires_manual_review,
        "notes": tech.notes,
        "by_country": dict(tech.by_country),
    }


def build_output(
    enriched: list[EnrichedTechnology],
    generated_at: str,
) -> dict:
    """Build the full output JSON structure for license enrichment results.

    Args:
        enriched: Enriched technology records.
        generated_at: Human-readable UTC timestamp.

    Returns:
        JSON-compatible output containing the timestamp, scope note, summary
        statistics, and serialized records.
    """
    status_counts = {
        status: sum(1 for tech in enriched if tech.license_status == status)
        for status in sorted(_VALID_LICENSE_STATUSES)
    }
    manual_review_queue_count = sum(
        1 for tech in enriched if tech.requires_manual_review
    )
    proprietary_or_service_count = (
        status_counts["proprietary"]
        + status_counts["not_applicable_service"]
    )

    return {
        "generated_at": generated_at,
        "scope_note": _SCOPE_NOTE,
        "stats": {
            "total_technologies": len(enriched),
            "osi_approved_count": status_counts["osi_approved"],
            "proprietary_or_service_count": proprietary_or_service_count,
            "unknown_count": status_counts["unknown"],
            "manual_review_queue_count": manual_review_queue_count,
            "by_license_status": status_counts,
        },
        "records": [to_dict(tech) for tech in enriched],
    }
