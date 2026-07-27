---
title: Technology Scanning
layout: page
---

<!-- TECH_STATS_START -->

_Stats as of 2026-07-27 13:19 UTC — last scan: 2026-07-27_

**50** scan batches run

**15,370** of **87,696** available pages scanned (**17.5%** coverage)
**7,049** pages with technology detections (**45.9%** of scanned)
**263** unique technologies identified

---

## Technology Scan by Country

| Country | URLs Scanned | Pages with Detections | Available | Last Scan |
|---------|-------------|----------------------|-----------|----------|
| Austria | 822 | 482 | 822 | 2026-07-26 |
| Belgium | 571 | 305 | 1,329 | 2026-07-26 |
| Bulgaria | 353 | 261 | 353 | 2026-07-26 |
| Canada | 697 | 279 | 4,469 | 2026-07-26 |
| Croatia | 257 | 253 | 257 | 2026-07-21 |
| Czechia | 746 | 208 | 866 | 2026-07-26 |
| Denmark | 1,086 | 574 | 1,536 | 2026-07-26 |
| Estonia | 401 | 376 | 401 | 2026-07-26 |
| Finland | 199 | 188 | 199 | 2026-07-22 |
| France | 473 | 138 | 10,009 | 2026-07-26 |
| Germany | 931 | 465 | 6,599 | 2026-07-26 |
| Greece | 663 | 297 | 1,752 | 2026-07-26 |
| Hungary | 392 | 296 | 392 | 2026-07-23 |
| Iceland | 145 | 143 | 145 | 2026-07-23 |
| Ireland | 536 | 286 | 536 | 2026-07-26 |
| Italy | 450 | 332 | 5,351 | 2026-07-26 |
| Latvia | 759 | 280 | 803 | 2026-07-26 |
| Lithuania | 122 | 112 | 122 | 2026-07-24 |
| Luxembourg | 573 | 216 | 573 | 2026-07-27 |
| Malta | 560 | 387 | 610 | 2026-07-27 |
| Netherlands | 819 | 373 | 945 | 2026-07-27 |
| Norway | 249 | 242 | 249 | 2026-07-25 |
| Poland | 525 | 218 | 14,951 | 2026-07-27 |
| Portugal | 689 | 272 | 3,508 | 2026-07-27 |
| Cyprus | 29 | 29 | 29 | 2026-07-25 |
| Romania | 75 | 38 | 807 | 2026-07-25 |
| Slovakia | 442 | 0 | 442 | 2026-07-25 |
| Slovenia | 214 | 0 | 214 | 2026-07-25 |
| Spain | 67 | 0 | 6,091 | 2026-07-25 |
| Sweden | 256 | 0 | 1,702 | 2026-07-26 |
| Switzerland | 651 | 0 | 2,123 | 2026-07-26 |
| United Kingdom | 620 | 0 | 19,511 | 2026-07-26 |

> Hover or focus any non-zero country-table count to preview matching pages. Activate the number to keep the preview open and download a CSV for that country and metric from [Download machine-readable technology data (JSON)](technology-data.json).

---

### Top Technologies

| # | Technology | Pages | Categories |
|--:|-----------|------:|-----------|
| 1 | jQuery | **3,909** | JavaScript libraries |
| 2 | PHP | **2,581** | Programming languages |
| 3 | Bootstrap | **1,873** | UI frameworks |
| 4 | Apache | **1,610** | Web servers |
| 5 | Font Awesome | **1,595** | Font scripts |
| 6 | Google Font API | **1,425** | Font scripts |
| 7 | MySQL | **1,390** | Databases |
| 8 | WordPress | **1,388** | Blogs, CMS |
| 9 | Nginx | **1,354** | Reverse proxies, Web servers |
| 10 | jQuery Migrate | **1,066** | JavaScript libraries |
| 11 | Cloudflare | **1,057** | CDN |
| 12 | Windows Server | **880** | Operating systems |
| 13 | IIS | **873** | Web servers |
| 14 | Microsoft ASP.NET | **773** | Web frameworks |
| 15 | jQuery UI | **703** | JavaScript libraries |
| 16 | Drupal | **673** | CMS |
| 17 | jsDelivr | **589** | CDN |
| 18 | Lightbox | **578** | JavaScript libraries |
| 19 | Yoast SEO | **531** | SEO |
| 20 | reCAPTCHA | **497** | Security |

### Top Technology Categories

| # | Category | Pages |
|--:|---------|------:|
| 1 | JavaScript libraries | **7,980** |
| 2 | Web servers | **4,240** |
| 3 | Programming languages | **3,157** |
| 4 | Font scripts | **3,063** |
| 5 | CMS | **2,644** |
| 6 | UI frameworks | **2,324** |
| 7 | CDN | **1,899** |
| 8 | Databases | **1,483** |
| 9 | Reverse proxies | **1,425** |
| 10 | Operating systems | **1,399** |
| 11 | Blogs | **1,388** |
| 12 | Web frameworks | **1,052** |
| 13 | JavaScript frameworks | **753** |
| 14 | Caching | **668** |
| 15 | Widgets | **631** |

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
