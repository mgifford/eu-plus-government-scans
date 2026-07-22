---
title: EU Government Website Scans
layout: home
---

This project discovers and catalogues how European (and allied) government websites
use social media, whether their URLs are accessible, and what technology platforms
power them, including which third-party JavaScript services they rely on.

## Current Scan Progress

<!-- SCAN_PROGRESS_START -->

_Progress as of 2026-07-22 10:56 UTC_

| Scan Type | Pages Scanned | Coverage | Avg Age |
|-----------|--------------|----------|---------|
| **Combined Reachability** | **35,630 confirmed reachable** | **<span role="img" aria-label="40.6% complete" class="sm-bar"><span class="sm-bar__track" style="width:120px;"><span class="sm-bar__fill sm-bar__fill--amber" style="width:49px;"></span></span><span class="sm-bar__label">40.6%</span></span>** | — |
| Social Media | 38,917 scanned (35,619 reachable) | <span role="img" aria-label="44.4% complete" class="sm-bar"><span class="sm-bar__track" style="width:120px;"><span class="sm-bar__fill sm-bar__fill--amber" style="width:53px;"></span></span><span class="sm-bar__label">44.4%</span></span> | 1.2 days |
| Technology | 3,268 scanned | <span role="img" aria-label="3.7% complete" class="sm-bar"><span class="sm-bar__track" style="width:120px;"><span class="sm-bar__fill sm-bar__fill--red" style="width:4px;"></span></span><span class="sm-bar__label">3.7%</span></span> | 1.0 days |
| Accessibility Statements | 10,663 scanned | <span role="img" aria-label="12.2% complete" class="sm-bar"><span class="sm-bar__track" style="width:120px;"><span class="sm-bar__fill sm-bar__fill--red" style="width:15px;"></span></span><span class="sm-bar__label">12.2%</span></span> | 1.1 days |

**32 countries** with scan data · **35,630** of **87,696** available pages confirmed reachable. See the [Scan Progress Report](scan-progress.md) for full details.

<!-- SCAN_PROGRESS_END -->

## Latest Scan Results

- **[Scan Progress Report](scan-progress.md)** — The best place to start for overall coverage, scan status, and country-level comparisons across the project.
- **[Social Media](social-media.md)** — Government use of legacy and open social platforms, with evidence behind the published counts.
- **[Accessibility Statements](accessibility-statements.md)** — Country-by-country evidence showing which pages do and do not publish accessibility statements.
- **[Technology Scanning](technology-scanning.md)** — Detected CMSs, frameworks, analytics tools, and other software found on government sites.
- **[Third-Party JavaScript](third-party-tools.md)** — External scripts, services, and hosted dependencies loaded by government pages.
- **[Lighthouse Scanning](lighthouse-scanning.md)** — Google Lighthouse methodology, workflow details, and page-level quality scores as they are collected.
- **[Government Domains](domains.md)** — The tracked source dataset: government domains and page URLs used as the input for scans, grouped by country.
- **[Scan Cycle Pace](pace-report.md)** — Whether each scanner is on pace to finish its target cycle (30 or 60 days), based on recent scan velocity.

## What We Track

### Social Media Presence

We check government pages for links to legacy and open social platforms, then classify what was found at page and country level.

See **[Social Media](social-media.md)** for platform coverage, tier definitions, and downloadable evidence.

### URL Validation

We validate tracked URLs, follow redirects, and monitor persistent failures so the source dataset stays current.

See **[Scan Progress Report](scan-progress.md)** for current validation coverage and country-level results.

### Technology Detection

We detect the CMS, framework, analytics, hosting, and other technologies used by government sites.

See **[Technology Scanning](technology-scanning.md)** for the detected technologies and country tables.

### Third-Party JavaScript

We track externally hosted scripts and services such as analytics tags, consent tools, CDNs, shared JavaScript libraries, and support widgets.

See **[Third-Party JavaScript](third-party-tools.md)** for the EU-wide breakdown and evidence exports.

### Lighthouse Audits

We run Google Lighthouse on each government page and record five quality scores:
performance, accessibility, best practices, SEO, and PWA compliance (0–100 scale).

See **[Lighthouse Scanning](lighthouse-scanning.md)** for full details.

## Countries Covered

The dataset covers **all EU member states** plus selected allied nations:
United Kingdom, Switzerland, Iceland, Norway, and Canada.

See **[Government Domains](domains.md)** for the full domain and page-url source list per country.

## How the Scans Work

Scans run automatically on a schedule via **GitHub Actions**:

| Scan | Schedule | Priority |
|------|----------|----------|
| Social Media | Every 3 hours | **Highest** — confirms reachability *and* collects social-link data in one pass |
| Technology Detection | On demand | Medium — run manually for new countries |
| URL Validation | Every 12 hours | Lowest — lightweight redirect/404 check; skipped for pages already confirmed reachable within 30 days |
| Lighthouse Audits | Weekly (Sundays 04:00 UTC) | Medium — slow per-URL (~5 s); weekly cadence keeps data fresh without overloading servers |
| Scan Progress Report | After every scan | — |

After each scan run, this site is automatically updated with the latest results.

## Accessing Scan Artifacts

Each GitHub Actions scan run uploads its results as a downloadable artifact:

1. Go to [GitHub Actions](https://github.com/mgifford/eu-plus-government-scans/actions)
2. Click the relevant workflow
3. Open a completed run and scroll to the **Artifacts** section
4. Download the artifact to inspect the database, annotated TOON files, and scan logs

> The [Scan Progress Report](scan-progress.md) is regenerated automatically, so most visitors should not need the raw artifacts unless they want to inspect the source outputs directly.

## Source Code & Data

- [GitHub Repository](https://github.com/mgifford/eu-plus-government-scans)
- [GitHub Actions Workflows](https://github.com/mgifford/eu-plus-government-scans/actions)
- [Data API](api.md)
- [Accessibility Statement](https://github.com/mgifford/eu-plus-government-scans/blob/main/ACCESSIBILITY.md)

---

*Scan data is collected by automated workflows and stored as GitHub Actions artifacts.
The progress report is regenerated after every scan and committed directly to this site.*
