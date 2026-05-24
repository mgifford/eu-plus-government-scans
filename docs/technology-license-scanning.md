---
title: Technology License Scanning
layout: page
---

# Technology License Scanning

## Introduction

The technology license enrichment pipeline adds upstream license metadata on top
of the existing technology detection index. It does not replace the technology
scanner; it classifies detected technology names with curated, best-effort
license information for downstream reporting.

## Important Caveats

This pipeline classifies upstream project licenses, not whether a specific
deployment is compliant with those licenses. SaaS and cloud services are not
"OSI-licensed" just because they may depend on open source internally. Manual
review is required before making public claims, and confidence levels should be
read as part of every result.

## License Status Values

| Value | Meaning |
|---|---|
| `osi_approved` | Best-effort match to an OSI-approved upstream license. |
| `proprietary` | Commercial or closed-source software with no OSI-approved license for the detected product. |
| `source_available` | Source may be available, but the license is not treated here as OSI-approved. |
| `not_applicable_service` | Hosted service, CDN, API, or SaaS detection where package-style OSI licensing does not cleanly apply. |
| `unknown` | No reliable classification yet; manual review is needed. |

## Confidence Levels

- **High** — widely documented and stable mapping between the detected name and
  its upstream license.
- **Medium** — generally reliable, but the detected name may span multiple
  products, versions, or licensing models.
- **Low** — weak signal, generic category, or incomplete evidence.

## Data Sources

The first source is the curated override file at
`data/technology-license-overrides.json`. Future enrichment can add cached or
live lookups from package and repository ecosystems such as GitHub, npm, and
Packagist, but those sources still require review before publication.

## Running the Enrichment

```bash
python3 -m src.cli.enrich_technology_licenses \
    --input docs/technology-index.json \
    --output docs/technology-license-index.json \
    --overrides data/technology-license-overrides.json \
    --summary docs/technology-license-summary.md
```

## Output Files

- `docs/technology-license-index.json` — machine-readable enrichment output
  with per-technology license metadata and summary stats.
- `docs/technology-license-summary.md` — human-readable markdown summary of the
  current enrichment results.
