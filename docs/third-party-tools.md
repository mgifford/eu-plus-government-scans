---
title: Third-Party JavaScript
layout: page
---

<!-- THIRD_PARTY_JS_STATS_START -->

_Stats as of 2026-08-05 06:41 UTC — last scan: 2026-08-05_

**3** scan batches run

**1,353** of **87,696** available pages scanned (**1.5%** coverage)
**1,259** of **1,353** scanned pages were reachable (**93.1%**)
**483** reachable pages loaded at least one third-party script (**38.4%** of reachable)
**354** known third-party service loads identified
**14** unique known services across **10** categories

---

## Third-Party JavaScript by Country

| Country | Scanned | Available | Reachable | URLs with 3rd-Party JS | Known Service Loads | JS URLs /100 Reachable | Known Loads /100 Reachable | Last Scan |
|---------|---------|-----------|-----------|------------------------|--------------------|------------------------|---------------------------|----------|
| Austria | 822 | 822 | 786 | 268 | 48 | 34.1 | 6.1 | 2026-08-05 |
| Bulgaria | 353 | 353 | 306 | 122 | 153 | 39.9 | 50.0 | 2026-08-05 |
| Canada | 178 | 4,469 | 167 | 93 | 153 | 55.7 | 91.6 | 2026-08-05 |

> Hover or focus any non-zero country-table count to preview matching pages. Activate the number to keep the preview open and download a CSV for that country and metric from [Download machine-readable third-party tools data (JSON)](third-party-tools-data.json).

---

### Top Third-Party Services

| # | Service | Loads |
|--:|---------|------:|
| 1 | Google Analytics (GA4) | **72** |
| 2 | jsDelivr CDN | **68** |
| 3 | cdnjs (Cloudflare CDN) | **45** |
| 4 | Google reCAPTCHA | **44** |
| 5 | Google Hosted Libraries | **33** |
| 6 | jQuery | **31** |
| 7 | unpkg CDN | **15** |
| 8 | Google Tag Manager | **14** |
| 9 | Font Awesome | **9** |
| 10 | Adobe Dynamic Tag Management / Launch | **8** |
| 11 | Cookiebot | **6** |
| 12 | Facebook Pixel | **4** |
| 13 | Bootstrap | **4** |
| 14 | Google Analytics (Universal) | **1** |

### Top Services by Page Prevalence

| # | Service | Reachable Pages | Prevalence of Reachable Pages |
|--:|---------|----------------:|------------------------------:|
| 1 | Google Analytics (GA4) | **69** | **41.3%** |
| 2 | jsDelivr CDN | **46** | **27.5%** |
| 3 | Google reCAPTCHA | **44** | **26.3%** |
| 4 | cdnjs (Cloudflare CDN) | **35** | **21.0%** |
| 5 | Google Hosted Libraries | **33** | **19.8%** |
| 6 | jQuery | **25** | **15.0%** |
| 7 | Google Tag Manager | **14** | **8.4%** |
| 8 | unpkg CDN | **11** | **6.6%** |
| 9 | Font Awesome | **9** | **5.4%** |
| 10 | Adobe Dynamic Tag Management / Launch | **8** | **4.8%** |
| 11 | Cookiebot | **6** | **3.6%** |
| 12 | Bootstrap | **4** | **2.4%** |
| 13 | Facebook Pixel | **4** | **2.4%** |
| 14 | Google Analytics (Universal) | **1** | **0.6%** |

### Top Service Categories

| # | Category | Loads |
|--:|----------|------:|
| 1 | CDN | **161** |
| 2 | Analytics | **85** |
| 3 | JavaScript Library | **64** |
| 4 | Security | **44** |
| 5 | CAPTCHA | **44** |
| 6 | Tag Manager | **22** |
| 7 | Icon Library | **9** |
| 8 | Cookie Consent | **6** |
| 9 | Advertising | **4** |
| 10 | UI Framework | **4** |

### Category Balance

Infrastructure-heavy categories (CDNs, core libraries, and UI assets):

| # | Infrastructure Category | Loads |
|--:|--------------------------|------:|
| 1 | CDN | **161** |
| 2 | JavaScript Library | **64** |
| 3 | Icon Library | **9** |
| 4 | UI Framework | **4** |

Policy-relevant categories (tracking, consent, support, and security tooling):

| # | Policy-Relevant Category | Loads |
|--:|--------------------------|------:|
| 1 | Analytics | **85** |
| 2 | Security | **44** |
| 3 | CAPTCHA | **44** |
| 4 | Tag Manager | **22** |
| 5 | Cookie Consent | **6** |
| 6 | Advertising | **4** |

### Unknown Third-Party Hosts (Review Queue)

| # | Host | Loads | Reachable Pages |
|--:|------|------:|----------------:|
| 1 | `webcachex-eu.datareporter.eu` | **162** | **162** |
| 2 | `www.csspo.gouv.qc.ca` | **33** | **3** |
| 3 | `s7.addthis.com` | **27** | **25** |
| 4 | `translate.google.com` | **24** | **24** |
| 5 | `www.canada.ca` | **12** | **6** |
| 6 | `www.gstatic.com` | **11** | **11** |
| 7 | `maps.googleapis.com` | **9** | **9** |
| 8 | `use.typekit.net` | **8** | **8** |
| 9 | `cdn-cookieyes.com` | **8** | **8** |
| 10 | `service.bmf.gv.at` | **7** | **3** |
| 11 | `maps.google.com` | **6** | **6** |
| 12 | `stp.wien.gv.at` | **6** | **6** |
| 13 | `static.etracker.com` | **6** | **6** |
| 14 | `inside.bundesheer.at` | **6** | **3** |
| 15 | `agriculture.alberta.ca` | **6** | **3** |

> These hosts were seen as third-party script sources but did not match a known service signature. Review this queue regularly and promote stable, policy-relevant hosts into the signature list.

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
