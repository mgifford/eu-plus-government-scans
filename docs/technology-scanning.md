---
title: Technology Scanning
layout: page
---

<!-- TECH_STATS_START -->

_Stats as of 2026-07-08 15:15 UTC — last scan: 2026-07-08_

**104** scan batches run

**54,670** of **82,714** available pages scanned (**66.1%** coverage)
**50,642** pages with technology detections (**92.6%** of scanned)
**410** unique technologies identified

---

## Technology Scan by Country

| Country | URLs Scanned | Pages with Detections | Available | Last Scan |
|---------|-------------|----------------------|-----------|----------|
| Austria | 821 | 787 | 821 | 2026-07-04 |
| Belgium | 1,309 | 1,221 | 1,309 | 2026-07-07 |
| Bulgaria | 291 | 265 | 291 | 2026-07-05 |
| Croatia | 233 | 231 | 233 | 2026-07-05 |
| Czechia | 843 | 806 | 843 | 2026-07-06 |
| Denmark | 1,521 | 1,500 | 1,521 | 2026-07-07 |
| Estonia | 396 | 381 | 396 | 2026-07-06 |
| Finland | 180 | 170 | 180 | 2026-07-06 |
| France | 5,699 | 5,345 | 10,007 | 2026-07-07 |
| Germany | 6,555 | 6,471 | 6,555 | 2026-07-07 |
| Greece | 1,748 | 1,631 | 1,748 | 2026-07-07 |
| Hungary | 390 | 298 | 390 | 2026-07-06 |
| Iceland | 139 | 137 | 139 | 2026-07-06 |
| Ireland | 522 | 490 | 522 | 2026-07-06 |
| Italy | 4,797 | 4,342 | 5,338 | 2026-07-08 |
| Latvia | 802 | 774 | 802 | 2026-07-02 |
| Lithuania | 120 | 110 | 120 | 2026-07-02 |
| Luxembourg | 571 | 445 | 571 | 2026-07-02 |
| Malta | 608 | 593 | 608 | 2026-07-02 |
| Netherlands | 937 | 912 | 937 | 2026-07-02 |
| Norway | 239 | 233 | 239 | 2026-07-05 |
| Poland | 6,490 | 5,925 | 14,938 | 2026-07-08 |
| Portugal | 3,503 | 2,932 | 3,503 | 2026-07-07 |
| Cyprus | 24 | 24 | 24 | 2026-07-02 |
| Romania | 799 | 342 | 799 | 2026-07-07 |
| Slovakia | 434 | 415 | 434 | 2026-07-07 |
| Slovenia | 200 | 193 | 200 | 2026-07-04 |
| Spain | 3,677 | 3,304 | 6,069 | 2026-07-08 |
| Sweden | 1,558 | 1,489 | 1,558 | 2026-07-07 |
| Switzerland | 2,117 | 2,078 | 2,117 | 2026-07-04 |
| United Kingdom | 7,147 | 6,798 | 19,502 | 2026-07-08 |

> Hover or focus any non-zero country-table count to preview matching pages. Activate the number to keep the preview open and download a CSV for that country and metric from [Download machine-readable technology data (JSON)](technology-data.json).

---

### Top Technologies

| # | Technology | Pages | Categories |
|--:|-----------|------:|-----------|
| 1 | jQuery | **27,736** | JavaScript libraries |
| 2 | PHP | **16,719** | Programming languages |
| 3 | Apache | **15,327** | Web servers |
| 4 | Bootstrap | **13,042** | UI frameworks |
| 5 | Font Awesome | **11,925** | Font scripts |
| 6 | Google Font API | **10,030** | Font scripts |
| 7 | MySQL | **9,340** | Databases |
| 8 | WordPress | **9,274** | Blogs, CMS |
| 9 | Nginx | **9,017** | Reverse proxies, Web servers |
| 10 | jQuery Migrate | **8,161** | JavaScript libraries |
| 11 | Windows Server | **4,903** | Operating systems |
| 12 | IIS | **4,836** | Web servers |
| 13 | jQuery UI | **4,674** | JavaScript libraries |
| 14 | Microsoft ASP.NET | **4,104** | Web frameworks |
| 15 | jsDelivr | **3,846** | CDN |
| 16 | Drupal | **3,811** | CMS |
| 17 | Cloudflare | **3,578** | CDN |
| 18 | Google Tag Manager | **3,574** | Tag managers |
| 19 | Yoast SEO | **2,976** | SEO |
| 20 | reCAPTCHA | **2,721** | Security |

### Top Technology Categories

| # | Category | Pages |
|--:|---------|------:|
| 1 | JavaScript libraries | **55,534** |
| 2 | Web servers | **32,349** |
| 3 | Font scripts | **22,399** |
| 4 | Programming languages | **22,191** |
| 5 | CMS | **17,898** |
| 6 | UI frameworks | **16,967** |
| 7 | Databases | **9,770** |
| 8 | Blogs | **9,307** |
| 9 | Reverse proxies | **9,273** |
| 10 | CDN | **9,123** |
| 11 | Operating systems | **8,331** |
| 12 | Web frameworks | **6,692** |
| 13 | JavaScript frameworks | **5,430** |
| 14 | Miscellaneous | **3,947** |
| 15 | Tag managers | **3,594** |

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
