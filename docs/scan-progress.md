---
title: Scan Progress Report
layout: page
---

_Generated: 2026-08-01 13:22 UTC_

This report tracks how far along each scan type is across all countries. It is regenerated automatically after every scan run.

## Overall Coverage

Coverage is measured as pages scanned out of **87,696** pages available in the seed files.

| Scan Type | Pages Scanned | Available | Coverage | Avg Age |
|-----------|--------------|-----------|----------|---------|
| Social Media | 0 scanned (0 reachable) | 87,696 | <span role="img" aria-label="0.0% complete" class="sm-bar"><span class="sm-bar__track" style="width:120px;"><span class="sm-bar__fill sm-bar__fill--red" style="width:0px;"></span></span><span class="sm-bar__label">0.0%</span></span> | — |
| Technology | 0 scanned | 87,696 | (manual scan) | — |
| Lighthouse | 8,708 scanned | 87,696 | <span role="img" aria-label="9.9% complete" class="sm-bar"><span class="sm-bar__track" style="width:120px;"><span class="sm-bar__fill sm-bar__fill--red" style="width:12px;"></span></span><span class="sm-bar__label">9.9%</span></span> | 7.2 days |
| Accessibility Statements | 0 scanned | 87,696 | <span role="img" aria-label="0.0% complete" class="sm-bar"><span class="sm-bar__track" style="width:120px;"><span class="sm-bar__fill sm-bar__fill--red" style="width:0px;"></span></span><span class="sm-bar__label">0.0%</span></span> | — |

> **Combined Reachability** counts each URL once if it was confirmed reachable by any scan type. **Avg Age** shows the mean number of days (or hours) since each URL in that scan type was last scanned — lower is fresher.

## Technology Scan

_No technology scans have been run yet. Trigger the **Scan Technology Stack** workflow manually._

## Lighthouse Scan by Country

| Country | URLs | Perf | A11y | Best Practices | SEO | Last Scan |
|---------|------|------|------|----------------|-----|----------|
| Austria | 733 | 88 | 90 | 91 | 89 | 2026-08-01 |
| Belgium | 577 | 87 | 91 | 92 | 91 | 2026-08-01 |
| Bulgaria | 316 | 87 | 81 | 88 | 87 | 2026-07-22 |
| Canada | 88 | 94 | 89 | 92 | 85 | 2026-07-28 |
| Croatia | 251 | 92 | 72 | 92 | 89 | 2026-07-20 |
| Czechia | 823 | 91 | 87 | 92 | 88 | 2026-08-01 |
| Denmark | 718 | 88 | 94 | 97 | 90 | 2026-07-30 |
| Estonia | 357 | 91 | 87 | 86 | 89 | 2026-07-23 |
| Finland | 181 | 86 | 94 | 96 | 87 | 2026-07-20 |
| France | 71 | 89 | 90 | 91 | 91 | 2026-07-28 |
| Germany | 69 | 93 | 89 | 96 | 90 | 2026-07-30 |
| Greece | 185 | 84 | 87 | 92 | 88 | 2026-07-30 |
| Hungary | 380 | 89 | 77 | 82 | 86 | 2026-07-23 |
| Iceland | 133 | 93 | 92 | 91 | 91 | 2026-07-21 |
| Ireland | 479 | 92 | 91 | 90 | 87 | 2026-07-30 |
| Italy | 53 | 81 | 87 | 89 | 86 | 2026-07-31 |
| Latvia | 331 | 87 | 85 | 91 | 85 | 2026-07-30 |
| Lithuania | 111 | 86 | 81 | 87 | 85 | 2026-07-21 |
| Luxembourg | 556 | 91 | 93 | 93 | 91 | 2026-07-28 |
| Malta | 566 | 89 | 85 | 78 | 83 | 2026-07-31 |
| Netherlands | 553 | 91 | 94 | 94 | 85 | 2026-07-31 |
| Norway | 247 | 90 | 93 | 92 | 89 | 2026-07-21 |
| Poland | 95 | 86 | 81 | 85 | 89 | 2026-08-01 |
| Portugal | 33 | 88 | 76 | 82 | 88 | 2026-08-01 |
| Cyprus | 27 | 81 | 86 | 84 | 86 | 2026-07-21 |
| Romania | 32 | 83 | 74 | 86 | 80 | 2026-07-26 |
| Slovakia | 291 | 91 | 87 | 91 | 88 | 2026-07-22 |
| Slovenia | 204 | 86 | 80 | 89 | 85 | 2026-07-22 |
| Sweden | 248 | 87 | 91 | 91 | 84 | 2026-07-31 |

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
