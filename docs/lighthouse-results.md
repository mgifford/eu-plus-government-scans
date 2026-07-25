---
title: Lighthouse Scan Results
layout: page
---

<!-- LIGHTHOUSE_STATS_START -->

_Stats as of 2026-07-25 03:24 UTC — last scan: 2026-07-25_

**35** scan batches run

**5,230** of **87,696** available pages audited (**6.0%** coverage)
**4,794** successful audits (**91.7%** of audited)

**Overall average Lighthouse scores** (0–100 scale):

| Performance | Accessibility | Best Practices | SEO |
|:-----------:|:-------------:|:--------------:|:---:|
| 89 | 86 | 90 | 87 |

---

## Lighthouse Scores by Country

| Country | Audited | Available | Perf | A11y | Best Practices | SEO | Last Scan |
|---------|--------:|----------:|:----:|:----:|:--------------:|:---:|-----------|
| Austria | 316 | 822 | 87 | 90 | 93 | 85 | 2026-07-23 |
| Belgium | 134 | 1,329 | 86 | 89 | 91 | 90 | 2026-07-24 |
| Bulgaria | 352 | 353 | 87 | 81 | 88 | 87 | 2026-07-22 |
| Croatia | 257 | 257 | 92 | 72 | 92 | 89 | 2026-07-22 |
| Czechia | 449 | 866 | 91 | 86 | 91 | 87 | 2026-07-24 |
| Denmark | 453 | 1,536 | 88 | 94 | 97 | 90 | 2026-07-24 |
| Estonia | 401 | 401 | 91 | 87 | 86 | 89 | 2026-07-23 |
| Finland | 199 | 199 | 86 | 94 | 96 | 87 | 2026-07-23 |
| Hungary | 392 | 392 | 89 | 77 | 82 | 86 | 2026-07-23 |
| Iceland | 145 | 145 | 93 | 92 | 91 | 91 | 2026-07-23 |
| Ireland | 316 | 536 | 92 | 90 | 90 | 86 | 2026-07-24 |
| Latvia | 316 | 803 | 86 | 85 | 90 | 84 | 2026-07-25 |
| Lithuania | 122 | 122 | 86 | 81 | 87 | 85 | 2026-07-24 |
| Luxembourg | 77 | 573 | 89 | 95 | 96 | 95 | 2026-07-22 |
| Malta | 282 | 610 | 90 | 85 | 79 | 83 | 2026-07-22 |
| Netherlands | 30 | 945 | 84 | 94 | 95 | 84 | 2026-07-23 |
| Norway | 249 | 249 | 90 | 93 | 92 | 89 | 2026-07-21 |
| Cyprus | 29 | 29 | 81 | 86 | 84 | 86 | 2026-07-21 |
| Romania | 51 | 807 | 81 | 72 | 87 | 79 | 2026-07-23 |
| Slovakia | 312 | 442 | 91 | 87 | 91 | 88 | 2026-07-22 |
| Slovenia | 214 | 214 | 86 | 80 | 89 | 85 | 2026-07-22 |
| Sweden | 136 | 1,702 | 89 | 90 | 88 | 86 | 2026-07-23 |

> Scores are averages across all successfully audited URLs, displayed as 0–100 (Lighthouse stores scores as 0.0–1.0 internally).

---

📥 Machine-readable results: [Download machine-readable Lighthouse data (JSON)](lighthouse-data.json) · [Download per-URL Lighthouse data (CSV)](lighthouse-data.csv)

<!-- LIGHTHOUSE_STATS_END -->

---

## Overview

The Lighthouse scanner runs the [Google Lighthouse CLI](https://github.com/GoogleChrome/lighthouse)
against each government page URL and extracts four headline category scores:

| Category | What it measures |
|---|---|
| **Performance** | Page speed and Core Web Vitals (LCP, FID, CLS, etc.) |
| **Accessibility** | WCAG-aligned accessibility checks (colour contrast, ARIA labels, keyboard navigation, …) |
| **Best Practices** | Security headers, HTTPS, modern web APIs, console errors |
| **SEO** | Search-engine crawlability, meta tags, structured data |

All scores are on a **0–100** scale (stored internally as 0.0–1.0).

> **Note:** PWA (Progressive Web App) audits are skipped for government sites because
> they are not relevant to the EU Web Accessibility Directive requirements and omitting
> them reduces per-URL scan time.

---

## How to Interpret the Scores

Lighthouse scores are based on a single page load at the time of the audit.
Scores can vary between runs due to network conditions and server load, so the
values shown here are averages across all successfully audited URLs for each
country.

- **90–100**: Good
- **50–89**: Needs improvement
- **0–49**: Poor

For a detailed breakdown of individual audit failures, download the
[machine-readable Lighthouse data (JSON)](lighthouse-data.json) or
the [per-URL Lighthouse data (CSV)](lighthouse-data.csv).

---

## Running a Scan

### Via GitHub Actions (recommended)

1. Go to [Actions → Scan Lighthouse](https://github.com/mgifford/eu-plus-government-scans/actions/workflows/scan-lighthouse.yml)
2. Click **Run workflow**
3. Optionally enter a country code (e.g. `ICELAND`) or leave blank to scan all
4. Optionally adjust the rate limit, concurrency, and skip-recently-scanned-days parameters

The scan runs automatically every day at 03:00 UTC.  With `--concurrency 3`
and skipping URLs audited within the last 30 days, each daily run covers
roughly 750–1,000 URLs while ensuring every URL is refreshed at least monthly.

### Via the command line

```bash
# Scan a single country
python3 -m src.cli.scan_lighthouse --country ICELAND

# Scan all countries (with a 110-minute runtime cap and 3 concurrent processes)
python3 -m src.cli.scan_lighthouse \
  --all \
  --max-runtime 110 \
  --concurrency 3 \
  --skip-recently-scanned-days 30 \
  --only-categories performance,accessibility,best-practices,seo \
  --throttling-method provided
```

---

## Architecture

```mermaid
flowchart TD
    A["scan-lighthouse.yml\n(GitHub Actions — daily at 03:00 UTC)"]
    A --> B["scan_lighthouse.py (CLI)"]
    B --> C["LighthouseScannerJob.scan_country()"]
    C --> D["Filter out recently-scanned URLs\n(_get_recently_scanned_urls)"]
    D --> E["LighthouseScanner.scan_urls_batch()\n(asyncio.Semaphore — up to 3 concurrent)"]
    E --> F["For each URL (parallel)"]
    F --> G["subprocess: lighthouse URL --output=json\n--only-categories=performance,accessibility,\nbest-practices,seo --throttling-method=provided"]
    G --> H["_parse_lighthouse_output() → 4 category scores"]
    H --> I["Save to url_lighthouse_results table\n(incremental, per URL)"]
    I --> J["Write *_lighthouse.toon output file"]
```

---

## Related Pages

- [Lighthouse Scanning Documentation](lighthouse-scanning.md) — full technical reference
- [Scan Progress Report](scan-progress.md) — overview of all scan types
- [Accessibility Statement Scanning](accessibility-statements.md) — EU Directive compliance
