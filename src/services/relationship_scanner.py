"""Service for extracting web page relationships (links, scripts, etc.)."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urljoin, urlparse

import tldextract
from bs4 import BeautifulSoup

from src.lib.gov_domain_registry import GovernmentDomainRegistry


@dataclass
class RelationshipEdge:
    """A single normalized relationship from a source page to a target."""
    source_domain: str
    target_domain: str
    target_hostname: str
    relationship_type: str
    target_category: str
    is_external: bool
    html_element: str
    page_region: str
    target_url: str


@dataclass
class RelationshipScanResult:
    """Result of relationship extraction for a single URL."""
    url: str
    is_reachable: bool
    relationships: list[RelationshipEdge] = field(default_factory=list)
    error_message: str | None = None
    scanned_at: str | None = None


class RelationshipScanner:
    """Extracts relationships from a fetched HTML response."""

    def __init__(
        self,
        categories_file: Path | None = None,
        gov_registry: GovernmentDomainRegistry | None = None,
    ):
        if categories_file is None:
            categories_file = Path("data/relationship_categories.json")

        self.categories = self._load_categories(categories_file)
        self.gov_registry = gov_registry or GovernmentDomainRegistry()
        self.tld_extract = tldextract.TLDExtract()

    def _load_categories(self, path: Path) -> dict[str, str]:
        """Load domain-to-category mapping from a JSON file."""
        mapping: dict[str, str] = {}
        if path.exists():
            try:
                with path.open("r", encoding="utf-8") as f:
                    data = json.load(f)
                for rule in data.get("rules", []):
                    category = rule.get("category")
                    for domain in rule.get("domains", []):
                        mapping[domain.lower()] = category
            except Exception as e:
                print(f"Warning: Failed to load categories from {path}: {e}")
        return mapping

    def _get_category(self, registrable_domain: str) -> str:
        """Assign a category to a target domain.

        Checks the government domain registry first (built from the TOON seed
        files) so a link to a *different* known government domain -- e.g. a
        Spanish ministry linking to govern.cat -- is correctly categorized as
        government rather than falling through to unknown_external. Falls
        back to the curated third-party rules, then unknown_external.
        """
        if self.gov_registry.is_government_domain(registrable_domain):
            return "known_government"
        return self.categories.get(registrable_domain, "unknown_external")

    def _determine_region(self, element: Any) -> str:
        """Determine if element is in main, nav, footer, header, or unknown."""
        for parent in element.parents:
            if parent.name in ("header", "nav", "footer", "main"):
                return parent.name
            
            # Check classes or IDs for common naming
            class_str = " ".join(parent.get("class", [])).lower()
            id_str = parent.get("id", "").lower()
            
            for region in ("header", "nav", "footer", "main"):
                if region in class_str or region in id_str:
                    return region

        return "unknown"

    def _normalize_url(self, url: str, base_url: str) -> tuple[str, str, str] | None:
        """
        Normalize URL and extract host/domain.
        Returns (normalized_url, target_hostname, target_registrable_domain) or None if invalid.
        """
        try:
            # Resolve relative URLs
            full_url = urljoin(base_url, url)
            
            parsed = urlparse(full_url)
            
            # Only accept http and https
            if parsed.scheme not in ("http", "https"):
                return None
                
            # Remove fragments
            parsed = parsed._replace(fragment="")
            
            # Normalize casing and drop default ports
            hostname = parsed.hostname
            if not hostname:
                return None
            
            # IDN conversion to uniform representation
            hostname = hostname.encode("idna").decode("utf-8").lower()
            
            # Strip default ports if they were parsed into the netloc but aren't standard
            netloc = hostname
            if parsed.port:
                if (parsed.scheme == "http" and parsed.port != 80) or \
                   (parsed.scheme == "https" and parsed.port != 443):
                    netloc = f"{hostname}:{parsed.port}"
            
            normalized_url = parsed._replace(netloc=netloc).geturl()
            
            # Get registrable domain
            extracted = self.tld_extract(hostname)
            if extracted.registered_domain:
                registrable_domain = extracted.registered_domain
            else:
                # Fallback for IP addresses or local domains
                registrable_domain = hostname
                
            return normalized_url, hostname, registrable_domain
        except Exception:
            return None

    def scan_html(
        self,
        url: str,
        html: str,
        final_url: str | None = None,
        scanned_at: str | None = None,
    ) -> RelationshipScanResult:
        """
        Extract relationships from HTML.
        """
        if not scanned_at:
            scanned_at = datetime.now(timezone.utc).isoformat()
            
        base_url = final_url or url
        source_extracted = self.tld_extract(urlparse(base_url).hostname or "")
        source_domain = source_extracted.registered_domain or (urlparse(base_url).hostname or "")
        
        try:
            soup = BeautifulSoup(html, "html.parser")
            
            edges_dedup_key: set[tuple[str, str, str]] = set()
            relationships: list[RelationshipEdge] = []
            
            def add_edge(target: str, rel_type: str, element_name: str, region: str):
                normalized = self._normalize_url(target, base_url)
                if not normalized:
                    return
                    
                target_url, target_hostname, target_domain = normalized
                is_external = source_domain != target_domain
                category = self._get_category(target_domain)
                
                # Deduplicate identical target relationships within each source page
                dedup_key = (target_domain, target_hostname, rel_type)
                if dedup_key in edges_dedup_key:
                    return
                edges_dedup_key.add(dedup_key)
                
                relationships.append(RelationshipEdge(
                    source_domain=source_domain,
                    target_domain=target_domain,
                    target_hostname=target_hostname,
                    relationship_type=rel_type,
                    target_category=category,
                    is_external=is_external,
                    html_element=element_name,
                    page_region=region,
                    target_url=target_url,
                ))

            # 1. editorial_link (<a href>)
            for a_tag in soup.find_all("a", href=True):
                region = self._determine_region(a_tag)
                add_edge(a_tag["href"], "editorial_link", "a", region)
                
            # 2. script_dependency (<script src>)
            for script_tag in soup.find_all("script", src=True):
                region = self._determine_region(script_tag)
                add_edge(script_tag["src"], "script_dependency", "script", region)
                
            # 3. stylesheet_dependency (<link rel="stylesheet">)
            for link_tag in soup.find_all("link", rel=True, href=True):
                rels = link_tag["rel"]
                if not isinstance(rels, list):
                    rels = [rels]
                
                region = self._determine_region(link_tag)
                
                if "stylesheet" in rels:
                    add_edge(link_tag["href"], "stylesheet_dependency", "link", region)
                elif "preload" in rels or "font" in rels or "preconnect" in rels:
                    add_edge(link_tag["href"], "font_or_preload_dependency", "link", region)
                    
            # 4. image_or_media_dependency (<img>)
            for img_tag in soup.find_all("img", src=True):
                region = self._determine_region(img_tag)
                add_edge(img_tag["src"], "image_or_media_dependency", "img", region)
                
            # 5. form_destination (<form action>)
            for form_tag in soup.find_all("form", action=True):
                region = self._determine_region(form_tag)
                add_edge(form_tag["action"], "form_destination", "form", region)
                
            return RelationshipScanResult(
                url=url,
                is_reachable=True,
                relationships=relationships,
                scanned_at=scanned_at,
            )
            
        except Exception as e:
            return RelationshipScanResult(
                url=url,
                is_reachable=True,
                error_message=f"Relationship extraction failed: {e}",
                scanned_at=scanned_at,
            )
