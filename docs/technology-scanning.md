---
title: Technology Scanning
layout: page
---

# Technology Scanning

<!-- TECH_STATS_START -->

_Stats as of 2026-04-07 22:20 UTC — last scan: 2026-04-07_

**6** scan batches run

**3,912** of **82,714** available pages scanned (**4.7%** coverage)
**3,720** pages with technology detections (**95.1%** of scanned)
**196** unique technologies identified

---

## Technology Scan by Country

| Country | URLs Scanned | Pages with Detections | Available | Last Scan |
|---------|-------------|----------------------|-----------|----------|
| AUSTRIA | 821 | 787 | 821 | 2026-04-07 |
| BELGIUM | 1,309 | 1,225 | 1,309 | 2026-04-07 |
| BULGARIA | 291 | 268 | 291 | 2026-04-07 |
| CROATIA | 233 | 230 | 233 | 2026-04-07 |
| CZECHIA | 843 | 798 | 843 | 2026-04-07 |
| DENMARK | 415 | 412 | 1,521 | 2026-04-07 |

---

### Top Technologies

| # | Technology | Pages | Categories |
|--:|-----------|------:|-----------|
| 1 | jQuery | **2,161** | JavaScript libraries |
| 2 | Font Awesome | **1,213** | Font scripts |
| 3 | PHP | **1,082** | Programming languages |
| 4 | Bootstrap | **1,016** | UI frameworks |
| 5 | Google Font API | **774** | Font scripts |
| 6 | Nginx | **676** | Reverse proxies, Web servers |
| 7 | Windows Server | **671** | Operating systems |
| 8 | IIS | **662** | Web servers |
| 9 | jQuery UI | **655** | JavaScript libraries |
| 10 | Microsoft ASP.NET | **572** | Web frameworks |
| 11 | Drupal | **558** | CMS |
| 12 | Apache | **531** | Web servers |
| 13 | Slick | **430** | JavaScript libraries |
| 14 | Lightbox | **428** | JavaScript libraries |
| 15 | WordPress | **327** | Blogs, CMS |
| 16 | MySQL | **327** | Databases |
| 17 | jQuery Migrate | **288** | JavaScript libraries |
| 18 | jsDelivr | **242** | CDN |
| 19 | Cloudflare | **235** | CDN |
| 20 | Varnish | **220** | Caching |

### Top Technology Categories

| # | Category | Pages |
|--:|---------|------:|
| 1 | JavaScript libraries | **4,466** |
| 2 | Font scripts | **2,016** |
| 3 | Web servers | **1,972** |
| 4 | Programming languages | **1,316** |
| 5 | UI frameworks | **1,124** |
| 6 | CMS | **1,063** |
| 7 | Operating systems | **762** |
| 8 | Reverse proxies | **706** |
| 9 | Web frameworks | **684** |
| 10 | CDN | **533** |
| 11 | Databases | **344** |
| 12 | Blogs | **329** |
| 13 | JavaScript frameworks | **302** |
| 14 | Maps | **279** |
| 15 | Caching | **256** |

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

```
scan-technology.yml (GitHub Actions — every 6 hours)
    ↓
scan_technology.py (CLI)
    ↓
TechScanner.scan_country()
    ↓
TechDetector.detect_urls_batch()
    ↓
For each URL:
    httpx.get()  →  HTML + headers
    Wappalyzer.analyze_with_versions_and_categories()
    ↓
Save to url_tech_results table (incremental, per URL)
    ↓
Write *_tech.toon output file
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
