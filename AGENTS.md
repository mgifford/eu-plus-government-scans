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
# Install uv (recommended)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create and activate virtual environment
uv venv
source .venv/bin/activate

# Install dependencies with uv
uv pip install -r requirements.txt

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

### Python Dependency Management (uv)

- Use **uv** as the preferred Python package manager for local development and CI setup
- Keep dependency versions pinned in `requirements.txt` for reproducibility
- Use virtual environments (`uv venv`) and avoid system-wide installs
- Before upgrading dependencies, check vulnerability advisories and license impact
- Track dependency inventory and licenses in `SBOM.md`

### Measuring change over time

The relationship dataset describes the corpus **now**.  Two mechanisms make
change measurable, and both are load-bearing:

- **Edges are retired, not deleted.**  `AggregatedRelationship.active` goes
  false once every page that carried an edge has been re-scanned successfully
  without it.  Nothing used to remove an edge, so the dataset only grew and a
  government migrating away from a provider looked exactly like no change.  Only
  *successfully* scanned pages count as evidence — treating a failed fetch as
  removal would turn every outage into a false result.  Retired rows stay
  published for `RETIRED_EDGE_RETENTION_DAYS`, then drop.
- **Dated snapshots.**  `src/cli/generate_snapshot.py` writes one compact file
  per day to `docs/data/snapshots/`.  Even a perfectly-run scanner cannot
  reconstruct "what share of this country's agencies used this provider in
  March" from the live dataset, because it holds no periodic record.  Snapshots
  are the only thing that can answer it, so they are worth writing long before
  anything reads them.

Any consumer reporting the current state must skip rows where `active` is
false; `generate_dependency_matrix.py` and `generate_snapshot.py` both do.

### Scan metadata artifacts

Scan state moves between workflow runs as a GitHub Actions artifact.  **Each
workflow owns exactly one artifact and writes only that one.**  Previously every
scan workflow downloaded, mutated and re-uploaded the same `validation-metadata`
artifact, which is a last-writer-wins race — four writers start together at
00:00 UTC alone, and whichever finished last discarded the others' results.

The ownership map lives in `src/lib/metadata_merge.py` (`ARTIFACT_TABLES`); it
is the single source of truth and the workflows are tested against it.  When
adding a scanner:

- Give it its own artifact and list the tables it owns there.
- Merge on the way in (`metadata_artifact merge`) so cross-scanner skip logic
  sees every scanner's results.
- Extract on the way out (`metadata_artifact extract`) so the upload carries
  only the tables you own.  Uploading the whole working database republishes a
  stale snapshot of everyone else's tables.

Merging is safe because result tables are append-only and keyed by
`(url, scan_id)`; two scanners cannot collide on a key.  Any table that is
`UPDATE`d in place must stay under a single artifact whose writers share a
concurrency group — that is why the four URL-validation workflows share
`validation-metadata` and the `validation-metadata-writers` group.

### GitHub Actions

- Batch validation workflow: `.github/workflows/validate-urls-batch.yml` (runs every 2 hours)
- Workflow timeout: 110 minutes; CLI `max_runtime_seconds` = 50 × 60 (with a 10-minute buffer)
- Default batch size: **2 countries per batch**
- Artifacts (SQLite DB, validated TOON files) are **stored as workflow artifacts**, not committed

### Independent Verification

Every aggregate number published in a report must be backed by machine-readable
source data so that any reader can independently verify the claim:

- **JSON** (e.g. `docs/lighthouse-data.json`) — full dataset including per-country
  summaries and, crucially, a `by_url` array containing one entry per scanned URL.
  The aggregate scores in the country table must be reproducible by grouping the
  `by_url` rows and recalculating averages.
- **CSV** (e.g. `docs/lighthouse-data.csv`) — the same per-URL rows exported as a
  spreadsheet-friendly flat file, one row per URL.  Scores are on the 0–100 scale.
  The CSV includes a UTF-8 BOM so it opens correctly in Excel without an import wizard.

Both files are uploaded as GitHub Actions workflow artifacts (not committed to the
repository, as they can be large).  New report generators must follow this pattern:
produce the aggregate Markdown page **and** the machine-readable backing data files.

### Large committed datasets

GitHub refuses to accept any pushed file larger than **100 MiB**, so a dataset that
is committed (rather than kept as an artifact) must not be allowed to grow into that
ceiling.  `docs/data/relationships.jsonl` did exactly that — it reached 100.00 MiB,
a few kilobytes short of breaking every push from the relationship scan workflow.

It is now split across `docs/data/relationships/`, one shard per source TLD, capped
at 32 MiB each and listed in `index.json`.  See `src/lib/relationship_shards.py`.
Any new committed dataset that grows on each scan cycle should reuse that module
rather than writing a single unbounded file.  Two properties matter:

- **Deterministic ordering.** git stores each revision as a delta against the last,
  so stable row order turns a scan that changes a few rows into a small delta
  instead of a full rewrite of every shard.
- **A size guard in the workflow.** Fail the run when a shard crosses the safety
  threshold, so the problem surfaces as a red job rather than as a rejected push
  inside a `[skip ci]` commit that nobody is watching.

---

- Original seed files (`*.toon`) are version-controlled
- Validated output files (`*_validated.toon`) are **excluded** from version control (see `.gitignore`)

---

## Python Coding Standards

All Python code in this repository must follow the guidelines in
[PYTHON_GUIDANCE.md](./PYTHON_GUIDANCE.md).  Key points:

- Use type annotations on every function signature.
- Add docstrings to every module, class, and public function; document private
  helpers when the behavior is not obvious (Google style preferred).
- Target functions ≤ 50 lines where that improves readability; split longer
  ones into focused helpers when practical.
- Never use a bare `except:`; always catch specific exception types.
- Only use `f"..."` strings when they actually interpolate a variable.
- Run `ruff check` on the Python files you change before committing, and move
  touched code toward full guide compliance.

`ruff check src/ tests/ scripts/` is clean and is enforced on every pull
request by `.github/workflows/python-ci.yml`, so keep it that way.

The rest of the guide — type annotations, docstrings, function length — is not
machine-checked and is still applied **incrementally**:

- New Python files should follow the guide in full.
- Modified Python files should be improved toward the guide as part of the
  change being made.
- Avoid repository-wide style churn unless a human maintainer explicitly asks
  for a cleanup pass.

---

## What AI Agents Should Do

- Follow existing code style and patterns; examine nearby files before introducing new patterns
- Follow the Python coding standards described in [PYTHON_GUIDANCE.md](./PYTHON_GUIDANCE.md)
- Run `python3 -m pytest tests/ -v` to verify changes do not break existing tests
- Keep commits focused and minimal; avoid reformatting unrelated code
- Update or add documentation in `docs/` when changing user-facing behaviour
- Use `src/lib/country_utils.py` for any country-code / filename conversions
- Respect rate limits in `src/services/url_validator.py` — do not bypass them
- When modifying the schema, update `src/storage/schema.py` and add a migration comment
- **Disclose AI use:** whenever you use an AI tool to contribute to this repository — whether
  for writing code, tests, or documentation — update the **AI Disclosure** section in
  `README.md` to record which LLM(s) were used, what they were used for (build-time
  assistance, runtime inference, browser-based features, etc.), and whether any AI runs as
  part of the application at runtime

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

- **Questions and discussions:** [GitHub Issues](https://github.com/mgifford/eu-plus-government-scans/issues)
- **Bugs and feature requests:** [GitHub Issues](https://github.com/mgifford/eu-plus-government-scans/issues)
- **Full documentation:** [`docs/`](./docs/)
