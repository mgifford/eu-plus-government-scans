---
title: Technology Scanning
layout: page
---

<!-- TECH_STATS_START -->

_Stats as of 2026-05-18 06:38 UTC — last scan: 2026-05-17_

**154** scan batches run

**51,356** of **82,714** available pages scanned (**62.1%** coverage)
**47,940** pages with technology detections (**93.3%** of scanned)
**402** unique technologies identified

---

## Technology Scan by Country

| Country | URLs Scanned | Pages with Detections | Available | Last Scan |
|---------|-------------|----------------------|-----------|----------|
| Austria | 821 | 790 | 821 | 2026-05-17 |
| Belgium | 1,309 | 1,223 | 1,309 | 2026-05-17 |
| Bulgaria | 291 | 264 | 291 | 2026-05-17 |
| Croatia | 233 | 232 | 233 | 2026-05-17 |
| Czechia | 843 | 803 | 843 | 2026-05-17 |
| Denmark | 1,521 | 1,504 | 1,521 | 2026-05-15 |
| Estonia | 396 | 383 | 396 | 2026-05-17 |
| Finland | 180 | 172 | 180 | 2026-05-17 |
| France | 4,586 | 4,317 | 10,007 | 2026-05-12 |
| Germany | 6,555 | 6,479 | 6,555 | 2026-05-12 |
| Greece | 1,748 | 1,626 | 1,748 | 2026-05-17 |
| Hungary | 390 | 366 | 390 | 2026-05-15 |
| Iceland | 139 | 135 | 139 | 2026-05-17 |
| Ireland | 522 | 495 | 522 | 2026-05-12 |
| Italy | 5,232 | 4,883 | 5,338 | 2026-05-13 |
| Latvia | 802 | 769 | 802 | 2026-05-11 |
| Lithuania | 120 | 108 | 120 | 2026-05-11 |
| Luxembourg | 571 | 385 | 571 | 2026-05-11 |
| Malta | 608 | 595 | 608 | 2026-05-11 |
| Netherlands | 937 | 910 | 937 | 2026-05-11 |
| Norway | 239 | 233 | 239 | 2026-05-11 |
| Poland | 4,666 | 4,358 | 14,938 | 2026-05-16 |
| Portugal | 3,503 | 2,936 | 3,503 | 2026-05-17 |
| Cyprus | 24 | 24 | 24 | 2026-05-12 |
| Romania | 709 | 301 | 799 | 2026-05-11 |
| Slovakia | 434 | 415 | 434 | 2026-05-15 |
| Slovenia | 200 | 190 | 200 | 2026-05-15 |
| Spain | 3,345 | 3,032 | 6,069 | 2026-05-11 |
| Sweden | 1,558 | 1,490 | 1,558 | 2026-05-15 |
| Switzerland | 2,117 | 2,083 | 2,117 | 2026-05-12 |
| United Kingdom | 6,757 | 6,439 | 19,502 | 2026-05-12 |

> Hover or focus any non-zero country-table count to preview matching pages. Activate the number to keep the preview open and download a CSV for that country and metric from [Download machine-readable technology data (JSON)](technology-data.json).

---

### Top Technologies

| # | Technology | Pages | Categories |
|--:|-----------|------:|-----------|
| 1 | jQuery | **26,992** | JavaScript libraries |
| 2 | PHP | **15,880** | Programming languages |
| 3 | Apache | **14,578** | Web servers |
| 4 | Bootstrap | **12,748** | UI frameworks |
| 5 | Font Awesome | **11,506** | Font scripts |
| 6 | Google Font API | **9,286** | Font scripts |
| 7 | MySQL | **8,793** | Databases |
| 8 | WordPress | **8,737** | Blogs, CMS |
| 9 | Nginx | **8,421** | Reverse proxies, Web servers |
| 10 | jQuery Migrate | **7,663** | JavaScript libraries |
| 11 | Windows Server | **4,909** | Operating systems |
| 12 | IIS | **4,837** | Web servers |
| 13 | jQuery UI | **4,670** | JavaScript libraries |
| 14 | Microsoft ASP.NET | **4,137** | Web frameworks |
| 15 | Drupal | **3,639** | CMS |
| 16 | Google Tag Manager | **3,411** | Tag managers |
| 17 | jsDelivr | **3,373** | CDN |
| 18 | Cloudflare | **3,301** | CDN |
| 19 | Yoast SEO | **2,857** | SEO |
| 20 | reCAPTCHA | **2,757** | Security |

### Top Technology Categories

| # | Category | Pages |
|--:|---------|------:|
| 1 | JavaScript libraries | **53,939** |
| 2 | Web servers | **30,599** |
| 3 | Font scripts | **21,211** |
| 4 | Programming languages | **20,984** |
| 5 | CMS | **17,022** |
| 6 | UI frameworks | **16,599** |
| 7 | Databases | **9,195** |
| 8 | Blogs | **8,770** |
| 9 | Reverse proxies | **8,701** |
| 10 | CDN | **8,320** |
| 11 | Operating systems | **8,305** |
| 12 | Web frameworks | **6,700** |
| 13 | JavaScript frameworks | **4,968** |
| 14 | Miscellaneous | **3,714** |
| 15 | Tag managers | **3,429** |

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
