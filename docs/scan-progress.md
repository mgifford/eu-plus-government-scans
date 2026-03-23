# Scan Progress Report

_Generated: 2026-03-23 05:45 UTC_

This report tracks how far along each scan type is across all countries. It is regenerated automatically after every scan run.

## Overall Coverage

| Scan Type | URLs Scanned | Coverage |
|-----------|-------------|----------|
| URL Validation | 2,422 URLs (28,383 valid) | ██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████ 1171.9% |
| Social Media | 2,978 URLs scanned (13,382 reachable) | █████████████████████████████████████████████████████████████████████████████████████████ 449.4% |
| Technology | 0 URLs scanned | (manual scan) |
| Lighthouse | 0 URLs scanned | (manual scan) |

## URL Validation by Country

| Country | Total | Valid | Invalid | Scan Period | Coverage |
|---------|-------|-------|---------|-------------|----------|
| AUSTRIA | 821 | 12,127 | 231 | Mar 2026 | █████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████ 1477.1% |
| BELGIUM | 1,309 | 16,025 | 651 | Mar 2026 | ███████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████ 1224.2% |
| BULGARIA | 291 | 231 | 82 | Mar 2026 | ███████████░░░░ 79.4% |
| CROATIA | 1 | 0 | 1 | Mar 2026 | ░░░░░░░░░░░░░░░ 0.0% |

## Social Media Scan by Country

| Country | Scanned | Reachable | Twitter-only | Modern | Mixed | No Social | Scan Period |
|---------|---------|-----------|-------------|--------|-------|-----------|-------------|
| AUSTRIA | 821 | 3,932 | 150 | 125 | 110 | 3,547 | Mar 2026 |
| BELGIUM | 1,309 | 6,124 | 1,018 | 286 | 226 | 4,594 | Mar 2026 |
| BULGARIA | 291 | 1,341 | 105 | 55 | 10 | 1,171 | Mar 2026 |
| CROATIA | 233 | 1,156 | 155 | 55 | 15 | 931 | Mar 2026 |
| CZECHIA | 324 | 829 | 147 | 20 | 8 | 654 | Mar 2026 |

## Social Media Platform Breakdown

Number of **reachable** pages per country that link to each platform. A page may link to more than one platform.

| Country | Reachable | Twitter | X | Bluesky | Mastodon | Legacy % | Modern % |
|---------|-----------|---------|---|---------|----------|----------|----------|
| AUSTRIA | 3,932 | 175 | 90 | 80 | 210 | 6.6% | 6.0% |
| BELGIUM | 6,124 | 894 | 370 | 135 | 437 | 20.3% | 8.4% |
| BULGARIA | 1,341 | 90 | 25 | 0 | 65 | 8.6% | 4.8% |
| CROATIA | 1,156 | 170 | 0 | 0 | 70 | 14.7% | 6.1% |
| CZECHIA | 829 | 155 | 1 | 0 | 28 | 18.7% | 3.4% |
| **Total** | **13,382** | **1,484** | **486** | **215** | **810** | **14.5%** | **6.8%** |

> **Legacy platforms** (Twitter / X) vs **modern open platforms** (Bluesky / Mastodon) — percentages are share of reachable pages that contain at least one link to any platform in that group.

## Technology Scan

_No technology scans have been run yet. Trigger the **Scan Technology Stack** workflow manually._

## Lighthouse Scan

_No Lighthouse scans have been run yet. Trigger the **Scan Lighthouse** workflow manually._

## Countries With Social Scan But No URL Validation

These countries have social media scan data but no URL validation data (URL validation may have been skipped because the social scan already confirmed reachability):

`CZECHIA`

## Scan Priority Guide

Scans are ordered from **highest** to **lowest** priority:

1. **Social Media Scan** — runs every 3 hours; downloads and parses full pages, confirming reachability *and* detecting social links in one pass.
2. **Technology Scan** — run on demand; detects CMS, framework, and analytics platforms.
3. **Lighthouse Scan** — run on demand; measures performance, accessibility (WCAG), best practices, and SEO for each URL.
4. **URL Validation** — runs every 6 hours in the background; a lightweight redirect/404 check that is **automatically skipped** for URLs already confirmed reachable by a higher-priority scan within the last 30 days.

> **Tip:** Run a social media scan first for a new country — this simultaneously validates all URLs *and* collects social media data, avoiding a separate URL-only pass.
