---
title: Third-Party JavaScript
layout: page
---

<!-- THIRD_PARTY_JS_STATS_START -->

_Stats as of 2026-07-20 12:49 UTC — last scan: 2026-07-20_

**3** scan batches run

**1,544** of **87,696** available pages scanned (**1.8%** coverage)
**1,461** of **1,544** scanned pages were reachable (**94.6%**)
**586** reachable pages loaded at least one third-party script (**40.1%** of reachable)
**525** known third-party service loads identified
**15** unique known services across **10** categories

---

## Third-Party JavaScript by Country

| Country | Scanned | Available | Reachable | URLs with 3rd-Party JS | Known Service Loads | JS URLs /100 Reachable | Known Loads /100 Reachable | Last Scan |
|---------|---------|-----------|-----------|------------------------|--------------------|------------------------|---------------------------|----------|
| Austria | 822 | 822 | 787 | 272 | 52 | 34.6 | 6.6 | 2026-07-20 |
| Bulgaria | 353 | 353 | 320 | 128 | 163 | 40.0 | 50.9 | 2026-07-20 |
| Canada | 369 | 4,469 | 354 | 186 | 310 | 52.5 | 87.6 | 2026-07-20 |

> Hover or focus any non-zero country-table count to preview matching pages. Activate the number to keep the preview open and download a CSV for that country and metric from [Download machine-readable third-party tools data (JSON)](third-party-tools-data.json).

---

### Top Third-Party Services

| # | Service | Loads |
|--:|---------|------:|
| 1 | jsDelivr CDN | **101** |
| 2 | Google Analytics (GA4) | **86** |
| 3 | Google Hosted Libraries | **70** |
| 4 | Google reCAPTCHA | **59** |
| 5 | cdnjs (Cloudflare CDN) | **57** |
| 6 | jQuery | **44** |
| 7 | unpkg CDN | **29** |
| 8 | Google Tag Manager | **22** |
| 9 | Font Awesome | **19** |
| 10 | Adobe Dynamic Tag Management / Launch | **19** |
| 11 | Cookiebot | **8** |
| 12 | Facebook Pixel | **5** |
| 13 | Bootstrap | **4** |
| 14 | Google Analytics (Universal) | **1** |
| 15 | Cloudflare Web Analytics | **1** |

### Top Services by Page Prevalence

| # | Service | Reachable Pages | Prevalence of Reachable Pages |
|--:|---------|----------------:|------------------------------:|
| 1 | Google Analytics (GA4) | **83** | **23.4%** |
| 2 | jsDelivr CDN | **74** | **20.9%** |
| 3 | Google Hosted Libraries | **60** | **16.9%** |
| 4 | Google reCAPTCHA | **58** | **16.4%** |
| 5 | cdnjs (Cloudflare CDN) | **44** | **12.4%** |
| 6 | jQuery | **37** | **10.5%** |
| 7 | Google Tag Manager | **21** | **5.9%** |
| 8 | unpkg CDN | **20** | **5.6%** |
| 9 | Adobe Dynamic Tag Management / Launch | **19** | **5.4%** |
| 10 | Font Awesome | **16** | **4.5%** |
| 11 | Cookiebot | **8** | **2.3%** |
| 12 | Facebook Pixel | **5** | **1.4%** |
| 13 | Bootstrap | **4** | **1.1%** |
| 14 | Cloudflare Web Analytics | **1** | **0.3%** |
| 15 | Google Analytics (Universal) | **1** | **0.3%** |

### Top Service Categories

| # | Category | Loads |
|--:|----------|------:|
| 1 | CDN | **257** |
| 2 | JavaScript Library | **114** |
| 3 | Analytics | **112** |
| 4 | Security | **59** |
| 5 | CAPTCHA | **59** |
| 6 | Tag Manager | **41** |
| 7 | Icon Library | **19** |
| 8 | Cookie Consent | **8** |
| 9 | Advertising | **5** |
| 10 | UI Framework | **4** |

### Category Balance

Infrastructure-heavy categories (CDNs, core libraries, and UI assets):

| # | Infrastructure Category | Loads |
|--:|--------------------------|------:|
| 1 | CDN | **257** |
| 2 | JavaScript Library | **114** |
| 3 | Icon Library | **19** |
| 4 | UI Framework | **4** |

Policy-relevant categories (tracking, consent, support, and security tooling):

| # | Policy-Relevant Category | Loads |
|--:|--------------------------|------:|
| 1 | Analytics | **112** |
| 2 | Security | **59** |
| 3 | CAPTCHA | **59** |
| 4 | Tag Manager | **41** |
| 5 | Cookie Consent | **8** |
| 6 | Advertising | **5** |

### Unknown Third-Party Hosts (Review Queue)

| # | Host | Loads | Reachable Pages |
|--:|------|------:|----------------:|
| 1 | `webcachex-eu.datareporter.eu` | **162** | **162** |
| 2 | `www.csspo.gouv.qc.ca` | **33** | **3** |
| 3 | `translate.google.com` | **28** | **28** |
| 4 | `d2i63gac8idpto.cloudfront.net` | **27** | **2** |
| 5 | `s7.addthis.com` | **26** | **24** |
| 6 | `content.powerapps.com` | **24** | **2** |
| 7 | `use.typekit.net` | **23** | **23** |
| 8 | `www.canada.ca` | **18** | **10** |
| 9 | `cdn-cookieyes.com` | **15** | **15** |
| 10 | `maps.googleapis.com` | **11** | **11** |
| 11 | `www.gstatic.com` | **9** | **9** |
| 12 | `service.bmf.gv.at` | **7** | **3** |
| 13 | `maps.google.com` | **6** | **6** |
| 14 | `stp.wien.gv.at` | **6** | **6** |
| 15 | `static.etracker.com` | **6** | **6** |

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
