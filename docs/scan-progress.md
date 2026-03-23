# Scan Progress Report

_Generated: 2026-03-23 08:18 UTC_

This report tracks how far along each scan type is across all countries. It is regenerated automatically after every scan run.

## Overall Coverage

| Scan Type | Pages Scanned | Available | Coverage |
|-----------|--------------|-----------|----------|
| URL Validation | 2,421 scanned (1,941 valid) | 36,755 | █░░░░░░░░░░░░░░░░░░░ 6.6% |
| Social Media | 2,978 scanned (787 reachable) | 36,755 | ██░░░░░░░░░░░░░░░░░░ 8.1% |
| Technology | 0 URLs scanned | — | (manual scan) |
| Lighthouse | 0 URLs scanned | — | (manual scan) |

## URL Validation by Country

| Country | Total | Valid | Invalid | Scan Period | Coverage |
|---------|-------|-------|---------|-------------|----------|
| AUSTRIA | 821 | 714 | 107 | Mar 2026 | ████████████████░░░░ 87.0% |
| BELGIUM | 1,309 | 1,238 | 71 | Mar 2026 | ████████████████████ 94.6% |
| BULGARIA | 291 | 231 | 60 | Mar 2026 | ███████████░░░░ 79.4% |

## Social Media Scan by Country

| Country | Scanned | Reachable | Twitter-only | Modern | Mixed | No Social | Scan Period |
|---------|---------|-----------|-------------|--------|-------|-----------|-------------|
| AUSTRIA | 821 | 787 | 90 | 75 | 66 | 589 | Mar 2026 |
| BELGIUM | 1,309 | 1,246 | 170 | 57 | 47 | 972 | Mar 2026 |
| BULGARIA | 291 | 278 | 21 | 11 | 2 | 244 | Mar 2026 |
| CROATIA | 233 | 222 | 31 | 11 | 3 | 177 | Mar 2026 |
| CZECHIA | 324 | 309 | 36 | 7 | 3 | 263 | Mar 2026 |

## Social Media Platform Breakdown

Number of **scanned** pages per country that link to each platform. A page may link to more than one platform.  Percentages show the share of all scanned pages.

| Country | Scanned | Reachable | Twitter | X | Bluesky | Mastodon | Legacy % | Modern % |
|---------|---------|-----------|---------|---|---------|----------|----------|----------|
| AUSTRIA | 821 | 787 | 105 | 54 | 48 | 126 | 19.4% | 21.2% |
| BELGIUM | 1,309 | 1,246 | 541 | 222 | 81 | 267 | 58.3% | 26.7% |
| BULGARIA | 291 | 278 | 54 | 15 | 0 | 39 | 23.7% | 13.4% |
| CROATIA | 233 | 222 | 102 | 0 | 0 | 42 | 43.8% | 18.0% |
| CZECHIA | 324 | 309 | 115 | 1 | 0 | 28 | 35.8% | 8.6% |
| **Total** | **2,978** | **2,842** | **917** | **292** | **129** | **502** | **40.7%** | **21.2%** |

> **Legacy platforms** (Twitter / X) vs **modern open platforms** (Bluesky / Mastodon) — percentages are share of all scanned pages that contain at least one link to any platform in that group.

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
