# Scan Progress Report

_Generated: 2026-03-22 19:58 UTC_

This report tracks how far along each scan type is across all countries. It is regenerated automatically after every scan run.

## Overall Coverage

| Scan Type | URLs Scanned | Coverage |
|-----------|-------------|----------|
| URL Validation | 2,421 URLs (16,754 valid) | ██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████ 692.0% |
| Social Media | 2,978 URLs scanned (10,950 reachable) | █████████████████████████████████████████████████████████████████████████ 367.7% |
| Technology | 0 URLs scanned | (manual scan) |
| Lighthouse | 0 URLs scanned | (manual scan) |

## URL Validation by Country

| Country | Total | Valid | Invalid | Scan Period | Coverage |
|---------|-------|-------|---------|-------------|----------|
| AUSTRIA | 821 | 7,170 | 216 | Mar 2026 | ██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████ 873.3% |
| BELGIUM | 1,309 | 9,353 | 538 | Mar 2026 | ███████████████████████████████████████████████████████████████████████████████████████████████████████████ 714.5% |
| BULGARIA | 291 | 231 | 60 | Mar 2026 | ███████████░░░░ 79.4% |

## Social Media Scan by Country

| Country | Scanned | Reachable | Twitter-only | Modern | Mixed | No Social | Scan Period |
|---------|---------|-----------|-------------|--------|-------|-----------|-------------|
| AUSTRIA | 821 | 3,148 | 120 | 100 | 88 | 2,840 | Mar 2026 |
| BELGIUM | 1,309 | 4,907 | 815 | 229 | 188 | 3,675 | Mar 2026 |
| BULGARIA | 291 | 1,073 | 84 | 44 | 8 | 937 | Mar 2026 |
| CROATIA | 233 | 924 | 124 | 44 | 12 | 744 | Mar 2026 |
| CZECHIA | 324 | 898 | 155 | 31 | 12 | 700 | Mar 2026 |

## Social Media Platform Breakdown

Number of **reachable** pages per country that link to each platform. A page may link to more than one platform.

| Country | Reachable | Twitter | X | Bluesky | Mastodon | Legacy % | Modern % |
|---------|-----------|---------|---|---------|----------|----------|----------|
| AUSTRIA | 3,148 | 140 | 72 | 64 | 168 | 6.6% | 6.0% |
| BELGIUM | 4,907 | 723 | 296 | 108 | 357 | 20.4% | 8.5% |
| BULGARIA | 1,073 | 72 | 20 | 0 | 52 | 8.6% | 4.8% |
| CROATIA | 924 | 136 | 0 | 0 | 56 | 14.7% | 6.1% |
| CZECHIA | 898 | 167 | 2 | 0 | 43 | 18.6% | 4.8% |
| **Total** | **10,950** | **1,238** | **390** | **172** | **676** | **14.7%** | **6.9%** |

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
