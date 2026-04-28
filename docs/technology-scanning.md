---
title: Technology Scanning
layout: page
---

<!-- TECH_STATS_START -->

_Stats as of 2026-04-28 06:15 UTC — last scan: 2026-04-28_

**63** scan batches run

**43,304** of **82,714** available pages scanned (**52.4%** coverage)
**39,739** pages with technology detections (**91.8%** of scanned)
**387** unique technologies identified

---

## Technology Scan by Country

| Country | URLs Scanned | Pages with Detections | Available | Last Scan |
|---------|-------------|----------------------|-----------|----------|
| Austria | 821 | 790 | 821 | 2026-04-24 |
| Belgium | 1,309 | 1,220 | 1,309 | 2026-04-24 |
| Bulgaria | 291 | 263 | 291 | 2026-04-25 |
| Croatia | 233 | 231 | 233 | 2026-04-25 |
| Czechia | 843 | 803 | 843 | 2026-04-25 |
| Denmark | 1,521 | 1,494 | 1,521 | 2026-04-26 |
| Estonia | 396 | 383 | 396 | 2026-04-25 |
| Finland | 180 | 172 | 180 | 2026-04-25 |
| France | 4,064 | 3,754 | 10,007 | 2026-04-26 |
| Germany | 6,555 | 6,468 | 6,555 | 2026-04-27 |
| Greece | 1,748 | 1,622 | 1,748 | 2026-04-25 |
| Hungary | 390 | 364 | 390 | 2026-04-25 |
| Iceland | 139 | 135 | 139 | 2026-04-25 |
| Ireland | 522 | 495 | 522 | 2026-04-28 |
| Italy | 4,701 | 4,249 | 5,338 | 2026-04-28 |
| Latvia | 802 | 762 | 802 | 2026-04-25 |
| Lithuania | 120 | 108 | 120 | 2026-04-26 |
| Luxembourg | 571 | 264 | 571 | 2026-04-26 |
| Malta | 608 | 595 | 608 | 2026-04-26 |
| Netherlands | 937 | 910 | 937 | 2026-04-26 |
| Norway | 239 | 233 | 239 | 2026-04-26 |
| Poland | 2,695 | 2,498 | 14,938 | 2026-04-24 |
| Portugal | 3,503 | 2,857 | 3,503 | 2026-04-25 |
| Cyprus | 24 | 24 | 24 | 2026-04-27 |
| Romania | 709 | 299 | 799 | 2026-04-25 |
| Slovakia | 434 | 412 | 434 | 2026-04-21 |
| Slovenia | 200 | 187 | 200 | 2026-04-21 |
| Spain | 3,345 | 2,927 | 6,069 | 2026-04-25 |
| Sweden | 1,558 | 1,480 | 1,558 | 2026-04-21 |
| Switzerland | 2,117 | 2,080 | 2,117 | 2026-04-21 |
| United Kingdom | 1,729 | 1,660 | 19,502 | 2026-04-26 |

> Hover or focus any non-zero country-table count to preview matching pages. Activate the number to keep the preview open and download a CSV for that country and metric from [Download machine-readable technology data (JSON)](technology-data.json).

---

### Top Technologies

| # | Technology | Pages | Categories |
|--:|-----------|------:|-----------|
| 1 | jQuery | **21,818** | JavaScript libraries |
| 2 | PHP | **12,747** | Programming languages |
| 3 | Apache | **12,514** | Web servers |
| 4 | Bootstrap | **10,490** | UI frameworks |
| 5 | Font Awesome | **8,791** | Font scripts |
| 6 | Google Font API | **7,213** | Font scripts |
| 7 | Nginx | **7,063** | Reverse proxies, Web servers |
| 8 | MySQL | **6,394** | Databases |
| 9 | WordPress | **6,343** | Blogs, CMS |
| 10 | jQuery Migrate | **5,532** | JavaScript libraries |
| 11 | Windows Server | **3,952** | Operating systems |
| 12 | jQuery UI | **3,900** | JavaScript libraries |
| 13 | IIS | **3,891** | Web servers |
| 14 | Microsoft ASP.NET | **3,336** | Web frameworks |
| 15 | Drupal | **3,183** | CMS |
| 16 | jsDelivr | **2,674** | CDN |
| 17 | Google Tag Manager | **2,500** | Tag managers |
| 18 | Cloudflare | **2,475** | CDN |
| 19 | reCAPTCHA | **2,168** | Security |
| 20 | Slick | **2,154** | JavaScript libraries |

### Top Technology Categories

| # | Category | Pages |
|--:|---------|------:|
| 1 | JavaScript libraries | **43,407** |
| 2 | Web servers | **25,458** |
| 3 | Programming languages | **17,263** |
| 4 | Font scripts | **16,356** |
| 5 | CMS | **13,755** |
| 6 | UI frameworks | **13,089** |
| 7 | Reverse proxies | **7,323** |
| 8 | Operating systems | **7,026** |
| 9 | Databases | **6,714** |
| 10 | Blogs | **6,373** |
| 11 | CDN | **6,281** |
| 12 | Web frameworks | **5,491** |
| 13 | JavaScript frameworks | **4,183** |
| 14 | Widgets | **2,738** |
| 15 | Caching | **2,578** |

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
