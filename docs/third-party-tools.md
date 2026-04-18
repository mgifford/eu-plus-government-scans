---
title: Third-Party JavaScript
layout: page
---

<!-- THIRD_PARTY_JS_STATS_START -->

_Stats as of 2026-04-18 05:49 UTC — last scan: 2026-04-17_

**10** scan batches run

**2,957** of **82,714** available pages scanned (**3.6%** coverage)
**2,814** of **2,957** scanned pages were reachable (**95.2%**)
**1,247** reachable pages loaded at least one third-party script (**44.3%** of reachable)
**1,235** known third-party service loads identified
**16** unique known services across **10** categories

---

## Third-Party JavaScript by Country

| Country | Scanned | Available | Reachable | URLs with 3rd-Party JS | Known Service Loads | Last Scan |
|---------|---------|-----------|-----------|------------------------|--------------------|----------|
| Austria | 821 | 821 | 790 | 266 | 44 | 2026-04-17 |
| Belgium | 1,309 | 1,309 | 1,227 | 632 | 717 | 2026-04-17 |
| Bulgaria | 291 | 291 | 269 | 107 | 120 | 2026-04-17 |
| Croatia | 233 | 233 | 232 | 120 | 167 | 2026-04-17 |
| Czechia | 303 | 843 | 296 | 122 | 187 | 2026-04-17 |

> Hover or focus any non-zero country-table count to preview matching pages. Activate the number to keep the preview open and download a CSV for that country and metric from [Download machine-readable third-party tools data (JSON)](third-party-tools-data.json).

---

### Top Third-Party Services

| # | Service | Loads |
|--:|---------|------:|
| 1 | jsDelivr CDN | **381** |
| 2 | unpkg CDN | **213** |
| 3 | Google Analytics (GA4) | **153** |
| 4 | cdnjs (Cloudflare CDN) | **134** |
| 5 | Google Tag Manager | **78** |
| 6 | Google reCAPTCHA | **73** |
| 7 | Google Hosted Libraries | **66** |
| 8 | jQuery | **50** |
| 9 | Cookiebot | **24** |
| 10 | Font Awesome | **20** |
| 11 | Bootstrap | **17** |
| 12 | Matomo Cloud | **11** |
| 13 | Facebook Pixel | **9** |
| 14 | Cloudflare Turnstile / Challenge | **2** |
| 15 | OneTrust | **2** |
| 16 | Google Analytics (Universal) | **2** |

### Top Service Categories

| # | Category | Loads |
|--:|----------|------:|
| 1 | CDN | **794** |
| 2 | Analytics | **175** |
| 3 | JavaScript Library | **116** |
| 4 | Tag Manager | **78** |
| 5 | Security | **75** |
| 6 | CAPTCHA | **73** |
| 7 | Cookie Consent | **26** |
| 8 | Icon Library | **20** |
| 9 | UI Framework | **17** |
| 10 | Advertising | **9** |

📥 Machine-readable results: [Download machine-readable third-party tools data (JSON)](third-party-tools-data.json)

<!-- THIRD_PARTY_JS_STATS_END -->

---

## Overview

This scan identifies **third-party JavaScript** loaded by government websites,
including analytics tags, tag managers, cookie-consent tools, CDNs, customer
support widgets, and other externally hosted scripts.

The goal is to make the external dependencies used across European government
sites easier to inspect. This helps answer questions like:

- Which analytics or advertising vendors appear most often?
- How common are third-party CDNs and consent managers?
- Which countries lean more heavily on externally hosted web tooling?

The scanner looks at every `<script src="...">` on a page, excludes
same-origin scripts, and then tries to match known services such as Google Tag
Manager, Google Analytics, Matomo Cloud, OneTrust, Cookiebot, Cloudflare,
Microsoft Clarity, HubSpot, and more.

---

## Why This Matters

Third-party JavaScript can affect:

- **Privacy**: analytics, advertising, and tracking integrations may send data
  to external services.
- **Security**: externally hosted libraries and widgets increase supply-chain
  risk.
- **Resilience**: a page may depend on third-party infrastructure outside the
  control of the public authority.
- **Performance**: extra scripts often increase page weight and network cost.

This page gives an EU-wide view of those dependencies.

---

## Usage

### Scan a single country

```bash
python3 -m src.cli.scan_third_party_js --country ICELAND --rate-limit 1.0
```

### Scan all countries

```bash
python3 -m src.cli.scan_third_party_js --all --rate-limit 1.0
```

### Scan all countries with a runtime cap

```bash
python3 -m src.cli.scan_third_party_js --all --max-runtime 110 --rate-limit 1.0
```

### Command-line options

| Option | Default | Description |
|---|---|---|
| `--country CODE` | — | Country code to scan (for example `FRANCE` or `ICELAND`) |
| `--all` | — | Scan all countries in the TOON directory |
| `--toon-dir PATH` | `data/toon-seeds/countries` | Directory with `.toon` seed files |
| `--rate-limit N` | `1.0` | Maximum HTTP requests per second |
| `--max-runtime N` | `0` (no limit) | Maximum runtime in minutes for graceful CI stops |

---

## GitHub Actions

The **Scan Third-Party JavaScript** workflow
(`.github/workflows/scan-third-party-js.yml`) runs automatically every 6 hours
and can also be triggered manually from the Actions tab.

Artifacts uploaded after each run:

| Artifact | Contents |
|---|---|
| `3pjs-scan-<run_number>` | `data/metadata.db`, scan output log, annotated `*_3pjs.toon` files |
| `validation-metadata` | `data/metadata.db` shared with the other scanners |

---

## Output

### Annotated TOON file

Each page entry in the output `*_3pjs.toon` file gains a `third_party_js`
field:

```json
{
  "url": "https://example.gov/",
  "third_party_js": [
    {
      "src": "https://www.googletagmanager.com/gtm.js?id=GTM-XXXX",
      "host": "www.googletagmanager.com",
      "service_name": "Google Tag Manager",
      "version": "GTM-XXXX",
      "categories": ["Tag Manager"]
    }
  ]
}
```

If scanning failed for a URL, a `third_party_js_error` field is added instead.

### Database table

Results are stored in the `url_third_party_js_results` table:

| Column | Type | Description |
|---|---|---|
| `url` | TEXT | Page URL |
| `country_code` | TEXT | Country identifier |
| `scan_id` | TEXT | Unique scan run ID |
| `is_reachable` | INTEGER | 1 = page fetched successfully |
| `scripts` | TEXT | JSON array of third-party script records |
| `error_message` | TEXT | Error message if the page fetch failed |
| `scanned_at` | TEXT | ISO-8601 timestamp |

---

## Related Pages

- [Technology Scanning](technology-scanning.md)
- [Accessibility Statements](accessibility-statements.md)
- [Social Media](social-media.md)
- [Scan Progress Report](scan-progress.md)
