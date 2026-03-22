# Scan Progress Report

_Generated: 2026-03-22 22:57 UTC_

This report tracks how far along each scan type is across all countries. It is regenerated automatically after every scan run.

## Overall Coverage

| Scan Type | URLs Scanned | Coverage |
|-----------|-------------|----------|
| URL Validation | 2,421 URLs (23,143 valid) | ███████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████ 955.9% |
| Social Media | 2,978 URLs scanned (10,754 reachable) | ████████████████████████████████████████████████████████████████████████ 361.1% |
| Technology | 0 URLs scanned | (manual scan) |
| Lighthouse | 0 URLs scanned | (manual scan) |

## URL Validation by Country

| Country | Total | Valid | Invalid | Scan Period | Coverage |
|---------|-------|-------|---------|-------------|----------|
| AUSTRIA | 821 | 10,006 | 225 | Mar 2026 | ██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████ 1218.8% |
| BELGIUM | 1,309 | 12,906 | 638 | Mar 2026 | ███████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████ 985.9% |
| BULGARIA | 291 | 231 | 60 | Mar 2026 | ███████████░░░░ 79.4% |

## Social Media Scan by Country

| Country | Scanned | Reachable | Twitter-only | Modern | Mixed | No Social | Scan Period |
|---------|---------|-----------|-------------|--------|-------|-----------|-------------|
| AUSTRIA | 821 | 3,148 | 120 | 100 | 88 | 2,840 | Mar 2026 |
| BELGIUM | 1,309 | 4,902 | 815 | 228 | 182 | 3,677 | Mar 2026 |
| BULGARIA | 291 | 1,073 | 84 | 44 | 8 | 937 | Mar 2026 |
| CROATIA | 233 | 925 | 124 | 44 | 12 | 745 | Mar 2026 |
| CZECHIA | 324 | 706 | 124 | 20 | 8 | 554 | Mar 2026 |

## Social Media Platform Breakdown

Number of **reachable** pages per country that link to each platform. A page may link to more than one platform.

| Country | Reachable | Twitter | X | Bluesky | Mastodon | Legacy % | Modern % |
|---------|-----------|---------|---|---------|----------|----------|----------|
| AUSTRIA | 3,148 | 140 | 72 | 64 | 168 | 6.6% | 6.0% |
| BELGIUM | 4,902 | 717 | 296 | 108 | 350 | 20.3% | 8.4% |
| BULGARIA | 1,073 | 72 | 20 | 0 | 52 | 8.6% | 4.8% |
| CROATIA | 925 | 136 | 0 | 0 | 56 | 14.7% | 6.1% |
| CZECHIA | 706 | 132 | 1 | 0 | 28 | 18.7% | 4.0% |
| **Total** | **10,754** | **1,197** | **389** | **172** | **654** | **14.6%** | **6.8%** |

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
