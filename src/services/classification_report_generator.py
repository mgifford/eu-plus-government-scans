"""Review report generation for the classification system.

Generates classification reports in `docs/data/classification/` for static publishing via GitHub Pages.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from .classification_engine import ClassificationEngine


class ClassificationReportGenerator:
    """Generates classification reports for static publishing."""

    def __init__(self, engine: ClassificationEngine) -> None:
        """Initialize with a classification engine."""
        self.engine = engine

    def generate_country_report(self, country_code: str) -> Dict[str, Any]:
        """Generate a classification report for a specific country."""
        # Get the country rule
        country_rule = self.engine.get_country_rule(country_code)
        if not country_rule:
            return {
                "country_code": country_code,
                "generated_at": datetime.now().isoformat(),
                "statistics": self._empty_statistics(),
                "domains": [],
            }

        # For now, we'll generate a report based on the country rule itself
        # In the future, this would load actual domain data
        stats = {
            "total_domains": 0,
            "classification_status": {
                "confirmed": 0,
                "probable": 0,
                "candidate": 0,
                "disputed": 0,
                "unknown": 0,
            },
            "central_administration": {
                "true": 0,
                "false": 0,
                "null": 0,
            },
            "government_levels": {},
            "organization_types": {},
        }

        return {
            "country_code": country_code,
            "generated_at": datetime.now().isoformat(),
            "statistics": stats,
            "domains": [],
            "country_rule": {
                "version": country_rule.rule_version,
                "administrative_context": country_rule.administrative_context,
                "central_administration_definition": country_rule.central_administration_definition,
                "included_organization_types": country_rule.include.get("organization_types", []),
                "excluded_organization_types": country_rule.exclude.get("organization_types", []),
                "domain_patterns": country_rule.domain_patterns,
                "exceptions": country_rule.exceptions,
            },
        }

    def generate_global_report(self) -> Dict[str, Any]:
        """Generate a global classification report."""
        # Generate reports for each country
        country_reports = []
        for country_code in self.engine.country_rules.keys():
            report = self.generate_country_report(country_code)
            country_reports.append(report)

        # Calculate global statistics
        global_stats = self._calculate_global_statistics(country_reports)

        return {
            "generated_at": datetime.now().isoformat(),
            "statistics": global_stats,
            "countries": country_reports,
        }

    def save_country_report(self, country_code: str, output_dir: Path) -> None:
        """Save a country report to the output directory."""
        report = self.generate_country_report(country_code)

        # Create output directory if it doesn't exist
        output_dir.mkdir(parents=True, exist_ok=True)

        # Save JSON report
        json_path = output_dir / f"{country_code.lower()}.json"
        with open(json_path, "w") as f:
            json.dump(report, f, indent=2)

        # Generate and save Markdown report
        markdown = self._generate_country_markdown(report)
        md_path = output_dir / f"{country_code.lower()}.md"
        with open(md_path, "w") as f:
            f.write(markdown)

    def save_global_report(self, output_dir: Path) -> None:
        """Save the global report to the output directory."""
        report = self.generate_global_report()

        # Create output directory if it doesn't exist
        output_dir.mkdir(parents=True, exist_ok=True)

        # Save JSON report
        json_path = output_dir / "global.json"
        with open(json_path, "w") as f:
            json.dump(report, f, indent=2)

        # Generate and save Markdown report
        markdown = self._generate_global_markdown(report)
        md_path = output_dir / "global.md"
        with open(md_path, "w") as f:
            f.write(markdown)

    def _empty_statistics(self) -> Dict[str, Any]:
        """Return empty statistics structure."""
        return {
            "total_domains": 0,
            "classification_status": {
                "confirmed": 0,
                "probable": 0,
                "candidate": 0,
                "disputed": 0,
                "unknown": 0,
            },
            "central_administration": {
                "true": 0,
                "false": 0,
                "null": 0,
            },
            "government_levels": {},
            "organization_types": {},
        }

    def _calculate_global_statistics(self, country_reports: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate global statistics from country reports."""
        total_domains = 0
        total_confirmed = 0
        total_probable = 0
        total_candidate = 0
        total_disputed = 0
        total_unknown = 0
        total_central_true = 0
        total_central_false = 0
        total_central_null = 0
        government_levels = {}
        organization_types = {}

        for report in country_reports:
            stats = report["statistics"]
            total_domains += stats["total_domains"]
            total_confirmed += stats["classification_status"]["confirmed"]
            total_probable += stats["classification_status"]["probable"]
            total_candidate += stats["classification_status"]["candidate"]
            total_disputed += stats["classification_status"]["disputed"]
            total_unknown += stats["classification_status"]["unknown"]
            total_central_true += stats["central_administration"]["true"]
            total_central_false += stats["central_administration"]["false"]
            total_central_null += stats["central_administration"]["null"]

            for level, count in stats["government_levels"].items():
                government_levels[level] = government_levels.get(level, 0) + count

            for org_type, count in stats["organization_types"].items():
                organization_types[org_type] = organization_types.get(org_type, 0) + count

        return {
            "total_countries": len(country_reports),
            "total_domains": total_domains,
            "classification_status": {
                "confirmed": total_confirmed,
                "probable": total_probable,
                "candidate": total_candidate,
                "disputed": total_disputed,
                "unknown": total_unknown,
            },
            "central_administration": {
                "true": total_central_true,
                "false": total_central_false,
                "null": total_central_null,
            },
            "government_levels": government_levels,
            "organization_types": organization_types,
        }

    def _generate_country_markdown(self, report: Dict[str, Any]) -> str:
        """Generate Markdown content for a country report."""
        stats = report["statistics"]
        country_rule = report.get("country_rule", {})

        md = f"""# Classification Report: {report['country_code']}

Generated: {report['generated_at']}

## Country Rule Information

- **Version:** {country_rule.get('version', 'N/A')}
- **Administrative Context:** {country_rule.get('administrative_context', 'N/A')}
- **Central Administration Definition:** {country_rule.get('central_administration_definition', 'N/A')}

### Included Organization Types

"""
        for org_type in country_rule.get('included_organization_types', []):
            md += f"- {org_type}\n"

        md += "\n### Excluded Organization Types\n\n"
        for org_type in country_rule.get('excluded_organization_types', []):
            md += f"- {org_type}\n"

        md += "\n### Domain Patterns\n\n"
        for pattern in country_rule.get('domain_patterns', {}).get('high_confidence', []):
            md += f"- `{pattern}` (high confidence)\n"
        for pattern in country_rule.get('domain_patterns', {}).get('supporting', []):
            md += f"- `{pattern}` (supporting)\n"

        md += "\n### Explicit Exceptions\n\n"
        exceptions = country_rule.get('exceptions', {})
        if exceptions.get('include'):
            md += "**Include Exceptions:**\n"
            for exc in exceptions['include']:
                md += f"- `{exc['domain']}`: {exc.get('reason', 'No reason provided')}\n"
        if exceptions.get('exclude'):
            md += "\n**Exclude Exceptions:**\n"
            for exc in exceptions['exclude']:
                md += f"- `{exc['domain']}`: {exc.get('reason', 'No reason provided')}\n"

        md += f"""
## Statistics

### Total Domains: {stats['total_domains']}

### Classification Status

| Status | Count |
|--------|-------|
| Confirmed | {stats['classification_status']['confirmed']} |
| Probable | {stats['classification_status']['probable']} |
| Candidate | {stats['classification_status']['candidate']} |
| Disputed | {stats['classification_status']['disputed']} |
| Unknown | {stats['classification_status']['unknown']} |

### Central Administration Status

| Status | Count |
|--------|-------|
| True (Central) | {stats['central_administration']['true']} |
| False (Non-Central) | {stats['central_administration']['false']} |
| Unknown | {stats['central_administration']['null']} |

### Government Levels

| Level | Count |
|-------|-------|
"""
        for level, count in sorted(stats['government_levels'].items()):
            md += f"| {level} | {count} |\n"

        md += """
### Organization Types

| Type | Count |
|------|-------|
"""
        for org_type, count in sorted(stats['organization_types'].items()):
            md += f"| {org_type} | {count} |\n"

        return md

    def _generate_global_markdown(self, report: Dict[str, Any]) -> str:
        """Generate Markdown content for the global report."""
        stats = report['statistics']

        md = f"""# Global Classification Report

Generated: {report['generated_at']}

## Overview

### Total Countries: {stats['total_countries']}
### Total Domains: {stats['total_domains']}

## Classification Status

| Status | Count |
|--------|-------|
| Confirmed | {stats['classification_status']['confirmed']} |
| Probable | {stats['classification_status']['probable']} |
| Candidate | {stats['classification_status']['candidate']} |
| Disputed | {stats['classification_status']['disputed']} |
| Unknown | {stats['classification_status']['unknown']} |

## Central Administration Status

| Status | Count |
|--------|-------|
| True (Central) | {stats['central_administration']['true']} |
| False (Non-Central) | {stats['central_administration']['false']} |
| Unknown | {stats['central_administration']['null']} |

## Government Levels

| Level | Count |
|-------|-------|
"""
        for level, count in sorted(stats['government_levels'].items()):
            md += f"| {level} | {count} |\n"

        md += """
## Organization Types

| Type | Count |
|------|-------|
"""
        for org_type, count in sorted(stats['organization_types'].items()):
            md += f"| {org_type} | {count} |\n"

        md += """
## Country Reports

| Country | Domains | Confirmed | Probable | Candidate | Disputed | Unknown |
|---------|---------|-----------|----------|-----------|----------|---------|
"""
        for country_report in report['countries']:
            country_stats = country_report['statistics']
            md += f"| {country_report['country_code']} | {country_stats['total_domains']} | {country_stats['classification_status']['confirmed']} | {country_stats['classification_status']['probable']} | {country_stats['classification_status']['candidate']} | {country_stats['classification_status']['disputed']} | {country_stats['classification_status']['unknown']} |\n"

        return md
