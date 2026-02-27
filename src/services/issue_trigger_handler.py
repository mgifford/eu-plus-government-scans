"""Handler for processing issue-triggered validation scans."""

from __future__ import annotations

import asyncio
import re
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.jobs.url_validation_scanner import UrlValidationScanner
from src.lib.country_utils import country_code_to_filename
from src.services.github_issue_manager import GitHubIssueManager


@dataclass
class TriggerConfig:
    """Configuration for a trigger type."""
    prefix: str
    is_periodic: bool  # If True, don't close issue after processing
    schedule: Optional[str] = None  # Human-readable schedule description


# Supported trigger prefixes
TRIGGER_CONFIGS = [
    TriggerConfig("SCAN:", is_periodic=False),
    TriggerConfig("QUARTERLY:", is_periodic=True, schedule="quarterly"),
    TriggerConfig("MONTHLY:", is_periodic=True, schedule="monthly"),
    TriggerConfig("WEEKLY:", is_periodic=True, schedule="weekly"),
    TriggerConfig("MONDAYS:", is_periodic=True, schedule="every Monday"),
    TriggerConfig("TUESDAYS:", is_periodic=True, schedule="every Tuesday"),
    TriggerConfig("WEDNESDAYS:", is_periodic=True, schedule="every Wednesday"),
    TriggerConfig("THURSDAYS:", is_periodic=True, schedule="every Thursday"),
    TriggerConfig("FRIDAYS:", is_periodic=True, schedule="every Friday"),
    TriggerConfig("SATURDAYS:", is_periodic=True, schedule="every Saturday"),
    TriggerConfig("SUNDAYS:", is_periodic=True, schedule="every Sunday"),
]


class IssueTriggerHandler:
    """Handles processing of issue-triggered validation scans."""

    def __init__(
        self,
        scanner: UrlValidationScanner,
        issue_manager: GitHubIssueManager,
        db_path: Path,
    ):
        self.scanner = scanner
        self.issue_manager = issue_manager
        self.db_path = db_path
        self.toon_dir = Path("data/toon-seeds/countries")

    def find_trigger_issues(self) -> List[Dict[str, Any]]:
        """
        Find open issues with trigger prefixes in their titles.
        
        Returns:
            List of issue dictionaries with keys: number, title, body, trigger_config
        """
        # Use GitHub CLI to list open issues
        try:
            result = subprocess.run(
                [
                    "gh", "issue", "list",
                    "--state", "open",
                    "--json", "number,title,body",
                    "--limit", "100",
                ],
                capture_output=True,
                text=True,
                timeout=30,
            )
            
            if result.returncode != 0:
                print(f"Warning: Could not list issues: {result.stderr}")
                return []
            
            import json
            issues = json.loads(result.stdout)
            
            # Filter issues with trigger prefixes
            trigger_issues = []
            for issue in issues:
                title = issue.get("title", "")
                
                for config in TRIGGER_CONFIGS:
                    if title.upper().startswith(config.prefix):
                        issue["trigger_config"] = config
                        trigger_issues.append(issue)
                        break
            
            return trigger_issues
        
        except Exception as e:
            print(f"Error finding trigger issues: {e}")
            return []

    async def process_trigger_issue(self, issue: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a trigger issue by running validation and posting results.
        
        Args:
            issue: Issue dictionary with number, title, body, trigger_config
            
        Returns:
            Dictionary with keys: success, closed, error (optional)
        """
        issue_number = issue["number"]
        title = issue["title"]
        config = issue["trigger_config"]
        
        print(f"Processing issue #{issue_number}: {title}")
        print(f"Trigger type: {config.prefix} ({'periodic' if config.is_periodic else 'one-time'})")
        print("")
        
        # Check if this is a validation request
        if "validate" in title.lower() and "url" in title.lower():
            return await self._process_url_validation(issue_number, config)
        else:
            print(f"⚠️  Unknown trigger action in title: {title}")
            return {
                "success": False,
                "error": "Unknown trigger action - title must contain 'validate url'",
            }

    async def _process_url_validation(
        self,
        issue_number: int,
        config: TriggerConfig,
    ) -> Dict[str, Any]:
        """Process URL validation for all countries."""
        print("Starting URL validation for all countries...")
        print("")
        
        # Get list of all countries
        countries = self._get_all_countries()
        print(f"Found {len(countries)} countries to validate")
        print("")
        
        # Validate all countries
        all_stats = []
        for idx, country_code in enumerate(countries, 1):
            try:
                toon_file = self.toon_dir / f"{country_code_to_filename(country_code)}.toon"
                
                if not toon_file.exists():
                    print(f"[{idx}/{len(countries)}] ⚠️  Skipping {country_code}: TOON file not found")
                    continue
                
                print(f"[{idx}/{len(countries)}] Processing {country_code}...")
                
                stats = await self.scanner.scan_country(
                    country_code,
                    toon_file,
                    rate_limit_per_second=2.0,
                )
                
                all_stats.append(stats)
                
                # Print brief summary
                print(f"  ✓ {stats['valid_urls']} valid, {stats['invalid_urls']} invalid, "
                      f"{stats['urls_removed']} removed")
                print("")
            
            except Exception as e:
                print(f"  ✗ Error: {e}")
                print("")
        
        # Generate report
        report = self._generate_validation_report(all_stats, config)
        
        # Post comment to issue
        print(f"Posting validation report to issue #{issue_number}...")
        self.issue_manager.add_comment(issue_number, report)
        
        # Close issue if one-time scan
        if not config.is_periodic:
            print(f"Closing issue #{issue_number} (one-time scan complete)")
            self._close_issue(issue_number, report)
            return {"success": True, "closed": True}
        else:
            print(f"Issue #{issue_number} remains open (periodic scan)")
            return {"success": True, "closed": False}

    def _get_all_countries(self) -> List[str]:
        """Get list of all countries from TOON files."""
        from src.lib.country_utils import country_filename_to_code
        
        countries = []
        if self.toon_dir.exists():
            for toon_file in sorted(self.toon_dir.glob("*.toon")):
                # Skip validated files
                if "_validated" in toon_file.stem:
                    continue
                country_code = country_filename_to_code(toon_file.stem)
                countries.append(country_code)
        
        return countries

    def _generate_validation_report(
        self,
        all_stats: List[Dict[str, Any]],
        config: TriggerConfig,
    ) -> str:
        """Generate a markdown report from validation statistics."""
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        
        # Calculate totals
        total_countries = len(all_stats)
        total_urls = sum(s.get("total_urls", 0) for s in all_stats)
        total_validated = sum(s.get("urls_validated", 0) for s in all_stats)
        total_valid = sum(s.get("valid_urls", 0) for s in all_stats)
        total_invalid = sum(s.get("invalid_urls", 0) for s in all_stats)
        total_redirected = sum(s.get("redirected_urls", 0) for s in all_stats)
        total_removed = sum(s.get("urls_removed", 0) for s in all_stats)
        
        # Calculate percentages safely
        valid_pct = (total_valid / total_validated * 100) if total_validated > 0 else 0
        invalid_pct = (total_invalid / total_validated * 100) if total_validated > 0 else 0
        
        report = f"""## URL Validation Report

**Trigger:** {config.prefix} {f"({config.schedule})" if config.schedule else ""}
**Completed:** {timestamp}
**Countries Processed:** {total_countries}

### Summary

| Metric | Count |
|--------|-------|
| Total URLs | {total_urls:,} |
| Validated | {total_validated:,} |
| Valid | {total_valid:,} ({valid_pct:.1f}%) |
| Invalid | {total_invalid:,} ({invalid_pct:.1f}%) |
| Redirected | {total_redirected:,} |
| Removed (failed 2x) | {total_removed:,} |

### Country Details

| Country | Total | Valid | Invalid | Redirected | Removed |
|---------|-------|-------|---------|------------|---------|
"""
        
        # Add country details
        for stats in all_stats:
            country = stats.get("country_code", "Unknown")
            total = stats.get("total_urls", 0)
            valid = stats.get("valid_urls", 0)
            invalid = stats.get("invalid_urls", 0)
            redirected = stats.get("redirected_urls", 0)
            removed = stats.get("urls_removed", 0)
            
            report += f"| {country} | {total} | {valid} | {invalid} | {redirected} | {removed} |\n"
        
        report += f"""
### Notes

- URLs are validated with a 20-second timeout
- Failed URLs are tracked across scans
- URLs are removed after failing twice
- Redirects are followed and URLs are updated
"""
        
        if config.is_periodic:
            report += f"\n**Next Run:** This issue will remain open and validation will run {config.schedule}.\n"
        else:
            report += f"\n**Status:** Validation complete. Issue will be closed.\n"
        
        return report

    def _close_issue(self, issue_number: int, final_report: str):
        """Close an issue after one-time scan."""
        try:
            subprocess.run(
                [
                    "gh", "issue", "close", str(issue_number),
                    "--reason", "completed",
                    "--comment", "Validation complete. See report above.",
                ],
                capture_output=True,
                text=True,
                timeout=30,
            )
        except Exception as e:
            print(f"Warning: Could not close issue: {e}")
