# SBOM (Software Bill of Materials)

This file tracks the primary software used in this repository to support security and legal review.

## Scope

- Top-level runtime, development, and CI tooling dependencies
- Versions are pinned where currently managed by repository manifests
- License values are from package metadata and should be re-verified during upgrades

## Software Inventory

| Component | Ecosystem | Version | License (declared) | Version Source | Notes |
|---|---|---:|---|---|---|
| Python | runtime | 3.12 | PSF | `.github/workflows/*`, docs | Primary language runtime |
| Node.js | runtime/tooling | 20.x | MIT-style | `.github/workflows/*`, docs | Required for Lighthouse/Playwright tooling |
| setuptools | pip | `>=68.0,<81.0` | UNKNOWN | `requirements.txt` | Kept for `python-Wappalyzer` / `pkg_resources` compatibility |
| fastapi | pip | `0.115.6` | UNKNOWN | `requirements.txt` | API framework |
| httpx | pip | `0.28.1` | BSD-3-Clause | `requirements.txt` | Async HTTP client |
| pydantic | pip | `2.10.5` | UNKNOWN | `requirements.txt` | Data validation |
| pydantic-settings | pip | `2.7.1` | UNKNOWN | `requirements.txt` | Settings management |
| APScheduler | pip | `3.10.4` | MIT | `requirements.txt` | Scheduling |
| tldextract | pip | `5.1.3` | BSD-3-Clause | `requirements.txt` | Domain parsing |
| beautifulsoup4 | pip | `4.12.3` | MIT License | `requirements.txt` | HTML parsing |
| tenacity | pip | `9.0.0` | Apache 2.0 | `requirements.txt` | Retry handling |
| python-Wappalyzer | pip | `0.3.1` | UNKNOWN | `requirements.txt` | Technology detection |
| pytest | pip | `8.3.4` | MIT | `requirements.txt` | Test runner |
| pytest-asyncio | pip | `0.25.2` | Apache 2.0 | `requirements.txt` | Async test support |
| pytest-mock | pip | `3.14.0` | MIT | `requirements.txt` | Mocking plugin |
| ruff | pip | `0.9.10` | MIT | `requirements.txt` | Linting |
| @axe-core/playwright | npm | `4.11.1` | MPL-2.0 | `package.json`, `package-lock.json` | Accessibility smoke tests |
| playwright | npm | `1.59.1` | Apache-2.0 | `package.json`, `package-lock.json` | Browser automation for site accessibility checks |
| uv | Python tooling | latest (install-time) | MIT OR Apache-2.0 | `AGENTS.md` setup guidance | Preferred package manager |

## Update Process

1. Update dependency manifests (`requirements.txt`, `package.json`, lockfiles).
2. Re-run dependency checks and tests.
3. Update this SBOM with new versions and license declarations.
4. Review and document any license or vulnerability risk before merge.

## Risk Management Notes

- Prefer pinned versions and reviewed upgrades.
- Track security advisories for changed dependencies.
- Verify unknown license declarations from upstream project metadata before broad adoption.
