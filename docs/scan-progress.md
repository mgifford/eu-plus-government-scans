---
title: Scan Progress Report
layout: page
---

_Generated: 2026-07-17 13:33 UTC_

This report tracks how far along each scan type is across all countries. It is regenerated automatically after every scan run.

## Overall Coverage

Coverage is measured as pages scanned out of **82,714** pages available in the seed files.

| Scan Type | Pages Scanned | Available | Coverage | Avg Age |
|-----------|--------------|-----------|----------|---------|
| Social Media | 0 scanned (0 reachable) | 82,714 | <span role="img" aria-label="0.0% complete" style="display:inline-flex;align-items:center;gap:4px;vertical-align:middle;"><span style="display:inline-block;width:120px;height:12px;background:#e2e8f0;border-radius:2px;overflow:hidden;"><span style="display:block;width:0px;height:100%;background:#b91c1c;"></span></span><span style="font-size:0.85em;color:#374151;">0.0%</span></span> | — |
| Technology | 0 scanned | 82,714 | (manual scan) | — |
| Lighthouse | 19,033 scanned | 82,714 | <span role="img" aria-label="23.0% complete" style="display:inline-flex;align-items:center;gap:4px;vertical-align:middle;"><span style="display:inline-block;width:120px;height:12px;background:#e2e8f0;border-radius:2px;overflow:hidden;"><span style="display:block;width:28px;height:100%;background:#b91c1c;"></span></span><span style="font-size:0.85em;color:#374151;">23.0%</span></span> | 41.1 days |
| Accessibility Statements | 0 scanned | 82,714 | <span role="img" aria-label="0.0% complete" style="display:inline-flex;align-items:center;gap:4px;vertical-align:middle;"><span style="display:inline-block;width:120px;height:12px;background:#e2e8f0;border-radius:2px;overflow:hidden;"><span style="display:block;width:0px;height:100%;background:#b91c1c;"></span></span><span style="font-size:0.85em;color:#374151;">0.0%</span></span> | — |

> **Combined Reachability** counts each URL once if it was confirmed reachable by any scan type. **Avg Age** shows the mean number of days (or hours) since each URL in that scan type was last scanned — lower is fresher.

## Technology Scan

_No technology scans have been run yet. Trigger the **Scan Technology Stack** workflow manually._

## Lighthouse Scan by Country

| Country | URLs | Perf | A11y | Best Practices | SEO | Last Scan |
|---------|------|------|------|----------------|-----|----------|
| Austria | 744 | 89 | 90 | 91 | 89 | 2026-07-16 |
| Belgium | 1,237 | 88 | 91 | 91 | 90 | 2026-07-16 |
| Bulgaria | 267 | 86 | 80 | 88 | 88 | 2026-07-03 |
| Croatia | 229 | 90 | 72 | 92 | 90 | 2026-07-03 |
| Czechia | 808 | 91 | 87 | 91 | 88 | 2026-07-11 |
| Denmark | 1,395 | 89 | 94 | 96 | 89 | 2026-07-16 |
| Estonia | 360 | 92 | 87 | 86 | 89 | 2026-07-04 |
| Finland | 163 | 88 | 94 | 95 | 88 | 2026-07-04 |
| France | 431 | 90 | 91 | 92 | 91 | 2026-07-16 |
| Germany | 1,795 | 91 | 91 | 96 | 88 | 2026-07-16 |
| Greece | 1,148 | 87 | 86 | 91 | 88 | 2026-07-17 |
| Hungary | 387 | 88 | 76 | 81 | 86 | 2026-07-04 |
| Iceland | 127 | 90 | 91 | 91 | 91 | 2026-07-04 |
| Ireland | 481 | 91 | 91 | 90 | 87 | 2026-07-11 |
| Italy | 880 | 87 | 88 | 94 | 88 | 2026-07-17 |
| Latvia | 767 | 83 | 87 | 89 | 88 | 2026-07-17 |
| Lithuania | 109 | 88 | 81 | 87 | 85 | 2026-07-05 |
| Luxembourg | 560 | 91 | 93 | 93 | 91 | 2026-07-17 |
| Malta | 591 | 88 | 85 | 79 | 81 | 2026-07-15 |
| Netherlands | 888 | 92 | 94 | 93 | 87 | 2026-07-15 |
| Norway | 237 | 91 | 93 | 92 | 90 | 2026-07-02 |
| Poland | 1,468 | 88 | 86 | 89 | 90 | 2026-07-12 |
| Portugal | 1,056 | 83 | 83 | 86 | 89 | 2026-07-13 |
| Cyprus | 23 | 82 | 86 | 82 | 87 | 2026-07-02 |
| Romania | 59 | 87 | 75 | 88 | 81 | 2026-07-08 |
| Slovakia | 415 | 86 | 87 | 90 | 88 | 2026-07-03 |
| Slovenia | 195 | 88 | 79 | 89 | 85 | 2026-07-03 |
| Spain | 346 | 86 | 87 | 88 | 87 | 2026-07-13 |
| Sweden | 760 | 89 | 92 | 92 | 85 | 2026-07-14 |
| Switzerland | 617 | 86 | 89 | 96 | 88 | 2026-07-14 |
| United Kingdom | 490 | 91 | 93 | 91 | 86 | 2026-07-15 |

> Scores are averages across all successfully audited URLs, displayed as 0–100 (multiply source values × 100).

## Accessibility Statement Scan

_No accessibility statement scans have been run yet. Trigger the **Scan Accessibility Statements** workflow manually or wait for the next scheduled run._

## Scan Priority Guide

Scans are ordered from **highest** to **lowest** priority:

1. **Social Media Scan** — runs every 3 hours; downloads and parses full pages, confirming reachability *and* detecting social links in one pass.
2. **Accessibility Statement Scan** — runs every 4 hours; checks whether each page links to an accessibility statement as required by the EU Web Accessibility Directive (Directive 2016/2102).
3. **Technology Scan** — run on demand; detects CMS, framework, and analytics platforms.
4. **Lighthouse Scan** — runs every 6 hours; measures performance, accessibility (WCAG), best practices, and SEO for each URL.
5. **URL Validation** — runs every 6 hours in the background; a lightweight redirect/404 check that is **automatically skipped** for URLs already confirmed reachable by a higher-priority scan within the last 30 days.

> **Tip:** Run a social media scan first for a new country — this simultaneously validates all URLs *and* collects social media data, avoiding a separate URL-only pass.

### Why are Social Media and URL Validation counts different?

The Social Media scanner runs more frequently than URL Validation and therefore covers more URLs over time.  Because the Social Media scanner already confirms whether each URL is reachable, the URL Validation job automatically *skips* any page already confirmed reachable within the last 30 days.  As a result the two individual scan counts do **not** simply add up — each scan covers a different subset of pages.

**What URL Validation adds beyond Social Media:**

- **Failure tracking** — records how many consecutive times each URL has failed; URLs that fail twice are removed from future scans to keep the seed file accurate.
- **Redirect-chain capture** — follows and stores the full redirect chain so the seed file can be updated with the final canonical URL.
- **Lightweight fallback** — a fast HTTP-only check for URLs that the Social Media scanner has not yet reached, without the overhead of downloading and parsing the full page.

The **Combined Reachability** row at the top of the coverage table counts each URL once if it was confirmed reachable by *either* scan, giving the most accurate picture of overall URL health.
