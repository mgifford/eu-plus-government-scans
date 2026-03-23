# Scan Progress Report

_Generated: 2026-03-23 12:17 UTC_

This report tracks how far along each scan type is across all countries. It is regenerated automatically after every scan run.

## Overall Coverage

Coverage is measured as pages scanned out of **82,714** pages available in the seed files.

| Scan Type | Pages Scanned | Coverage |
|-----------|--------------|----------|
| URL Validation | 2,421 validated (2,115 valid) | ░░░░░░░░░░░░░░░░░░░░ 2.9% |
| Social Media | 2,978 scanned (2,793 reachable) | ░░░░░░░░░░░░░░░░░░░░ 3.6% |
| Technology | 0 scanned | (manual scan) |
| Lighthouse | 0 scanned | (manual scan) |

> **Combined Reachability** (shown after the next scan run) counts each URL once if it was confirmed reachable by *either* URL Validation or Social Media scanning.  URL Validation automatically skips pages already confirmed reachable by the Social Media scanner (within the last 30 days), so the two individual counts complement rather than duplicate each other.

## URL Validation by Country

| Country | Total | Valid | Invalid | Scan Period | Coverage |
|---------|-------|-------|---------|-------------|----------|
| AUSTRIA | 821 | 718 | 127 | Mar 2026 | ███████████████ 100.0% |
| BELGIUM | 1,309 | 1,166 | 419 | Mar 2026 | ███████████████ 100.0% |
| BULGARIA | 291 | 231 | 60 | Mar 2026 | ███████████████ 100.0% |

## Social Media Scan by Country

| Country | Scanned | Available | Reachable | Twitter-only | Modern | Mixed | No Social | Scan Period |
|---------|---------|-----------|-----------|-------------|--------|-------|-----------|-------------|
| AUSTRIA | 821 | 821 | 787 | 30 | 25 | 22 | 710 | Mar 2026 |
| BELGIUM | 1,309 | 1,309 | 1,229 | 205 | 58 | 47 | 924 | Mar 2026 |
| BULGARIA | 291 | 291 | 269 | 21 | 11 | 2 | 235 | Mar 2026 |
| CROATIA | 233 | 233 | 232 | 31 | 11 | 3 | 187 | Mar 2026 |
| CZECHIA | 324 | 843 | 276 | 48 | 11 | 4 | 213 | Mar 2026 |

## Social Media Platform Breakdown

Number of **scanned** pages per country that link to each platform. A page may link to more than one platform.

| Country | Scanned | Twitter | X | Bluesky | Mastodon | Legacy % | Modern % |
|---------|---------|---------|---|---------|----------|----------|----------|
| AUSTRIA | 821 | 35 | 18 | 16 | 42 | 6.3% | 5.7% |
| BELGIUM | 1,309 | 182 | 74 | 27 | 90 | 19.3% | 8.0% |
| BULGARIA | 291 | 18 | 5 | 0 | 13 | 7.9% | 4.5% |
| CROATIA | 233 | 34 | 0 | 0 | 14 | 14.6% | 6.0% |
| CZECHIA | 324 | 52 | 1 | 0 | 15 | 16.0% | 4.6% |
| **Total** | **2,978** | **321** | **98** | **43** | **174** | **13.9%** | **6.5%** |

> **Legacy platforms** (Twitter / X) vs **modern open platforms** (Bluesky / Mastodon) — percentages are share of **scanned** pages that contain at least one link to any platform in that group.

## Technology Scan

_No technology scans have been run yet. Trigger the **Scan Technology Stack** workflow manually._

## Lighthouse Scan

_No Lighthouse scans have been run yet. Trigger the **Scan Lighthouse** workflow manually._

## Countries With Social Scan But No URL Validation

These countries have social media scan data but no URL validation data (URL validation may have been skipped because the social scan already confirmed reachability):

`CROATIA`, `CZECHIA`

## Scan Priority Guide

Scans are ordered from **highest** to **lowest** priority:

1. **Social Media Scan** — runs every 3 hours; downloads and parses full pages, confirming reachability *and* detecting social links in one pass.
2. **Technology Scan** — run on demand; detects CMS, framework, and analytics platforms.
3. **Lighthouse Scan** — run on demand; measures performance, accessibility (WCAG), best practices, and SEO for each URL.
4. **URL Validation** — runs every 6 hours in the background; a lightweight redirect/404 check that is **automatically skipped** for URLs already confirmed reachable by a higher-priority scan within the last 30 days.

> **Tip:** Run a social media scan first for a new country — this simultaneously validates all URLs *and* collects social media data, avoiding a separate URL-only pass.

### Why are Social Media and URL Validation counts different?

The Social Media scanner runs more frequently than URL Validation and therefore covers more URLs over time.  Because the Social Media scanner already confirms whether each URL is reachable, the URL Validation job automatically *skips* any page already confirmed reachable within the last 30 days.  As a result the two individual scan counts do **not** simply add up — each scan covers a different subset of pages.

**What URL Validation adds beyond Social Media:**

- **Failure tracking** — records how many consecutive times each URL has failed; URLs that fail twice are removed from future scans to keep the seed file accurate.
- **Redirect-chain capture** — follows and stores the full redirect chain so the seed file can be updated with the final canonical URL.
- **Lightweight fallback** — a fast HTTP-only check for URLs that the Social Media scanner has not yet reached, without the overhead of downloading and parsing the full page.

The **Combined Reachability** row at the top of the coverage table counts each URL once if it was confirmed reachable by *either* scan, giving the most accurate picture of overall URL health.
