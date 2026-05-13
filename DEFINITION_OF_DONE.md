# Definition of Done for Report Pages

This file is intentionally **not** a blank template. It captures what can already
be filled in from the current repository state and defines what must be true
before a report page in this project should be considered done.

## Scope

This definition of done applies to generated report pages and their backing data,
including the current report set in `docs/`:

- `scan-progress.md`
- `social-media.md`
- `technology-scanning.md`
- `third-party-tools.md`
- `accessibility-statements.md`
- `lighthouse-results.md`
- any future generated report page published to the project site

## Repository-specific facts already confirmed

The following are already true in this repository today:

- Report generation is automated through GitHub Actions, especially
  `.github/workflows/generate-scan-progress.yml`.
- The repository already publishes report pages to GitHub Pages via the `docs/`
  directory.
- The homepage at `docs/index.md` already links to the current report family.
- The project requires documentation and generated outputs to meet **WCAG 2.2 AA**
  expectations.
- The project requires machine-readable backing data for aggregate report claims.
- The Lighthouse report already has explicit JSON and CSV evidence exports linked
  from the page.

## Definition of done

A report is done when **all** of the items below are true.

### 1. The report is generated, not hand-maintained

- [x] This repository already uses generator CLIs and workflows for current reports.
- [ ] The specific report being delivered has a clear generating command or workflow step.
- [ ] The workflow updates the report consistently without requiring manual content edits.

**Repository evidence:** `generate-scan-progress.yml` runs:

- `src.cli.generate_scan_progress`
- `src.cli.generate_social_media_report`
- `src.cli.generate_domains_report`
- `src.cli.generate_technology_report`
- `src.cli.generate_third_party_js_report`
- `src.cli.generate_accessibility_report`
- `src.cli.generate_lighthouse_report`

### 2. The report says what it is and when it was generated

- [x] Existing reports already use page titles and generated timestamps.
- [ ] The specific report includes a clear title.
- [ ] The specific report includes a generation timestamp and, where relevant, the scan date or scan period.
- [ ] The report explains what the numbers mean in plain language.

**Repository evidence:** `docs/scan-progress.md` and `docs/lighthouse-results.md`
both show generated or stats timestamps, and both include explanatory text.

### 3. The numbers are independently verifiable

- [x] AGENTS.md already requires machine-readable backing data for aggregate claims.
- [ ] Every aggregate number in the report can be recomputed from machine-readable rows.
- [ ] The report has at least one published machine-readable backing file.
- [ ] If the report publishes aggregates, it should publish both JSON and CSV unless there is a documented reason not to.
- [ ] The JSON should include a `by_url` array when the report is based on per-URL evidence.

**Repository evidence:** `AGENTS.md` requires JSON plus UTF-8 BOM CSV backing data
for aggregate reports. `docs/lighthouse-results.md` links to both
`lighthouse-data.json` and `lighthouse-data.csv`.

### 4. The report page links to its evidence

- [x] The Lighthouse report already links directly to downloadable evidence files.
- [ ] The report page links directly to its JSON backing data.
- [ ] The report page links directly to its CSV backing data when a CSV exists.
- [ ] Readers can reach the evidence from the report page without needing to inspect workflow artifacts first.

**Current status:** fully confirmed for Lighthouse; other report types should be
checked per page before claiming parity.

### 5. The report is accessible

- [x] The repository has a WCAG 2.2 AA accessibility commitment.
- [x] Existing reports already use semantic tables and descriptive headings.
- [x] Existing progress-bar cells already include `role="img"` and `aria-label`.
- [ ] Any interactive disclosure, tooltip, or drilldown added by the report is keyboard accessible.
- [ ] Any generated HTML is escaped before rendering.
- [ ] Links are descriptive and understandable out of context.

**Repository evidence:** `ACCESSIBILITY.md` sets the accessibility requirement.
`docs/scan-progress.md` shows accessible progress bars. `ACCESSIBILITY.md` also
documents the tooltip/details accessibility rules already used by the social
media report.

### 6. The report is integrated into the published site

- [x] The homepage already links to the current report set.
- [ ] If the report is user-facing, it is linked from `docs/index.md`.
- [ ] Related documentation pages point readers to the report where appropriate.
- [ ] The report fits the current docs structure and naming style.

**Repository evidence:** `docs/index.md` links to Scan Progress, Social Media,
Accessibility Statements, Technology Scanning, Third-Party JavaScript, and
Lighthouse Scanning.

### 7. The workflow preserves and publishes outputs correctly

- [x] The report-generation workflow already uploads report artifacts.
- [x] The report-generation workflow already uploads JSON and CSV outputs where configured.
- [ ] The specific report's workflow includes the report and its backing data in uploaded artifacts.
- [ ] If the report depends on metadata artifacts, the workflow handles missing data safely.

**Repository evidence:** `generate-scan-progress.yml` uploads the generated
Markdown pages and backing JSON/CSV files as artifacts. It also downloads the
latest metadata artifacts before regeneration.

### 8. The report reflects real repository conventions

- [x] Existing reports use marker blocks, generated timestamps, and explanatory prose.
- [ ] The report follows the existing generated-report style instead of introducing a new layout without a reason.
- [ ] Any new aggregate-report pattern follows the independent-verification rules in `AGENTS.md`.
- [ ] Any documentation change caused by the report is reflected in the relevant docs.

### 9. Validation has been attempted

- [ ] The existing validation command for the affected area has been run.
- [ ] Any failures unrelated to the report are noted separately.
- [ ] If the change is documentation-only, validation is still attempted where practical and any environment limitation is recorded.

**Current session note:** a baseline attempt to run
`python3 -m pytest tests/ -v` failed in this environment because `pytest` is not
installed.

## What can already be marked done for the current repository

Based on the current repository state, these statements can already be treated as
done for the existing report system:

- [x] Reports are generated through versioned CLI entry points and GitHub Actions.
- [x] The project has a documented accessibility standard for report outputs.
- [x] The project has a documented independent-verification requirement.
- [x] The published site already exposes a stable family of report pages.
- [x] The report-generation workflow already uploads generated reports and backing files as artifacts.
- [x] The Lighthouse report already demonstrates the strongest end-to-end pattern:
  generated page, timestamped stats block, linked JSON/CSV evidence, and workflow automation.

## Items that still need per-report confirmation before sign-off

These cannot be marked universally done from a repository read-through alone and
should be checked for any specific report deliverable:

- [ ] The exact report page contains all expected evidence links.
- [ ] The specific backing JSON contains the fields needed to reproduce the published aggregates.
- [ ] A CSV export exists when the report is claiming spreadsheet-friendly verification support.
- [ ] The latest workflow run for that report completed successfully.
- [ ] Any newly added interaction has been checked for keyboard and screen-reader accessibility.

## Practical sign-off rule

For this project, a report should not be called done unless a reviewer can answer
**yes** to all of the following:

1. Is the page generated by the documented workflow or CLI?
2. Can a reader understand what the report measures and when it was generated?
3. Can the published numbers be verified from machine-readable evidence?
4. Can keyboard and assistive-technology users use the page?
5. Is the report linked into the published documentation site?
6. Did the workflow produce and preserve the expected outputs?

If any answer is **no**, the report is not done yet.
