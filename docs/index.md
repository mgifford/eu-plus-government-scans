---
title: EU Government Website Scans
layout: home
---

This project discovers and catalogues how European (and allied) government websites
use social media, whether their URLs are accessible, and what technology platforms
power them.

## Latest Scan Results

- **[Scan Progress Report](scan-progress.md)** — Up-to-date social media, URL validation, and
  technology scan coverage across all countries.

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

### URL Validation

We validate each URL and track:

- HTTP status codes and redirect chains
- Persistent failures (a URL is removed after 2 consecutive failures)
- Final redirect destinations (updated for future scans)

### Technology Detection

We detect the CMS, framework, and analytics platforms used by each government site.

## Countries Covered

The dataset covers **all EU member states** plus selected allied nations:
United Kingdom, Switzerland, Iceland, Norway, and Canada.

## How the Scans Work

Scans run automatically on a schedule via **GitHub Actions**:

| Scan | Schedule |
|------|----------|
| Social Media | Every 3 hours |
| URL Validation | Every 6 hours |
| Technology Detection | On demand |
| Scan Progress Report | After every scan |

After each scan run, this site is automatically updated with the latest results.

## Source Code & Data

- [GitHub Repository](https://github.com/mgifford/eu-plus-government-scans)
- [GitHub Actions Workflows](https://github.com/mgifford/eu-plus-government-scans/actions)
- [Accessibility Statement](https://github.com/mgifford/eu-plus-government-scans/blob/main/ACCESSIBILITY.md)

---

*Scan data is collected by automated workflows and stored as GitHub Actions artifacts.
The progress report is regenerated after every scan and committed directly to this site.*
