---
title: Data API
layout: page
---

This project publishes machine-readable JSON files via GitHub Pages so that
other tools and researchers can query the scan data programmatically.  No
authentication is needed; every endpoint is a plain HTTPS GET request.

---

## Base URL

```
https://mgifford.github.io/eu-plus-government-scans/
```

---

## Available Endpoints

The table below lists every JSON file served via GitHub Pages.  Files marked
**committed** are small enough to live in the repository and are always
available via HTTPS.  Files marked **artifact-only** are too large to commit
but can be downloaded from the GitHub Actions workflow run that produced them
(see [Accessing Artifact Files](#accessing-artifact-files) below).

| Endpoint | Availability | Description |
|----------|-------------|-------------|
| [`technology-index.json`](#technology-indexjson) | **committed** | Compact cross-reference: technology → page count, categories, per-country page counts. Ideal for finding which countries use a given technology. |
| [`third-party-tools-data.json`](#third-party-tools-datajson) | **committed** | Third-party JavaScript scan summary: top services, categories, per-country stats, and unknown host review queue. |
| [`technology-data.json`](#technology-datajson) | artifact-only | Full technology scan data with per-country page-level drilldowns. |
| [`social-media-data.json`](#social-media-datajson) | artifact-only | Full social-media scan data with per-URL evidence for every country. |
| [`accessibility-data.json`](#accessibility-datajson) | artifact-only | Full accessibility-statement scan data with per-URL evidence. |
| [`lighthouse-data.json`](#lighthouse-datajson) | artifact-only | Full Lighthouse audit data with per-URL scores. |
| [`lighthouse-data.csv`](#lighthouse-datacsv) | artifact-only | Same Lighthouse data as a flat CSV (UTF-8 BOM, opens in Excel). |

---

## technology-index.json

**URL:** `https://mgifford.github.io/eu-plus-government-scans/technology-index.json`

A compact cross-reference index generated from the technology scan database.
Every detected technology is listed with its total page count, detected
categories, and a per-country page count breakdown.  No per-URL data is
included; this keeps the file small enough to commit and serve directly.

Use this endpoint to answer questions like:
- _How many government pages use WordPress, and in which countries?_
- _Which countries have the most Drupal deployments?_
- _Which technologies appear under the "CMS" category?_

### Schema

```jsonc
{
  "generated_at": "2026-05-21 00:00 UTC",   // ISO-style UTC timestamp
  "base_url": "https://mgifford.github.io/eu-plus-government-scans/",
  "note": "...",

  // by_technology — keyed by technology name, sorted by page count descending
  "by_technology": {
    "WordPress": {
      "pages": 8762,                // total pages where this technology was detected
      "categories": ["Blogs", "CMS"],  // sorted list of Wappalyzer categories
      "by_country": {              // page count per country code, sorted alphabetically
        "FRANCE": 1234,
        "GERMANY": 567
      }
    }
    // … one entry per detected technology
  },

  // by_category — keyed by category name, sorted by page count descending
  "by_category": {
    "JavaScript libraries": {
      "pages": 54158,              // total pages with at least one tech in this category
      "technologies": ["Bootstrap", "jQuery", "jQuery Migrate"]  // sorted alphabetically
    }
    // … one entry per detected category
  }
}
```

### Example: find all countries using Drupal

```bash
curl -s https://mgifford.github.io/eu-plus-government-scans/technology-index.json \
  | python3 -c "
import json, sys
data = json.load(sys.stdin)
drupal = data['by_technology'].get('Drupal', {})
print(f'Total pages: {drupal.get(\"pages\", 0)}')
for country, count in sorted(drupal.get('by_country', {}).items(),
                              key=lambda x: -x[1]):
    print(f'  {country}: {count}')
"
```

### Example: list all CMS technologies

```bash
curl -s https://mgifford.github.io/eu-plus-government-scans/technology-index.json \
  | python3 -c "
import json, sys
data = json.load(sys.stdin)
cms = data['by_category'].get('CMS', {})
print('CMS technologies:', cms.get('technologies', []))
print('Total pages:', cms.get('pages', 0))
"
```

### JavaScript example

```javascript
const BASE = 'https://mgifford.github.io/eu-plus-government-scans/';

const res = await fetch(BASE + 'technology-index.json');
const data = await res.json();

// Which countries use jQuery most?
const jquery = data.by_technology['jQuery'];
const ranked = Object.entries(jquery.by_country)
  .sort(([, a], [, b]) => b - a)
  .slice(0, 5);
console.log('Top 5 jQuery countries:', ranked);

// All CMS technologies
const cmsTechs = data.by_category['CMS']?.technologies ?? [];
console.log('CMS technologies:', cmsTechs);
```

---

## third-party-tools-data.json

**URL:** `https://mgifford.github.io/eu-plus-government-scans/third-party-tools-data.json`

Summary of the third-party JavaScript scan: which external scripts and
services government pages load, how often, and from which countries.

### Schema (top-level keys)

```jsonc
{
  "generated_at": "...",
  "summary": {
    "total_batches": 225,
    "total_scanned": 14043,
    "total_reachable": 13119,
    "urls_with_scripts": 5991,
    "total_available": 82714,
    "identified_service_loads": 7788,
    "unique_services": 24,
    "unique_categories": 16,
    "first_scan": "...",
    "last_scan": "..."
  },
  "top_services": [
    {
      "name": "cdnjs (Cloudflare CDN)",
      "loads": 1926,
      "reachable_pages": 773,
      "prevalence_pct": 5.89
    }
    // …
  ],
  "top_categories": [
    { "name": "CDN", "loads": 4626 }
    // …
  ],
  "by_country": [
    {
      "country_code": "AUSTRIA",
      "total_scanned": 821,
      "total_reachable": 790,
      "urls_with_scripts": 266,
      "identified_service_loads": 44,
      "last_scan": "2026-05-16"
    }
    // …
  ],
  "unknown_hosts": [
    {
      "host": "ajax.aspnetcdn.com",
      "loads": 582,
      "reachable_pages": 287
    }
    // …
  ],
  "country_drilldowns": {
    "AUSTRIA": {
      "with_scripts": [
        {
          "page_url": "https://...",
          "scripts": [
            {
              "src": "https://cdnjs.cloudflare.com/...",
              "host": "cdnjs.cloudflare.com",
              "service_name": "cdnjs (Cloudflare CDN)",
              "categories": ["CDN"]
            }
          ]
        }
      ]
    }
  }
}
```

### JavaScript example

```javascript
const BASE = 'https://mgifford.github.io/eu-plus-government-scans/';

const res = await fetch(BASE + 'third-party-tools-data.json');
const data = await res.json();

// Top 10 external services
data.top_services.slice(0, 10).forEach(s => {
  console.log(`${s.name}: ${s.loads} loads on ${s.reachable_pages} pages`);
});

// Countries that load Google Analytics most
const gaCountries = data.by_country
  .filter(c => c.identified_service_loads > 0)
  .sort((a, b) => b.identified_service_loads - a.identified_service_loads)
  .slice(0, 5);
console.log('Top service-load countries:', gaCountries.map(c => c.country_code));
```

---

## technology-data.json

**Availability:** GitHub Actions artifact (`scan-progress-report-*`)

Full technology scan data including per-country page-level drilldowns
(one entry per scanned URL).  This file can exceed GitHub's 100 MB file-size
limit as scan coverage grows, so it is not committed to the repository.

### Schema (top-level keys)

```jsonc
{
  "generated_at": "...",
  "summary": { ... },          // same as technology-index.json summary
  "top_technologies": [ ... ], // [{name, pages, categories}]
  "top_categories": [ ... ],   // [{name, pages}]
  "by_country": [ ... ],       // per-country totals
  "country_drilldowns": {
    "GERMANY": {
      "scanned": [
        {
          "page_url": "https://...",
          "technologies": [
            { "name": "Nginx", "categories": ["Web servers"], "versions": ["1.24"] }
          ],
          "technology_names": ["Nginx"],
          "error_message": "",
          "last_scanned": "2026-05-19T..."
        }
      ],
      "detected": [ ... ]    // subset where at least one technology was found
    }
  }
}
```

Download from [GitHub Actions](https://github.com/mgifford/eu-plus-government-scans/actions)
→ **Generate Scan Progress Report** → latest completed run → **Artifacts**
→ `scan-progress-report-*` → `docs/technology-data.json`.

---

## social-media-data.json

**Availability:** GitHub Actions artifact (`scan-progress-report-*`)

Full social-media scan data.  Per-URL evidence showing which social platforms
(Twitter/X, Bluesky, Mastodon, etc.) each government page links to.

See [`docs/social-media.md`](social-media.md) for an overview of the scan
and field definitions.

---

## accessibility-data.json

**Availability:** GitHub Actions artifact (`scan-progress-report-*`)

Full accessibility-statement scan data.  Per-URL evidence showing whether each
page has an accessibility statement and where it was found.

See [`docs/accessibility-statements.md`](accessibility-statements.md) for
field definitions and methodology.

---

## lighthouse-data.json

**Availability:** GitHub Actions artifact (`scan-progress-report-*`)

Full Google Lighthouse audit results.  One entry per scanned URL with
performance, accessibility, best-practices, SEO, and PWA scores (0–100 scale).

See [`docs/lighthouse-results.md`](lighthouse-results.md) for methodology.

---

## lighthouse-data.csv

**Availability:** GitHub Actions artifact (`scan-progress-report-*`)

Same Lighthouse data as a flat CSV (UTF-8 BOM for correct Excel import).
Columns: `url`, `country_code`, `performance`, `accessibility`,
`best_practices`, `seo`, `pwa`, `scanned_at`.

---

## Accessing Artifact Files

Files marked **artifact-only** are uploaded after each
[Generate Scan Progress Report](https://github.com/mgifford/eu-plus-government-scans/actions/workflows/generate-scan-progress.yml)
workflow run and retained for 30 days.

**To download an artifact:**

1. Go to [Actions → Generate Scan Progress Report](https://github.com/mgifford/eu-plus-government-scans/actions/workflows/generate-scan-progress.yml)
2. Click the most recent completed run
3. Scroll to the **Artifacts** section at the bottom of the page
4. Download `scan-progress-report-*` — it contains all JSON and CSV data files

**To download via the GitHub API:**

```bash
# Find the latest artifact run ID
RUN_ID=$(gh api --paginate \
  "/repos/mgifford/eu-plus-government-scans/actions/artifacts?per_page=100&name=scan-progress-report" \
  --jq '.artifacts[] | select(.expired == false) | "\(.created_at) \(.id)"' \
  | sort -rk1 | head -1 | awk '{print $2}')

# Download and unzip
gh api "/repos/mgifford/eu-plus-government-scans/actions/artifacts/${RUN_ID}/zip" \
  > scan-data.zip
unzip scan-data.zip -d scan-data/
```

---

## Update Frequency

All JSON files are regenerated by the
[Generate Scan Progress Report](https://github.com/mgifford/eu-plus-government-scans/actions/workflows/generate-scan-progress.yml)
workflow, which runs **daily at 05:15 UTC** and after every major scan run.

| File | Committed to repo | Regenerated |
|------|-------------------|-------------|
| `technology-index.json` | ✅ Yes | Daily |
| `third-party-tools-data.json` | ✅ Yes | Daily |
| `technology-data.json` | ❌ Artifact only | Daily |
| `social-media-data.json` | ❌ Artifact only | Daily |
| `accessibility-data.json` | ❌ Artifact only | Daily |
| `lighthouse-data.json` | ❌ Artifact only | Daily |
| `lighthouse-data.csv` | ❌ Artifact only | Daily |

---

## CORS and Caching

GitHub Pages sets permissive CORS headers (`Access-Control-Allow-Origin: *`),
so all committed JSON files can be fetched directly from client-side JavaScript
running on any origin.

Responses are cached by GitHub's CDN.  To get the freshest data, add a cache-
busting query string or use conditional `If-None-Match` / `If-Modified-Since`
headers.

---

## Related Pages

- [Technology Scanning](technology-scanning.md) — methodology and summary tables
- [Third-Party JavaScript](third-party-tools.md) — external script analysis
- [Accessibility Statements](accessibility-statements.md)
- [Social Media](social-media.md)
- [Lighthouse Scanning](lighthouse-scanning.md)
- [Scan Progress Report](scan-progress.md)
