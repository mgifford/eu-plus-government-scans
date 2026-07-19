---
title: Third-Party JavaScript
layout: page
---

<!-- THIRD_PARTY_JS_STATS_START -->

_Stats as of 2026-07-19 03:23 UTC — last scan: 2026-07-19_

**3** scan batches run

**1,350** of **82,714** available pages scanned (**1.6%** coverage)
**1,248** of **1,350** scanned pages were reachable (**92.4%**)
**483** reachable pages loaded at least one third-party script (**38.7%** of reachable)
**221** known third-party service loads identified
**13** unique known services across **10** categories

---

## Third-Party JavaScript by Country

| Country | Scanned | Available | Reachable | URLs with 3rd-Party JS | Known Service Loads | JS URLs /100 Reachable | Known Loads /100 Reachable | Last Scan |
|---------|---------|-----------|-----------|------------------------|--------------------|------------------------|---------------------------|----------|
| Austria | 821 | 821 | 784 | 273 | 52 | 34.8 | 6.6 | 2026-07-19 |
| Bulgaria | 291 | 291 | 260 | 102 | 124 | 39.2 | 47.7 | 2026-07-19 |
| France | 238 | 10,007 | 204 | 108 | 45 | 52.9 | 22.1 | 2026-07-19 |

> Hover or focus any non-zero country-table count to preview matching pages. Activate the number to keep the preview open and download a CSV for that country and metric from [Download machine-readable third-party tools data (JSON)](third-party-tools-data.json).

---

### Top Third-Party Services

| # | Service | Loads |
|--:|---------|------:|
| 1 | jsDelivr CDN | **49** |
| 2 | Google Analytics (GA4) | **30** |
| 3 | Google reCAPTCHA | **27** |
| 4 | Google Hosted Libraries | **27** |
| 5 | cdnjs (Cloudflare CDN) | **27** |
| 6 | unpkg CDN | **16** |
| 7 | jQuery | **14** |
| 8 | Cookiebot | **8** |
| 9 | Font Awesome | **7** |
| 10 | Bootstrap | **5** |
| 11 | Google Tag Manager | **4** |
| 12 | Facebook Pixel | **4** |
| 13 | Matomo Cloud | **3** |

### Top Services by Page Prevalence

| # | Service | Reachable Pages | Prevalence of Reachable Pages |
|--:|---------|----------------:|------------------------------:|
| 1 | Google Analytics (GA4) | **30** | **14.7%** |
| 2 | jsDelivr CDN | **28** | **13.7%** |
| 3 | Google reCAPTCHA | **27** | **13.2%** |
| 4 | Google Hosted Libraries | **26** | **12.7%** |
| 5 | cdnjs (Cloudflare CDN) | **23** | **11.3%** |
| 6 | jQuery | **12** | **5.9%** |
| 7 | unpkg CDN | **12** | **5.9%** |
| 8 | Cookiebot | **8** | **3.9%** |
| 9 | Font Awesome | **7** | **3.4%** |
| 10 | Bootstrap | **5** | **2.5%** |
| 11 | Facebook Pixel | **4** | **2.0%** |
| 12 | Google Tag Manager | **4** | **2.0%** |
| 13 | Matomo Cloud | **3** | **1.5%** |

### Top Service Categories

| # | Category | Loads |
|--:|----------|------:|
| 1 | CDN | **119** |
| 2 | JavaScript Library | **41** |
| 3 | Analytics | **37** |
| 4 | Security | **27** |
| 5 | CAPTCHA | **27** |
| 6 | Cookie Consent | **8** |
| 7 | Icon Library | **7** |
| 8 | UI Framework | **5** |
| 9 | Tag Manager | **4** |
| 10 | Advertising | **4** |

### Category Balance

Infrastructure-heavy categories (CDNs, core libraries, and UI assets):

| # | Infrastructure Category | Loads |
|--:|--------------------------|------:|
| 1 | CDN | **119** |
| 2 | JavaScript Library | **41** |
| 3 | Icon Library | **7** |
| 4 | UI Framework | **5** |

Policy-relevant categories (tracking, consent, support, and security tooling):

| # | Policy-Relevant Category | Loads |
|--:|--------------------------|------:|
| 1 | Analytics | **37** |
| 2 | Security | **27** |
| 3 | CAPTCHA | **27** |
| 4 | Cookie Consent | **8** |
| 5 | Tag Manager | **4** |
| 6 | Advertising | **4** |

### Unknown Third-Party Hosts (Review Queue)

| # | Host | Loads | Reachable Pages |
|--:|------|------:|----------------:|
| 1 | `cdn.ent.auvergnerhonealpes.fr` | **452** | **45** |
| 2 | `webcachex-eu.datareporter.eu` | **162** | **162** |
| 3 | `cdn.ecollege.haute-garonne.fr` | **97** | **10** |
| 4 | `static.crisp.help` | **39** | **16** |
| 5 | `s7.addthis.com` | **27** | **25** |
| 6 | `translate.google.com` | **20** | **20** |
| 7 | `www.gstatic.com` | **9** | **9** |
| 8 | `service.bmf.gv.at` | **7** | **3** |
| 9 | `moncompte.paris.fr` | **7** | **7** |
| 10 | `maps.google.com` | **6** | **6** |
| 11 | `stp.wien.gv.at` | **6** | **6** |
| 12 | `static.etracker.com` | **6** | **6** |
| 13 | `inside.bundesheer.at` | **6** | **3** |
| 14 | `analytics.silktide.com` | **5** | **5** |
| 15 | `consent.cookiebot.eu` | **5** | **5** |

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
