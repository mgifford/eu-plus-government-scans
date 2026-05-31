---
title: Technology Scanning
layout: page
---

<!-- TECH_STATS_START -->

_Stats as of 2026-05-31 14:52 UTC — last scan: 2026-05-31_

**42** scan batches run

**38,645** of **82,714** available pages scanned (**46.7%** coverage)
**35,527** pages with technology detections (**91.9%** of scanned)
**381** unique technologies identified

---

## Technology Scan by Country

| Country | URLs Scanned | Pages with Detections | Available | Last Scan |
|---------|-------------|----------------------|-----------|----------|
| Austria | 821 | 779 | 821 | 2026-05-31 |
| Belgium | 1,309 | 1,221 | 1,309 | 2026-05-31 |
| Bulgaria | 291 | 265 | 291 | 2026-05-31 |
| Croatia | 233 | 229 | 233 | 2026-05-31 |
| Czechia | 843 | 799 | 843 | 2026-05-30 |
| Denmark | 1,521 | 1,495 | 1,521 | 2026-05-25 |
| Estonia | 396 | 380 | 396 | 2026-05-25 |
| Finland | 180 | 170 | 180 | 2026-05-25 |
| France | 3,323 | 3,058 | 10,007 | 2026-05-30 |
| Germany | 6,555 | 6,447 | 6,555 | 2026-05-30 |
| Greece | 1,748 | 1,616 | 1,748 | 2026-05-25 |
| Hungary | 390 | 281 | 390 | 2026-05-25 |
| Iceland | 139 | 135 | 139 | 2026-05-25 |
| Ireland | 522 | 485 | 522 | 2026-05-30 |
| Italy | 3,059 | 2,732 | 5,338 | 2026-05-30 |
| Latvia | 802 | 752 | 802 | 2026-05-28 |
| Lithuania | 120 | 110 | 120 | 2026-05-28 |
| Luxembourg | 571 | 406 | 571 | 2026-05-28 |
| Malta | 608 | 590 | 608 | 2026-05-28 |
| Netherlands | 937 | 906 | 937 | 2026-05-28 |
| Norway | 239 | 233 | 239 | 2026-05-31 |
| Poland | 4,676 | 4,276 | 14,938 | 2026-05-31 |
| Portugal | 2,816 | 2,281 | 3,503 | 2026-05-29 |
| Cyprus | 24 | 24 | 24 | 2026-05-29 |
| Romania | 523 | 221 | 799 | 2026-05-29 |
| Slovakia | 434 | 410 | 434 | 2026-05-30 |
| Slovenia | 200 | 193 | 200 | 2026-05-30 |
| Spain | 1,464 | 1,279 | 6,069 | 2026-05-30 |
| Sweden | 1,558 | 1,474 | 1,558 | 2026-05-30 |
| Switzerland | 2,117 | 2,068 | 2,117 | 2026-05-30 |
| United Kingdom | 226 | 212 | 19,502 | 2026-05-30 |

> Hover or focus any non-zero country-table count to preview matching pages. Activate the number to keep the preview open and download a CSV for that country and metric from [Download machine-readable technology data (JSON)](technology-data.json).

---

### Top Technologies

| # | Technology | Pages | Categories |
|--:|-----------|------:|-----------|
| 1 | jQuery | **19,750** | JavaScript libraries |
| 2 | PHP | **12,170** | Programming languages |
| 3 | Apache | **11,410** | Web servers |
| 4 | Bootstrap | **9,204** | UI frameworks |
| 5 | Font Awesome | **8,162** | Font scripts |
| 6 | Google Font API | **7,060** | Font scripts |
| 7 | MySQL | **6,501** | Databases |
| 8 | Nginx | **6,489** | Reverse proxies, Web servers |
| 9 | WordPress | **6,453** | Blogs, CMS |
| 10 | jQuery Migrate | **5,459** | JavaScript libraries |
| 11 | Windows Server | **3,364** | Operating systems |
| 12 | jQuery UI | **3,349** | JavaScript libraries |
| 13 | IIS | **3,320** | Web servers |
| 14 | jsDelivr | **2,872** | CDN |
| 15 | Microsoft ASP.NET | **2,870** | Web frameworks |
| 16 | Drupal | **2,733** | CMS |
| 17 | Cloudflare | **2,222** | CDN |
| 18 | Google Tag Manager | **2,200** | Tag managers |
| 19 | Yoast SEO | **2,157** | SEO |
| 20 | Lightbox | **2,103** | JavaScript libraries |

### Top Technology Categories

| # | Category | Pages |
|--:|---------|------:|
| 1 | JavaScript libraries | **39,922** |
| 2 | Web servers | **23,298** |
| 3 | Programming languages | **16,101** |
| 4 | Font scripts | **15,517** |
| 5 | CMS | **13,305** |
| 6 | UI frameworks | **11,405** |
| 7 | Databases | **6,835** |
| 8 | Reverse proxies | **6,750** |
| 9 | Blogs | **6,477** |
| 10 | Operating systems | **5,941** |
| 11 | CDN | **5,859** |
| 12 | Web frameworks | **4,440** |
| 13 | JavaScript frameworks | **3,810** |
| 14 | Caching | **2,443** |
| 15 | Miscellaneous | **2,368** |

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
