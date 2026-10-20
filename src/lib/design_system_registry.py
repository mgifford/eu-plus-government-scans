"""Lookup of government design systems and their adoption signatures.

Which design systems exist, which organisation they belong to, and what a
consuming site's HTML looks like when it uses them cannot be derived by a
scanner: that mapping is curated by hand in ``data/design-systems.yaml`` and
read here, following the same doctrine as
:mod:`src.lib.provider_registry`.

Two rules govern edits to the table:

- **Leave an ``adoption_signatures`` list empty rather than guess.**  A wrong
  signature reports false adoption, which is worse than an absent count.
  Entries without signatures are surfaced by the coverage report so the
  curation work stays visible and finite.
- **Anything below ``confidence: high`` carries ``needs_review: true``**, so no
  figure is ever published as more certain than its inputs.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

DEFAULT_REGISTRY_PATH = Path("data/design-systems.yaml")

DESIGN_SYSTEM_TYPES = frozenset({"design_system", "brand_identity", "accessibility_guide"})

# Signatures shorter than this are too likely to collide with unrelated markup
# (e.g. a bare "hds" matching random attribute names), so they are dropped
# rather than matched.
MIN_SIGNATURE_LENGTH = 4


@dataclass(frozen=True)
class DesignSystem:
    """One curated design system (or brand/guidance entry)."""

    name: str
    country_code: str
    type: str
    scope: str
    url: str
    repo: str
    adoption_signatures: tuple[str, ...]
    confidence: str
    needs_review: bool
    notes: str

    @property
    def has_signatures(self) -> bool:
        """Whether adoption of this system can be measured from page HTML."""
        return bool(self.adoption_signatures)


class DesignSystemRegistry:
    """Reads the curated design-system table and answers lookups against it."""

    def __init__(self, path: Path | None = None):
        self._systems: list[DesignSystem] = []
        self._load(path or DEFAULT_REGISTRY_PATH)

    def _load(self, path: Path) -> None:
        """Load the table, tolerating its absence so scans still run without it."""
        if not path.is_file():
            return
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        except (OSError, yaml.YAMLError):
            return

        for entry in data.get("design_systems") or []:
            if not isinstance(entry, dict):
                continue
            name = str(entry.get("name", "")).strip()
            if not name:
                continue
            raw_signatures = entry.get("adoption_signatures") or []
            signatures = tuple(
                str(sig).strip().lower()
                for sig in raw_signatures
                if str(sig).strip() and len(str(sig).strip()) >= MIN_SIGNATURE_LENGTH
            )
            entry_type = str(entry.get("type", "design_system")).strip()
            self._systems.append(
                DesignSystem(
                    name=name,
                    country_code=str(entry.get("country_code", "") or "").strip().upper(),
                    type=entry_type if entry_type in DESIGN_SYSTEM_TYPES else "design_system",
                    scope=str(entry.get("scope", "unknown") or "").strip() or "unknown",
                    url=str(entry.get("url", "") or "").strip(),
                    repo=str(entry.get("repo", "") or "").strip(),
                    adoption_signatures=signatures,
                    confidence=str(entry.get("confidence", "medium")).strip(),
                    needs_review=bool(entry.get("needs_review", False)),
                    notes=str(entry.get("notes", "") or "").strip(),
                )
            )

    def all_systems(self) -> list[DesignSystem]:
        """Return every curated entry, ordered by country then name."""
        return sorted(
            self._systems,
            key=lambda s: (s.country_code or "ZZ", s.name.lower()),
        )

    def by_country(self) -> dict[str, list[DesignSystem]]:
        """Return entries grouped by country code.

        Supranational and unconfirmed entries (empty ``country_code``) are
        grouped under the empty string rather than dropped, so they remain
        visible in coverage counts.
        """
        grouped: dict[str, list[DesignSystem]] = {}
        for system in self.all_systems():
            grouped.setdefault(system.country_code, []).append(system)
        return grouped

    def matched_systems(self, html: str) -> list[str]:
        """Return names of systems whose adoption signatures appear in *html*.

        Matching is case-insensitive substring search over the raw HTML, the
        same approach the overlay scanner uses for vendor signatures.

        Args:
            html: Raw HTML source of the page.

        Returns:
            Sorted list of matching system names; empty when none match or the
            registry is empty.
        """
        if not self._systems or not html:
            return []
        html_lower = html.lower()
        detected: list[str] = []
        for system in self._systems:
            for signature in system.adoption_signatures:
                if signature in html_lower:
                    detected.append(system.name)
                    break  # only add each system once
        return sorted(detected)

    def coverage(self) -> dict[str, int]:
        """Return counts describing the registry's own completeness.

        Published alongside any adoption figure so a reader can see how much
        of the table is still unmeasurable.
        """
        total = len(self._systems)
        with_signatures = sum(1 for s in self._systems if s.has_signatures)
        needing_review = sum(1 for s in self._systems if s.needs_review)
        with_country = sum(1 for s in self._systems if s.country_code)
        return {
            "total": total,
            "with_adoption_signatures": with_signatures,
            "without_adoption_signatures": total - with_signatures,
            "needs_review": needing_review,
            "with_country_code": with_country,
        }

    def __len__(self) -> int:
        return len(self._systems)

    def __contains__(self, name: str) -> bool:
        return any(s.name == name for s in self._systems)
