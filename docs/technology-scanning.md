---
title: Technology Scanning
layout: page
---

<!-- TECH_STATS_START -->

_Stats as of 2026-07-23 15:31 UTC — last scan: 2026-07-23_

**13** scan batches run

**4,460** of **87,696** available pages scanned (**5.1%** coverage)
**4,122** pages with technology detections (**92.4%** of scanned)
**218** unique technologies identified

---

## Technology Scan by Country

| Country | URLs Scanned | Pages with Detections | Available | Last Scan |
|---------|-------------|----------------------|-----------|----------|
| Austria | 505 | 482 | 822 | 2026-07-20 |
| Belgium | 337 | 305 | 1,329 | 2026-07-20 |
| Bulgaria | 292 | 261 | 353 | 2026-07-21 |
| Canada | 313 | 279 | 4,469 | 2026-07-21 |
| Croatia | 257 | 253 | 257 | 2026-07-21 |
| Czechia | 227 | 208 | 866 | 2026-07-21 |
| Denmark | 585 | 574 | 1,536 | 2026-07-21 |
| Estonia | 393 | 376 | 401 | 2026-07-22 |
| Finland | 199 | 188 | 199 | 2026-07-22 |
| France | 160 | 138 | 10,009 | 2026-07-22 |
| Germany | 481 | 465 | 6,599 | 2026-07-22 |
| Greece | 319 | 297 | 1,752 | 2026-07-23 |
| Hungary | 392 | 296 | 392 | 2026-07-23 |

> Hover or focus any non-zero country-table count to preview matching pages. Activate the number to keep the preview open and download a CSV for that country and metric from [Download machine-readable technology data (JSON)](technology-data.json).

---

### Top Technologies

| # | Technology | Pages | Categories |
|--:|-----------|------:|-----------|
| 1 | jQuery | **2,194** | JavaScript libraries |
| 2 | PHP | **1,367** | Programming languages |
| 3 | Bootstrap | **936** | UI frameworks |
| 4 | Font Awesome | **884** | Font scripts |
| 5 | Apache | **883** | Web servers |
| 6 | Nginx | **882** | Reverse proxies, Web servers |
| 7 | Google Font API | **707** | Font scripts |
| 8 | Windows Server | **562** | Operating systems |
| 9 | IIS | **557** | Web servers |
| 10 | Drupal | **511** | CMS |
| 11 | Microsoft ASP.NET | **501** | Web frameworks |
| 12 | WordPress | **490** | Blogs, CMS |
| 13 | MySQL | **490** | Databases |
| 14 | Cloudflare | **481** | CDN |
| 15 | jQuery UI | **465** | JavaScript libraries |
| 16 | jQuery Migrate | **435** | JavaScript libraries |
| 17 | Varnish | **319** | Caching |
| 18 | Lightbox | **300** | JavaScript libraries |
| 19 | Slick | **295** | JavaScript libraries |
| 20 | jsDelivr | **259** | CDN |

### Top Technology Categories

| # | Category | Pages |
|--:|---------|------:|
| 1 | JavaScript libraries | **4,518** |
| 2 | Web servers | **2,510** |
| 3 | Font scripts | **1,623** |
| 4 | Programming languages | **1,607** |
| 5 | CMS | **1,332** |
| 6 | UI frameworks | **1,095** |
| 7 | Reverse proxies | **918** |
| 8 | CDN | **832** |
| 9 | Operating systems | **686** |
| 10 | Web frameworks | **637** |
| 11 | Databases | **520** |
| 12 | Blogs | **490** |
| 13 | JavaScript frameworks | **394** |
| 14 | Caching | **393** |
| 15 | Miscellaneous | **281** |

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

## License and Digital Public Goods status (Top Technologies)

To support policy tracking of open source and free software use, this page now
includes a machine-readable license registry for the current **Top
Technologies** list:

- [Download technology license data (JSON)](technology-license-data.json)

Current summary from `technology-license-data.json`:

- **DPGA Registry listed:** Drupal
- **OSI-approved license (yes):** jQuery, PHP, Apache, Bootstrap, MySQL,
  WordPress, Nginx, jQuery Migrate, jQuery UI, Drupal, Yoast SEO
- **Partial/mixed:** Font Awesome, Microsoft ASP.NET, jsDelivr
- **Not OSI-approved (no):** Google Font API, Windows Server, IIS,
  Google Tag Manager, Cloudflare, reCAPTCHA

> Notes:
> - This is a best-effort mapping of detected technology names to primary
>   upstream licenses.
> - Some detections are products/services (not single software packages), so
>   their licensing model can be mixed or proprietary.
> - DPGA status is based on a checked snapshot at generation time and may change.

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
