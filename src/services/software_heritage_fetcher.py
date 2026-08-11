"""Service to fetch and cache the Software Heritage world-gov-domain-names dataset."""

from __future__ import annotations

import csv
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any

import httpx

from src.models.domain_model import SourceEvidence


class SoftwareHeritageFetcher:
    """Fetches and caches the world-gov-domain-names dataset."""

    def __init__(self, cache_dir: Path = Path("data/imports/software-heritage")):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        # Using a fallback generic structure if we don't know the exact repo,
        # but designing it to support a commit-pinned fetch.
        self.default_repo_url = "https://raw.githubusercontent.com/softwareheritage/world-gov-domain-names"

    async def fetch_and_cache(
        self,
        commit_sha: str = "HEAD",
        filename: str = "domains.csv"
    ) -> Path:
        """Fetch the dataset and pin it to a commit if not cached."""
        # Sanitize commit_sha for filename
        safe_commit = "".join(c for c in commit_sha if c.isalnum() or c in "-_")
        cache_file = self.cache_dir / f"world_gov_domains_{safe_commit}.csv"

        if cache_file.exists():
            return cache_file

        url = f"{self.default_repo_url}/{commit_sha}/{filename}"

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, follow_redirects=True)
                response.raise_for_status()
            except httpx.HTTPError as e:
                # If we fail to fetch, and we don't have a cache, we must raise.
                # If we had a fallback cache we could use it, but here we enforce versioning.
                raise RuntimeError(f"Failed to fetch Software Heritage dataset from {url}: {e}")

        # Cache the file
        with cache_file.open("w", encoding="utf-8") as f:
            f.write(response.text)

        return cache_file

    def parse_dataset(self, cache_file: Path) -> Dict[str, Dict[str, Any]]:
        """Parse the cached CSV into a dictionary keyed by domain."""
        parsed_data = {}
        now = datetime.now(timezone.utc).isoformat()

        # Determine the retrieval date from the file's modification time
        try:
            mtime = cache_file.stat().st_mtime
            retrieved_at = datetime.fromtimestamp(mtime, tz=timezone.utc).isoformat()
        except OSError:
            retrieved_at = now

        with cache_file.open("r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                domain = row.get("domain", "").strip().lower()
                if not domain:
                    continue

                confidence_str = row.get("confidence", "0").strip()
                try:
                    confidence = int(confidence_str)
                except ValueError:
                    confidence = None

                evidence = SourceEvidence(
                    name="software_heritage",
                    source_url=f"local_cache:{cache_file.name}",
                    retrieved_at=retrieved_at,
                    confidence=confidence,
                )

                parsed_data[domain] = {
                    "country": row.get("country", "").strip().upper(),
                    "government_level": row.get("level", "unknown").strip().lower(),
                    "organization_type": row.get("type", "unknown").strip().lower(),
                    "evidence": evidence
                }

        return parsed_data
