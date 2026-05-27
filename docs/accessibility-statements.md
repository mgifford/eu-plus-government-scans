---
title: Accessibility Statement Scanning
layout: page
---

<!-- ACCESSIBILITY_STATS_START -->

_Stats as of 2026-05-27 20:57 UTC — last scan: 2026-05-27_

**48** scan batches run

**52,883** of **82,714** available pages scanned (**63.9%** coverage)
**48,474** of **52,883** scanned pages were reachable (**91.7%**)
**23,511** of **48,474** reachable pages have an accessibility statement (**48.5%**)
**20,883** pages have the statement link in the footer (**88.8%** of pages with a statement)

📥 Machine-readable results are available as the [accessibility-data.json artifact (machine-readable JSON)](https://github.com/mgifford/eu-plus-government-scans/actions/workflows/generate-scan-progress.yml).

Each country entry in the JSON file includes page-level evidence for pages with and without accessibility statements, plus a per-domain summary you can share to validate the published counts.

> Hover or focus any non-zero count in the country table to preview the matching pages. If there are 20 or fewer URLs, the preview shows all of them; otherwise it shows a short sample. Full machine-readable data is available as the [accessibility-data.json artifact (machine-readable JSON)](https://github.com/mgifford/eu-plus-government-scans/actions/workflows/generate-scan-progress.yml).

---

## Accessibility Statement Scan by Country

| Country | Scanned | Available | Reachable | Has Statement | In Footer | Statement % | Scan Period |
|---------|---------|-----------|-----------|--------------|-----------|------------|-------------|
| Austria | 821 | 821 | 778 | 547 | 517 | 70.3% | May 2026 |
| Belgium | 1,309 | 1,309 | 1,219 | 558 | 508 | 45.8% | May 2026 |
| Bulgaria | 291 | 291 | 264 | 61 | 59 | 23.1% | May 2026 |
| Croatia | 233 | 233 | 227 | 83 | 59 | 36.6% | May 2026 |
| Czechia | 843 | 843 | 799 | 409 | 351 | 51.2% | May 2026 |
| Denmark | 1,521 | 1,521 | 1,495 | 960 | 940 | 64.2% | May 2026 |
| Estonia | 396 | 396 | 380 | 141 | 77 | 37.1% | May 2026 |
| Finland | 180 | 180 | 170 | 115 | 108 | 67.6% | May 2026 |
| France | 5,699 | 10,007 | 5,366 | 1,726 | 1,650 | 32.2% | May 2026 |
| Germany | 6,555 | 6,555 | 6,395 | 4,570 | 3,837 | 71.5% | May 2026 |
| Greece | 1,748 | 1,748 | 1,600 | 404 | 244 | 25.2% | May 2026 |
| Hungary | 390 | 390 | 278 | 49 | 41 | 17.6% | May 2026 |
| Iceland | 139 | 139 | 135 | 12 | 5 | 8.9% | May 2026 |
| Ireland | 522 | 522 | 487 | 211 | 196 | 43.3% | May 2026 |
| Italy | 5,338 | 5,338 | 4,816 | 2,645 | 2,573 | 54.9% | May 2026 |
| Latvia | 802 | 802 | 756 | 485 | 445 | 64.2% | May 2026 |
| Lithuania | 120 | 120 | 110 | 0 | 0 | 0.0% | May 2026 |
| Luxembourg | 571 | 571 | 392 | 228 | 217 | 58.2% | May 2026 |
| Malta | 608 | 608 | 590 | 384 | 377 | 65.1% | May 2026 |
| Netherlands | 937 | 937 | 906 | 440 | 430 | 48.6% | May 2026 |
| Norway | 239 | 239 | 233 | 107 | 101 | 45.9% | May 2026 |
| Poland | 4,911 | 14,938 | 4,505 | 1,753 | 1,215 | 38.9% | May 2026 |
| Portugal | 3,503 | 3,503 | 2,857 | 865 | 702 | 30.3% | May 2026 |
| Cyprus | 24 | 24 | 24 | 0 | 0 | 0.0% | May 2026 |
| Romania | 799 | 799 | 338 | 27 | 9 | 8.0% | May 2026 |
| Slovakia | 434 | 434 | 408 | 186 | 171 | 45.6% | May 2026 |
| Slovenia | 200 | 200 | 190 | 100 | 74 | 52.6% | May 2026 |
| Spain | 4,546 | 6,069 | 3,950 | 1,624 | 1,422 | 41.1% | May 2026 |
| Sweden | 1,558 | 1,558 | 1,474 | 837 | 764 | 56.8% | May 2026 |
| Switzerland | 2,117 | 2,117 | 2,072 | 991 | 990 | 47.8% | May 2026 |
| United Kingdom | 5,529 | 19,502 | 5,260 | 2,993 | 2,801 | 56.9% | May 2026 |
| **Total** | **52,883** | **82,714** | **48,474** | **23,511** | **20,883** | **48.5%** | — |

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
