---
title: Technology Scanning
layout: page
---

<!-- TECH_STATS_START -->

_Stats as of 2026-05-08 05:55 UTC — last scan: 2026-05-07_

**110** scan batches run

**50,687** of **82,714** available pages scanned (**61.3%** coverage)
**47,096** pages with technology detections (**92.9%** of scanned)
**404** unique technologies identified

---

## Technology Scan by Country

| Country | URLs Scanned | Pages with Detections | Available | Last Scan |
|---------|-------------|----------------------|-----------|----------|
| Austria | 821 | 790 | 821 | 2026-05-02 |
| Belgium | 1,309 | 1,223 | 1,309 | 2026-05-03 |
| Bulgaria | 291 | 264 | 291 | 2026-05-02 |
| Croatia | 233 | 231 | 233 | 2026-05-02 |
| Czechia | 843 | 803 | 843 | 2026-05-02 |
| Denmark | 1,521 | 1,503 | 1,521 | 2026-05-07 |
| Estonia | 396 | 383 | 396 | 2026-05-02 |
| Finland | 180 | 172 | 180 | 2026-05-02 |
| France | 4,448 | 4,173 | 10,007 | 2026-05-07 |
| Germany | 6,555 | 6,477 | 6,555 | 2026-05-07 |
| Greece | 1,748 | 1,624 | 1,748 | 2026-05-03 |
| Hungary | 390 | 364 | 390 | 2026-05-02 |
| Iceland | 139 | 135 | 139 | 2026-05-02 |
| Ireland | 522 | 495 | 522 | 2026-05-07 |
| Italy | 4,701 | 4,252 | 5,338 | 2026-05-01 |
| Latvia | 802 | 766 | 802 | 2026-05-04 |
| Lithuania | 120 | 108 | 120 | 2026-05-03 |
| Luxembourg | 571 | 382 | 571 | 2026-05-03 |
| Malta | 608 | 595 | 608 | 2026-05-03 |
| Netherlands | 937 | 910 | 937 | 2026-05-03 |
| Norway | 239 | 233 | 239 | 2026-05-03 |
| Poland | 4,666 | 4,336 | 14,938 | 2026-05-02 |
| Portugal | 3,503 | 2,932 | 3,503 | 2026-05-03 |
| Cyprus | 24 | 24 | 24 | 2026-05-05 |
| Romania | 709 | 301 | 799 | 2026-05-03 |
| Slovakia | 434 | 415 | 434 | 2026-05-06 |
| Slovenia | 200 | 190 | 200 | 2026-05-06 |
| Spain | 3,345 | 3,019 | 6,069 | 2026-05-04 |
| Sweden | 1,558 | 1,487 | 1,558 | 2026-05-06 |
| Switzerland | 2,117 | 2,083 | 2,117 | 2026-05-06 |
| United Kingdom | 6,757 | 6,426 | 19,502 | 2026-05-05 |

> Hover or focus any non-zero country-table count to preview matching pages. Activate the number to keep the preview open and download a CSV for that country and metric from [Download machine-readable technology data (JSON)](technology-data.json).

---

### Top Technologies

| # | Technology | Pages | Categories |
|--:|-----------|------:|-----------|
| 1 | jQuery | **26,526** | JavaScript libraries |
| 2 | PHP | **15,598** | Programming languages |
| 3 | Apache | **14,343** | Web servers |
| 4 | Bootstrap | **12,442** | UI frameworks |
| 5 | Font Awesome | **11,268** | Font scripts |
| 6 | Google Font API | **9,204** | Font scripts |
| 7 | MySQL | **8,614** | Databases |
| 8 | WordPress | **8,560** | Blogs, CMS |
| 9 | Nginx | **8,456** | Reverse proxies, Web servers |
| 10 | jQuery Migrate | **7,494** | JavaScript libraries |
| 11 | Windows Server | **4,829** | Operating systems |
| 12 | IIS | **4,757** | Web servers |
| 13 | jQuery UI | **4,641** | JavaScript libraries |
| 14 | Microsoft ASP.NET | **4,059** | Web frameworks |
| 15 | Drupal | **3,558** | CMS |
| 16 | Google Tag Manager | **3,378** | Tag managers |
| 17 | jsDelivr | **3,303** | CDN |
| 18 | Cloudflare | **3,275** | CDN |
| 19 | Yoast SEO | **2,766** | SEO |
| 20 | reCAPTCHA | **2,715** | Security |

### Top Technology Categories

| # | Category | Pages |
|--:|---------|------:|
| 1 | JavaScript libraries | **53,115** |
| 2 | Web servers | **30,290** |
| 3 | Font scripts | **20,859** |
| 4 | Programming languages | **20,690** |
| 5 | CMS | **16,744** |
| 6 | UI frameworks | **16,245** |
| 7 | Databases | **9,001** |
| 8 | Reverse proxies | **8,749** |
| 9 | Blogs | **8,593** |
| 10 | Operating systems | **8,249** |
| 11 | CDN | **8,180** |
| 12 | Web frameworks | **6,580** |
| 13 | JavaScript frameworks | **4,857** |
| 14 | Miscellaneous | **3,626** |
| 15 | Tag managers | **3,396** |

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
