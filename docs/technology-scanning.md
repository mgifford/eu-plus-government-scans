---
title: Technology Scanning
layout: page
---

<!-- TECH_STATS_START -->

_Stats as of 2026-07-24 05:24 UTC — last scan: 2026-07-24_

**17** scan batches run

**5,575** of **87,696** available pages scanned (**6.4%** coverage)
**5,163** pages with technology detections (**92.6%** of scanned)
**230** unique technologies identified

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
| Iceland | 145 | 143 | 145 | 2026-07-23 |
| Ireland | 313 | 286 | 536 | 2026-07-23 |
| Italy | 352 | 332 | 5,351 | 2026-07-24 |
| Latvia | 305 | 280 | 803 | 2026-07-24 |

> Hover or focus any non-zero country-table count to preview matching pages. Activate the number to keep the preview open and download a CSV for that country and metric from [Download machine-readable technology data (JSON)](technology-data.json).

---

### Top Technologies

| # | Technology | Pages | Categories |
|--:|-----------|------:|-----------|
| 1 | jQuery | **2,926** | JavaScript libraries |
| 2 | PHP | **1,908** | Programming languages |
| 3 | Bootstrap | **1,440** | UI frameworks |
| 4 | Apache | **1,275** | Web servers |
| 5 | Nginx | **1,077** | Reverse proxies, Web servers |
| 6 | Font Awesome | **1,065** | Font scripts |
| 7 | Google Font API | **915** | Font scripts |
| 8 | WordPress | **883** | Blogs, CMS |
| 9 | MySQL | **883** | Databases |
| 10 | Windows Server | **684** | Operating systems |
| 11 | IIS | **678** | Web servers |
| 12 | jQuery UI | **617** | JavaScript libraries |
| 13 | Drupal | **613** | CMS |
| 14 | Microsoft ASP.NET | **612** | Web frameworks |
| 15 | jQuery Migrate | **593** | JavaScript libraries |
| 16 | Cloudflare | **571** | CDN |
| 17 | reCAPTCHA | **392** | Security |
| 18 | Ubuntu | **366** | Operating systems |
| 19 | Varnish | **355** | Caching |
| 20 | Lightbox | **352** | JavaScript libraries |

### Top Technology Categories

| # | Category | Pages |
|--:|---------|------:|
| 1 | JavaScript libraries | **5,827** |
| 2 | Web servers | **3,299** |
| 3 | Programming languages | **2,251** |
| 4 | Font scripts | **2,013** |
| 5 | CMS | **1,881** |
| 6 | UI frameworks | **1,634** |
| 7 | Reverse proxies | **1,117** |
| 8 | Operating systems | **1,115** |
| 9 | CDN | **1,053** |
| 10 | Databases | **954** |
| 11 | Blogs | **883** |
| 12 | Web frameworks | **791** |
| 13 | JavaScript frameworks | **509** |
| 14 | Caching | **461** |
| 15 | Security | **397** |

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
