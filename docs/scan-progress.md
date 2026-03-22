# Scan Progress Report

_Generated: 2026-03-22 06:13 UTC_

This report tracks how far along each scan type is across all countries. It is regenerated automatically after every scan run.

## Overall Coverage

| Scan Type | URLs Scanned | Coverage |
|-----------|-------------|----------|
| URL Validation | 2,130 URLs (1,887 valid) | █████████████████░░░ 88.6% |
| Social Media | 2,764 URLs scanned (2,599 reachable) | ██████████████████░░ 94.0% |
| Technology | 0 URLs scanned | (manual scan) |
| Lighthouse | 0 URLs scanned | (manual scan) |

## URL Validation by Country

| Country | Total | Valid | Invalid | Scan Period | Coverage |
|---------|-------|-------|---------|-------------|----------|
| AUSTRIA | 821 | 718 | 208 | Mar 2026 | █████████████░░ 87.5% |
| BELGIUM | 1,309 | 1,169 | 281 | Mar 2026 | █████████████░░ 89.3% |

## Social Media Scan by Country

| Country | Scanned | Reachable | Twitter-only | Modern | Mixed | No Social | Scan Period |
|---------|---------|-----------|-------------|--------|-------|-----------|-------------|
| AUSTRIA | 821 | 787 | 30 | 25 | 22 | 710 | Mar 2026 |
| BELGIUM | 1,309 | 1,227 | 203 | 57 | 47 | 920 | Mar 2026 |
| BULGARIA | 291 | 268 | 21 | 11 | 2 | 234 | Mar 2026 |
| CROATIA | 233 | 232 | 31 | 11 | 3 | 187 | Mar 2026 |
| CZECHIA | 110 | 85 | 17 | 0 | 0 | 68 | Mar 2026 |

## Social Media Platform Breakdown

Number of **reachable** pages per country that link to each platform. A page may link to more than one platform.

| Country | Reachable | Twitter | X | Bluesky | Mastodon | Legacy % | Modern % |
|---------|-----------|---------|---|---------|----------|----------|----------|
| AUSTRIA | 787 | 35 | 18 | 16 | 42 | 6.6% | 6.0% |
| BELGIUM | 1,227 | 180 | 74 | 27 | 89 | 20.4% | 8.5% |
| BULGARIA | 268 | 18 | 5 | 0 | 13 | 8.6% | 4.9% |
| CROATIA | 232 | 34 | 0 | 0 | 14 | 14.7% | 6.0% |
| CZECHIA | 85 | 17 | 0 | 0 | 0 | 20.0% | 0.0% |
| **Total** | **2,599** | **284** | **97** | **43** | **158** | **14.5%** | **6.8%** |

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
