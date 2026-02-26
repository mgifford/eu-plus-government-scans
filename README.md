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
- `src/cli/validate_urls.py` - CLI interface for running scans

Key features:
- Validates URLs and tracks HTTP status codes and errors
- Records and follows redirects, updating URLs for future scans
- Tracks failure counts: first failure is noted, second failure removes URL
- No retry within same scan session
- Supports quarterly validation runs

See [docs/url-validation-scanner.md](docs/url-validation-scanner.md) for usage instructions.

Quick start:

```bash
# Install dependencies
pip install -r requirements.txt

# Validate a specific country
python3 -m src.cli.validate_urls --country iceland --rate-limit 2

# Validate all countries
python3 -m src.cli.validate_urls --all --rate-limit 2
```

## Next steps

- Continue implementation by work package (`WP02`, `WP03`, ...)
- Use TOON seeds as source inputs for country scans
- Refine statement detection confidence and multilingual glossary coverage
