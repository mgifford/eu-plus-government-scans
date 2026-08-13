"""Lookup of who operates a third-party host, and under whose jurisdiction.

The scan data records that a government site loads assets from
``googleapis.com``.  It cannot say that this is Google LLC, a US company, which
is the fact a digital-sovereignty question turns on.  That mapping is curated by
hand in ``data/providers/jurisdictions.yaml``; this module reads it.

Coverage is partial by design.  A host nobody has confirmed is reported as
unclassified rather than guessed at, because a wrong nationality claim in a
sovereignty report is worse than an absent one.  Any figure derived from this
registry therefore has to be published with its coverage stated.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

DEFAULT_REGISTRY_PATH = Path("data/providers/jurisdictions.yaml")

# Jurisdictions whose organisations are subject to EU/EEA law.  Used to answer
# "how much of this depends on providers outside Europe".
EU_EEA = frozenset({
    "AT", "BE", "BG", "HR", "CY", "CZ", "DK", "EE", "FI", "FR", "DE", "GR",
    "HU", "IE", "IT", "LV", "LT", "LU", "MT", "NL", "PL", "PT", "RO", "SK",
    "SI", "ES", "SE", "IS", "LI", "NO",
})


@dataclass(frozen=True)
class Provider:
    """Who operates a third-party host."""

    domain: str
    operator: str
    jurisdiction: str | None
    kind: str
    category: str
    confidence: str
    needs_review: bool = False
    notes: str = ""

    @property
    def is_eu_eea(self) -> bool:
        """Whether the operator sits under EU/EEA jurisdiction."""
        return self.jurisdiction in EU_EEA

    @property
    def is_government(self) -> bool:
        """Whether this host is a public body rather than a commercial provider.

        Some public bodies are absent from the government domain registry and so
        get counted as third-party dependencies; treating them as external
        overstates a country's exposure.
        """
        return self.kind == "government"


class ProviderRegistry:
    """Reads the curated provider table and answers lookups against it."""

    def __init__(self, path: Path | None = None):
        self._providers: dict[str, Provider] = {}
        self._load(path or DEFAULT_REGISTRY_PATH)

    def _load(self, path: Path) -> None:
        """Load the table, tolerating its absence so scans still run without it."""
        if not path.is_file():
            return
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        except (OSError, yaml.YAMLError):
            return

        for domain, entry in (data.get("providers") or {}).items():
            if not isinstance(entry, dict):
                continue
            key = str(domain).strip().lower()
            jurisdiction = entry.get("jurisdiction")
            self._providers[key] = Provider(
                domain=key,
                operator=str(entry.get("operator", "")).strip(),
                jurisdiction=str(jurisdiction).upper() if jurisdiction else None,
                kind=str(entry.get("kind", "commercial")).strip(),
                category=str(entry.get("category", "")).strip(),
                confidence=str(entry.get("confidence", "medium")).strip(),
                needs_review=bool(entry.get("needs_review", False)),
                notes=str(entry.get("notes", "") or "").strip(),
            )

    def get(self, host: str) -> Provider | None:
        """Return the provider for *host*, or None when it is unclassified.

        Falls back to the registrable domain, so a table entry for
        ``cloudflare.com`` also answers for ``cdnjs.cloudflare.com`` without the
        table needing a row per subdomain.

        Args:
            host: Hostname or registrable domain from the scan data.

        Returns:
            The matching provider, or None.
        """
        if not host:
            return None
        key = host.strip().lower().rstrip(".")
        if key in self._providers:
            return self._providers[key]

        # Walk up the labels: sub.example.com -> example.com -> com
        parts = key.split(".")
        for i in range(1, len(parts) - 1):
            candidate = ".".join(parts[i:])
            if candidate in self._providers:
                return self._providers[candidate]
        return None

    def __len__(self) -> int:
        return len(self._providers)

    def __contains__(self, host: str) -> bool:
        return self.get(host) is not None

    def all_providers(self) -> list[Provider]:
        """Return every curated provider, ordered by domain."""
        return [self._providers[k] for k in sorted(self._providers)]
