---
title: Technology Scanning
layout: page
---

<!-- TECH_STATS_START -->

_Stats as of 2026-05-27 17:24 UTC — last scan: 2026-05-26_

**15** scan batches run

**15,136** of **82,714** available pages scanned (**18.3%** coverage)
**14,180** pages with technology detections (**93.7%** of scanned)
**300** unique technologies identified

---

## Technology Scan by Country

| Country | URLs Scanned | Pages with Detections | Available | Last Scan |
|---------|-------------|----------------------|-----------|----------|
| Austria | 821 | 772 | 821 | 2026-05-24 |
| Belgium | 1,309 | 1,218 | 1,309 | 2026-05-24 |
| Bulgaria | 291 | 264 | 291 | 2026-05-24 |
| Croatia | 233 | 229 | 233 | 2026-05-24 |
| Czechia | 358 | 349 | 843 | 2026-05-24 |
| Denmark | 1,521 | 1,495 | 1,521 | 2026-05-25 |
| Estonia | 396 | 380 | 396 | 2026-05-25 |
| Finland | 180 | 170 | 180 | 2026-05-25 |
| France | 1,271 | 1,168 | 10,007 | 2026-05-25 |
| Germany | 3,373 | 3,313 | 6,555 | 2026-05-25 |
| Greece | 1,748 | 1,616 | 1,748 | 2026-05-25 |
| Hungary | 390 | 281 | 390 | 2026-05-25 |
| Iceland | 139 | 135 | 139 | 2026-05-25 |
| Ireland | 405 | 373 | 522 | 2026-05-25 |
| Italy | 2,701 | 2,417 | 5,338 | 2026-05-26 |

> Hover or focus any non-zero country-table count to preview matching pages. Activate the number to keep the preview open and download a CSV for that country and metric from [Download machine-readable technology data (JSON)](technology-data.json).

---

### Top Technologies

| # | Technology | Pages | Categories |
|--:|-----------|------:|-----------|
| 1 | jQuery | **7,837** | JavaScript libraries |
| 2 | PHP | **5,483** | Programming languages |
| 3 | Bootstrap | **4,161** | UI frameworks |
| 4 | Apache | **4,119** | Web servers |
| 5 | Font Awesome | **3,168** | Font scripts |
| 6 | Nginx | **2,912** | Reverse proxies, Web servers |
| 7 | MySQL | **2,515** | Databases |
| 8 | WordPress | **2,507** | Blogs, CMS |
| 9 | Google Font API | **2,311** | Font scripts |
| 10 | jQuery Migrate | **1,868** | JavaScript libraries |
| 11 | Drupal | **1,635** | CMS |
| 12 | Windows Server | **1,563** | Operating systems |
| 13 | IIS | **1,541** | Web servers |
| 14 | jQuery UI | **1,481** | JavaScript libraries |
| 15 | Microsoft ASP.NET | **1,349** | Web frameworks |
| 16 | jsDelivr | **1,026** | CDN |
| 17 | Ubuntu | **982** | Operating systems |
| 18 | reCAPTCHA | **968** | Security |
| 19 | Lightbox | **956** | JavaScript libraries |
| 20 | Varnish | **934** | Caching |

### Top Technology Categories

| # | Category | Pages |
|--:|---------|------:|
| 1 | JavaScript libraries | **15,953** |
| 2 | Web servers | **9,064** |
| 3 | Programming languages | **6,476** |
| 4 | Font scripts | **5,619** |
| 5 | CMS | **5,500** |
| 6 | UI frameworks | **4,775** |
| 7 | Reverse proxies | **3,044** |
| 8 | Operating systems | **2,891** |
| 9 | Databases | **2,672** |
| 10 | Blogs | **2,513** |
| 11 | CDN | **2,129** |
| 12 | Web frameworks | **1,861** |
| 13 | JavaScript frameworks | **1,357** |
| 14 | Caching | **1,247** |
| 15 | Security | **987** |

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
