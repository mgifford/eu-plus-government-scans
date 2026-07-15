# Country-Specific Governance Classification System

## Overview

This document describes the country-specific governance classification system for distinguishing central administration domains from non-central public bodies. The system applies institutional evidence, country-specific rules, and deterministic classification to ensure consistent and verifiable results.

## Core Principles

### 1. Evidence-Based Classification

Central-administration status requires institutional evidence. Classifications are not inferred from:
- Graph centrality metrics
- TLD patterns alone
- Software Heritage presence
- HTTP 200 responses
- Domain pattern matching as primary evidence

### 2. Country-Specific Rules Override Global Baseline

Each country has its own governance model that defines:
- Administrative context
- Central administration definition
- Included/excluded organization types
- Domain patterns (supporting evidence only)
- Explicit exceptions
- Authoritative sources
- Known ambiguities

### 3. Unresolved Over Uncertainty

When evidence is insufficient, classifications remain unresolved (null) rather than being assigned uncertain values. This prevents false certainty and encourages evidence gathering.

### 4. Deterministic Output

The classification engine produces deterministic results. Given the same domain and rules, the output will always be identical. This ensures reproducibility and auditability.

## Classification Pipeline

The classification engine applies rules in strict precedence:

1. **Explicit Exceptions** - Domain-specific inclusions/exclusions
2. **Organization Type** - Based on organization type and country rules
3. **Authoritative Assertions** - From authoritative sources
4. **Domain Patterns** - Supporting evidence only
5. **Government Level** - Additional context

## Data Structure

### Country Governance Models

Country governance models are stored in `data/classification/countries/` as YAML files. Each file contains:

- `country_code` - ISO-3166-1 alpha-2 code
- `version` - Rule version number
- `administrative_context` - Description of country's administrative structure
- `central_administration_definition` - What counts as central administration
- `included_organization_types` - Types classified as central administration
- `excluded_organization_types` - Types classified as non-central
- `domain_patterns` - Supporting domain patterns
- `include_exceptions` - Explicit inclusions
- `exclude_exceptions` - Explicit exclusions
- `authoritative_sources` - Source URLs
- `known_ambiguities` - Documented ambiguities

### Canonical Domain Model

The canonical domain model includes new fields for classification:

- `central_administration` - Boolean (true/false/null)
- `classification_status` - Status (confirmed/probable/candidate/disputed/retired/unknown)
- `classification_basis` - List of evidence sources
- `classification_rule` - Applied rule identifier
- `review_status` - Review status (pending/reviewed/approved/rejected/unknown)
- `reviewed_at` - ISO date of last review
- `reviewed_by` - Reviewer identifier
- `conflicts` - List of conflicting source assertions
- `applied_rules` - List of classification rules applied

## Country Rules

### Canada (CA)

**Administrative Context:** Federal parliamentary democracy with 10 provinces and 3 territories.

**Central Administration Definition:** Federal government departments and agencies reporting directly to Parliament or the Prime Minister.

**Included Organization Types:**
- ministry
- department
- executive_office
- head_of_government

**Excluded Organization Types:**
- agency
- crown_corporation
- regulator
- public_broadcaster
- state_owned_enterprise

**Domain Patterns:**
- `*.canada.ca` (supporting evidence only)

**Explicit Exceptions:**
- Exclude: `sac-stat.canada.ca` (Shared Services Canada)

### France (FR)

**Administrative Context:** Unitary semi-presidential republic with 18 regions and 101 departments.

**Central Administration Definition:** Central government ministries and services at the national level.

**Included Organization Types:**
- ministry
- direction_centrale
- secretariat
- executive_office

**Excluded Organization Types:**
- agency
- regulator
- public_operator
- public_establishment
- regional_council
- departmental_council

**Domain Patterns:**
- `*.gouv.fr` (supporting evidence only)

**Explicit Exceptions:**
- Exclude: `etalab.gouv.fr` (Etalab/DINUM)

### Germany (DE)

**Administrative Context:** Federal parliamentary republic with 16 states (Länder).

**Central Administration Definition:** Federal ministries and authorities at the national level.

**Included Organization Types:**
- ministry
- federal_ministry
- federal_authority
- executive_office

**Excluded Organization Types:**
- agency
- regulator
- federal_police
- constitutional_protection
- state_government

**Domain Patterns:**
- `*.bund.de` (supporting evidence only)

**Explicit Exceptions:**
- None currently

### Spain (ES)

**Administrative Context:** Unitary parliamentary constitutional monarchy with 17 autonomous communities and 2 autonomous cities.

**Central Administration Definition:** National government ministries and agencies at the central level.

**Included Organization Types:**
- ministry
- secretariat
- executive_office
- national_government

**Excluded Organization Types:**
- agency
- regulator
- autonomous_community
- provincial_council
- municipality

**Domain Patterns:**
- `*.gob.es` (supporting evidence only)

**Explicit Exceptions:**
- Exclude: `sepe.gob.es` (Public Employment Service)

### United Kingdom (GB)

**Administrative Context:** Unitary parliamentary constitutional monarchy with England, Scotland, Wales, and Northern Ireland.

**Central Administration Definition:** UK government departments and offices of the constitutional monarch.

**Included Organization Types:**
- ministry
- department
- executive_office
- office_of_state

**Excluded Organization Types:**
- executive_agency
- regulator
- non_departmental_public_body
- nhs
- local_authority
- devolved_administration

**Domain Patterns:**
- `*.gov.uk` (supporting evidence only)

**Explicit Exceptions:**
- Exclude: `nhs.uk` (National Health Service)
- Exclude: `metoffice.gov.uk` (Met Office)

## Usage

### Generating Reports

```bash
# Generate a report for a specific country
python -m src.cli.generate_classification_report --country CA

# Generate a global report
python -m src.cli.generate_classification_report
```

### Classifying Domains

```python
from src.services.classification_engine import ClassificationEngine
from src.models.domain_model import CanonicalDomain

engine = ClassificationEngine()

domain = CanonicalDomain(
    id="ca-treasury-board",
    domain="sct-ftb.canada.ca",
    country="CA",
    organization_name="Treasury Board of Canada Secretariat",
    government_level="national",
    organization_type="ministry",
)

result = engine.classify_domain(domain)
print(result.central_administration)  # True
print(result.classification_status)  # "confirmed"
print(result.applied_rules)  # ["CA-INCLUDE-MINISTRY"]
```

## Contributing

### Adding a New Country

1. Create a new YAML file in `data/classification/countries/` with the country code
2. Fill in all required fields
3. Add explicit exceptions for known edge cases
4. Document authoritative sources
5. Add tests for the new country rules

### Updating Country Rules

1. Update the YAML file for the country
2. Increment the version number
3. Document the changes
4. Add tests for the new rules
5. Generate updated reports

### Submitting Domain Corrections

Use the GitHub issue templates to submit:
- New domain submissions
- Classification corrections
- Country governance rule proposals
- Disputed classification reports
- Domain retirement requests

## Testing

Run tests with:

```bash
python -m pytest tests/unit/test_classification_engine.py -v
```

## Reports

Classification reports are generated in `docs/data/classification/` and are published via GitHub Pages. Each country gets:
- A JSON file with full data
- A Markdown file with human-readable summary

The global report provides an overview of all countries and their classification statistics.
