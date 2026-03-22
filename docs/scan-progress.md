# Scan Progress Report

_Generated: 2026-03-22 18:04 UTC_

This report tracks how far along each scan type is across all countries. It is regenerated automatically after every scan run.

## Overall Coverage

| Scan Type | URLs Scanned | Coverage |
|-----------|-------------|----------|
| URL Validation | 2,421 URLs (16,754 valid) | ██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████ 692.0% |
| Social Media | 2,978 URLs scanned (8,160 reachable) | ██████████████████████████████████████████████████████ 274.0% |
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
| AUSTRIA | 821 | 2,361 | 90 | 75 | 66 | 2,130 | Mar 2026 |
| BELGIUM | 1,309 | 3,679 | 610 | 171 | 141 | 2,757 | Mar 2026 |
| BULGARIA | 291 | 805 | 63 | 33 | 6 | 703 | Mar 2026 |
| CROATIA | 233 | 693 | 93 | 33 | 9 | 558 | Mar 2026 |
| CZECHIA | 324 | 622 | 107 | 20 | 8 | 487 | Mar 2026 |

## Social Media Platform Breakdown

Number of **reachable** pages per country that link to each platform. A page may link to more than one platform.

| Country | Reachable | Twitter | X | Bluesky | Mastodon | Legacy % | Modern % |
|---------|-----------|---------|---|---------|----------|----------|----------|
| AUSTRIA | 2,361 | 105 | 54 | 48 | 126 | 6.6% | 6.0% |
| BELGIUM | 3,679 | 541 | 222 | 81 | 267 | 20.4% | 8.5% |
| BULGARIA | 805 | 54 | 15 | 0 | 39 | 8.6% | 4.8% |
| CROATIA | 693 | 102 | 0 | 0 | 42 | 14.7% | 6.1% |
| CZECHIA | 622 | 115 | 1 | 0 | 28 | 18.5% | 4.5% |
| **Total** | **8,160** | **917** | **292** | **129** | **502** | **14.6%** | **6.9%** |

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
