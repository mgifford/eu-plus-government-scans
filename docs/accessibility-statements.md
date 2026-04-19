---
title: Accessibility Statement Scanning
layout: page
---

<!-- ACCESSIBILITY_STATS_START -->

_Stats as of 2026-04-19 05:55 UTC — last scan: 2026-04-19_

**22** scan batches run

**17,337** of **82,714** available pages scanned (**21.0%** coverage)
**16,083** of **17,337** scanned pages were reachable (**92.8%**)
**7,861** of **16,083** reachable pages have an accessibility statement (**48.9%**)
**6,786** pages have the statement link in the footer (**86.3%** of pages with a statement)

📥 Machine-readable results are available as the [accessibility-data.json artifact (machine-readable JSON)](https://github.com/mgifford/eu-plus-government-scans/actions/workflows/generate-scan-progress.yml).

Each country entry in the JSON file includes page-level evidence for pages with and without accessibility statements, plus a per-domain summary you can share to validate the published counts.

> Hover or focus any non-zero count in the country table to preview the matching pages. If there are 20 or fewer URLs, the preview shows all of them; otherwise it shows a short sample. Full machine-readable data is available as the [accessibility-data.json artifact (machine-readable JSON)](https://github.com/mgifford/eu-plus-government-scans/actions/workflows/generate-scan-progress.yml).

---

## Accessibility Statement Scan by Country

| Country | Scanned | Available | Reachable | Has Statement | In Footer | Statement % | Scan Period |
|---------|---------|-----------|-----------|--------------|-----------|------------|-------------|
| Austria | 821 | 821 | 788 | 547 | 517 | 69.4% | Apr 2026 |
| Belgium | 1,309 | 1,309 | 1,224 | 493 | 450 | 40.3% | Apr 2026 |
| Bulgaria | 291 | 291 | 268 | 61 | 59 | 22.8% | Apr 2026 |
| Croatia | 233 | 233 | 232 | 86 | 62 | 37.1% | Apr 2026 |
| Czechia | 351 | 843 | 342 | 157 | 138 | 45.9% | Apr 2026 |
| Denmark | 1,521 | 1,521 | 1,503 | 1,028 | 1,008 | 68.4% | Apr 2026 |
| Estonia | 396 | 396 | 382 | 141 | 71 | 36.9% | Apr 2026 |
| Finland | 180 | 180 | 172 | 112 | 105 | 65.1% | Apr 2026 |
| France | 747 | 10,007 | 699 | 198 | 195 | 28.3% | Apr 2026 |
| Germany | 3,035 | 6,555 | 2,971 | 1,836 | 1,577 | 61.8% | Apr 2026 |
| Greece | 1,748 | 1,748 | 1,618 | 384 | 233 | 23.7% | Apr 2026 |
| Hungary | 390 | 390 | 364 | 64 | 48 | 17.6% | Apr 2026 |
| Iceland | 139 | 139 | 133 | 16 | 7 | 12.0% | Apr 2026 |
| Ireland | 522 | 522 | 492 | 215 | 194 | 43.7% | Apr 2026 |
| Italy | 981 | 5,338 | 777 | 526 | 518 | 67.7% | Apr 2026 |
| Latvia | 802 | 802 | 755 | 467 | 426 | 61.9% | Apr 2026 |
| Lithuania | 120 | 120 | 108 | 0 | 0 | 0.0% | Apr 2026 |
| Luxembourg | 571 | 571 | 249 | 99 | 88 | 39.8% | Apr 2026 |
| Malta | 608 | 608 | 592 | 376 | 369 | 63.5% | Apr 2026 |
| Netherlands | 347 | 937 | 323 | 126 | 126 | 39.0% | Apr 2026 |
| Norway | 239 | 239 | 233 | 108 | 102 | 46.4% | Apr 2026 |
| Poland | 1,986 | 14,938 | 1,858 | 821 | 493 | 44.2% | Apr 2026 |
| **Total** | **17,337** | **82,714** | **16,083** | **7,861** | **6,786** | **48.9%** | — |

> **Statement %** is the percentage of *reachable* pages that contain at least one link to an accessibility statement.

<!-- ACCESSIBILITY_STATS_END -->

---

## Overview

The accessibility statement scanner checks whether each government page links
to an **accessibility statement** as required by the
[EU Web Accessibility Directive (Directive 2016/2102)](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32016L2102).

Under the Directive, public-sector bodies must:

1. Publish an accessibility statement describing the accessibility of their
   website or mobile app.
2. Include a clearly labelled link to that statement on the page, ideally in
   the footer.

The scanner detects these links using multilingual term matching across all
**24 EU official languages** plus Norwegian and Icelandic.

Scans run **automatically every 4 hours** via GitHub Actions so that the full
set of ~80,000 URLs across 31 countries can be covered gradually without
overloading government servers.

---

## What Is Checked

For each scanned page the scanner:

1. Fetches the page HTML.
2. Searches **first inside `<footer>` elements** for links whose text or href
   matches known accessibility-statement terminology.
3. If not found in the footer, searches the **entire page**.
4. Records whether a matching link was found, where it was found (footer or
   page body), and what text triggered the match.

---

## Multilingual Term Matching

The glossary covers the following languages:

| Region | Languages |
|--------|----------|
| EU official languages | Bulgarian, Croatian, Czech, Danish, Dutch, English, Estonian, Finnish, French, German, Greek, Hungarian, Irish, Italian, Latvian, Lithuanian, Maltese, Polish, Portuguese, Romanian, Slovak, Slovenian, Spanish, Swedish |
| Allied nations | Icelandic, Norwegian |

Example recognised terms include *"accessibility statement"* (EN),
*"déclaration d'accessibilité"* (FR), *"Erklärung zur Barrierefreiheit"* (DE),
and equivalents in all supported languages.

---

## Tier Classification

Each scanned page is assigned one of three outcomes:

| Outcome | Meaning |
|---------|---------|
| `unreachable` | Page could not be fetched (network error, timeout, 4xx/5xx) |
| `no_statement` | Page is reachable but no accessibility statement link was found |
| `has_statement` | Page contains at least one link to an accessibility statement |

Pages where the statement link was found inside a `<footer>` element are
additionally flagged with `found_in_footer = true`, since placing the link in
the footer is considered best practice.

---

## Viewing Results

### Scan Progress Report

The **[Scan Progress Report](scan-progress.md)** includes a per-country
accessibility statement breakdown showing:

- Total pages scanned and reachable count
- Number of pages with a statement link
- Number of pages where the link was found in the footer
- Date range showing when each country was last scanned

### GitHub Actions Artifacts

Each workflow run uploads a scan artifact containing:

- `data/metadata.db` — the full SQLite results database
- `accessibility-scan-output.txt` — the raw scan log
- `data/toon-seeds/countries/**_accessibility.toon` — annotated TOON files

To download artifacts:

1. Go to [GitHub Actions → Scan Accessibility Statements](https://github.com/mgifford/eu-plus-government-scans/actions/workflows/scan-accessibility.yml)
2. Click on the relevant workflow run
3. Scroll to the **Artifacts** section at the bottom of the run summary page
4. Download `accessibility-scan-<run_number>` to inspect the database or TOON files

---

## Running a Scan Manually

### Via GitHub Actions (recommended)

1. Go to [Actions → Scan Accessibility Statements](https://github.com/mgifford/eu-plus-government-scans/actions/workflows/scan-accessibility.yml)
2. Click **Run workflow**
3. Optionally enter a country code (e.g. `ICELAND`) or leave blank to scan all
4. Optionally adjust the rate limit (default: 1.0 req/sec)

### Via the command line

```bash
# Scan a single country
python3 -m src.cli.scan_accessibility --country ICELAND --rate-limit 1.0

# Scan all countries (with a 110-minute runtime cap)
python3 -m src.cli.scan_accessibility --all --max-runtime 110 --rate-limit 1.0
```

---

## Output Format

### Annotated TOON file (`*_accessibility.toon`)

Each page entry gains an `accessibility` field:

```json
{
  "url": "https://example.gov/",
  "is_root_page": true,
  "accessibility": {
    "is_reachable": true,
    "has_statement": true,
    "found_in_footer": true,
    "statement_links": ["https://example.gov/accessibility"],
    "matched_terms": ["accessibility statement"]
  }
}
```

### Database table (`url_accessibility_results`)

| Column | Type | Description |
|--------|------|-------------|
| `url` | TEXT | Page URL |
| `country_code` | TEXT | Country identifier (e.g. `ICELAND`) |
| `scan_id` | TEXT | Unique scan run identifier |
| `is_reachable` | INTEGER | 1 = reachable, 0 = not reachable |
| `has_statement` | INTEGER | 1 = accessibility statement link found |
| `found_in_footer` | INTEGER | 1 = link was found inside a `<footer>` element |
| `statement_links` | TEXT | JSON list of resolved statement URLs |
| `matched_terms` | TEXT | JSON list of matched glossary terms |
| `error_message` | TEXT | Error message if fetch failed |
| `scanned_at` | TEXT | ISO-8601 timestamp of scan |

---

## Countries Covered

Scans cover all 27 EU member states plus 4 allied nations:

| Region | Countries |
|--------|----------|
| EU member states | Austria, Belgium, Bulgaria, Croatia, Czechia, Denmark, Estonia, Finland, France, Germany, Greece, Hungary, Ireland, Italy, Latvia, Lithuania, Luxembourg, Malta, Netherlands, Poland, Portugal, Republic of Cyprus, Romania, Slovakia, Slovenia, Spain, Sweden |
| Allied nations | Iceland, Norway, Switzerland, United Kingdom |

---

## Architecture

```mermaid
flowchart TD
    A["scan-accessibility.yml\n(GitHub Actions — every 4 hours)"]
    A --> B["scan_accessibility.py (CLI)"]
    B --> C["AccessibilityScannerJob.scan_country()"]
    C --> D["AccessibilityScanner.scan_urls_batch()"]
    D --> E["For each URL"]
    E --> F["httpx.get() → HTML content"]
    F --> G["BeautifulSoup → find footer links, then full-page links\nMatch against multilingual glossary terms"]
    G --> H["Classify: has_statement / found_in_footer"]
    H --> I["Save to url_accessibility_results table"]
    I --> J["Write *_accessibility.toon output file"]
```
