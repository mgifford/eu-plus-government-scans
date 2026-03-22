# Scan Progress Report

_Generated: 2026-03-22 10:59 UTC_

This report tracks how far along each scan type is across all countries. It is regenerated automatically after every scan run.

## Overall Coverage

| Scan Type | URLs Scanned | Coverage |
|-----------|-------------|----------|
| URL Validation | 2,130 URLs (5,648 valid) | █████████████████████████████████████████████████████ 265.2% |
| Social Media | 2,971 URLs scanned (8,150 reachable) | ██████████████████████████████████████████████████████ 274.3% |
| Technology | 0 URLs scanned | (manual scan) |
| Lighthouse | 0 URLs scanned | (manual scan) |

## URL Validation by Country

| Country | Total | Valid | Invalid | Scan Period | Coverage |
|---------|-------|-------|---------|-------------|----------|
| AUSTRIA | 821 | 2,154 | 206 | Mar 2026 | ███████████████████████████████████████ 262.4% |
| BELGIUM | 1,309 | 3,494 | 290 | Mar 2026 | ████████████████████████████████████████ 266.9% |

## Social Media Scan by Country

| Country | Scanned | Reachable | Twitter-only | Modern | Mixed | No Social | Scan Period |
|---------|---------|-----------|-------------|--------|-------|-----------|-------------|
| AUSTRIA | 821 | 2,359 | 90 | 75 | 66 | 2,128 | Mar 2026 |
| BELGIUM | 1,309 | 3,679 | 610 | 171 | 141 | 2,757 | Mar 2026 |
| BULGARIA | 291 | 804 | 63 | 33 | 6 | 702 | Mar 2026 |
| CROATIA | 233 | 693 | 93 | 33 | 9 | 558 | Mar 2026 |
| CZECHIA | 317 | 615 | 105 | 18 | 8 | 484 | Mar 2026 |

## Social Media Platform Breakdown

Number of **reachable** pages per country that link to each platform. A page may link to more than one platform.

| Country | Reachable | Twitter | X | Bluesky | Mastodon | Legacy % | Modern % |
|---------|-----------|---------|---|---------|----------|----------|----------|
| AUSTRIA | 2,359 | 105 | 54 | 48 | 126 | 6.6% | 6.0% |
| BELGIUM | 3,679 | 541 | 222 | 81 | 267 | 20.4% | 8.5% |
| BULGARIA | 804 | 54 | 15 | 0 | 39 | 8.6% | 4.9% |
| CROATIA | 693 | 102 | 0 | 0 | 42 | 14.7% | 6.1% |
| CZECHIA | 615 | 113 | 0 | 0 | 26 | 18.4% | 4.2% |
| **Total** | **8,150** | **915** | **291** | **129** | **500** | **14.6%** | **6.9%** |

> **Legacy platforms** (Twitter / X) vs **modern open platforms** (Bluesky / Mastodon) — percentages are share of reachable pages that contain at least one link to any platform in that group.

## Technology Scan

_No technology scans have been run yet. Trigger the **Scan Technology Stack** workflow manually._

## Lighthouse Scan

_No Lighthouse scans have been run yet. Trigger the **Scan Lighthouse** workflow manually._

## Countries With Social Scan But No URL Validation

These countries have social media scan data but no URL validation data (URL validation may have been skipped because the social scan already confirmed reachability):

`BULGARIA`, `CROATIA`, `CZECHIA`

## Scan Priority Guide

Scans are ordered from **highest** to **lowest** priority:

1. **Social Media Scan** — runs every 3 hours; downloads and parses full pages, confirming reachability *and* detecting social links in one pass.
2. **Technology Scan** — run on demand; detects CMS, framework, and analytics platforms.
3. **Lighthouse Scan** — run on demand; measures performance, accessibility (WCAG), best practices, and SEO for each URL.
4. **URL Validation** — runs every 6 hours in the background; a lightweight redirect/404 check that is **automatically skipped** for URLs already confirmed reachable by a higher-priority scan within the last 30 days.

> **Tip:** Run a social media scan first for a new country — this simultaneously validates all URLs *and* collects social media data, avoiding a separate URL-only pass.
