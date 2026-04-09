---
title: Lighthouse Scanning
layout: page
---

This page describes how the project runs Google Lighthouse audits on European government
websites to measure performance, accessibility, best practices, SEO, and Progressive Web App
(PWA) quality.

---

## Overview

The Lighthouse scanner runs the [Google Lighthouse CLI](https://github.com/GoogleChrome/lighthouse)
against each government page URL and extracts the five headline category scores:

| Category | What it measures |
|---|---|
| **Performance** | Page speed and Core Web Vitals (LCP, FID, CLS, etc.) |
| **Accessibility** | WCAG-aligned accessibility checks (colour contrast, ARIA labels, keyboard navigation, …) |
| **Best Practices** | Security headers, HTTPS, modern web APIs, console errors |
| **SEO** | Search-engine crawlability, meta tags, structured data |
| **PWA** | Progressive Web App criteria (service worker, offline capability, installability) |

All scores are on a **0–100** scale (stored internally as 0.0–1.0).

---

## Usage

### Prerequisites

```bash
# Install the Lighthouse CLI globally
npm install -g lighthouse

# Chromium must also be available (pre-installed on ubuntu-latest GitHub runners)
```

### Scan a single country

```bash
python3 -m src.cli.scan_lighthouse --country ICELAND
```

### Scan all countries

```bash
python3 -m src.cli.scan_lighthouse --all
```

### Scan all countries with a runtime cap (recommended for CI)

```bash
python3 -m src.cli.scan_lighthouse --all --max-runtime 110 --rate-limit 0.2
```

### Command-line options

| Option | Default | Description |
|---|---|---|
| `--country CODE` | — | Country code to scan (e.g. `FRANCE`, `ICELAND`) |
| `--all` | — | Scan all countries in the TOON directory |
| `--toon-dir PATH` | `data/toon-seeds/countries` | Directory with `.toon` seed files |
| `--rate-limit N` | `0.2` | Maximum Lighthouse runs per second (0.2 = one every 5 s) |
| `--max-runtime N` | `0` (no limit) | Maximum runtime in minutes.  The scanner stops gracefully before this limit so that partial results can be saved.  Set to ~10 minutes less than the GitHub Actions `timeout-minutes` value. |
| `--lighthouse-path PATH` | `lighthouse` | Path to the Lighthouse binary (defaults to `PATH` lookup) |

---

## GitHub Actions

The **Scan Lighthouse** workflow (`.github/workflows/scan-lighthouse.yml`) runs automatically
once a week (Sunday at 04:00 UTC) and can also be triggered manually from the Actions tab:

1. Go to **Actions → Scan Lighthouse → Run workflow**
2. Optionally enter a country code (leave blank to scan all countries)
3. Optionally adjust the rate limit

### Why weekly?

Lighthouse is slow (~30–90 s per URL).  At the default 0.2 req/s rate (one URL every 5 s) a
two-hour run covers roughly 1,400 URLs.  The full corpus of ~82k URLs takes many weeks at this
rate; a weekly schedule keeps the data reasonably fresh without placing sustained load on
government servers.  Consider bumping `--rate-limit` for faster initial coverage.

### Artifacts uploaded after each run

| Artifact | Contents |
|---|---|
| `lighthouse-scan-<run_number>` | `data/metadata.db`, scan output log, annotated `*_lighthouse.toon` files |
| `validation-metadata` | `data/metadata.db` (shared with URL validation, social media, and tech scans) |

---

## Output

### Annotated TOON file

Each page entry in the output `*_lighthouse.toon` file gains a `lighthouse` field:

```json
{
  "url": "https://example.gov/",
  "is_root_page": true,
  "lighthouse": {
    "performance": 0.95,
    "accessibility": 0.87,
    "best_practices": 1.0,
    "seo": 0.92,
    "pwa": 0.0
  }
}
```

If the Lighthouse audit failed for a URL, a `lighthouse_error` field is added instead:

```json
{
  "url": "https://unreachable.gov/",
  "lighthouse_error": "Lighthouse timed out after 120s"
}
```

### Database table

Results are stored in the `url_lighthouse_results` table:

| Column | Type | Description |
|---|---|---|
| `url` | TEXT | Page URL |
| `country_code` | TEXT | Country identifier |
| `scan_id` | TEXT | Unique scan run ID |
| `performance_score` | REAL | Performance score (0.0–1.0), NULL if not available |
| `accessibility_score` | REAL | Accessibility score (0.0–1.0), NULL if not available |
| `best_practices_score` | REAL | Best Practices score (0.0–1.0), NULL if not available |
| `seo_score` | REAL | SEO score (0.0–1.0), NULL if not available |
| `pwa_score` | REAL | PWA score (0.0–1.0), NULL if not available |
| `error_message` | TEXT | Error message (if audit failed) |
| `scanned_at` | TEXT | ISO-8601 timestamp |

Query example:

```sql
SELECT url, accessibility_score * 100 AS accessibility
FROM url_lighthouse_results
WHERE country_code = 'ICELAND'
ORDER BY accessibility_score DESC;
```

---

## Architecture

```
scan-lighthouse.yml (GitHub Actions — weekly + manual)
    ↓
scan_lighthouse.py (CLI)
    ↓
LighthouseScannerJob.scan_country()
    ↓
LighthouseScanner.scan_urls_batch()
    ↓
For each URL:
    subprocess: lighthouse <url> --output=json --output-path=stdout
    ↓
_parse_lighthouse_output()  →  5 category scores
    ↓
Save to url_lighthouse_results table (incremental, per URL)
    ↓
Write *_lighthouse.toon output file
```

---

## Notes

- **Rate limiting** is applied between audits to avoid overloading government servers.
  The default is 0.2 runs/s (one URL every 5 s), much slower than other scanners because
  Lighthouse is CPU-intensive and drives a full headless Chrome session.
- Lighthouse requires **Chrome or Chromium** to be installed.  On GitHub Actions
  `ubuntu-latest` runners, Chromium is pre-installed.
- Failed Lighthouse audits do **not** remove a URL from future scans — errors are recorded
  but the URL is kept for subsequent validation cycles.
- Results are persisted **incrementally** (one URL at a time) so that partial results are
  preserved even if the GitHub Actions job times out.
- The `*_lighthouse.toon` output files are excluded from version control (see `.gitignore`).
- Lighthouse measures page quality at scan time; scores can vary between runs due to network
  conditions and server load.
