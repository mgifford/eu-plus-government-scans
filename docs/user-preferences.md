---
title: Browser User Preferences & Design Systems
layout: page
---

# Browser user preferences and design-system adoption

EN 301 549 v4.1.1 introduced clause **9.7 — user preferences for web pages**:
a page must not block or explicitly override the modes in which the browser
presents it according to the user's own settings (colour filters, contrast,
text size, pointer size, text cursor, reduced motion), unless that is
essential to the content. The page below tracks two related questions across
the government sites in this corpus:

1. **How many pages show evidence of respecting browser-set preferences** —
   CSS media features like `prefers-color-scheme`, `prefers-reduced-motion`,
   `prefers-contrast`, `forced-colors`, and the `color-scheme` property, plus
   script-side theme switchers (`matchMedia`, `data-theme`).
2. **Which design systems those sites use** — a curated registry of
   government design systems, brand identities, and their adoption
   signatures, because a design system that handles preference support
   correctly propagates it to every site that adopts it.

<!-- USER_PREFERENCES_STATS_START -->

_No scan data yet — stats update automatically after every scan run._

<!-- USER_PREFERENCES_STATS_END -->

## What this scan measures (and what it does not)

**These are signals of effort, not conformance verdicts.**

- Clause 9.7 is a *do not override* rule. A page with no media queries can
  still comply, and a page whose stylesheet mentions `prefers-color-scheme`
  can still break in forced-colours mode. Only manual testing with the real
  settings (contrast themes, reduce motion, dark mode, 200% zoom) can clear
  a site.
- Detection runs in two tiers: the page HTML (inline styles,
  `<meta name="color-scheme">`, inline scripts), and the page's linked
  stylesheets (capped per page, cached across the run). Pages whose
  stylesheets could not be fetched are reported separately — a "signal %"
  computed over a corpus where the CSS tier never ran would understate
  support, so the CSS-tier coverage is published alongside the counts.
- `forced-color-adjust: none` is recorded as an **override risk** because
  clause 9.7's NOTE 4 names that property as the way a page overrides user
  settings. It can be legitimate (a colour swatch where the colour *is* the
  information); it flags a page for manual review, it does not fail it.
- Design-system adoption is matched from curated signatures
  (`data/design-systems.yaml`). Entries with no confirmed signature cannot be
  measured for adoption — that gap is published as registry coverage rather
  than reported as zero adoption.

## Machine-readable data

- **`user-preferences-data.json`** — `summary`, `by_country`,
  `design_system_registry`, and a `by_url` array with one row per scanned
  URL (features, per-origin `feature_sources`, override signals, matched
  design systems). Every aggregate above is recomputable by grouping these
  rows.
- **`user-preferences-data.csv`** — the same rows as a flat file with one
  boolean column per signal, UTF-8 BOM for spreadsheets.

Both files are uploaded as GitHub Actions workflow artifacts by the
[generate-scan-progress workflow](https://github.com/mgifford/eu-plus-government-scans/actions/workflows/generate-scan-progress.yml),
not committed to the repository.

## Related pages

- [Accessibility Statements](accessibility-statements.md) — which pages publish an accessibility statement
- [Lighthouse Results](lighthouse-results.md) — automated accessibility scores
- [Dependency Matrix](dependency-matrix.md) — third-party dependencies by country
