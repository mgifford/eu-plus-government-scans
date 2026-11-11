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

_Stats as of 2026-11-11 14:18 UTC — last scan: 2026-11-05_

**Browser user preferences and design-system adoption**

**5,031** of **87,696** available pages scanned (**5.7%** coverage)
**4,622** of **5,031** scanned pages were reachable (**91.9%**)
**3,999** of **4,622** reachable pages had at least one stylesheet checked (CSS tier: **86.5%**)
**2,007** of **4,622** reachable pages show at least one user-preference signal (**43.4%**)
Pages containing an explicit override (`forced-color-adjust: none`): **38** — a *risk signal* for manual review under EN 301 549 clause 9.7, not a confirmed failure
Pages matching the HTML signatures of a curated design system: **11**

> Registry coverage: **4** of **22** curated design-system entries have confirmed adoption signatures (**6** entries still need review). Systems without signatures cannot yet be measured for adoption.

---

## Signals detected

| Signal | Pages | % of reachable |
|--------|------:|---------------:|
| Dark/light colour scheme (`prefers-color-scheme`) | 211 | 4.6% |
| Declared colour scheme (`color-scheme`) | 257 | 5.6% |
| Reduced motion (`prefers-reduced-motion`) | 1,836 | 39.7% |
| Increased contrast (`prefers-contrast`) | 123 | 2.7% |
| Reduced transparency (`prefers-reduced-transparency`) | 2 | 0.0% |
| Forced colours / high contrast (`forced-colors`) | 142 | 3.1% |

Counts are pages where the signal appeared in the page HTML **or** a fetched stylesheet. Attribution (HTML vs first-party CSS vs third-party CSS) is in the JSON ``feature_sources`` field.

---

## Design systems and adoption

| Design system | Country | Type | Signatures | Pages matched |
|---------------|---------|------|-----------:|--------------:|
| [Austria Design System](https://design.austria.info/manual/en/design-system) ⚠ | Austria | design_system | not curated | 0 |
| [Digitale Huisstijl Antwerpen](https://digitalehuisstijl.antwerpen.be/) | Belgium | brand_identity | not curated | 0 |
| [Stijlgids Stad Gent](https://stijlgids.stad.gent/v6/) | Belgium | brand_identity | not curated | 0 |
| [Vlaanderen Design System](https://www.vlaanderen.be/vlaanderen-design-system) | Belgium | design_system | not curated | 0 |
| [Design System České republiky](https://designsystem.gov.cz/zaciname/for-developers.html) | Czechia | design_system | not curated | 0 |
| [Designsystem.dk](https://designsystem.dk/) | Denmark | design_system | not curated | 0 |
| [Helsinki Design System](https://hds.hel.fi/) ⚠ | Finland | design_system | ✓ | 0 |
| [Suomi.fi Design System](https://designsystem.suomi.fi/) | Finland | design_system | not curated | 0 |
| [Système de Design de l'État](https://www.systeme-de-design.gouv.fr/version-courante/fr) | France | design_system | ✓ | 11 |
| [Angie Design System](https://digitalservicebund.github.io/angie/) | Germany | design_system | not curated | 0 |
| [Government Digital Services Design Guide](https://guide.services.gov.gr/) ⚠ | Greece | design_system | not curated | 0 |
| [Government Design System (Hungary)](https://services.gov.hu/design-system) | Hungary | design_system | not curated | 0 |
| [Accessibilité public.lu](https://accessibilite.public.lu/en/index.html) ⚠ | Luxembourg | accessibility_guide | not curated | 0 |
| [NL Design System](https://nldesignsystem.nl/) ⚠ | Netherlands | design_system | ✓ | 0 |
| [DESY Design System](https://desy.aragon.es/) | Spain | design_system | not curated | 0 |
| [Dintel Design System](https://dintel.redsara.es/) | Spain | design_system | not curated | 0 |
| [Sharing Sweden Brand Identity](https://sharingsweden.se/the-sweden-brand/brand-visual-identity) | Sweden | brand_identity | not curated | 0 |
| [GOV.UK Design System](https://design-system.service.gov.uk/) | United Kingdom | design_system | ✓ | 0 |
| [EU Web Guide Design System](https://op.europa.eu/en/web/webguide/design-system) | — | design_system | not curated | 0 |
| [EUAA Design System](https://www.euaa.europa.eu/design_system/index.html) | — | design_system | not curated | 0 |
| [European Commission Component Library](https://ec.europa.eu/component-library/) | — | design_system | not curated | 0 |
| [zeroheight design systems documentation](https://zeroheight.com/1be481dc2/p/218cab-design-systems) ⚠ | — | design_system | not curated | 0 |

**Pages matched** is the number of scanned pages whose HTML contains that system's adoption signatures (class prefixes, asset paths). It measures footprint on the pages in this corpus only — systems are adopted outside these domains too, and an empty signature list means adoption is not yet measurable for that entry.

⚠ = entry flagged for review (confidence below high or an unconfirmed classification). Registry source: [`data/design-systems.yaml`](https://github.com/mgifford/eu-plus-government-scans/blob/main/data/design-systems.yaml).

---

## User-preference signals by country

| Country | Scanned | Available | Reachable | CSS checked | Signal pages | Signal % | Dark scheme | Reduced motion | Forced colours | Override risk | Design-system pages |
|---------|--------:|----------:|----------:|------------:|-------------:|---------:|------------:|---------------:|---------------:|--------------:|--------------------:|
| Austria | 822 | 822 | 748 | 720 | 545 | 72.9% | 23 | 540 | 21 | 0 | 3 |
| Belgium | 1,329 | 1,329 | 1,192 | 1,064 | 413 | 34.6% | 77 | 376 | 41 | 6 | 3 |
| Bulgaria | 353 | 353 | 295 | 223 | 111 | 37.6% | 2 | 111 | 5 | 0 | 0 |
| Canada | 2,527 | 4,469 | 2,387 | 1,992 | 938 | 39.3% | 109 | 809 | 75 | 32 | 5 |
| **Total** | **5,031** | **87,696** | **4,622** | **3,999** | **2,007** | **43.4%** | **211** | **1,836** | **142** | **38** | **11** |

---

## How to read these numbers

Signals are collected from the page HTML (inline styles, `<meta name="color-scheme">`, `matchMedia` scripts) and from fetched stylesheets (capped per page; shared CSS is cached). They are evidence of effort, **not** EN 301 549 clause 9.7 conformance: a page with no media query can still comply, and a page with one can still break in forced-colours mode. Only manual testing can clear a site.

📥 Machine-readable results: [user-preferences-data.json](https://github.com/mgifford/eu-plus-government-scans/actions/workflows/generate-scan-progress.yml) (`by_url` carries one row per scanned URL so every aggregate above can be independently recomputed) and `user-preferences-data.csv` (same rows, one per URL, boolean columns per signal), both published as workflow artifacts.

Context: [EN 301 549 clause 9.7 — user preferences for web pages](https://www.webyes.com/blogs/en-301-549-user-preferences/).

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
