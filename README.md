# eu-plus-government-scans

Scans and seed datasets for finding accessibility statements on government websites,
with a Europe-first scope (plus selected non-EU countries like UK and Switzerland).

## What is in this repository

- Planning and implementation artifacts for feature `001-eu-government-accessibility-statement-discovery`
- Imported government domain/page source lists from Google Sheets
- Country-split TOON seed files that include domains and page URLs

## Data imports

Imported CSV source sheets are stored under:

- `data/imports/google_sheets/`
- `data/imports/government_domains_pages_gid_242285945.csv` (Canada list)

Useful generated summaries:

- `data/imports/google_sheets/manifest.csv`
- `data/imports/google_sheets/summary.json`
- `data/imports/google_sheets/coverage_check.json`
- `data/imports/google_sheets/all_sheets_merged.csv`

## TOON seed outputs

All-country seed files:

- `data/toon-seeds/countries/*.toon`
- `data/toon-seeds/index.json`

Review bundles:

- EU-only bundle: `data/toon-seeds/eu-only/countries/*.toon`
- EU-only index: `data/toon-seeds/eu-only/index.json`
- UK + Switzerland bundle: `data/toon-seeds/uk-ch/countries/*.toon`
- UK + Switzerland index: `data/toon-seeds/uk-ch/index.json`

Each `.toon` seed currently contains, per country:

- `domains[]` keyed by canonical domain
- `pages[]` including URL and root-page flag (plus score fields when present)
- `source_tabs[]` provenance references (`sheet_id`, `gid`, source URL)

## WP01 foundation implementation

Initial backend foundation for the feature is included (WP01):

- `src/lib/settings.py` runtime settings and validation
- `src/services/source_ingest.py` source ingestion adapters
- `src/services/domain_normalizer.py` hostname normalization helpers
- `src/storage/schema.py` metadata schema bootstrap + migration seed
- Unit/integration tests under `tests/`

## URL Validation Scanner

A URL validation scanner is available to validate government site accessibility from TOON files:

- `src/services/url_validator.py` - Async URL validation with redirect tracking
- `src/jobs/url_validation_scanner.py` - Batch scanner for TOON files
- `src/cli/validate_urls.py` - CLI interface for running scans (legacy)
- `src/cli/validate_urls_batch.py` - **New batched CLI for large-scale validation**
- `src/cli/generate_validation_report.py` - Generate validation reports from database

Key features:
- Validates URLs and tracks HTTP status codes and errors
- Records and follows redirects, updating URLs for future scans
- Tracks failure counts: first failure is noted, second failure removes URL
- No retry within same scan session
- **Batched processing** - Handle 80k+ URLs without timeout
- **GitHub Issue tracking** - Monitor progress across multiple runs
- **Automated cron scheduling** - Run every 2 hours automatically

### Batched Validation (Recommended)

For large-scale validation (all countries), use the **batched system** which:
- Processes countries in small batches (default: 5 at a time)
- Runs automatically every 2 hours via GitHub Actions cron
- Tracks progress in a GitHub Issue
- Never times out (spreads work over multiple days)
- Fully resumable if interrupted

See **[docs/batched-validation.md](docs/batched-validation.md)** for complete documentation.

Quick start:
```bash
# Process next batch of countries (creates GitHub issue)
python3 -m src.cli.validate_urls_batch --batch-mode --create-issue

# Process specific batch size
python3 -m src.cli.validate_urls_batch --batch-mode --batch-size 10
```

**Workflows:**
- `.github/workflows/validate-urls-batch.yml` - Runs every 2 hours (automatic)
- `.github/workflows/reopen-validation-cycle.yml` - Starts new cycles quarterly

### Single Country / Legacy Validation

For validating individual countries or small sets:

**GitHub Action (UI-based):**

The easiest way to run single-country validations:

1. Go to the **Actions** tab in this repository
2. Select **"Validate Government URLs"**
3. Click **"Run workflow"** and optionally specify a country
4. View results in the workflow summary and download detailed reports

See [docs/github-action-validation.md](docs/github-action-validation.md) for full instructions.

**CLI Usage:**

For local or manual validation:

```bash
# Install dependencies
pip install -r requirements.txt

# Validate a specific country
python3 -m src.cli.validate_urls --country ICELAND --rate-limit 2

# Validate all countries (may timeout - use batch mode instead)
python3 -m src.cli.validate_urls --all --rate-limit 2

# Generate a report from validation results
python3 -m src.cli.generate_validation_report --output validation-report.md
```

See [docs/url-validation-scanner.md](docs/url-validation-scanner.md) for detailed CLI usage.

## Next steps

- Continue implementation by work package (`WP02`, `WP03`, ...)
- Use TOON seeds as source inputs for country scans
- Refine statement detection confidence and multilingual glossary coverage

## Data Caching and Storage

### Validation Metadata Database

The validation system uses an SQLite database (`data/metadata.db`) to track:
- URL validation results (status codes, errors, redirect chains)
- Failure counts across scans (remove URLs after 2 failures)
- Batch processing state (cycle tracking, country progress)

**Storage Location:**
- **NOT committed to the repository** (excluded in `.gitignore`)
- Stored as a **GitHub Actions artifact** named `validation-metadata`
- Artifact retention: **90 days**
- Automatically downloaded at the start of each workflow run
- Automatically uploaded at the end of each workflow run

This approach ensures:
- State persists across workflow runs without bloating the repository
- Failed URLs are consistently tracked and eventually removed
- Batch validation cycles can resume after any interruption
- No merge conflicts or version control issues with binary database files

**Viewing Artifacts:**
1. Go to a completed workflow run in the **Actions** tab
2. Scroll to the **Artifacts** section at the bottom
3. Download `validation-metadata` to inspect the database locally

### Validated TOON Files

Updated TOON files with validation results are also **not committed**:
- Pattern: `data/toon-seeds/countries/*_validated.toon`
- Excluded in `.gitignore`
- Generated during validation runs
- Contain validation metadata (status codes, redirects, etc.)

Only the original seed TOON files (without `_validated` suffix) are version controlled.
