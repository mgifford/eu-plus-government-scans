---
title: Technology Scanning
layout: page
---

# Technology Scanning

<!-- TECH_STATS_START -->

_Stats as of 2026-04-09 12:52 UTC — last scan: 2026-04-09_

**15** scan batches run

**13,463** of **82,714** available pages scanned (**16.3%** coverage)
**12,804** pages with technology detections (**95.1%** of scanned)
**301** unique technologies identified

---

## Technology Scan by Country

| Country | URLs Scanned | Pages with Detections | Available | Last Scan |
|---------|-------------|----------------------|-----------|----------|
| AUSTRIA | 821 | 787 | 821 | 2026-04-07 |
| BELGIUM | 1,309 | 1,225 | 1,309 | 2026-04-07 |
| BULGARIA | 291 | 268 | 291 | 2026-04-07 |
| CROATIA | 233 | 230 | 233 | 2026-04-07 |
| CZECHIA | 843 | 798 | 843 | 2026-04-07 |
| DENMARK | 415 | 412 | 1,521 | 2026-04-07 |
| ESTONIA | 396 | 388 | 396 | 2026-04-08 |
| FINLAND | 180 | 172 | 180 | 2026-04-08 |
| FRANCE | 2,457 | 2,282 | 10,007 | 2026-04-08 |
| GERMANY | 3,431 | 3,363 | 6,555 | 2026-04-08 |
| GREECE | 1,748 | 1,609 | 1,748 | 2026-04-09 |
| HUNGARY | 390 | 363 | 390 | 2026-04-09 |
| ICELAND | 139 | 135 | 139 | 2026-04-09 |
| IRELAND | 522 | 492 | 522 | 2026-04-09 |
| ITALY | 288 | 280 | 5,338 | 2026-04-09 |

> Hover or focus any non-zero country-table count to preview matching pages. Activate the number to keep the preview open and download a CSV for that country and metric from [technology-data.json](technology-data.json).

---

### Top Technologies

| # | Technology | Pages | Categories |
|--:|-----------|------:|-----------|
| 1 | jQuery | **6,602** | JavaScript libraries |
| 2 | PHP | **4,699** | Programming languages |
| 3 | Apache | **3,377** | Web servers |
| 4 | Bootstrap | **3,175** | UI frameworks |
| 5 | Font Awesome | **3,031** | Font scripts |
| 6 | Nginx | **2,755** | Reverse proxies, Web servers |
| 7 | Google Font API | **2,246** | Font scripts |
| 8 | MySQL | **1,977** | Databases |
| 9 | WordPress | **1,966** | Blogs, CMS |
| 10 | jQuery Migrate | **1,713** | JavaScript libraries |
| 11 | jQuery UI | **1,414** | JavaScript libraries |
| 12 | Drupal | **1,374** | CMS |
| 13 | Windows Server | **1,129** | Operating systems |
| 14 | IIS | **1,103** | Web servers |
| 15 | jsDelivr | **1,021** | CDN |
| 16 | Microsoft ASP.NET | **945** | Web frameworks |
| 17 | Slick | **931** | JavaScript libraries |
| 18 | Lightbox | **883** | JavaScript libraries |
| 19 | TYPO3 CMS | **801** | CMS |
| 20 | Cloudflare | **690** | CDN |

### Top Technology Categories

| # | Category | Pages |
|--:|---------|------:|
| 1 | JavaScript libraries | **14,239** |
| 2 | Web servers | **7,732** |
| 3 | Programming languages | **5,534** |
| 4 | Font scripts | **5,395** |
| 5 | CMS | **4,617** |
| 6 | UI frameworks | **3,704** |
| 7 | Reverse proxies | **2,830** |
| 8 | Databases | **2,094** |
| 9 | Blogs | **1,976** |
| 10 | CDN | **1,959** |
| 11 | Operating systems | **1,842** |
| 12 | Web frameworks | **1,412** |
| 13 | JavaScript frameworks | **1,165** |
| 14 | Caching | **996** |
| 15 | Miscellaneous | **709** |

📥 Machine-readable results: [technology-data.json](technology-data.json)

<!-- TECH_STATS_END -->

---

## Overview

The technology scanner fetches each government page and uses
[python-Wappalyzer](https://github.com/chorsley/python-Wappalyzer) to identify
technologies from HTTP response headers and HTML content.  Detected
technologies (CMS, web server, JavaScript frameworks, analytics, etc.) and
their versions are stored in the metadata database and written back into an
annotated `*_tech.toon` TOON file.

Scans run **automatically every 6 hours** via GitHub Actions so that the full
set of URLs across all countries can be covered gradually without overloading
government servers.

---

## Usage

### Scan a single country

```bash
python3 -m src.cli.scan_technology --country ICELAND --rate-limit 2
```

### Scan all countries

```bash
python3 -m src.cli.scan_technology --all --rate-limit 2
```

### Scan all countries with a runtime cap (recommended for CI)

```bash
python3 -m src.cli.scan_technology --all --max-runtime 110 --rate-limit 2.0
```

### Command-line options

| Option | Default | Description |
|---|---|---|
| `--country CODE` | — | Country code to scan (e.g. `FRANCE`, `ICELAND`) |
| `--all` | — | Scan all countries in the TOON directory |
| `--toon-dir PATH` | `data/toon-seeds/countries` | Directory with `.toon` seed files |
| `--rate-limit N` | `2.0` | Maximum HTTP requests per second |
| `--max-runtime N` | `0` (no limit) | Maximum runtime in minutes.  The scanner stops gracefully before this limit so that partial results can be saved.  Set to ~10 minutes less than the GitHub Actions `timeout-minutes` value. |

---

## GitHub Actions

The **Scan Technology Stack** workflow (`.github/workflows/scan-technology.yml`)
runs automatically every 6 hours and can also be triggered manually from the
Actions tab:

1. Go to **Actions → Scan Technology Stack → Run workflow**
2. Optionally enter a country code (leave blank to scan all countries)
3. Optionally adjust the rate limit

Artifacts uploaded after each run:

| Artifact | Contents |
|---|---|
| `tech-scan-<run_number>` | `data/metadata.db`, scan output log, annotated `*_tech.toon` files |
| `validation-metadata` | `data/metadata.db` (shared with URL validation and social media scans) |

---

## Output

### Annotated TOON file

Each page entry in the output `*_tech.toon` file gains a `technologies` field:

```json
{
  "url": "https://example.gov/",
  "is_root_page": true,
  "technologies": {
    "Nginx": { "versions": ["1.24"], "categories": ["Web servers"] },
    "WordPress": { "versions": ["6.2"], "categories": ["CMS", "Blogs"] }
  }
}
```

If detection failed for a URL, a `tech_error` field is added instead:

```json
{
  "url": "https://unreachable.gov/",
  "tech_error": "Connection error: ..."
}
```

### Database table

Results are stored in the `url_tech_results` table:

| Column | Type | Description |
|---|---|---|
| `url` | TEXT | Page URL |
| `country_code` | TEXT | Country identifier |
| `scan_id` | TEXT | Unique scan run ID |
| `technologies` | TEXT | JSON object of detected technologies |
| `error_message` | TEXT | Error message (if detection failed) |
| `scanned_at` | TEXT | ISO-8601 timestamp |

Query example:

```sql
SELECT url, technologies
FROM url_tech_results
WHERE country_code = 'ICELAND'
ORDER BY scanned_at DESC;
```

---

## Architecture

```
scan-technology.yml (GitHub Actions — every 6 hours)
    ↓
scan_technology.py (CLI)
    ↓
TechScanner.scan_country()
    ↓
TechDetector.detect_urls_batch()
    ↓
For each URL:
    httpx.get()  →  HTML + headers
    Wappalyzer.analyze_with_versions_and_categories()
    ↓
Save to url_tech_results table (incremental, per URL)
    ↓
Write *_tech.toon output file
```

---

## Notes

- **Rate limiting** is applied between requests to avoid overloading government
  servers.  The default is 2 requests per second.
- Technology fingerprinting is best-effort; some sites may return no detections
  if they use custom or obfuscated stacks.
- Unlike the URL validator, failed tech scans do **not** mark a URL for removal
  — errors are recorded but the URL is kept in future scan cycles.
- Results are persisted **incrementally** (one URL at a time) so that partial
  results are preserved even if the GitHub Actions job times out.
- The `*_tech.toon` output files are excluded from version control (see
  `.gitignore`).
