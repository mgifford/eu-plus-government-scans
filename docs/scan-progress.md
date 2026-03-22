# Scan Progress Report

_Generated: 2026-03-22 14:12 UTC_

This report tracks how far along each scan type is across all countries. It is regenerated automatically after every scan run.

## Overall Coverage

| Scan Type | URLs Scanned | Coverage |
|-----------|-------------|----------|
| URL Validation | 2,421 URLs (14,979 valid) | ███████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████ 618.7% |
| Social Media | 2,963 URLs scanned (5,369 reachable) | ████████████████████████████████████ 181.2% |
| Technology | 0 URLs scanned | (manual scan) |
| Lighthouse | 0 URLs scanned | (manual scan) |

## URL Validation by Country

| Country | Total | Valid | Invalid | Scan Period | Coverage |
|---------|-------|-------|---------|-------------|----------|
| AUSTRIA | 821 | 6,452 | 216 | Mar 2026 | █████████████████████████████████████████████████████████████████████████████████████████████████████████████████████ 785.9% |
| BELGIUM | 1,309 | 8,296 | 535 | Mar 2026 | ███████████████████████████████████████████████████████████████████████████████████████████████ 633.8% |
| BULGARIA | 291 | 231 | 60 | Mar 2026 | ███████████░░░░ 79.4% |

## Social Media Scan by Country

| Country | Scanned | Reachable | Twitter-only | Modern | Mixed | No Social | Scan Period |
|---------|---------|-----------|-------------|--------|-------|-----------|-------------|
| AUSTRIA | 821 | 1,574 | 60 | 50 | 44 | 1,420 | Mar 2026 |
| BELGIUM | 1,309 | 2,451 | 405 | 113 | 94 | 1,839 | Mar 2026 |
| BULGARIA | 291 | 536 | 42 | 22 | 4 | 468 | Mar 2026 |
| CROATIA | 233 | 462 | 62 | 22 | 6 | 372 | Mar 2026 |
| CZECHIA | 309 | 346 | 59 | 9 | 4 | 274 | Mar 2026 |

## Social Media Platform Breakdown

Number of **reachable** pages per country that link to each platform. A page may link to more than one platform.

| Country | Reachable | Twitter | X | Bluesky | Mastodon | Legacy % | Modern % |
|---------|-----------|---------|---|---------|----------|----------|----------|
| AUSTRIA | 1,574 | 70 | 36 | 32 | 84 | 6.6% | 6.0% |
| BELGIUM | 2,451 | 359 | 148 | 54 | 177 | 20.4% | 8.4% |
| BULGARIA | 536 | 36 | 10 | 0 | 26 | 8.6% | 4.9% |
| CROATIA | 462 | 68 | 0 | 0 | 28 | 14.7% | 6.1% |
| CZECHIA | 346 | 63 | 0 | 0 | 13 | 18.2% | 3.8% |
| **Total** | **5,369** | **596** | **194** | **86** | **328** | **14.5%** | **6.9%** |

> **Legacy platforms** (Twitter / X) vs **modern open platforms** (Bluesky / Mastodon) — percentages are share of reachable pages that contain at least one link to any platform in that group.

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
