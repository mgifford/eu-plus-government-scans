---
title: Technology Scanning
layout: page
---

<!-- TECH_STATS_START -->

_Stats as of 2026-04-11 05:42 UTC — last scan: 2026-04-11_

**28** scan batches run

**21,010** of **82,714** available pages scanned (**25.4%** coverage)
**19,135** pages with technology detections (**91.1%** of scanned)
**337** unique technologies identified

---

## Technology Scan by Country

| Country | URLs Scanned | Pages with Detections | Available | Last Scan |
|---------|-------------|----------------------|-----------|----------|
| Austria | 821 | 787 | 821 | 2026-04-07 |
| Belgium | 1,309 | 1,225 | 1,309 | 2026-04-07 |
| Bulgaria | 291 | 268 | 291 | 2026-04-07 |
| Croatia | 233 | 230 | 233 | 2026-04-07 |
| Czechia | 843 | 798 | 843 | 2026-04-07 |
| Denmark | 415 | 412 | 1,521 | 2026-04-07 |
| Estonia | 396 | 388 | 396 | 2026-04-08 |
| Finland | 180 | 172 | 180 | 2026-04-08 |
| France | 2,457 | 2,282 | 10,007 | 2026-04-08 |
| Germany | 3,431 | 3,363 | 6,555 | 2026-04-08 |
| Greece | 1,748 | 1,609 | 1,748 | 2026-04-09 |
| Hungary | 390 | 363 | 390 | 2026-04-09 |
| Iceland | 139 | 135 | 139 | 2026-04-09 |
| Ireland | 522 | 492 | 522 | 2026-04-09 |
| Italy | 288 | 280 | 5,338 | 2026-04-09 |
| Latvia | 802 | 766 | 802 | 2026-04-10 |
| Lithuania | 120 | 108 | 120 | 2026-04-10 |
| Luxembourg | 571 | 245 | 571 | 2026-04-10 |
| Malta | 608 | 595 | 608 | 2026-04-10 |
| Netherlands | 937 | 902 | 937 | 2026-04-10 |
| Norway | 239 | 233 | 239 | 2026-04-10 |
| Poland | 232 | 216 | 14,938 | 2026-04-10 |
| Portugal | 1,148 | 899 | 3,503 | 2026-04-10 |
| Cyprus | 24 | 24 | 24 | 2026-04-10 |
| Romania | 525 | 226 | 799 | 2026-04-10 |
| Slovakia | 434 | 412 | 434 | 2026-04-11 |
| Slovenia | 200 | 190 | 200 | 2026-04-11 |
| Spain | 1,707 | 1,515 | 6,069 | 2026-04-11 |

> Hover or focus any non-zero country-table count to preview matching pages. Activate the number to keep the preview open and download a CSV for that country and metric from [technology-data.json](technology-data.json).

---

### Top Technologies

| # | Technology | Pages | Categories |
|--:|-----------|------:|-----------|
| 1 | jQuery | **9,835** | JavaScript libraries |
| 2 | PHP | **6,895** | Programming languages |
| 3 | Apache | **5,266** | Web servers |
| 4 | Bootstrap | **4,821** | UI frameworks |
| 5 | Font Awesome | **4,669** | Font scripts |
| 6 | Google Font API | **3,873** | Font scripts |
| 7 | Nginx | **3,749** | Reverse proxies, Web servers |
| 8 | MySQL | **3,237** | Databases |
| 9 | WordPress | **3,223** | Blogs, CMS |
| 10 | jQuery Migrate | **2,905** | JavaScript libraries |
| 11 | jQuery UI | **2,100** | JavaScript libraries |
| 12 | Drupal | **1,875** | CMS |
| 13 | Windows Server | **1,775** | Operating systems |
| 14 | IIS | **1,744** | Web servers |
| 15 | jsDelivr | **1,673** | CDN |
| 16 | Cloudflare | **1,569** | CDN |
| 17 | Microsoft ASP.NET | **1,476** | Web frameworks |
| 18 | Lightbox | **1,408** | JavaScript libraries |
| 19 | Yoast SEO | **1,255** | SEO |
| 20 | Slick | **1,164** | JavaScript libraries |

### Top Technology Categories

| # | Category | Pages |
|--:|---------|------:|
| 1 | JavaScript libraries | **21,501** |
| 2 | Web servers | **11,618** |
| 3 | Font scripts | **8,708** |
| 4 | Programming languages | **8,176** |
| 5 | CMS | **6,786** |
| 6 | UI frameworks | **6,012** |
| 7 | Reverse proxies | **3,881** |
| 8 | CDN | **3,785** |
| 9 | Databases | **3,387** |
| 10 | Blogs | **3,233** |
| 11 | Operating systems | **2,970** |
| 12 | Web frameworks | **2,226** |
| 13 | JavaScript frameworks | **1,938** |
| 14 | Widgets | **1,664** |
| 15 | Miscellaneous | **1,434** |

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
