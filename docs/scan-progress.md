# Scan Progress Report

_Generated: 2026-03-29 08:33 UTC_

This report tracks how far along each scan type is across all countries. It is regenerated automatically after every scan run.

## Overall Coverage

Coverage is measured as pages scanned out of **82,714** pages available in the seed files.

| Scan Type | Pages Scanned | Available | Coverage |
|-----------|--------------|-----------|----------|
| **Combined Reachability** | **1,255 confirmed reachable** | 82,714 | **░░░░░░░░░░░░░░░░░░░░ 1.5%** |
| URL Validation | 0 validated (0 valid) | 82,714 | ░░░░░░░░░░░░░░░░░░░░ 0.0% |
| Social Media | 1,533 scanned (1,255 reachable) | 82,714 | ░░░░░░░░░░░░░░░░░░░░ 1.9% |
| Technology | 0 scanned | 82,714 | (manual scan) |
| Lighthouse | 295 scanned | 82,714 | ░░░░░░░░░░░░░░░░░░░░ 0.4% |
| Accessibility Statements | 0 scanned | 82,714 | ░░░░░░░░░░░░░░░░░░░░ 0.0% |

> **Combined Reachability** counts each URL once if it was confirmed reachable by *either* URL Validation or Social Media scanning.  URL Validation automatically skips pages already confirmed reachable by the Social Media scanner (within the last 30 days), so the two individual counts complement rather than duplicate each other.

## Social Media Scan by Country

| Country | Scanned | Available | Reachable | Twitter-only | Modern | Mixed | No Social | Scan Period |
|---------|---------|-----------|-----------|-------------|--------|-------|-----------|-------------|
| AUSTRIA | 821 | 821 | 785 | 30 | 25 | 22 | 708 | Mar 2026 |
| BELGIUM | 712 | 1,309 | 470 | 51 | 22 | 20 | 377 | Mar 2026 |

## Social Media Platform Breakdown

Number of **scanned** pages per country that link to each platform. A page may link to more than one platform.  Percentages show the share of all scanned pages.

| Country | Scanned | Reachable | Twitter | X | Bluesky | Mastodon | Legacy % | Modern % |
|---------|---------|-----------|---------|---|---------|----------|----------|----------|
| AUSTRIA | 821 | 785 | 35 | 18 | 16 | 42 | 6.3% | 5.7% |
| BELGIUM | 712 | 470 | 49 | 22 | 1 | 41 | 10.0% | 5.9% |
| **Total** | **1,533** | **1,255** | **84** | **40** | **17** | **83** | **8.0%** | **5.8%** |

> **Legacy platforms** (Twitter / X) vs **modern open platforms** (Bluesky / Mastodon) — percentages are share of **scanned** pages that contain at least one link to any platform in that group.

## Technology Scan

_No technology scans have been run yet. Trigger the **Scan Technology Stack** workflow manually._

## Lighthouse Scan by Country

| Country | URLs | Perf | A11y | Best Practices | SEO | Last Scan |
|---------|------|------|------|----------------|-----|----------|
| AUSTRIA | 295 | 68 | 89 | 93 | 85 | 2026-03-29 |

> Scores are averages across all successfully audited URLs, displayed as 0–100 (multiply source values × 100).

## Accessibility Statement Scan

_No accessibility statement scans have been run yet. Trigger the **Scan Accessibility Statements** workflow manually or wait for the next scheduled run._

## Countries With Social Scan But No URL Validation

These countries have social media scan data but no URL validation data (URL validation may have been skipped because the social scan already confirmed reachability):

`AUSTRIA`, `BELGIUM`

## Scan Priority Guide

Scans are ordered from **highest** to **lowest** priority:

1. **Social Media Scan** — runs every 3 hours; downloads and parses full pages, confirming reachability *and* detecting social links in one pass.
2. **Accessibility Statement Scan** — runs every 4 hours; checks whether each page links to an accessibility statement as required by the EU Web Accessibility Directive (Directive 2016/2102).
3. **Technology Scan** — run on demand; detects CMS, framework, and analytics platforms.
4. **Lighthouse Scan** — run on demand; measures performance, accessibility (WCAG), best practices, and SEO for each URL.
5. **URL Validation** — runs every 6 hours in the background; a lightweight redirect/404 check that is **automatically skipped** for URLs already confirmed reachable by a higher-priority scan within the last 30 days.

> **Tip:** Run a social media scan first for a new country — this simultaneously validates all URLs *and* collects social media data, avoiding a separate URL-only pass.

### Why are Social Media and URL Validation counts different?

The Social Media scanner runs more frequently than URL Validation and therefore covers more URLs over time.  Because the Social Media scanner already confirms whether each URL is reachable, the URL Validation job automatically *skips* any page already confirmed reachable within the last 30 days.  As a result the two individual scan counts do **not** simply add up — each scan covers a different subset of pages.

**What URL Validation adds beyond Social Media:**

- **Failure tracking** — records how many consecutive times each URL has failed; URLs that fail twice are removed from future scans to keep the seed file accurate.
- **Redirect-chain capture** — follows and stores the full redirect chain so the seed file can be updated with the final canonical URL.
- **Lightweight fallback** — a fast HTTP-only check for URLs that the Social Media scanner has not yet reached, without the overhead of downloading and parsing the full page.

The **Combined Reachability** row at the top of the coverage table counts each URL once if it was confirmed reachable by *either* scan, giving the most accurate picture of overall URL health.
