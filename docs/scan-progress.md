---
title: Scan Progress Report
layout: page
---

_Generated: 2026-07-20 05:26 UTC_

This report tracks how far along each scan type is across all countries. It is regenerated automatically after every scan run.

## Overall Coverage

Coverage is measured as pages scanned out of **87,696** pages available in the seed files.

| Scan Type | Pages Scanned | Available | Coverage | Avg Age |
|-----------|--------------|-----------|----------|---------|
| **Combined Reachability** | **4,000 confirmed reachable** | 87,696 | **<span role="img" aria-label="4.6% complete" class="sm-bar"><span class="sm-bar__track" style="width:120px;"><span class="sm-bar__fill sm-bar__fill--red" style="width:5px;"></span></span><span class="sm-bar__label">4.6%</span></span>** | — |
| Social Media | 0 scanned (0 reachable) | 87,696 | <span role="img" aria-label="0.0% complete" class="sm-bar"><span class="sm-bar__track" style="width:120px;"><span class="sm-bar__fill sm-bar__fill--red" style="width:0px;"></span></span><span class="sm-bar__label">0.0%</span></span> | — |
| Technology | 0 scanned | 87,696 | (manual scan) | — |
| Lighthouse | 0 scanned | 87,696 | (manual scan) | — |
| Accessibility Statements | 0 scanned | 87,696 | <span role="img" aria-label="0.0% complete" class="sm-bar"><span class="sm-bar__track" style="width:120px;"><span class="sm-bar__fill sm-bar__fill--red" style="width:0px;"></span></span><span class="sm-bar__label">0.0%</span></span> | — |

> **Combined Reachability** counts each URL once if it was confirmed reachable by any scan type. **Avg Age** shows the mean number of days (or hours) since each URL in that scan type was last scanned — lower is fresher.

## URL Validation by Country

| Country | Total | Valid | Invalid | Scan Period | Coverage |
|---------|-------|-------|---------|-------------|----------|
| Austria | 822 | 711 | 111 | Jul 2026 | <span role="img" aria-label="100.0% complete" class="sm-bar"><span class="sm-bar__track" style="width:90px;"><span class="sm-bar__fill sm-bar__fill--green" style="width:90px;"></span></span><span class="sm-bar__label">100.0%</span></span> |
| Belgium | 1,235 | 1,066 | 169 | Jul 2026 | <span role="img" aria-label="92.9% complete" class="sm-bar"><span class="sm-bar__track" style="width:90px;"><span class="sm-bar__fill sm-bar__fill--green" style="width:84px;"></span></span><span class="sm-bar__label">92.9%</span></span> |
| Croatia | 257 | 248 | 9 | Jul 2026 | <span role="img" aria-label="100.0% complete" class="sm-bar"><span class="sm-bar__track" style="width:90px;"><span class="sm-bar__fill sm-bar__fill--green" style="width:90px;"></span></span><span class="sm-bar__label">100.0%</span></span> |
| Czechia | 866 | 775 | 91 | Jul 2026 | <span role="img" aria-label="100.0% complete" class="sm-bar"><span class="sm-bar__track" style="width:90px;"><span class="sm-bar__fill sm-bar__fill--green" style="width:90px;"></span></span><span class="sm-bar__label">100.0%</span></span> |
| Denmark | 1,384 | 1,200 | 184 | Jul 2026 | <span role="img" aria-label="90.1% complete" class="sm-bar"><span class="sm-bar__track" style="width:90px;"><span class="sm-bar__fill sm-bar__fill--green" style="width:81px;"></span></span><span class="sm-bar__label">90.1%</span></span> |

> Hover or focus any non-zero **Total**, **Valid**, or **Invalid** count to preview matching URLs. **Valid** and **Invalid** can overlap because a URL may have passed in one validation run and failed in another during the same scan period; download the CSV for the underlying evidence from [scan-progress-data.json](scan-progress-data.json).

## Technology Scan

_No technology scans have been run yet. Trigger the **Scan Technology Stack** workflow manually._

## Lighthouse Scan

_No Lighthouse scans have been run yet. Trigger the **Scan Lighthouse** workflow manually._

## Accessibility Statement Scan

_No accessibility statement scans have been run yet. Trigger the **Scan Accessibility Statements** workflow manually or wait for the next scheduled run._

## Countries Pending Social Media Scan

These countries have URL validation data but have not yet been scanned for social media links:

`AUSTRIA`, `BELGIUM`, `CROATIA`, `CZECHIA`, `DENMARK`

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
