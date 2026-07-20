"""Shared registry of known government domains, built from the TOON seed files.

This is the single source of truth for "is this domain a known government
domain, and for which country" -- replaces three previously-independent and
disagreeing definitions: relationship_scanner.py's same-origin-as-"known_government"
mislabeling, relationship_scanner_job.py's hardcoded TLD-to-country table, and
network.html's isGovernmentDomain() regex heuristic.
"""

from __future__ import annotations

import json
from pathlib import Path

from src.lib.country_utils import country_filename_to_code

DEFAULT_TOON_DIR = Path("data/toon-seeds/countries")


class GovernmentDomainRegistry:
    """Looks up whether a domain is a known government domain, and its country."""

    def __init__(self, toon_dir: Path | None = None):
        self._domain_to_country: dict[str, str] = {}
        self._load(toon_dir or DEFAULT_TOON_DIR)

    def _load(self, toon_dir: Path) -> None:
        if not toon_dir.exists():
            return
        for toon_path in sorted(toon_dir.glob("*.toon")):
            country_code = country_filename_to_code(toon_path.stem)
            try:
                with toon_path.open("r", encoding="utf-8") as f:
                    data = json.load(f)
            except (OSError, json.JSONDecodeError):
                continue
            for domain_entry in data.get("domains", []):
                domain = domain_entry.get("canonical_domain")
                if domain:
                    self._domain_to_country[domain.lower()] = country_code

    def is_government_domain(self, domain: str) -> bool:
        """Return True if `domain` is a known government domain in any country."""
        return domain.lower() in self._domain_to_country

    def country_for_domain(self, domain: str) -> str | None:
        """Return the country code for `domain`, or None if not a known government domain."""
        return self._domain_to_country.get(domain.lower())

    def all_domains(self) -> dict[str, str]:
        """Return a copy of the full domain-to-country-code mapping."""
        return dict(self._domain_to_country)

    def __len__(self) -> int:
        return len(self._domain_to_country)
