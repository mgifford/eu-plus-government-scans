---
title: Lighthouse Scan Results
layout: page
---

<!-- LIGHTHOUSE_STATS_START -->

_Stats as of 2026-07-19 05:10 UTC — last scan: 2026-07-19_

**193** scan batches run

**20,662** of **82,714** available pages audited (**25.0%** coverage)
**19,036** successful audits (**92.1%** of audited)

**Overall average Lighthouse scores** (0–100 scale):

| Performance | Accessibility | Best Practices | SEO |
|:-----------:|:-------------:|:--------------:|:---:|
| 89 | 89 | 91 | 88 |

---

## Lighthouse Scores by Country

| Country | Audited | Available | Perf | A11y | Best Practices | SEO | Last Scan |
|---------|--------:|----------:|:----:|:----:|:--------------:|:---:|-----------|
| Austria | 821 | 821 | 89 | 90 | 91 | 89 | 2026-07-18 |
| Belgium | 1,309 | 1,309 | 88 | 91 | 91 | 90 | 2026-07-18 |
| Bulgaria | 291 | 291 | 86 | 80 | 88 | 88 | 2026-07-03 |
| Croatia | 233 | 233 | 90 | 72 | 92 | 90 | 2026-07-03 |
| Czechia | 843 | 843 | 91 | 87 | 91 | 88 | 2026-07-18 |
| Denmark | 1,521 | 1,521 | 89 | 94 | 96 | 89 | 2026-07-18 |
| Estonia | 396 | 396 | 92 | 87 | 86 | 89 | 2026-07-04 |
| Finland | 180 | 180 | 88 | 94 | 95 | 88 | 2026-07-04 |
| France | 502 | 10,007 | 90 | 91 | 92 | 91 | 2026-07-16 |
| Germany | 1,895 | 6,555 | 91 | 91 | 96 | 88 | 2026-07-16 |
| Greece | 1,241 | 1,748 | 87 | 86 | 91 | 88 | 2026-07-17 |
| Hungary | 390 | 390 | 88 | 76 | 81 | 86 | 2026-07-04 |
| Iceland | 139 | 139 | 90 | 91 | 91 | 91 | 2026-07-04 |
| Ireland | 522 | 522 | 91 | 91 | 90 | 87 | 2026-07-19 |
| Italy | 1,019 | 5,338 | 87 | 88 | 94 | 88 | 2026-07-17 |
| Latvia | 802 | 802 | 83 | 87 | 89 | 88 | 2026-07-17 |
| Lithuania | 120 | 120 | 88 | 81 | 87 | 85 | 2026-07-05 |
| Luxembourg | 571 | 571 | 91 | 93 | 93 | 91 | 2026-07-17 |
| Malta | 608 | 608 | 88 | 85 | 79 | 81 | 2026-07-17 |
| Netherlands | 937 | 937 | 92 | 94 | 93 | 88 | 2026-07-18 |
| Norway | 239 | 239 | 91 | 93 | 92 | 90 | 2026-07-02 |
| Poland | 1,607 | 14,938 | 88 | 86 | 88 | 90 | 2026-07-17 |
| Portugal | 1,241 | 3,503 | 83 | 83 | 85 | 89 | 2026-07-18 |
| Cyprus | 24 | 24 | 82 | 86 | 82 | 87 | 2026-07-02 |
| Romania | 216 | 799 | 87 | 75 | 88 | 81 | 2026-07-18 |
| Slovakia | 434 | 434 | 86 | 87 | 90 | 88 | 2026-07-03 |
| Slovenia | 200 | 200 | 88 | 79 | 89 | 85 | 2026-07-03 |
| Spain | 396 | 6,069 | 86 | 87 | 87 | 87 | 2026-07-18 |
| Sweden | 804 | 1,558 | 89 | 91 | 92 | 85 | 2026-07-19 |
| Switzerland | 649 | 2,117 | 86 | 89 | 96 | 88 | 2026-07-14 |
| United Kingdom | 512 | 19,502 | 91 | 93 | 91 | 86 | 2026-07-15 |

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
