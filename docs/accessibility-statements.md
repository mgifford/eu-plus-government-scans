---
title: Accessibility Statement Scanning
layout: page
---

# Accessibility Statement Scanning

<!-- ACCESSIBILITY_STATS_START -->

_Stats as of 2026-04-06 16:17 UTC — last scan: 2026-04-05_

**85** scan batches run

**72,735** of **82,714** available pages scanned (**87.9%** coverage)
**67,160** of **72,735** scanned pages were reachable (**92.3%**)
**32,480** of **67,160** reachable pages have an accessibility statement (**48.4%**)
**28,105** pages have the statement link in the footer (**86.5%** of pages with a statement)

📥 Machine-readable results: [accessibility-data.json](accessibility-data.json)

---

## Accessibility Statement Scan by Country

| Country | Scanned | Available | Reachable | Has Statement | In Footer | Statement % | Scan Period |
|---------|---------|-----------|-----------|--------------|-----------|------------|-------------|
| AUSTRIA | 821 | 821 | 787 | 547 | 517 | 69.5% | Mar 2026 – Apr 2026 |
| BELGIUM | 1,309 | 1,309 | 1,229 | 548 | 499 | 44.6% | Mar 2026 – Apr 2026 |
| BULGARIA | 291 | 291 | 269 | 61 | 59 | 22.7% | Mar 2026 – Apr 2026 |
| CROATIA | 233 | 233 | 231 | 85 | 61 | 36.8% | Mar 2026 – Apr 2026 |
| CZECHIA | 843 | 843 | 803 | 427 | 365 | 53.2% | Mar 2026 – Apr 2026 |
| DENMARK | 1,521 | 1,521 | 1,503 | 1,036 | 1,019 | 68.9% | Mar 2026 – Apr 2026 |
| ESTONIA | 396 | 396 | 389 | 136 | 65 | 35.0% | Mar 2026 – Apr 2026 |
| FINLAND | 180 | 180 | 172 | 111 | 104 | 64.5% | Mar 2026 – Apr 2026 |
| FRANCE | 10,007 | 10,007 | 9,425 | 3,655 | 3,516 | 38.8% | Mar 2026 – Apr 2026 |
| GERMANY | 6,555 | 6,555 | 6,456 | 4,570 | 3,861 | 70.8% | Mar 2026 – Apr 2026 |
| GREECE | 1,748 | 1,748 | 1,627 | 409 | 238 | 25.1% | Mar 2026 – Apr 2026 |
| HUNGARY | 390 | 390 | 366 | 64 | 48 | 17.5% | Mar 2026 – Apr 2026 |
| ICELAND | 139 | 139 | 135 | 15 | 7 | 11.1% | Mar 2026 – Apr 2026 |
| IRELAND | 522 | 522 | 498 | 226 | 205 | 45.4% | Mar 2026 – Apr 2026 |
| ITALY | 5,338 | 5,338 | 4,830 | 2,613 | 2,547 | 54.1% | Mar 2026 – Apr 2026 |
| LATVIA | 802 | 802 | 771 | 488 | 444 | 63.3% | Mar 2026 – Apr 2026 |
| LITHUANIA | 120 | 120 | 108 | 0 | 0 | 0.0% | Mar 2026 – Apr 2026 |
| LUXEMBOURG | 571 | 571 | 250 | 85 | 74 | 34.0% | Mar 2026 – Apr 2026 |
| MALTA | 608 | 608 | 595 | 381 | 374 | 64.0% | Mar 2026 – Apr 2026 |
| NETHERLANDS | 937 | 937 | 909 | 449 | 439 | 49.4% | Mar 2026 – Apr 2026 |
| NORWAY | 239 | 239 | 233 | 108 | 102 | 46.4% | Mar 2026 – Apr 2026 |
| POLAND | 13,875 | 14,938 | 12,857 | 5,300 | 3,363 | 41.2% | Mar 2026 – Apr 2026 |
| PORTUGAL | 3,503 | 3,503 | 2,931 | 885 | 710 | 30.2% | Mar 2026 – Apr 2026 |
| REPUBLIC_OF_CYPRUS | 24 | 24 | 24 | 0 | 0 | 0.0% | Mar 2026 |
| ROMANIA | 799 | 799 | 351 | 28 | 9 | 8.0% | Mar 2026 |
| SLOVAKIA | 434 | 434 | 411 | 187 | 172 | 45.5% | Mar 2026 |
| SLOVENIA | 200 | 200 | 188 | 95 | 69 | 50.5% | Mar 2026 |
| SPAIN | 6,069 | 6,069 | 5,316 | 2,339 | 2,043 | 44.0% | Mar 2026 – Apr 2026 |
| SWEDEN | 1,558 | 1,558 | 1,483 | 857 | 782 | 57.8% | Mar 2026 |
| SWITZERLAND | 2,117 | 2,117 | 2,080 | 979 | 977 | 47.1% | Mar 2026 – Apr 2026 |
| UNITED_KINGDOM_UK | 10,586 | 19,502 | 9,933 | 5,796 | 5,436 | 58.4% | Mar 2026 – Apr 2026 |
| **Total** | **72,735** | **82,714** | **67,160** | **32,480** | **28,105** | **48.4%** | — |

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

```
scan-accessibility.yml (GitHub Actions — every 4 hours)
    ↓
scan_accessibility.py (CLI)
    ↓
AccessibilityScannerJob.scan_country()
    ↓
AccessibilityScanner.scan_urls_batch()
    ↓
For each URL:
    httpx.get()  →  HTML content
    BeautifulSoup  →  find <footer> links, then full-page links
    Match against multilingual glossary terms
    ↓
Classify: has_statement / found_in_footer
    ↓
Save to url_accessibility_results table
    ↓
Write *_accessibility.toon output file
```
