---
title: Lighthouse Scan Results
layout: page
---

<!-- LIGHTHOUSE_STATS_START -->

_Stats as of 2026-09-17 05:06 UTC — last scan: 2026-09-17_

**353** scan batches run

**23,920** of **87,696** available pages audited (**27.3%** coverage)
**19,423** successful audits (**81.2%** of audited)

**Overall average Lighthouse scores** (0–100 scale):

| Performance | Accessibility | Best Practices | SEO |
|:-----------:|:-------------:|:--------------:|:---:|
| 89 | 89 | 91 | 88 |

---

## Lighthouse Scores by Country

| Country | Audited | Available | Perf | A11y | Best Practices | SEO | Last Scan |
|---------|--------:|----------:|:----:|:----:|:--------------:|:---:|-----------|
| Austria | 822 | 822 | 88 | 90 | 91 | 89 | 2026-09-13 |
| Belgium | 1,075 | 1,329 | 87 | 91 | 91 | 90 | 2026-09-13 |
| Bulgaria | 352 | 353 | 86 | 81 | 88 | 88 | 2026-08-24 |
| Canada | 454 | 4,469 | 94 | 88 | 90 | 87 | 2026-09-13 |
| Croatia | 257 | 257 | 91 | 72 | 92 | 89 | 2026-08-24 |
| Czechia | 866 | 866 | 89 | 87 | 92 | 88 | 2026-09-13 |
| Denmark | 1,142 | 1,536 | 88 | 95 | 96 | 89 | 2026-09-13 |
| Estonia | 401 | 401 | 91 | 87 | 85 | 89 | 2026-08-25 |
| Finland | 199 | 199 | 86 | 94 | 96 | 87 | 2026-08-25 |
| France | 307 | 10,009 | 92 | 92 | 93 | 92 | 2026-09-14 |
| Germany | 1,073 | 6,599 | 91 | 91 | 97 | 88 | 2026-09-14 |
| Greece | 814 | 1,752 | 86 | 86 | 90 | 88 | 2026-09-15 |
| Hungary | 392 | 392 | 89 | 77 | 82 | 86 | 2026-08-25 |
| Iceland | 145 | 145 | 92 | 92 | 91 | 91 | 2026-08-25 |
| Ireland | 536 | 536 | 91 | 91 | 90 | 88 | 2026-09-13 |
| Italy | 1,576 | 5,351 | 88 | 88 | 93 | 87 | 2026-09-15 |
| Latvia | 405 | 803 | 87 | 86 | 91 | 85 | 2026-09-14 |
| Lithuania | 122 | 122 | 86 | 81 | 87 | 85 | 2026-08-26 |
| Luxembourg | 573 | 573 | 91 | 93 | 93 | 91 | 2026-09-14 |
| Malta | 610 | 610 | 89 | 85 | 78 | 82 | 2026-09-14 |
| Netherlands | 945 | 945 | 92 | 94 | 94 | 88 | 2026-09-15 |
| Norway | 249 | 249 | 91 | 93 | 92 | 89 | 2026-09-15 |
| Poland | 1,603 | 14,951 | 88 | 86 | 89 | 90 | 2026-09-16 |
| Portugal | 922 | 3,508 | 85 | 82 | 82 | 88 | 2026-09-16 |
| Cyprus | 29 | 29 | 81 | 86 | 83 | 85 | 2026-08-23 |
| Romania | 807 | 807 | 87 | 78 | 90 | 84 | 2026-09-15 |
| Slovakia | 442 | 442 | 90 | 87 | 90 | 88 | 2026-09-17 |
| Slovenia | 214 | 214 | 87 | 80 | 89 | 85 | 2026-08-24 |
| Spain | 1,312 | 6,091 | 82 | 75 | 76 | 82 | 2026-09-16 |
| Sweden | 1,496 | 1,702 | 90 | 93 | 92 | 87 | 2026-09-15 |
| Switzerland | 2,123 | 2,123 | 85 | 91 | 96 | 87 | 2026-09-17 |
| United Kingdom | 1,661 | 19,511 | 92 | 94 | 91 | 87 | 2026-09-17 |

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
