---
title: Technology Scanning
layout: page
---

<!-- TECH_STATS_START -->

_Stats as of 2026-08-31 16:55 UTC — last scan: 2026-08-31_

**91** scan batches run

**83,373** of **87,696** available pages scanned (**95.1%** coverage)
**16,921** pages with technology detections (**20.3%** of scanned)
**325** unique technologies identified

---

## Technology Scan by Country

| Country | URLs Scanned | Pages with Detections | Available | Last Scan |
|---------|-------------|----------------------|-----------|----------|
| Austria | 822 | 0 | 822 | 2026-08-11 |
| Belgium | 1,329 | 0 | 1,329 | 2026-08-15 |
| Bulgaria | 353 | 0 | 353 | 2026-08-12 |
| Canada | 4,469 | 0 | 4,469 | 2026-08-16 |
| Croatia | 257 | 0 | 257 | 2026-08-12 |
| Czechia | 866 | 0 | 866 | 2026-08-12 |
| Denmark | 1,536 | 0 | 1,536 | 2026-08-19 |
| Estonia | 401 | 0 | 401 | 2026-08-12 |
| Finland | 199 | 0 | 199 | 2026-08-12 |
| France | 10,009 | 1,818 | 10,009 | 2026-08-29 |
| Germany | 6,599 | 0 | 6,599 | 2026-08-24 |
| Greece | 1,752 | 0 | 1,752 | 2026-08-16 |
| Hungary | 392 | 0 | 392 | 2026-08-13 |
| Iceland | 145 | 0 | 145 | 2026-08-13 |
| Ireland | 536 | 0 | 536 | 2026-08-13 |
| Italy | 5,351 | 402 | 5,351 | 2026-08-27 |
| Latvia | 803 | 0 | 803 | 2026-08-13 |
| Lithuania | 122 | 0 | 122 | 2026-08-13 |
| Luxembourg | 573 | 0 | 573 | 2026-08-13 |
| Malta | 610 | 0 | 610 | 2026-08-17 |
| Netherlands | 945 | 0 | 945 | 2026-08-14 |
| Norway | 249 | 0 | 249 | 2026-08-14 |
| Poland | 10,634 | 4,084 | 14,951 | 2026-08-31 |
| Portugal | 3,508 | 0 | 3,508 | 2026-08-20 |
| Cyprus | 29 | 0 | 29 | 2026-08-14 |
| Romania | 807 | 0 | 807 | 2026-08-23 |
| Slovakia | 442 | 0 | 442 | 2026-08-15 |
| Slovenia | 214 | 0 | 214 | 2026-08-15 |
| Spain | 6,091 | 1,043 | 6,091 | 2026-08-29 |
| Sweden | 1,702 | 0 | 1,702 | 2026-08-21 |
| Switzerland | 2,123 | 0 | 2,123 | 2026-08-15 |
| United Kingdom | 19,511 | 9,574 | 19,511 | 2026-08-31 |

> Hover or focus any non-zero country-table count to preview matching pages. Activate the number to keep the preview open and download a CSV for that country and metric from [Download machine-readable technology data (JSON)](technology-data.json).

---

### Top Technologies

| # | Technology | Pages | Categories |
|--:|-----------|------:|-----------|
| 1 | jQuery | **8,697** | JavaScript libraries |
| 2 | PHP | **5,978** | Programming languages |
| 3 | Google Tag Manager | **4,777** | Tag managers |
| 4 | Font Awesome | **4,712** | Font scripts |
| 5 | Google Font API | **4,249** | Font scripts |
| 6 | MySQL | **3,810** | Databases |
| 7 | WordPress | **3,767** | Blogs, CMS |
| 8 | Bootstrap | **3,683** | UI frameworks |
| 9 | Apache | **3,551** | Web servers |
| 10 | jQuery Migrate | **3,292** | JavaScript libraries |
| 11 | Nginx | **2,895** | Reverse proxies, Web servers |
| 12 | Cloudflare | **2,357** | CDN |
| 13 | reCAPTCHA | **1,749** | Security |
| 14 | Amazon Web Services | **1,741** | PaaS |
| 15 | Amazon Cloudfront | **1,733** | CDN |
| 16 | Windows Server | **1,401** | Operating systems |
| 17 | IIS | **1,390** | Web servers |
| 18 | Microsoft ASP.NET | **1,326** | Web frameworks |
| 19 | Yoast SEO | **1,177** | SEO |
| 20 | Drupal | **1,141** | CMS |

### Top Technology Categories

| # | Category | Pages |
|--:|---------|------:|
| 1 | JavaScript libraries | **17,592** |
| 2 | Font scripts | **9,301** |
| 3 | Web servers | **9,191** |
| 4 | Programming languages | **6,655** |
| 5 | CMS | **6,068** |
| 6 | CDN | **5,368** |
| 7 | UI frameworks | **5,151** |
| 8 | Tag managers | **4,785** |
| 9 | Databases | **3,991** |
| 10 | Blogs | **3,871** |
| 11 | Reverse proxies | **2,934** |
| 12 | Operating systems | **1,994** |
| 13 | Security | **1,970** |
| 14 | PaaS | **1,902** |
| 15 | Web frameworks | **1,602** |

📥 Machine-readable results: [Download machine-readable technology data (JSON)](technology-data.json)

<!-- TECH_STATS_END -->

---

## Overview

The technology scanner fetches each government page and uses
[wappalyzer-python3](https://github.com/omkarcloud/wappalyzer-python3) to identify
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
