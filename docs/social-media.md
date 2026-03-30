---
title: Social Media Scanning
layout: page
---

# Social Media Scanning

<!-- SOCIAL_MEDIA_STATS_START -->

_Stats as of 2026-03-29 23:25 UTC — last scan: 2026-03-29_

**78** scan batches run

**42,197** of **82,714** available pages scanned (**51.0%** coverage)
**39,017** of **42,197** scanned pages were reachable (**92.5%**)

| Platform | Pages with link | % of scanned | % of reachable |
|----------|----------------|:------------:|:--------------:|
| 🐦 Twitter | **7,325** | 17.4% | 18.8% |
| ✖ X | **1,449** | 3.4% | 3.7% |
| 🦋 Bluesky | **377** | 0.9% | 1.0% |
| 🐘 Mastodon / Fediverse | **2,342** | 5.6% | 6.0% |

📥 Machine-readable results: [social-media-data.json](social-media-data.json)

---

## Social Media Scan by Country

Tier columns classify each page by its overall social media presence. Platform columns count pages with at least one link to that platform — a page may appear in more than one platform column.

| Country | Scanned | Available | Reachable | Twitter-only | Modern | Mixed | No Social | Twitter | X | Bluesky | Mastodon | Scan Period |
|---------|---------|-----------|-----------|-------------|--------|-------|-----------|---------|---|---------|----------|-------------|
| AUSTRIA | 821 | 821 | 787 | 30 | 25 | 22 | 710 | 35 | 18 | 16 | 42 | Mar 2026 |
| BELGIUM | 1,309 | 1,309 | 1,230 | 206 | 58 | 47 | 929 | 183 | 74 | 27 | 90 | Mar 2026 |
| BULGARIA | 291 | 291 | 269 | 21 | 11 | 2 | 235 | 18 | 5 | 0 | 13 | Mar 2026 |
| CROATIA | 233 | 233 | 232 | 31 | 11 | 3 | 187 | 34 | 0 | 0 | 14 | Mar 2026 |
| CZECHIA | 843 | 843 | 803 | 124 | 21 | 15 | 643 | 131 | 10 | 0 | 36 | Mar 2026 |
| DENMARK | 1,521 | 1,521 | 1,503 | 177 | 10 | 17 | 1,299 | 176 | 21 | 17 | 13 | Mar 2026 |
| ESTONIA | 396 | 396 | 384 | 65 | 22 | 4 | 293 | 67 | 2 | 0 | 26 | Mar 2026 |
| FINLAND | 180 | 180 | 172 | 38 | 2 | 0 | 132 | 26 | 13 | 2 | 0 | Mar 2026 |
| FRANCE | 10,007 | 10,007 | 9,373 | 1,935 | 212 | 361 | 6,865 | 1,799 | 629 | 124 | 495 | Mar 2026 |
| GERMANY | 6,555 | 6,555 | 6,443 | 1,083 | 301 | 191 | 4,868 | 1,171 | 174 | 118 | 441 | Mar 2026 |
| GREECE | 1,748 | 1,748 | 1,604 | 229 | 40 | 54 | 1,281 | 232 | 56 | 0 | 94 | Mar 2026 |
| HUNGARY | 390 | 390 | 366 | 24 | 20 | 5 | 317 | 29 | 0 | 0 | 25 | Mar 2026 |
| ICELAND | 139 | 139 | 135 | 5 | 8 | 6 | 116 | 8 | 5 | 0 | 14 | Mar 2026 |
| IRELAND | 522 | 522 | 494 | 149 | 25 | 29 | 291 | 153 | 31 | 18 | 42 | Mar 2026 |
| ITALY | 5,338 | 5,338 | 4,729 | 1,891 | 81 | 168 | 2,589 | 1,991 | 90 | 0 | 249 | Mar 2026 |
| LATVIA | 802 | 802 | 769 | 262 | 23 | 60 | 424 | 279 | 47 | 0 | 83 | Mar 2026 |
| LITHUANIA | 120 | 120 | 108 | 5 | 4 | 0 | 99 | 5 | 0 | 0 | 4 | Mar 2026 |
| LUXEMBOURG | 571 | 571 | 250 | 31 | 21 | 15 | 183 | 43 | 3 | 11 | 33 | Mar 2026 |
| MALTA | 608 | 608 | 595 | 60 | 20 | 14 | 501 | 57 | 17 | 0 | 34 | Mar 2026 |
| NETHERLANDS | 937 | 937 | 908 | 162 | 54 | 49 | 643 | 147 | 74 | 43 | 77 | Mar 2026 |
| NORWAY | 239 | 239 | 233 | 20 | 2 | 0 | 211 | 10 | 13 | 0 | 2 | Mar 2026 |
| POLAND | 6,244 | 14,938 | 5,688 | 447 | 255 | 179 | 4,807 | 519 | 135 | 1 | 433 | Mar 2026 |
| PORTUGAL | 2,383 | 3,503 | 1,942 | 215 | 53 | 29 | 1,645 | 212 | 32 | 0 | 82 | Mar 2026 |
| **Total** | **42,197** | **82,714** | **39,017** | **7,210** | **1,279** | **1,270** | **29,268** | **7,325** | **1,449** | **377** | **2,342** | — |

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
