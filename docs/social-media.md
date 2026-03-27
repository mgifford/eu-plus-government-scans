---
title: Social Media Scanning
layout: page
---

# Social Media Scanning

<!-- SOCIAL_MEDIA_STATS_START -->

_Stats as of 2026-03-27 14:25 UTC — last scan: 2026-03-27_

**53** scan batches run

**14,200** of **82,714** available pages scanned (**17.2%** coverage)
**13,450** of **14,200** scanned pages were reachable (**94.7%**)

| Platform | Pages with link | % of scanned | % of reachable |
|----------|----------------|:------------:|:--------------:|
| 🐦 Twitter | **2,000** | 14.1% | 14.9% |
| ✖ X | **438** | 3.1% | 3.3% |
| 🦋 Bluesky | **151** | 1.1% | 1.1% |
| 🐘 Mastodon / Fediverse | **578** | 4.1% | 4.3% |

📥 Machine-readable results: [social-media-data.json](social-media-data.json)

---

## Social Media Scan by Country

| Country | Scanned | Available | Reachable | Twitter-only | Modern | Mixed | No Social | Scan Period |
|---------|---------|-----------|-----------|-------------|--------|-------|-----------|-------------|
| AUSTRIA | 821 | 821 | 787 | 30 | 25 | 22 | 710 | Mar 2026 |
| BELGIUM | 1,309 | 1,309 | 1,230 | 206 | 58 | 47 | 929 | Mar 2026 |
| BULGARIA | 291 | 291 | 269 | 21 | 11 | 2 | 235 | Mar 2026 |
| CROATIA | 233 | 233 | 232 | 31 | 11 | 3 | 187 | Mar 2026 |
| CZECHIA | 843 | 843 | 803 | 124 | 21 | 15 | 643 | Mar 2026 |
| DENMARK | 1,521 | 1,521 | 1,503 | 177 | 10 | 17 | 1,299 | Mar 2026 |
| ESTONIA | 396 | 396 | 384 | 65 | 22 | 4 | 293 | Mar 2026 |
| FINLAND | 180 | 180 | 172 | 38 | 2 | 0 | 132 | Mar 2026 |
| FRANCE | 8,606 | 10,007 | 8,070 | 1,334 | 159 | 247 | 6,330 | Mar 2026 |
| **Total** | **14,200** | **82,714** | **13,450** | **2,026** | **319** | **357** | **10,758** | — |

---

## Social Media Platform Breakdown

Number of **scanned** pages per country that link to each platform. A page may link to more than one platform. Percentages show the share of all scanned pages.

| Country | Scanned | Reachable | Twitter | X | Bluesky | Mastodon | Legacy % | Modern % |
|---------|---------|-----------|---------|---|---------|----------|----------|----------|
| AUSTRIA | 821 | 787 | 35 | 18 | 16 | 42 | 6.3% | 5.7% |
| BELGIUM | 1,309 | 1,230 | 183 | 74 | 27 | 90 | 19.3% | 8.0% |
| BULGARIA | 291 | 269 | 18 | 5 | 0 | 13 | 7.9% | 4.5% |
| CROATIA | 233 | 232 | 34 | 0 | 0 | 14 | 14.6% | 6.0% |
| CZECHIA | 843 | 803 | 131 | 10 | 0 | 36 | 16.5% | 4.3% |
| DENMARK | 1,521 | 1,503 | 176 | 21 | 17 | 13 | 12.8% | 1.8% |
| ESTONIA | 396 | 384 | 67 | 2 | 0 | 26 | 17.4% | 6.6% |
| FINLAND | 180 | 172 | 26 | 13 | 2 | 0 | 21.1% | 1.1% |
| FRANCE | 8,606 | 8,070 | 1,330 | 295 | 89 | 344 | 18.4% | 4.7% |
| **Total** | **14,200** | **13,450** | **2,000** | **438** | **151** | **578** | **16.8%** | **4.8%** |

> **Legacy platforms** (Twitter / X) vs **modern open platforms** (Bluesky / Mastodon) — percentages are share of **scanned** pages that contain at least one link to any platform in that group.

<!-- SOCIAL_MEDIA_STATS_END -->

---

## Overview

The social media scanner fetches each government page and inspects the HTML for
links to known social platforms. Results are stored in the metadata database
and published to this site via the [Scan Progress Report](scan-progress.md).

Scans run **automatically every 3 hours** via GitHub Actions so that the full
set of ~80,000 URLs across 31 countries can be covered gradually without
overloading government servers.

---

## Platforms Tracked

| Platform | Domains detected |
|----------|-----------------|
| **Twitter** | `twitter.com` |
| **X** | `x.com` |
| **Bluesky** | `bsky.app`, `bsky.social` |
| **Mastodon / Fediverse** | 40+ known instances + `/@username` pattern detection |

---

## Tier Classification

Each scanned page is assigned one of five tiers:

| Tier | Meaning |
|------|---------|
| `unreachable` | Page could not be fetched (network error, timeout, 4xx/5xx) |
| `no_social` | Page is reachable but contains no recognised social media links |
| `twitter_only` | Page links only to Twitter / X (legacy platform) |
| `modern_only` | Page links only to Bluesky or Mastodon (modern / open platforms) |
| `mixed` | Page links to Twitter/X **and** at least one modern platform |

---

## Viewing Results

### Scan Progress Report

The **[Scan Progress Report](scan-progress.md)** is regenerated after every
scan and shows per-country breakdowns including:

- Total URLs scanned and reachable count
- Tier distribution (twitter-only / modern / mixed / no-social / unreachable)
- Per-platform link counts (Twitter, X, Bluesky, Mastodon)
- Date range showing when each country was last scanned

### GitHub Actions Artifacts

Each workflow run also uploads a scan artifact containing:

- `data/metadata.db` — the full SQLite results database
- `social-scan-output.txt` — the raw scan log
- `data/toon-seeds/countries/**_social.toon` — annotated TOON files

To download artifacts:

1. Go to [GitHub Actions → Scan Social Media Links](https://github.com/mgifford/eu-plus-government-scans/actions/workflows/scan-social-media.yml)
2. Click on the relevant workflow run
3. Scroll to the **Artifacts** section at the bottom of the run summary page
4. Download `social-scan-<run_number>` to inspect the database or TOON files

---

## Running a Scan Manually

### Via GitHub Actions (recommended)

1. Go to [Actions → Scan Social Media Links](https://github.com/mgifford/eu-plus-government-scans/actions/workflows/scan-social-media.yml)
2. Click **Run workflow**
3. Optionally enter a country code (e.g. `ICELAND`) or leave blank to scan all
4. Optionally adjust the rate limit (default: 1.0 req/sec)

### Via the command line

```bash
# Scan a single country
python3 -m src.cli.scan_social_media --country ICELAND --rate-limit 1.0

# Scan all countries (with a 110-minute runtime cap)
python3 -m src.cli.scan_social_media --all --max-runtime 110 --rate-limit 1.0
```

---

## Output Format

### Annotated TOON file (`*_social.toon`)

Each page entry gains a `social_media` field:

```json
{
  "url": "https://example.gov/",
  "is_root_page": true,
  "social_media": {
    "is_reachable": true,
    "social_tier": "mixed",
    "twitter_links": ["https://twitter.com/example_gov"],
    "x_links": [],
    "bluesky_links": ["https://bsky.app/profile/example.bsky.social"],
    "mastodon_links": []
  }
}
```

### Database table (`url_social_media_results`)

| Column | Type | Description |
|--------|------|-------------|
| `url` | TEXT | Page URL |
| `country_code` | TEXT | Country identifier (e.g. `ICELAND`) |
| `scan_id` | TEXT | Unique scan run identifier |
| `is_reachable` | INTEGER | 1 = reachable, 0 = not reachable |
| `twitter_links` | TEXT | JSON list of `twitter.com` hrefs found |
| `x_links` | TEXT | JSON list of `x.com` hrefs found |
| `bluesky_links` | TEXT | JSON list of Bluesky hrefs found |
| `mastodon_links` | TEXT | JSON list of Mastodon hrefs found |
| `social_tier` | TEXT | Tier classification (see above) |
| `scanned_at` | TEXT | ISO-8601 timestamp of scan |

---

## Countries Covered

Scans cover all 27 EU member states plus 4 allied nations:

| Region | Countries |
|--------|----------|
| EU member states | Austria, Belgium, Bulgaria, Croatia, Czechia, Denmark, Estonia, Finland, France, Germany, Greece, Hungary, Ireland, Italy, Latvia, Lithuania, Luxembourg, Malta, Netherlands, Poland, Portugal, Republic of Cyprus, Romania, Slovakia, Slovenia, Spain, Sweden |
| Allied nations | Iceland, Norway, Switzerland, United Kingdom |

See also the **[Government Domains](domains.md)** page for a full listing of
all domains tracked per country.

---

## Architecture

```
scan-social-media.yml (GitHub Actions — every 3 hours)
    ↓
scan_social_media.py (CLI)
    ↓
SocialMediaScannerJob.scan_country()
    ↓
SocialMediaScanner.scan_urls_batch()
    ↓
For each URL:
    httpx.get()  →  HTML content
    BeautifulSoup  →  extract <a href="..."> links
    Match against platform patterns
    ↓
Classify into social_tier
    ↓
Save to url_social_media_results table
    ↓
Write *_social.toon output file
```
