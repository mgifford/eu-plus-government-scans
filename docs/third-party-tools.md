---
title: Third-Party JavaScript
layout: page
---

<!-- THIRD_PARTY_JS_STATS_START -->

_Stats as of 2026-08-06 04:38 UTC — last scan: 2026-08-05_

**2** scan batches run

**1,166** of **87,696** available pages scanned (**1.3%** coverage)
**1,079** of **1,166** scanned pages were reachable (**92.5%**)
**393** reachable pages loaded at least one third-party script (**36.4%** of reachable)
**201** known third-party service loads identified
**13** unique known services across **10** categories

---

## Third-Party JavaScript by Country

| Country | Scanned | Available | Reachable | URLs with 3rd-Party JS | Known Service Loads | JS URLs /100 Reachable | Known Loads /100 Reachable | Last Scan |
|---------|---------|-----------|-----------|------------------------|--------------------|------------------------|---------------------------|----------|
| Austria | 813 | 822 | 774 | 270 | 47 | 34.9 | 6.1 | 2026-08-05 |
| Bulgaria | 353 | 353 | 305 | 123 | 154 | 40.3 | 50.5 | 2026-08-05 |

> Hover or focus any non-zero country-table count to preview matching pages. Activate the number to keep the preview open and download a CSV for that country and metric from [Download machine-readable third-party tools data (JSON)](third-party-tools-data.json).

---

### Top Third-Party Services

| # | Service | Loads |
|--:|---------|------:|
| 1 | jsDelivr CDN | **42** |
| 2 | Google reCAPTCHA | **32** |
| 3 | Google Analytics (GA4) | **28** |
| 4 | cdnjs (Cloudflare CDN) | **27** |
| 5 | Google Hosted Libraries | **25** |
| 6 | jQuery | **15** |
| 7 | Google Tag Manager | **9** |
| 8 | Font Awesome | **8** |
| 9 | Cookiebot | **6** |
| 10 | unpkg CDN | **4** |
| 11 | Bootstrap | **3** |
| 12 | Facebook Pixel | **1** |
| 13 | Google Analytics (Universal) | **1** |

### Top Services by Page Prevalence

| # | Service | Reachable Pages | Prevalence of Reachable Pages |
|--:|---------|----------------:|------------------------------:|
| 1 | Google reCAPTCHA | **32** | **10.5%** |
| 2 | Google Analytics (GA4) | **28** | **9.2%** |
| 3 | jsDelivr CDN | **27** | **8.9%** |
| 4 | Google Hosted Libraries | **25** | **8.2%** |
| 5 | cdnjs (Cloudflare CDN) | **24** | **7.9%** |
| 6 | jQuery | **12** | **3.9%** |
| 7 | Google Tag Manager | **9** | **3.0%** |
| 8 | Font Awesome | **8** | **2.6%** |
| 9 | Cookiebot | **6** | **2.0%** |
| 10 | unpkg CDN | **4** | **1.3%** |
| 11 | Bootstrap | **3** | **1.0%** |
| 12 | Facebook Pixel | **1** | **0.3%** |
| 13 | Google Analytics (Universal) | **1** | **0.3%** |

### Top Service Categories

| # | Category | Loads |
|--:|----------|------:|
| 1 | CDN | **98** |
| 2 | JavaScript Library | **40** |
| 3 | Security | **32** |
| 4 | CAPTCHA | **32** |
| 5 | Analytics | **30** |
| 6 | Tag Manager | **9** |
| 7 | Icon Library | **8** |
| 8 | Cookie Consent | **6** |
| 9 | UI Framework | **3** |
| 10 | Advertising | **1** |

### Category Balance

Infrastructure-heavy categories (CDNs, core libraries, and UI assets):

| # | Infrastructure Category | Loads |
|--:|--------------------------|------:|
| 1 | CDN | **98** |
| 2 | JavaScript Library | **40** |
| 3 | Icon Library | **8** |
| 4 | UI Framework | **3** |

Policy-relevant categories (tracking, consent, support, and security tooling):

| # | Policy-Relevant Category | Loads |
|--:|--------------------------|------:|
| 1 | Security | **32** |
| 2 | CAPTCHA | **32** |
| 3 | Analytics | **30** |
| 4 | Tag Manager | **9** |
| 5 | Cookie Consent | **6** |
| 6 | Advertising | **1** |

### Unknown Third-Party Hosts (Review Queue)

| # | Host | Loads | Reachable Pages |
|--:|------|------:|----------------:|
| 1 | `webcachex-eu.datareporter.eu` | **159** | **159** |
| 2 | `s7.addthis.com` | **27** | **25** |
| 3 | `translate.google.com` | **21** | **21** |
| 4 | `www.gstatic.com` | **11** | **11** |
| 5 | `service.bmf.gv.at` | **7** | **3** |
| 6 | `maps.google.com` | **6** | **6** |
| 7 | `stp.wien.gv.at` | **6** | **6** |
| 8 | `static.etracker.com` | **6** | **6** |
| 9 | `inside.bundesheer.at` | **6** | **3** |
| 10 | `analytics.silktide.com` | **5** | **5** |
| 11 | `consent.cookiebot.eu` | **5** | **5** |
| 12 | `concierge.goodguys.ai` | **5** | **5** |
| 13 | `cdn.userway.org` | **4** | **4** |
| 14 | `cdn.priv.center` | **4** | **4** |
| 15 | `chat.oesterreich.gv.at` | **4** | **4** |

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
