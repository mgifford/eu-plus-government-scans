---
title: Social Media Scanning
layout: page
---

> **Method change, November 2026.** Until this change, any link whose address
> contained `/@name` was counted as Mastodon. TikTok, YouTube, Threads, Medium
> and Substack use the same pattern, so their links were counted as Mastodon
> too. That overstated Mastodon use and raised Digital Sovereignty Scores.
> Results stored before the change are corrected automatically, and TikTok,
> YouTube, Blacksky and Gander are now tracked as platforms of their own.
> TikTok and YouTube counts stay incomplete until every page has been
> rescanned, because older scans kept only the TikTok and YouTube links that
> used `/@name`.
>
> **Counting change, November 2026.** Figures used to count a page under a
> platform if any scan had ever found a link, so a government that left a
> platform still counted as using it. Each page is now counted as of its most
> recent successful scan. A scan that fails, or returns an error page such as
> a 404, is not treated as the page dropping its links.

<!-- SOCIAL_MEDIA_STATS_START -->

<div id="sm-tier-pie-container" style="float:right;margin:0 0 1rem 1.5rem;width:260px;max-width:45%;">
<svg role="img" aria-labelledby="pie-title pie-desc" viewBox="0 0 240 314" width="240" height="314" xmlns="http://www.w3.org/2000/svg">
<title id="pie-title">Social media tier distribution</title>
<desc id="pie-desc">Pie chart: social media tier distribution across 87,696 scanned pages. Legacy only: 32,207 (36.7%), Modern only: 149 (0.2%), Mixed: 1,119 (1.3%), No Social: 48,840 (55.7%)</desc>
<path d="M 120,110 L 120.000,20.000 A 90,90 0 0,1 176.815,179.800 Z" fill="#1a8cd8" stroke="#fff" stroke-width="1"><title>Twitter/X only: 32,207 (39.1%)</title></path>
<path d="M 120,110 L 176.815,179.800 A 90,90 0 0,1 176.018,180.442 Z" fill="#0085ff" stroke="#fff" stroke-width="1"><title>Modern only: 149 (0.2%)</title></path>
<path d="M 120,110 L 176.018,180.442 A 90,90 0 0,1 169.804,184.964 Z" fill="#7856ff" stroke="#fff" stroke-width="1"><title>Mixed: 1,119 (1.4%)</title></path>
<path d="M 120,110 L 169.804,184.964 A 90,90 0 1,1 120.000,20.000 Z" fill="#cccccc" stroke="#fff" stroke-width="1"><title>No Social: 48,840 (59.3%)</title></path>
<rect x="20" y="216" width="14" height="14" fill="#1a8cd8"/>
<text x="40" y="227" font-size="11" font-family="sans-serif" fill="#333">Twitter/X only (39.1%)</text>
<rect x="20" y="238" width="14" height="14" fill="#0085ff"/>
<text x="40" y="249" font-size="11" font-family="sans-serif" fill="#333">Modern only (0.2%)</text>
<rect x="20" y="260" width="14" height="14" fill="#7856ff"/>
<text x="40" y="271" font-size="11" font-family="sans-serif" fill="#333">Mixed (1.4%)</text>
<rect x="20" y="282" width="14" height="14" fill="#cccccc"/>
<text x="40" y="293" font-size="11" font-family="sans-serif" fill="#333">No Social (59.3%)</text>
</svg>
<p style="text-align:center;font-size:0.75em;margin:0.3rem 0 0;color:#555;font-style:italic;">Social media tier distribution</p>
</div>

_Stats as of 2026-11-18 18:22 UTC — last scan: 2026-11-18_

**428** scan batches run

**87,690** of **87,696** available pages scanned (**100.0%** coverage)
**82,309** of **87,690** scanned pages were reachable (**93.9%**)

**Legacy social media** (older, centralised platforms):

| Platform | Pages with link | % of scanned | % of reachable |
|----------|----------------|:------------:|:--------------:|
| 🐦 Twitter | **13,630** | 15.5% | 16.6% |
| ✖ X | **3,840** | 4.4% | 4.7% |
| 👍 Facebook | **29,396** | 33.5% | 35.7% |
| 💼 LinkedIn | **10,725** | 12.2% | 13.0% |
| TikTok | **1,652** | 1.9% | 2.0% |
| YouTube | **7,066** | 8.1% | 8.6% |

**Modern / open social media** (decentralised or open platforms):

| Platform | Pages with link | % of scanned | % of reachable |
|----------|----------------|:------------:|:--------------:|
| 🦋 Bluesky | **867** | 1.0% | 1.1% |
| Blacksky | **0** | 0.0% | 0.0% |
| Gander | **0** | 0.0% | 0.0% |
| 🐘 Mastodon / Fediverse | **500** | 0.6% | 0.6% |

<div style="clear:both;"></div>

📥 Machine-readable results are available as the [social-media-data.json artifact (machine-readable JSON)](https://github.com/mgifford/eu-plus-government-scans/actions/workflows/generate-scan-progress.yml).

---

## Digital Sovereignty Rankings

Countries ranked by **Digital Sovereignty Score**: the percentage of reachable pages using *no social media* or *modern open platforms only* (Mastodon, Bluesky, Blacksky, Gander).  A higher score means fewer links to centralised corporate social-media platforms (Twitter / X, Facebook, LinkedIn, TikTok, YouTube).  Pages with no social-media links at all score highest; pages linking only to open platforms also rank well.  **Legacy Exposure** shows the percentage of reachable pages that still link to at least one of those corporate platforms.

| Rank | Country | Sovereignty Score | No Social | Modern Only | Legacy Exposure | Tier |
|------|---------|:-----------------:|:---------:|:-----------:|:---------------:|------|
| 1 | Finland | 76.7% | 145 | 0 | 23.3% | 🥉 Growing |
| 2 | Norway | 75.8% | 183 | 2 | 24.2% | 🥉 Growing |
| 3 | Lithuania | 74.6% | 85 | 0 | 25.4% | 🥉 Growing |
| 4 | Iceland | 72.7% | 104 | 0 | 27.3% | 🥉 Growing |
| 5 | Malta | 71.8% | 427 | 0 | 28.2% | 🥉 Growing |
| 6 | Germany | 67.1% | 4,319 | 46 | 32.9% | 🥉 Growing |
| 7 | France | 66.7% | 6,209 | 15 | 33.3% | 🥉 Growing |
| 8 | Canada | 66.1% | 2,829 | 4 | 33.9% | 🥉 Growing |
| 9 | Portugal | 66.1% | 2,130 | 1 | 33.9% | 🥉 Growing |
| 10 | Netherlands | 64.8% | 583 | 10 | 35.2% | 🥉 Growing |
| 11 | Switzerland | 64.3% | 1,327 | 13 | 35.7% | 🥉 Growing |
| 12 | Denmark | 63.1% | 952 | 0 | 36.9% | 🥉 Growing |
| 13 | United Kingdom | 63.0% | 11,789 | 7 | 37.0% | 🥉 Growing |
| 14 | Greece | 62.7% | 1,034 | 1 | 37.3% | 🥉 Growing |
| 15 | Slovenia | 62.5% | 130 | 0 | 37.5% | 🥉 Growing |
| 16 | Czechia | 62.1% | 499 | 0 | 37.9% | 🥉 Growing |
| 17 | Sweden | 61.8% | 1,008 | 1 | 38.2% | 🥉 Growing |
| 18 | Romania | 61.6% | 214 | 3 | 38.4% | 🥉 Growing |
| 19 | Slovakia | 61.2% | 256 | 0 | 38.8% | 🥉 Growing |
| 20 | Croatia | 58.7% | 149 | 0 | 41.3% | 🥉 Growing |
| 21 | Belgium | 58.5% | 722 | 4 | 41.5% | 🥉 Growing |
| 22 | Hungary | 57.5% | 220 | 2 | 42.5% | 🥉 Growing |
| 23 | Bulgaria | 56.7% | 173 | 0 | 43.3% | 🥉 Growing |
| 24 | Spain | 56.6% | 3,064 | 2 | 43.4% | 🥉 Growing |
| 25 | Austria | 52.2% | 412 | 0 | 47.8% | 🥉 Growing |
| 26 | Estonia | 50.3% | 193 | 0 | 49.7% | 🥉 Growing |
| 27 | Poland | 48.5% | 6,708 | 33 | 51.5% | 🥉 Growing |
| 28 | Cyprus | 48.3% | 14 | 0 | 51.7% | 🥉 Growing |
| 29 | Ireland | 47.1% | 236 | 0 | 52.9% | 🥉 Growing |
| 30 | Italy | 45.0% | 2,189 | 5 | 55.0% | 🥉 Growing |
| 31 | Luxembourg | 44.8% | 244 | 0 | 55.2% | 🥉 Growing |
| 32 | Latvia | 38.2% | 293 | 0 | 61.8% | ⚠️ Legacy-heavy |

---

## Social Media Scan by Country

**Available**: all government pages tracked in our domain list. **Reachable**: of those scanned, pages that returned a valid HTTP response (not an error or timeout). **Sov. Score**: Digital Sovereignty Score — % of reachable pages with no social media or modern-only social presence. Tier columns classify each page by its overall social media presence; platform columns count pages with at least one link to that platform, so a page may appear in more than one platform column. Both describe each page as of its most recent successful scan: a page that removed a link no longer counts, and a failed scan leaves the page as it was last seen.

| Country | Scanned | Available | Reachable | Sov. Score | No Social | Legacy-only | Twitter | X | Facebook | LinkedIn | TikTok | YouTube | Modern | Mixed | Bluesky | Blacksky | Gander | Mastodon | Scan Period |
|---------|---------|-----------|-----------|:----------:|-----------|-------------|---------|---|----------|----------|--------|---------|--------|-------|---------|----------|--------|----------|-------------|
| Austria | 822 | 822 | 789 | 52.2% | 412 | 359 | 32 | 24 | 351 | 187 | 19 | 258 | 0 | 18 | 18 | 0 | 0 | 0 | Aug 2026 – Nov 2026 |
| Belgium | 1,329 | 1,329 | 1,240 | 58.5% | 722 | 469 | 158 | 79 | 456 | 331 | 21 | 229 | 4 | 45 | 27 | 0 | 0 | 22 | Aug 2026 – Nov 2026 |
| Bulgaria | 353 | 353 | 305 | 56.7% | 173 | 132 | 22 | 6 | 114 | 11 | 2 | 63 | 0 | 0 | 0 | 0 | 0 | 0 | Aug 2026 – Nov 2026 |
| Canada | 4,469 | 4,469 | 4,284 | 66.1% | 2,829 | 1,403 | 457 | 153 | 1,315 | 590 | 22 | 517 | 4 | 48 | 51 | 0 | 0 | 1 | Aug 2026 – Nov 2026 |
| Croatia | 257 | 257 | 254 | 58.7% | 149 | 105 | 47 | 15 | 98 | 35 | 22 | 68 | 0 | 0 | 0 | 0 | 0 | 0 | Aug 2026 – Nov 2026 |
| Czechia | 866 | 866 | 804 | 62.1% | 499 | 305 | 129 | 32 | 277 | 40 | 0 | 134 | 0 | 0 | 0 | 0 | 0 | 0 | Aug 2026 – Nov 2026 |
| Denmark | 1,536 | 1,536 | 1,509 | 63.1% | 952 | 540 | 157 | 18 | 451 | 323 | 0 | 36 | 0 | 17 | 17 | 0 | 0 | 0 | Aug 2026 – Nov 2026 |
| Estonia | 401 | 401 | 384 | 50.3% | 193 | 191 | 52 | 5 | 183 | 71 | 3 | 113 | 0 | 0 | 0 | 0 | 0 | 0 | Aug 2026 – Nov 2026 |
| Finland | 199 | 199 | 189 | 76.7% | 145 | 43 | 11 | 6 | 31 | 34 | 0 | 25 | 0 | 1 | 1 | 0 | 0 | 0 | Aug 2026 – Nov 2026 |
| France | 10,009 | 10,009 | 9,330 | 66.7% | 6,209 | 2,972 | 1,457 | 623 | 2,692 | 1,705 | 216 | 485 | 15 | 134 | 130 | 0 | 0 | 37 | Aug 2026 – Nov 2026 |
| Germany | 6,599 | 6,599 | 6,502 | 67.1% | 4,319 | 1,891 | 1,101 | 199 | 1,641 | 646 | 142 | 418 | 46 | 246 | 137 | 0 | 0 | 226 | Aug 2026 – Nov 2026 |
| Greece | 1,752 | 1,752 | 1,650 | 62.7% | 1,034 | 613 | 237 | 70 | 565 | 138 | 15 | 387 | 1 | 2 | 0 | 0 | 0 | 3 | Aug 2026 – Nov 2026 |
| Hungary | 392 | 392 | 386 | 57.5% | 220 | 164 | 29 | 0 | 155 | 15 | 21 | 92 | 2 | 0 | 0 | 0 | 0 | 2 | Aug 2026 – Nov 2026 |
| Iceland | 145 | 145 | 143 | 72.7% | 104 | 39 | 6 | 6 | 39 | 7 | 6 | 14 | 0 | 0 | 0 | 0 | 0 | 0 | Aug 2026 – Nov 2026 |
| Ireland | 536 | 536 | 501 | 47.1% | 236 | 247 | 152 | 40 | 221 | 111 | 22 | 166 | 0 | 18 | 15 | 0 | 0 | 3 | Aug 2026 – Nov 2026 |
| Italy | 5,351 | 5,351 | 4,875 | 45.0% | 2,189 | 2,663 | 1,998 | 148 | 2,527 | 582 | 44 | 600 | 5 | 18 | 0 | 0 | 0 | 23 | Aug 2026 – Nov 2026 |
| Latvia | 803 | 803 | 767 | 38.2% | 293 | 463 | 275 | 63 | 451 | 185 | 31 | 308 | 0 | 11 | 5 | 0 | 0 | 6 | Aug 2026 – Nov 2026 |
| Lithuania | 122 | 122 | 114 | 74.6% | 85 | 29 | 2 | 4 | 29 | 18 | 0 | 20 | 0 | 0 | 0 | 0 | 0 | 0 | Aug 2026 – Nov 2026 |
| Luxembourg | 573 | 573 | 545 | 44.8% | 244 | 160 | 178 | 9 | 269 | 233 | 14 | 106 | 0 | 141 | 141 | 0 | 0 | 3 | Aug 2026 – Nov 2026 |
| Malta | 610 | 610 | 595 | 71.8% | 427 | 168 | 47 | 15 | 158 | 71 | 10 | 56 | 0 | 0 | 0 | 0 | 0 | 0 | Aug 2026 – Nov 2026 |
| Netherlands | 945 | 945 | 915 | 64.8% | 583 | 258 | 107 | 85 | 279 | 210 | 7 | 160 | 10 | 64 | 46 | 0 | 0 | 33 | Aug 2026 – Nov 2026 |
| Norway | 249 | 249 | 244 | 75.8% | 183 | 59 | 9 | 13 | 40 | 45 | 0 | 16 | 2 | 0 | 0 | 0 | 0 | 2 | Aug 2026 – Nov 2026 |
| Poland | 14,951 | 14,951 | 13,890 | 48.5% | 6,708 | 7,099 | 1,021 | 342 | 7,004 | 815 | 541 | 829 | 33 | 50 | 1 | 0 | 0 | 82 | Aug 2026 – Nov 2026 |
| Portugal | 3,508 | 3,508 | 3,226 | 66.1% | 2,130 | 1,088 | 345 | 94 | 1,019 | 264 | 44 | 362 | 1 | 7 | 2 | 0 | 0 | 6 | Aug 2026 – Nov 2026 |
| Cyprus | 29 | 29 | 29 | 48.3% | 14 | 15 | 9 | 1 | 15 | 3 | 0 | 13 | 0 | 0 | 0 | 0 | 0 | 0 | Aug 2026 – Nov 2026 |
| Romania | 807 | 807 | 352 | 61.6% | 214 | 135 | 40 | 8 | 133 | 16 | 5 | 24 | 3 | 0 | 0 | 0 | 0 | 3 | Aug 2026 – Nov 2026 |
| Slovakia | 442 | 442 | 418 | 61.2% | 256 | 161 | 19 | 12 | 154 | 62 | 10 | 77 | 0 | 1 | 1 | 0 | 0 | 0 | Aug 2026 – Nov 2026 |
| Slovenia | 214 | 214 | 208 | 62.5% | 130 | 77 | 24 | 7 | 68 | 12 | 6 | 47 | 0 | 1 | 1 | 0 | 0 | 0 | Aug 2026 – Nov 2026 |
| Spain | 6,091 | 6,091 | 5,415 | 56.6% | 3,064 | 2,269 | 1,619 | 508 | 1,774 | 540 | 167 | 403 | 2 | 80 | 72 | 0 | 0 | 10 | Aug 2026 – Nov 2026 |
| Sweden | 1,702 | 1,702 | 1,633 | 61.8% | 1,008 | 606 | 82 | 21 | 506 | 419 | 26 | 152 | 1 | 18 | 18 | 0 | 0 | 1 | Aug 2026 – Nov 2026 |
| Switzerland | 2,123 | 2,123 | 2,085 | 64.3% | 1,327 | 673 | 213 | 226 | 240 | 563 | 12 | 212 | 13 | 72 | 55 | 0 | 0 | 32 | Aug 2026 – Nov 2026 |
| United Kingdom | 19,511 | 19,511 | 18,734 | 63.0% | 11,789 | 6,811 | 3,601 | 1,014 | 6,147 | 2,443 | 224 | 679 | 7 | 127 | 129 | 0 | 0 | 5 | Aug 2026 – Nov 2026 |
| **Total** | **87,696** | **87,696** | **82,315** | **59.5%** | **48,840** | **32,207** | **13,636** | **3,846** | **29,402** | **10,725** | **1,652** | **7,069** | **149** | **1,119** | **867** | **0** | **0** | **500** | — |

> Hover or focus any non-zero country-table count to preview matching pages. Activate the number to keep the preview open. Full machine-readable data is available as the [social-media-data.json artifact (machine-readable JSON)](https://github.com/mgifford/eu-plus-government-scans/actions/workflows/generate-scan-progress.yml).

<!-- SOCIAL_MEDIA_STATS_END -->

---

## Overview

The social media scanner fetches each government page and inspects the HTML for
links to known social platforms. Results are stored in the metadata database
and published to this site via the [Scan Progress Report](scan-progress.md).

Scans run **automatically every 8 hours** via GitHub Actions so that the full
set of ~88,000 URLs across 32 countries can be covered gradually without
overloading government servers.

---

## Platforms Tracked

### Legacy Social Media (older, centralised platforms)

| Platform | Domains detected |
|----------|-----------------|
| **Twitter** | `twitter.com` |
| **X** | `x.com` |
| **Facebook** | `facebook.com`, `fb.com` |
| **LinkedIn** | `linkedin.com` |
| **TikTok** | `tiktok.com`, `m.tiktok.com`, `vm.tiktok.com` |
| **YouTube** | `youtube.com`, `m.youtube.com`, `youtu.be` |

### Modern / Open Social Media (decentralised or open platforms)

| Platform | Domains detected |
|----------|-----------------|
| **Bluesky** | `bsky.app`, `bsky.social` |
| **Blacksky** | `blacksky.community` (an AT Protocol app, like Bluesky) |
| **Gander** | `gander.social`, `gandersocial.ca` (a Canadian AT Protocol app) |
| **Mastodon / Fediverse** | 40+ known instances + `/@username` pattern detection |

The `/@username` pattern is only applied to hosts that are not listed above.
Threads, Medium and Substack also use `/@username` addresses but are not
counted as Mastodon. Threads lets some accounts federate with Mastodon, but it
is run by Meta, so it is not treated as an open platform.

---

## Tier Classification

Each scanned page is assigned one of five tiers:

| Tier | Meaning |
|------|---------|
| `unreachable` | Page could not be fetched (network error, timeout, 4xx/5xx) |
| `no_social` | Page is reachable but contains no recognised social media links |
| `twitter_only` | Page links only to legacy platforms (Twitter, X, Facebook, LinkedIn, TikTok or YouTube) |
| `modern_only` | Page links only to modern / open platforms (Bluesky, Blacksky, Gander or Mastodon) |
| `mixed` | Page links to at least one legacy platform **and** at least one modern platform |

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

Each scanned page entry gains a `social_media` field. A page that could not be
fetched gets a `social_media_error` field holding the error message instead.

```json
{
  "url": "https://example.gov/",
  "is_root_page": true,
  "social_media": {
    "tier": "mixed",
    "twitter": ["https://twitter.com/example_gov"],
    "x": [],
    "bluesky": ["https://bsky.app/profile/example.bsky.social"],
    "mastodon": [],
    "facebook": [],
    "linkedin": [],
    "tiktok": [],
    "youtube": [],
    "blacksky": [],
    "gander": []
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
| `facebook_links` | TEXT | JSON list of `facebook.com` / `fb.com` hrefs found |
| `linkedin_links` | TEXT | JSON list of `linkedin.com` hrefs found |
| `tiktok_links` | TEXT | JSON list of TikTok hrefs found |
| `youtube_links` | TEXT | JSON list of YouTube hrefs found |
| `bluesky_links` | TEXT | JSON list of Bluesky hrefs found |
| `blacksky_links` | TEXT | JSON list of Blacksky hrefs found |
| `gander_links` | TEXT | JSON list of Gander hrefs found |
| `mastodon_links` | TEXT | JSON list of Mastodon hrefs found |
| `social_tier` | TEXT | Tier classification (see above) |
| `scanned_at` | TEXT | ISO-8601 timestamp of scan |

---

## Countries Covered

Scans cover all 27 EU member states plus 5 allied nations:

| Region | Countries |
|--------|----------|
| EU member states | Austria, Belgium, Bulgaria, Croatia, Czechia, Denmark, Estonia, Finland, France, Germany, Greece, Hungary, Ireland, Italy, Latvia, Lithuania, Luxembourg, Malta, Netherlands, Poland, Portugal, Republic of Cyprus, Romania, Slovakia, Slovenia, Spain, Sweden |
| Allied nations | Canada, Iceland, Norway, Switzerland, United Kingdom |

See also the **[Government Domains](domains.md)** page for a full listing of
all domains tracked per country.

---

## Architecture

```mermaid
flowchart TD
    A["scan-social-media.yml\n(GitHub Actions, every 8 hours)"]
    A --> B["scan_social_media.py (CLI)"]
    B --> C["SocialMediaScannerJob.scan_country()"]
    C --> D["SocialMediaScanner.scan_urls_batch()"]
    D --> E["For each URL"]
    E --> F["httpx.get() → HTML content"]
    F --> G["BeautifulSoup → extract href links\nMatch against platform patterns"]
    G --> H["Classify into social_tier"]
    H --> I["Save to url_social_media_results table"]
    I --> J["Write *_social.toon output file"]
```
