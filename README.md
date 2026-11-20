# EU Plus Government Scans

**Open-source research and comparative monitoring of government websites across Europe and selected other countries.**

[![License: AGPL v3](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](LICENSE)
[![Deploy GitHub Pages](https://github.com/mgifford/eu-plus-government-scans/actions/workflows/deploy-pages.yml/badge.svg)](https://github.com/mgifford/eu-plus-government-scans/actions/workflows/deploy-pages.yml)
[![Documentation Links](https://github.com/mgifford/eu-plus-government-scans/actions/workflows/check-links.yml/badge.svg)](https://github.com/mgifford/eu-plus-government-scans/actions/workflows/check-links.yml)

EU Plus Government Scans collects evidence about how governments build, maintain, and operate their public websites.

The project examines accessibility statements, web technologies, third-party services, performance, browser user preferences, social media platforms, and dependencies on external digital infrastructure.

It covers European Union Member States and selected other countries, including the United Kingdom, Switzerland, Norway, Iceland, and Canada.

The goal is to make government digital practices more transparent and comparable, identify opportunities for improvement, and support evidence-based discussion about accessibility, procurement, open source, digital sovereignty, and public-sector technology.

**[Explore the published reports](https://mgifford.github.io/eu-plus-government-scans/)**

Reports are freely available without an account or software installation.

## Why this matters for European governments

European governments share many digital policy objectives, but their websites, implementation practices, and monitoring approaches are not identical.

A government may have a strong accessibility policy while individual websites fail to publish discoverable accessibility statements. Another country may demonstrate widespread use of a common design system, while others maintain numerous independently implemented websites.

Different countries may also make different technology and infrastructure choices despite operating under related European policy frameworks.

Comparative evidence can help governments ask:

- How do our public websites compare with those of other countries?
- Are our accessibility policies reflected in observable website practices?
- Where do government websites appear inconsistent with national guidance?
- Are government design systems being adopted across public services?
- Which technologies and external services are most common?
- How are open-source and proprietary technologies represented?
- What evidence suggests opportunities to improve accessibility, performance, or sustainability?
- How complete and reliable is our government's website inventory?

The project supports comparisons across countries, but a simple overall ranking would conceal important differences in website coverage, testing methods, organizational responsibilities, and national requirements.

Country results should therefore be interpreted alongside their sources, dates, denominators, and methodological limitations.

## The Web Accessibility Directive

The [EU Web Accessibility Directive, Directive (EU) 2016/2102](https://eur-lex.europa.eu/eli/dir/2016/2102/oj), establishes accessibility obligations for websites and mobile applications of public-sector bodies within its scope.

EU Member States are responsible for implementing the Directive through national measures, monitoring the relevant services, and operating enforcement procedures.

The Directive is supported by implementing decisions addressing accessibility statements and monitoring methodology, including:

- [Commission Implementing Decision (EU) 2018/1523](https://eur-lex.europa.eu/eli/dec_impl/2018/1523/oj): The model accessibility statement.
- [Commission Implementing Decision (EU) 2018/1524](https://eur-lex.europa.eu/eli/dec_impl/2018/1524/oj): Monitoring methodology and reporting arrangements.

The monitoring methodology distinguishes simplified and in-depth evaluation. It addresses sampling, relevant accessibility requirements, and the documentation of results.

Member States submit reports on monitoring and enforcement activities to the European Commission every three years.

### National accessibility monitoring authorities

The European Commission maintains a [directory of national bodies responsible for Web Accessibility Directive monitoring, reporting, and enforcement](https://digital-strategy.ec.europa.eu/en/policies/web-accessibility-monitoring).

These responsibilities may be divided among different organizations within a country or across levels of government.

**EU Plus Government Scans is independent of these authorities and does not replace their statutory responsibilities.**

Its monitoring can provide supplementary evidence for public-sector organizations and researchers, particularly concerning accessibility-statement discovery and trends in observable website practices.

It does not constitute a complete assessment under the Directive's monitoring methodology, and its automated findings should not be presented as official determinations of legal compliance.

### Comparing accessibility policy and implementation

The project can help identify possible differences between:

- European accessibility requirements.
- National laws and implementation guidance.
- Accessibility statement formats and publication practices.
- Observable website accessibility signals.
- Government design-system adoption.
- National monitoring and reporting practices.

For example, the presence of a standardized accessibility statement, a clearly identified enforcement mechanism, or a link to national accessibility guidance may provide useful evidence about how policy is communicated.

The absence of a detected statement is a reason to investigate. It is not automatically proof that a public body has violated the law.

An important longer-term research opportunity is to examine these observations alongside the [national Web Accessibility Directive monitoring reports for 2022–2024](https://digital-strategy.ec.europa.eu/en/news/web-accessibility-directive-monitoring-reports-2022-2024).

Such comparisons must clearly distinguish independently collected evidence from official national findings and account for differences in scope and methods.

## Explore the research

The published reports provide several ways to investigate government technology and website practices.

| Report | What you can investigate |
|---|---|
| [Scan Progress](https://mgifford.github.io/eu-plus-government-scans/scan-progress.html) | Website inventory size, scanner coverage, freshness, and country-level differences |
| [Accessibility Statements](https://mgifford.github.io/eu-plus-government-scans/accessibility-statements.html) | Whether government websites publish discoverable accessibility statements |
| [Technology Adoption](https://mgifford.github.io/eu-plus-government-scans/technology-scanning.html) | Detected content management systems, frameworks, analytics tools, and other technologies |
| [Technology Licensing](https://mgifford.github.io/eu-plus-government-scans/technology-license-summary.html) | Open-source licensing and selected public-interest classifications |
| [Third-Party Services](https://mgifford.github.io/eu-plus-government-scans/third-party-tools.html) | External JavaScript services and hosted dependencies |
| [Digital Dependencies](https://mgifford.github.io/eu-plus-government-scans/dependency-matrix.html) | How reliance on external service providers varies between countries |
| [Social Media](https://mgifford.github.io/eu-plus-government-scans/social-media.html) | Government links to commercial, federated, and other social platforms |
| [Lighthouse Results](https://mgifford.github.io/eu-plus-government-scans/lighthouse-results.html) | Automated accessibility, performance, best-practices, and SEO indicators |
| [User Preferences and Design Systems](https://mgifford.github.io/eu-plus-government-scans/user-preferences.html) | Signals associated with reduced motion, colour schemes, contrast preferences, and design-system adoption |
| [Network Explorer](https://mgifford.github.io/eu-plus-government-scans/network.html) | Relationships between government websites and external domains |

Each report should be read with its accompanying methodology, coverage information, and evidence limitations.

## An evolving inventory of government websites

**A critical part of this project is determining which websites genuinely belong in a country's government inventory.**

The initial datasets were assembled from available government-domain lists, public sources, and imported research data.

Considerable effort has gone into finding relevant government websites across countries. However, these inventories have not all been independently verified by the responsible public authorities.

Some government websites may be missing. Others may have been included incorrectly.

A website can look governmental without being operated by a public-sector body. Conversely, legitimate government services may use domains that do not resemble conventional government domain names.

### What can go wrong?

The inventory may contain:

- Government websites that have been missed.
- Websites mistakenly classified as government-operated.
- Former government domains that now redirect or have changed ownership.
- Duplicate domains and aliases.
- Websites operated by public bodies but hosted under unusual domains.
- Commercial services providing government-related information.
- Websites whose status differs by administrative level or legal definition.
- Government services operated through third-party platforms.

These distinctions matter.

An incorrect website inventory can distort country comparisons, technology adoption figures, accessibility-statement coverage, and assessments of external dependencies.

### An example from France

France provides a useful model for improving source quality.

The [Observatoire de l'écosystème numérique de l'État](https://www.data.gouv.fr/datasets/observatoire-de-lecosysteme-numerique-de-letat-sites-internet), published by the Service d'Information du Gouvernement, provides data about central-government websites and their administrative relationships.

Its published inventory offers a more authoritative basis for checking relevant websites than relying only on domain-name patterns.

However, a central-government inventory is not necessarily a complete list of every public-sector website covered by accessibility obligations. Regional and local government bodies may require additional sources.

Equivalent authoritative datasets should be identified wherever possible for other countries.

### Help improve your country's inventory

**Input from people who understand each country's public administration is particularly valuable.**

National monitoring authorities, digital government teams, public-sector employees, researchers, and local contributors can help identify omissions and errors.

Please [open a GitHub issue](https://github.com/mgifford/eu-plus-government-scans/issues) if you can:

- Identify a missing government website.
- Identify a website incorrectly included as governmental.
- Provide an authoritative government website inventory.
- Clarify which public body operates a particular domain.
- Explain a country's national, regional, or local administrative structure.
- Identify authoritative sources for public-sector websites.
- Correct a country classification or outdated URL.
- Identify national accessibility legislation or official monitoring guidance relevant to the scanned sites.

Useful submissions include the domain, country, operating organization, administrative level, authoritative source URL, and a short explanation.

Where the evidence is uncertain, state that explicitly.

Corrections should preserve the provenance of the original record rather than silently changing historical research results.

The long-term goal is to produce more trustworthy, transparent, and reusable inventories with clear source attribution and independently reviewed classifications.

## What does the project measure?

### Accessibility and inclusion

The project investigates accessibility statements, automated accessibility indicators, and selected technologies associated with inclusive design.

It examines:

- Accessibility statement discovery.
- Lighthouse accessibility results.
- Browser user-preference signals.
- Government design-system adoption.
- Accessibility overlay detection.
- Selected historical changes.

Finding an accessibility statement does not establish that the website conforms to WCAG.

Likewise, a Lighthouse accessibility score cannot determine complete accessibility conformance.

Browser preference detection identifies technical signals rather than demonstrating that a website works correctly for everyone.

These findings support investigation and should be complemented by manual testing and user research.

### Technology adoption and open source

The project detects technologies including content management systems, frameworks, JavaScript libraries, analytics platforms, hosting-related technologies, and other identifiable software.

Selected technologies are enriched with license metadata and public-interest classifications, including OSI-approved licensing and Digital Public Goods Registry references.

These observations can help researchers compare technology adoption and identify opportunities for open-source collaboration.

Technology signatures are imperfect. Detection does not establish a project's governance, procurement arrangements, security, or maintenance quality.

### Digital sovereignty and dependencies

The project records relationships between government websites and external services.

Relevant resources include:

- Scripts.
- Stylesheets.
- Fonts.
- Media.
- Other externally hosted assets.

The resulting evidence can identify concentration around common service providers and differences in government reliance on external technologies.

The [country-by-service dependency matrix](https://mgifford.github.io/eu-plus-government-scans/dependency-matrix.html) uses the proportion of scanned government domains loading resources from particular services.

Provider-jurisdiction information comes from a curated registry with stated confidence and coverage limitations.

**A detected external dependency does not establish where data is stored or processed, or which jurisdiction exercises effective control.**

These findings can inform digital sovereignty research but are not definitive sovereignty assessments.

### Performance and sustainability

Google Lighthouse collects automated indicators for:

- Performance.
- Accessibility.
- Best practices.
- Search engine optimization.

Resource and third-party service inventories provide additional context.

These indicators can help identify opportunities to reduce unnecessary transfers, technical complexity, and resource use.

They do not directly measure energy consumption or establish a website's total carbon footprint.

### Social media and public communication

The project examines government website links to commercial and open social platforms, including Mastodon and services based on the AT Protocol.

Historical observations can identify newly detected or missing links.

These signals do not automatically establish that an account is official or currently maintained.

The project can also generate [weekly Mastodon digest drafts](docs/weekly-digest.md) for human review. Publication is not automatic.

### User preferences and design systems

The project examines evidence of support for browser and operating-system preferences, including:

- Light and dark colour schemes.
- Reduced motion.
- Increased contrast.
- Forced-colours modes.
- Other selected CSS preference features.

It also maintains a curated registry of government design-system signatures.

These findings can help identify where common design systems may support more consistent implementation of accessibility expectations.

A detected CSS feature does not establish that a site fully respects the corresponding preference.

## Relationships to other European digital government assessments

EU Plus Government Scans can complement established European and national digital government research.

For example, the European Commission's [eGovernment Benchmark 2026](https://digital-strategy.ec.europa.eu/en/library/digital-decade-2026-egovernment-benchmark-2026) evaluates selected digital public services across nine life events using a user-centred assessment methodology.

This differs from EU Plus Government Scans, which examines a broader seeded collection of websites and observable technical characteristics.

France's government digital observatory also illustrates how public-sector websites can be assessed across several dimensions, including performance and accessibility.

These approaches offer opportunities to align research questions and compare methodology, but their scores and samples are not directly interchangeable.

Potential future work could examine relationships with:

- The EU eGovernment Benchmark.
- National Web Accessibility Directive monitoring reports.
- Government digital service quality assessments.
- National design-system adoption programmes.
- Public-sector open-source and procurement reporting.
- Digital sovereignty and public infrastructure research.
- Government website sustainability indicators.

**These are opportunities for future research, not claims that the project currently integrates or reproduces those assessment frameworks.**

Any future integration should preserve the source methodology, date, scope, and limitations of each dataset rather than combine incompatible measures into a single unexplained score.

## How monitoring works

EU Plus Government Scans begins with country-specific inventories of government domains and URLs.

Specialized tools then collect different types of observations.

```text
Government website source lists
              |
              v
Country-level seed datasets
              |
              v
URL validation and normalization
              |
              v
Specialized scanning workflows
              |
              +-- Accessibility statements
              +-- Technology identification
              +-- Third-party dependencies
              +-- Social media links
              +-- Lighthouse
              +-- User preferences
              +-- Domain relationships
              |
              v
Recorded observations and metadata
              |
              v
Aggregation and comparative analysis
              |
              v
Published reports and data exports
```

### Incremental scanning

Different scanners run at different frequencies according to their purpose and computational cost.

Rate limiting, bounded execution, and controls for skipping recently scanned pages help distribute work across the website inventory.

GitHub Actions runs the scheduled and manually triggered workflows.

A completed workflow does not necessarily mean that every target was successfully scanned.

### Historical evidence

Selected historical datasets and scan metadata support analysis over time.

Relationship observations can be marked inactive when subsequent successful scans no longer detect them.

Dated snapshots support comparisons of changes in inventories and external dependencies.

Historical analysis must account for changing site coverage, scanner versions, and detection rules.

An absent observation is not automatically proof that a technology has been removed or a problem has been resolved.

## Understanding country comparisons

Country comparisons are useful only when their underlying evidence is sufficiently clear.

A country with a large inventory is not automatically better represented than one with a smaller, more carefully verified list.

The project therefore distinguishes several related concepts:

- **Inventory size:** How many websites or pages have been identified.
- **Inventory confidence:** How reliably those websites have been classified as governmental.
- **Coverage:** How much of the available inventory a scanner assessed.
- **Freshness:** When observations were collected.
- **Observed results:** What the scanner detected.
- **Uncertainty:** What the evidence does not establish.

A percentage based on ten websites should not be treated as directly equivalent to the same percentage based on thousands of websites without examining the sampling and classification methods.

Government services also differ by administrative level, purpose, and legal obligations.

Where comparative tables are provided, readers should be able to inspect the denominator, country inventory, observation dates, and supporting evidence.

The project does not establish a universal ranking of governments or their digital accessibility.

## Open data and reproducibility

The project publishes reports alongside selected machine-readable evidence.

Formats include JSON, CSV, TOON source files, and historical relationship datasets.

Smaller datasets and indexes are available through GitHub Pages. Larger data exports may be stored as GitHub Actions workflow artifacts.

Not every raw artifact is retained permanently.

See the [Data API documentation](https://mgifford.github.io/eu-plus-government-scans/api.html) for the available datasets and their access arrangements.

Published aggregate figures should be reproducible from the relevant underlying evidence whenever it is available.

The project's [Definition of Done](DEFINITION_OF_DONE.md) establishes expectations for independently verifiable report outputs.

## Who is this for?

EU Plus Government Scans serves several audiences.

### European governments and digital service teams

Public bodies can examine their country's observable website practices, investigate gaps, compare approaches with other jurisdictions, and identify opportunities for improvement.

### National accessibility monitoring authorities

Organizations responsible for implementing, monitoring, reporting, or enforcing the Web Accessibility Directive may find the independent accessibility-statement and website inventories useful as supplementary research.

The project welcomes collaboration on inventory quality, classification, national guidance, and methodological limitations.

### European institutions and policy researchers

Researchers can investigate differences in technology adoption, accessibility practices, third-party dependencies, and public-sector digital infrastructure.

### Open-source communities and civil society

Developers and civil society organizations can examine technology adoption, identify opportunities for collaboration, and investigate public-sector dependence on proprietary services.

### Journalists and the public

Published reports and source data can support independent examination of government technology choices, provided the conclusions reflect the limitations of the evidence.

## Contributing

Contributions are welcome from national monitoring authorities, government employees, developers, researchers, accessibility specialists, and members of the public.

Priority contributions include:

- Correcting government website inventories.
- Providing authoritative national domain lists.
- Verifying operating organizations and administrative classifications.
- Identifying missing accessibility statements or incorrect detections.
- Improving source provenance.
- Reviewing false positives.
- Improving detection rules and historical comparisons.
- Expanding research into other relevant European digital government indicators.
- Improving accessibility and usability of the reporting site.
- Contributing code, tests, and documentation.

**[Open a GitHub issue or propose a contribution](https://github.com/mgifford/eu-plus-government-scans/issues)**

Contributors do not need to write code to help improve the research.

Country-specific expertise and independently verifiable corrections are particularly valuable.

## Running the project locally

The project uses Python for scanning and data processing, GitHub Actions for scheduled execution, and Jekyll for publishing reports.

Development requirements include Python, Git, project dependencies, and the supporting tools needed for particular scanners.

### Install and test

```bash
git clone https://github.com/mgifford/eu-plus-government-scans.git
cd eu-plus-government-scans

python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt

python -m pytest tests/ -v
```

### Validate a country

For a controlled validation of one country's seeded URLs:

```bash
python -m src.cli.validate_urls \
  --country ICELAND \
  --rate-limit 2
```

This performs live requests.

Review the website inventory, command options, and rate limits before starting a scan.

For larger datasets, use the batched validation workflow.

Technical instructions are available in:

- [URL Validation Scanner](docs/url-validation-scanner.md).
- [Batched Validation](docs/batched-validation.md).
- [Issue-Triggered Validation](docs/issue-triggered-validation.md).
- [Lighthouse Scanning](docs/lighthouse-scanning.md).
- [GitHub Actions Validation](docs/github-action-validation.md).

## Related projects

- **[VITAL Scans](https://github.com/mgifford/vital-core):** Continuous website quality monitoring with detailed findings and historical evidence.
- **[Open Scans](https://github.com/mgifford/open-scans):** Multi-engine accessibility testing and ACT-rule comparisons.
- **[Firefox Energy Scanner](https://github.com/mgifford/firefox-energy-scanner):** Controlled investigations of browser activity and energy consumption.
- **[Find Public Code](https://github.com/mgifford/find-publiccode.yml):** Discovery of `publiccode.yml` metadata associated with public-sector software.

EU Plus Government Scans concentrates on comparative evidence about government websites and their technology ecosystems across countries.

## Accessibility and sustainability

The project is committed to providing accessible reports and documentation.

It aims to conform to [WCAG 2.2 AA](https://www.w3.org/TR/WCAG22/) and supports semantic markup, keyboard access, understandable data presentations, and automated accessibility checks.

Passing automated tests does not establish complete conformance.

The project also aims to limit unnecessary requests, repeated scanning, excessive data storage, and avoidable computational work.

See the [Accessibility Commitment](ACCESSIBILITY.md).

## AI transparency

AI coding assistants have contributed to the development, testing, documentation, and maintenance of this project.

The regular scanning and reporting tools use deterministic processing rather than runtime large language model inference.

AI-generated code, documentation, and conclusions require human review.

Research findings must remain independently verifiable against their recorded sources.

See [AGENTS.md](AGENTS.md) for contributor requirements.

The existing detailed history of AI-assisted contributions should be preserved in separate documentation.

## Documentation

- [Published Research Site](https://mgifford.github.io/eu-plus-government-scans/).
- [Scan Progress](docs/scan-progress.md).
- [Government Domains](docs/domains.md).
- [Classification System](docs/classification-system.md).
- [Technology Scanning](docs/technology-scanning.md).
- [Third-Party Services](docs/third-party-tools.md).
- [Lighthouse Scanning](docs/lighthouse-scanning.md).
- [User Preferences](docs/user-preferences.md).
- [Data API](docs/api.md).
- [Weekly Digest](docs/weekly-digest.md).
- [Definition of Done](DEFINITION_OF_DONE.md).
- [AI Agent Instructions](AGENTS.md).
- [Software Bill of Materials](SBOM.md).

### European policy and research references

- [Web Accessibility Directive](https://eur-lex.europa.eu/eli/dir/2016/2102/oj).
- [European Commission: National Accessibility Monitoring Bodies](https://digital-strategy.ec.europa.eu/en/policies/web-accessibility-monitoring).
- [Web Accessibility Directive Monitoring Methodology](https://eur-lex.europa.eu/eli/dec_impl/2018/1524/oj).
- [National Monitoring Reports, 2022–2024](https://digital-strategy.ec.europa.eu/en/news/web-accessibility-directive-monitoring-reports-2022-2024).
- [eGovernment Benchmark 2026](https://digital-strategy.ec.europa.eu/en/library/digital-decade-2026-egovernment-benchmark-2026).
- [France: Observatoire de l'écosystème numérique de l'État](https://www.data.gouv.fr/datasets/observatoire-de-lecosysteme-numerique-de-letat-sites-internet).

## License

EU Plus Government Scans is free and open-source software distributed under the [GNU Affero General Public License, version 3](LICENSE).

Third-party dependencies and imported datasets may have separate licenses or reuse conditions. Consult their original sources before redistribution.

The project welcomes contributions that make government digital infrastructure more transparent, accessible, sustainable, and accountable.
