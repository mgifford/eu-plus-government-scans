# AGENTS.md — Instructions for AI Coding Agents

This file follows the [agents.md](https://agents.md/) convention and provides guidance for AI coding
agents (GitHub Copilot, Claude, Gemini, ChatGPT, etc.) working in this repository.

---

## Project Overview

**eu-plus-government-scans** discovers and catalogues accessibility-statement URLs published by
European (and selected allied) government websites. It:

- Maintains TOON seed files (per country) that list government domains and known page URLs
- Validates those URLs asynchronously with rate-limiting and redirect tracking
- Tracks validation state in a lightweight SQLite / PostgreSQL-compatible metadata database
- Runs automated batch-validation cycles via GitHub Actions (cron + issue-triggered)
- Generates markdown validation reports

---

## Repository Layout

```
.github/workflows/      GitHub Actions CI/CD and cron workflows
data/
  imports/              Raw CSV imports from Google Sheets
  toon-seeds/           TOON seed files per country (*.toon JSON)
docs/                   User-facing documentation (markdown)
src/
  api/                  FastAPI application (if/when served)
  cli/                  Command-line entry points
  jobs/                 Background job logic (URL validation scanner)
  lib/                  Shared utilities (settings, country helpers, …)
  models/               Pydantic models
  services/             Core service logic (URL validator, batch coordinator, …)
  storage/              Schema bootstrap and database helpers
  glossary/             Multilingual accessibility-statement term lists
tests/
  unit/                 Unit tests
  integration/          Integration tests
requirements.txt        Python dependencies
```

---

## Technology Stack

- **Python 3.12** — primary language
- **FastAPI** — API layer (optional serving)
- **HTTPX** — async HTTP client for URL validation
- **Pydantic** — data validation and settings management
- **APScheduler** — background job scheduling
- **tldextract** — domain parsing
- **beautifulsoup4** — HTML parsing
- **tenacity** — retry logic
- **SQLite** (local/dev) / **PostgreSQL-compatible schema** (server)
- **pytest** — test runner

---

## Development Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Run all tests
python3 -m pytest tests/ -v

# Validate a specific country
python3 -m src.cli.validate_urls --country ICELAND --rate-limit 2

# Run a batch validation cycle
python3 -m src.cli.validate_urls_batch --batch-mode --batch-size 2

# Generate a validation report
python3 -m src.cli.generate_validation_report --output validation-report.md
```

---

## Conventions and Constraints

### Country Codes and Filenames

- Country codes use **UPPER_SNAKE_CASE** with country identifier suffix, e.g. `UNITED_KINGDOM_UK`
- Filenames use **lowercase-hyphenated** form, e.g. `united-kingdom-uk.toon`
- Use `src/lib/country_utils.py` helpers (`country_filename_to_code`, `country_code_to_filename`) for all conversions — never hardcode formats

### URL Validation

- URL validation tracks failures across sessions; a URL is **removed after 2 failures**
- No retry within the same scan session (by design)
- Redirects are followed and the final URL is recorded for future scans
- The async `httpx` event hooks must be `async` functions (not sync)

### Database / Storage

- Validation metadata lives in `data/metadata.db` (SQLite, **not committed**)
- Batch state is tracked in `validation_batch_state` table
- See `src/storage/schema.py` for full schema

### GitHub Actions

- Batch validation workflow: `.github/workflows/validate-urls-batch.yml` (runs every 2 hours)
- Workflow timeout: 110 minutes; CLI `max_runtime_seconds` = 50 × 60 (with a 10-minute buffer)
- Default batch size: **2 countries per batch**
- Artifacts (SQLite DB, validated TOON files) are **stored as workflow artifacts**, not committed

### TOON Files

- Original seed files (`*.toon`) are version-controlled
- Validated output files (`*_validated.toon`) are **excluded** from version control (see `.gitignore`)

---

## What AI Agents Should Do

- Follow existing code style and patterns; examine nearby files before introducing new patterns
- Run `python3 -m pytest tests/ -v` to verify changes do not break existing tests
- Keep commits focused and minimal; avoid reformatting unrelated code
- Update or add documentation in `docs/` when changing user-facing behaviour
- Use `src/lib/country_utils.py` for any country-code / filename conversions
- Respect rate limits in `src/services/url_validator.py` — do not bypass them
- When modifying the schema, update `src/storage/schema.py` and add a migration comment

## What AI Agents Should NOT Do

- Do not commit `data/metadata.db` or `*_validated.toon` files
- Do not push changes unless explicitly asked to do so by a human
- Do not add yourself as author or co-author in commits
- Do not bypass the two-failure URL-removal policy in the validator
- Do not scrape or reproduce third-party content that prohibits AI use (check `robots.txt` and terms)
- Do not introduce breaking changes to the TOON file format without updating all relevant parsers and tests

---

## Accessibility Commitment

This project tracks government accessibility-statement compliance. We hold ourselves to the same
standard: all documentation and data outputs must follow **WCAG 2.2 AA** guidelines. See
[ACCESSIBILITY.md](./ACCESSIBILITY.md) for details.

---

## Getting Help

- **Questions and discussions:** [GitHub Discussions](https://github.com/mgifford/eu-plus-government-scans/discussions)
- **Bugs and feature requests:** [GitHub Issues](https://github.com/mgifford/eu-plus-government-scans/issues)
- **Full documentation:** [`docs/`](./docs/)
