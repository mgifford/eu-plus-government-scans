---
title: Technology Scanning
layout: page
---

<!-- TECH_STATS_START -->

_Stats as of 2026-04-19 05:55 UTC — last scan: 2026-04-18_

**22** scan batches run

**18,170** of **82,714** available pages scanned (**22.0%** coverage)
**16,815** pages with technology detections (**92.5%** of scanned)
**322** unique technologies identified

---

## Technology Scan by Country

| Country | URLs Scanned | Pages with Detections | Available | Last Scan |
|---------|-------------|----------------------|-----------|----------|
| Austria | 821 | 790 | 821 | 2026-04-17 |
| Belgium | 1,309 | 1,220 | 1,309 | 2026-04-17 |
| Bulgaria | 291 | 262 | 291 | 2026-04-17 |
| Croatia | 233 | 230 | 233 | 2026-04-17 |
| Czechia | 843 | 800 | 843 | 2026-04-17 |
| Denmark | 414 | 411 | 1,521 | 2026-04-17 |
| Estonia | 396 | 350 | 396 | 2026-04-17 |
| Finland | 180 | 168 | 180 | 2026-04-17 |
| France | 1,395 | 1,197 | 10,007 | 2026-04-17 |
| Germany | 3,465 | 3,386 | 6,555 | 2026-04-17 |
| Greece | 1,748 | 1,617 | 1,748 | 2026-04-18 |
| Hungary | 390 | 349 | 390 | 2026-04-18 |
| Iceland | 139 | 135 | 139 | 2026-04-18 |
| Ireland | 378 | 350 | 522 | 2026-04-18 |
| Italy | 2,714 | 2,507 | 5,338 | 2026-04-18 |
| Latvia | 802 | 762 | 802 | 2026-04-18 |
| Lithuania | 120 | 108 | 120 | 2026-04-18 |
| Luxembourg | 571 | 264 | 571 | 2026-04-18 |
| Malta | 608 | 594 | 608 | 2026-04-18 |
| Netherlands | 937 | 910 | 937 | 2026-04-18 |
| Norway | 239 | 233 | 239 | 2026-04-18 |
| Poland | 177 | 172 | 14,938 | 2026-04-18 |

> Hover or focus any non-zero country-table count to preview matching pages. Activate the number to keep the preview open and download a CSV for that country and metric from [Download machine-readable technology data (JSON)](technology-data.json).

---

### Top Technologies

| # | Technology | Pages | Categories |
|--:|-----------|------:|-----------|
| 1 | jQuery | **9,210** | JavaScript libraries |
| 2 | PHP | **6,558** | Programming languages |
| 3 | Bootstrap | **4,792** | UI frameworks |
| 4 | Apache | **4,704** | Web servers |
| 5 | Font Awesome | **3,988** | Font scripts |
| 6 | MySQL | **3,386** | Databases |
| 7 | WordPress | **3,376** | Blogs, CMS |
| 8 | Nginx | **3,199** | Reverse proxies, Web servers |
| 9 | Google Font API | **3,144** | Font scripts |
| 10 | jQuery Migrate | **2,603** | JavaScript libraries |
| 11 | jQuery UI | **1,732** | JavaScript libraries |
| 12 | Drupal | **1,571** | CMS |
| 13 | Windows Server | **1,535** | Operating systems |
| 14 | IIS | **1,507** | Web servers |
| 15 | jsDelivr | **1,468** | CDN |
| 16 | Cloudflare | **1,352** | CDN |
| 17 | Microsoft ASP.NET | **1,317** | Web frameworks |
| 18 | reCAPTCHA | **1,273** | Security |
| 19 | Lightbox | **1,241** | JavaScript libraries |
| 20 | Yoast SEO | **1,125** | SEO |

### Top Technology Categories

| # | Category | Pages |
|--:|---------|------:|
| 1 | JavaScript libraries | **19,273** |
| 2 | Web servers | **10,048** |
| 3 | Programming languages | **7,680** |
| 4 | Font scripts | **7,312** |
| 5 | CMS | **6,582** |
| 6 | UI frameworks | **5,688** |
| 7 | Databases | **3,560** |
| 8 | Blogs | **3,381** |
| 9 | Reverse proxies | **3,354** |
| 10 | CDN | **3,195** |
| 11 | Operating systems | **3,089** |
| 12 | Web frameworks | **1,977** |
| 13 | Caching | **1,455** |
| 14 | JavaScript frameworks | **1,449** |
| 15 | Widgets | **1,295** |

📥 Machine-readable results: [Download machine-readable technology data (JSON)](technology-data.json)

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

```mermaid
flowchart TD
    A["scan-technology.yml\n(GitHub Actions — every 6 hours)"]
    A --> B["scan_technology.py (CLI)"]
    B --> C["TechScanner.scan_country()"]
    C --> D["TechDetector.detect_urls_batch()"]
    D --> E["For each URL"]
    E --> F["httpx.get() → HTML + headers"]
    F --> G["Wappalyzer.analyze_with_versions_and_categories()"]
    G --> H["Save to url_tech_results table\n(incremental, per URL)"]
    H --> I["Write *_tech.toon output file"]
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
