---
title: Technology Scanning
layout: page
---

<!-- TECH_STATS_START -->

_Stats as of 2026-07-16 23:12 UTC — last scan: 2026-07-16_

**161** scan batches run

**69,679** of **82,714** available pages scanned (**84.2%** coverage)
**64,273** pages with technology detections (**92.2%** of scanned)
**431** unique technologies identified

---

## Technology Scan by Country

| Country | URLs Scanned | Pages with Detections | Available | Last Scan |
|---------|-------------|----------------------|-----------|----------|
| Austria | 821 | 787 | 821 | 2026-07-12 |
| Belgium | 1,309 | 1,224 | 1,309 | 2026-07-15 |
| Bulgaria | 291 | 265 | 291 | 2026-07-12 |
| Croatia | 233 | 231 | 233 | 2026-07-12 |
| Czechia | 843 | 806 | 843 | 2026-07-13 |
| Denmark | 1,521 | 1,500 | 1,521 | 2026-07-14 |
| Estonia | 396 | 381 | 396 | 2026-07-13 |
| Finland | 180 | 170 | 180 | 2026-07-13 |
| France | 10,007 | 9,242 | 10,007 | 2026-07-15 |
| Germany | 6,555 | 6,477 | 6,555 | 2026-07-15 |
| Greece | 1,748 | 1,634 | 1,748 | 2026-07-15 |
| Hungary | 390 | 298 | 390 | 2026-07-13 |
| Iceland | 139 | 137 | 139 | 2026-07-13 |
| Ireland | 522 | 490 | 522 | 2026-07-14 |
| Italy | 5,338 | 4,820 | 5,338 | 2026-07-16 |
| Latvia | 802 | 774 | 802 | 2026-07-10 |
| Lithuania | 120 | 110 | 120 | 2026-07-10 |
| Luxembourg | 571 | 445 | 571 | 2026-07-10 |
| Malta | 608 | 593 | 608 | 2026-07-10 |
| Netherlands | 937 | 912 | 937 | 2026-07-13 |
| Norway | 239 | 233 | 239 | 2026-07-15 |
| Poland | 8,189 | 7,529 | 14,938 | 2026-07-15 |
| Portugal | 3,503 | 2,935 | 3,503 | 2026-07-15 |
| Cyprus | 24 | 24 | 24 | 2026-07-10 |
| Romania | 799 | 342 | 799 | 2026-07-15 |
| Slovakia | 434 | 415 | 434 | 2026-07-15 |
| Slovenia | 200 | 193 | 200 | 2026-07-11 |
| Spain | 6,069 | 5,305 | 6,069 | 2026-07-16 |
| Sweden | 1,558 | 1,489 | 1,558 | 2026-07-15 |
| Switzerland | 2,117 | 2,080 | 2,117 | 2026-07-12 |
| United Kingdom | 13,216 | 12,432 | 19,502 | 2026-07-16 |

> Hover or focus any non-zero country-table count to preview matching pages. Activate the number to keep the preview open and download a CSV for that country and metric from [Download machine-readable technology data (JSON)](technology-data.json).

---

### Top Technologies

| # | Technology | Pages | Categories |
|--:|-----------|------:|-----------|
| 1 | jQuery | **34,845** | JavaScript libraries |
| 2 | PHP | **21,300** | Programming languages |
| 3 | Apache | **18,660** | Web servers |
| 4 | Bootstrap | **16,109** | UI frameworks |
| 5 | Font Awesome | **15,343** | Font scripts |
| 6 | Google Font API | **12,880** | Font scripts |
| 7 | MySQL | **11,955** | Databases |
| 8 | WordPress | **11,867** | Blogs, CMS |
| 9 | Nginx | **11,354** | Reverse proxies, Web servers |
| 10 | jQuery Migrate | **10,452** | JavaScript libraries |
| 11 | Windows Server | **5,896** | Operating systems |
| 12 | jQuery UI | **5,808** | JavaScript libraries |
| 13 | IIS | **5,807** | Web servers |
| 14 | Microsoft ASP.NET | **5,020** | Web frameworks |
| 15 | Google Tag Manager | **5,007** | Tag managers |
| 16 | Cloudflare | **4,917** | CDN |
| 17 | Drupal | **4,909** | CMS |
| 18 | jsDelivr | **4,691** | CDN |
| 19 | Yoast SEO | **3,849** | SEO |
| 20 | reCAPTCHA | **3,715** | Security |

### Top Technology Categories

| # | Category | Pages |
|--:|---------|------:|
| 1 | JavaScript libraries | **69,377** |
| 2 | Web servers | **39,882** |
| 3 | Font scripts | **28,732** |
| 4 | Programming languages | **27,475** |
| 5 | CMS | **22,536** |
| 6 | UI frameworks | **21,354** |
| 7 | CDN | **12,511** |
| 8 | Databases | **12,509** |
| 9 | Blogs | **11,941** |
| 10 | Reverse proxies | **11,672** |
| 11 | Operating systems | **9,889** |
| 12 | Web frameworks | **8,036** |
| 13 | JavaScript frameworks | **6,669** |
| 14 | Miscellaneous | **5,171** |
| 15 | Tag managers | **5,042** |

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
