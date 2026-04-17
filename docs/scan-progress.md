---
title: Scan Progress Report
layout: page
---

_Generated: 2026-04-17 05:57 UTC_

This report tracks how far along each scan type is across all countries. It is regenerated automatically after every scan run.

## Overall Coverage

Coverage is measured as pages scanned out of **82,714** pages available in the seed files.

| Scan Type | Pages Scanned | Available | Coverage |
|-----------|--------------|-----------|----------|
| **Combined Reachability** | **2,814 confirmed reachable** | 82,714 | **<span role="img" aria-label="3.4% complete" style="display:inline-flex;align-items:center;gap:4px;vertical-align:middle;"><span style="display:inline-block;width:120px;height:12px;background:#e2e8f0;border-radius:2px;overflow:hidden;"><span style="display:block;width:4px;height:100%;background:#b91c1c;"></span></span><span style="font-size:0.85em;color:#374151;">3.4%</span></span>** |
| URL Validation | 0 validated (0 valid) | 82,714 | <span role="img" aria-label="0.0% complete" style="display:inline-flex;align-items:center;gap:4px;vertical-align:middle;"><span style="display:inline-block;width:120px;height:12px;background:#e2e8f0;border-radius:2px;overflow:hidden;"><span style="display:block;width:0px;height:100%;background:#b91c1c;"></span></span><span style="font-size:0.85em;color:#374151;">0.0%</span></span> |
| Social Media | 2,978 scanned (2,814 reachable) | 82,714 | <span role="img" aria-label="3.6% complete" style="display:inline-flex;align-items:center;gap:4px;vertical-align:middle;"><span style="display:inline-block;width:120px;height:12px;background:#e2e8f0;border-radius:2px;overflow:hidden;"><span style="display:block;width:4px;height:100%;background:#b91c1c;"></span></span><span style="font-size:0.85em;color:#374151;">3.6%</span></span> |
| Technology | 0 scanned | 82,714 | (manual scan) |
| Lighthouse | 300 scanned | 82,714 | <span role="img" aria-label="0.4% complete" style="display:inline-flex;align-items:center;gap:4px;vertical-align:middle;"><span style="display:inline-block;width:120px;height:12px;background:#e2e8f0;border-radius:2px;overflow:hidden;"><span style="display:block;width:2px;height:100%;background:#b91c1c;"></span></span><span style="font-size:0.85em;color:#374151;">0.4%</span></span> |
| Accessibility Statements | 0 scanned | 82,714 | <span role="img" aria-label="0.0% complete" style="display:inline-flex;align-items:center;gap:4px;vertical-align:middle;"><span style="display:inline-block;width:120px;height:12px;background:#e2e8f0;border-radius:2px;overflow:hidden;"><span style="display:block;width:0px;height:100%;background:#b91c1c;"></span></span><span style="font-size:0.85em;color:#374151;">0.0%</span></span> |

> **Combined Reachability** counts each URL once if it was confirmed reachable by *either* URL Validation or Social Media scanning.  URL Validation automatically skips pages already confirmed reachable by the Social Media scanner (within the last 30 days), so the two individual counts complement rather than duplicate each other.

## Social Media Scan by Country

| Country | Scanned | Available | Reachable | Twitter-only | Modern | Mixed | No Social | Twitter | X | Bluesky | Mastodon | Scan Period |
|---------|---------|-----------|-----------|-------------|--------|-------|-----------|---------|---|---------|----------|-------------|
| Austria | 821 | 821 | 790 | 314 | 2 | 45 | 429 | 35 | 17 | 16 | 42 | Apr 2026 |
| Belgium | 1,309 | 1,309 | 1,223 | 352 | 9 | 90 | 772 | 175 | 44 | 24 | 87 | Apr 2026 |
| Bulgaria | 291 | 291 | 263 | 87 | 1 | 12 | 163 | 15 | 5 | 0 | 13 | Apr 2026 |
| Croatia | 233 | 233 | 231 | 70 | 0 | 14 | 147 | 34 | 0 | 0 | 14 | Apr 2026 |
| Czechia | 324 | 843 | 307 | 77 | 0 | 15 | 215 | 52 | 1 | 0 | 15 | Apr 2026 |

> **Tier columns** (Twitter-only / Modern / Mixed / No Social) classify each page by its overall social media presence. **Platform columns** (Twitter / X / Bluesky / Mastodon) count pages with at least one link to that platform — a page may appear in more than one platform column.

> Hover or focus any non-zero platform count to preview matching pages. Activate the number to keep the preview open and download a CSV for that country and platform from [social-media-data.json](social-media-data.json).

## Technology Scan

_No technology scans have been run yet. Trigger the **Scan Technology Stack** workflow manually._

## Lighthouse Scan by Country

| Country | URLs | Perf | A11y | Best Practices | SEO | Last Scan |
|---------|------|------|------|----------------|-----|----------|
| Austria | 300 | 68 | 89 | 93 | 85 | 2026-04-17 |

> Scores are averages across all successfully audited URLs, displayed as 0–100 (multiply source values × 100).

## Accessibility Statement Scan

_No accessibility statement scans have been run yet. Trigger the **Scan Accessibility Statements** workflow manually or wait for the next scheduled run._

## Countries With Social Scan But No URL Validation

These countries have social media scan data but no URL validation data (URL validation may have been skipped because the social scan already confirmed reachability):

`AUSTRIA`, `BELGIUM`, `BULGARIA`, `CROATIA`, `CZECHIA`

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
