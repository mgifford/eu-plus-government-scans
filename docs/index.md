---
title: EU Government Website Scans
layout: home
---

This project discovers and catalogues how European (and allied) government websites
use social media, whether their URLs are accessible, and what technology platforms
power them.

## Current Scan Progress

<!-- SCAN_PROGRESS_START -->

_Progress as of 2026-03-29 20:08 UTC_

| Scan Type | Pages Scanned | Coverage |
|-----------|--------------|----------|
| **Combined Reachability** | **37,233 confirmed reachable** | **█████████░░░░░░░░░░░ 45.0%** |
| Social Media | 39,814 scanned (37,075 reachable) | █████████░░░░░░░░░░░ 48.1% |
| URL Validation | 11,017 validated (9,299 valid) | ██░░░░░░░░░░░░░░░░░░ 13.3% |
| Accessibility Statements | 38,509 scanned | █████████░░░░░░░░░░░ 46.6% |

**23 countries** with scan data · **37,233** of **82,714** available pages confirmed reachable. See the [Scan Progress Report](scan-progress.md) for full details.

<!-- SCAN_PROGRESS_END -->

## Latest Scan Results

- **[Scan Progress Report](scan-progress.md)** — Up-to-date social media, URL validation,
  accessibility, and technology scan coverage across all countries, including the date range each country was scanned.
- **[Social Media](social-media.md)** — Detailed breakdown of social platform usage across
  government sites, with per-country platform counts (Twitter, X, Bluesky, Mastodon).
- **[Accessibility Statements](accessibility-statements.md)** — Per-country tracking of
  accessibility statement links as required by the EU Web Accessibility Directive.
- **[Technology Scanning](technology-scanning.md)** — Technologies detected on government sites
  (CMS, web server, analytics, and more).
- **[Government Domains](domains.md)** — Full listing of all ~36,000 government domains tracked
  across 31 countries.

## Accessing Scan Artifacts

Each GitHub Actions scan run uploads its results as a downloadable artifact:

1. Go to [GitHub Actions](https://github.com/mgifford/eu-plus-government-scans/actions)
2. Click the relevant workflow (e.g. **Scan Social Media Links**)
3. Open a completed run and scroll to the **Artifacts** section
4. Download the artifact (e.g. `social-scan-<run_number>`) to inspect:
   - `data/metadata.db` — the full SQLite results database
   - `*_social.toon` / `*_tech.toon` — annotated TOON files
   - Scan output logs

> The [Scan Progress Report](scan-progress.md) is regenerated automatically
> after every scan and committed to this site, so you can always see the
> latest aggregated results here without downloading artifacts.

## What We Track

### Social Media Presence

We check every government URL for links to:

| Platform | Includes |
|----------|----------|
| **Twitter / X** | `twitter.com`, `x.com` |
| **Bluesky** | `bsky.app`, `bsky.social` |
| **Mastodon / Fediverse** | 40+ known instances + `/@user` pattern detection |

Each scanned page is classified into one of the following tiers:

| Tier | Meaning |
|------|---------|
| `no_social` | Page is reachable but contains no social media links |
| `twitter_only` | Only links to Twitter / X (legacy platform) |
| `modern_only` | Only links to Bluesky or Mastodon (modern / open platforms) |
| `mixed` | Links to both Twitter/X **and** at least one modern platform |
| `unreachable` | Page could not be fetched |

See the **[Social Media](social-media.md)** page for full details.

### URL Validation

We validate each URL and track:

- HTTP status codes and redirect chains
- Persistent failures (a URL is removed after 2 consecutive failures)
- Final redirect destinations (updated for future scans)

### Technology Detection

We detect the CMS, framework, and analytics platforms used by each government site.

### Lighthouse Audits

We run Google Lighthouse on each government page and record five quality scores:
performance, accessibility, best practices, SEO, and PWA compliance (0–100 scale).

See **[Lighthouse Scanning](lighthouse-scanning.md)** for full details.

## Countries Covered

The dataset covers **all EU member states** plus selected allied nations:
United Kingdom, Switzerland, Iceland, Norway, and Canada.

See **[Government Domains](domains.md)** for the full domain listing per country.

## How the Scans Work

Scans run automatically on a schedule via **GitHub Actions**:

| Scan | Schedule | Priority |
|------|----------|----------|
| Social Media | Every 3 hours | **Highest** — confirms reachability *and* collects social-link data in one pass |
| Technology Detection | On demand | Medium — run manually for new countries |
| URL Validation | Every 12 hours | Lowest — lightweight redirect/404 check; skipped for pages already confirmed reachable within 30 days |
| Lighthouse Audits | Weekly (Sundays 04:00 UTC) | Medium — slow per-URL (~5 s); weekly cadence keeps data fresh without overloading servers |
| Scan Progress Report | After every scan | — |

After each scan run, this site is automatically updated with the latest results.

## Source Code & Data

- [GitHub Repository](https://github.com/mgifford/eu-plus-government-scans)
- [GitHub Actions Workflows](https://github.com/mgifford/eu-plus-government-scans/actions)
- [Accessibility Statement](https://github.com/mgifford/eu-plus-government-scans/blob/main/ACCESSIBILITY.md)

---

*Scan data is collected by automated workflows and stored as GitHub Actions artifacts.
The progress report is regenerated after every scan and committed directly to this site.*
