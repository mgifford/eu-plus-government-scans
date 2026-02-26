"""GitHub Issue manager for tracking validation cycles."""

from __future__ import annotations

import os
import subprocess
from typing import Optional


class GitHubIssueManager:
    """Manages GitHub issues for validation cycle tracking."""

    def __init__(self, repo: str = "mgifford/eu-plus-government-scans"):
        self.repo = repo
        self._has_gh_cli = self._check_gh_cli()

    def _check_gh_cli(self) -> bool:
        """Check if GitHub CLI is available."""
        try:
            result = subprocess.run(
                ["gh", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    def _run_gh_command(self, args: list[str]) -> tuple[bool, str]:
        """
        Run a GitHub CLI command.
        
        Returns:
            Tuple of (success, output)
        """
        if not self._has_gh_cli:
            return False, "GitHub CLI not available"

        try:
            result = subprocess.run(
                ["gh"] + args,
                capture_output=True,
                text=True,
                timeout=30,
                env={**os.environ, "GH_REPO": self.repo}
            )
            return result.returncode == 0, result.stdout.strip()
        except subprocess.TimeoutExpired:
            return False, "Command timed out"
        except Exception as e:
            return False, str(e)

    def create_validation_issue(self, cycle_id: str) -> Optional[int]:
        """
        Create a GitHub issue to track a validation cycle.
        
        Args:
            cycle_id: The cycle ID
            
        Returns:
            Issue number if created successfully, None otherwise
        """
        title = f"URL Validation Cycle: {cycle_id}"
        body = f"""This issue tracks the automated URL validation cycle `{cycle_id}`.

## Progress

Batch validation is in progress. This issue will be automatically updated with progress.

**Status:** 🟡 In Progress

This issue will be automatically closed when all countries have been validated.

---
*This issue is managed by the automated URL validation workflow.*
"""

        success, output = self._run_gh_command([
            "issue", "create",
            "--title", title,
            "--body", body,
            "--label", "url-validation",
            "--label", "automated"
        ])

        if success:
            # Parse issue number from output (format: "URL")
            # Example: https://github.com/owner/repo/issues/123
            try:
                issue_number = int(output.split("/")[-1])
                return issue_number
            except (ValueError, IndexError):
                return None

        return None

    def update_issue_progress(
        self,
        issue_number: int,
        cycle_id: str,
        total: int,
        completed: int,
        processing: int,
        pending: int,
        failed: int,
    ):
        """
        Update issue with current progress.
        
        Args:
            issue_number: GitHub issue number
            cycle_id: Cycle ID
            total: Total countries
            completed: Completed countries
            processing: Currently processing countries
            pending: Pending countries
            failed: Failed countries
        """
        progress_pct = (completed / total * 100) if total > 0 else 0
        
        # Create progress bar
        bar_length = 20
        filled = int(bar_length * completed / total) if total > 0 else 0
        bar = "█" * filled + "░" * (bar_length - filled)
        
        status_emoji = "🟢" if pending == 0 and processing == 0 else "🟡"
        
        body = f"""This issue tracks the automated URL validation cycle `{cycle_id}`.

## Progress

**Status:** {status_emoji} {"Complete" if pending == 0 and processing == 0 else "In Progress"}

{bar} {progress_pct:.1f}%

- ✅ Completed: {completed}/{total}
- 🔄 Processing: {processing}
- ⏳ Pending: {pending}
- ❌ Failed: {failed}

### Details

The validation workflow runs every 2 hours and processes countries in batches to avoid GitHub Actions timeouts.

---
*Last updated: Automatically by URL validation workflow*
*This issue is managed by automated workflow and will close when complete.*
"""

        self._run_gh_command([
            "issue", "edit", str(issue_number),
            "--body", body
        ])

    def close_validation_issue(
        self,
        issue_number: int,
        cycle_id: str,
        total: int,
        completed: int,
        failed: int,
    ):
        """
        Close a validation cycle issue.
        
        Args:
            issue_number: GitHub issue number
            cycle_id: Cycle ID
            total: Total countries
            completed: Successfully completed countries
            failed: Failed countries
        """
        body = f"""This validation cycle `{cycle_id}` has completed.

## Final Results

**Status:** 🟢 Complete

- ✅ Successfully validated: {completed}/{total} countries
- ❌ Failed: {failed} countries

All countries have been processed. The validation cycle is complete.

---
*Closed automatically by URL validation workflow*
"""

        self._run_gh_command([
            "issue", "edit", str(issue_number),
            "--body", body
        ])
        
        self._run_gh_command([
            "issue", "close", str(issue_number),
            "--reason", "completed"
        ])

    def add_comment(self, issue_number: int, comment: str):
        """Add a comment to an issue."""
        self._run_gh_command([
            "issue", "comment", str(issue_number),
            "--body", comment
        ])

    def reopen_issue(self, issue_number: int):
        """Reopen a closed issue."""
        self._run_gh_command([
            "issue", "reopen", str(issue_number)
        ])

    def find_open_validation_issue(self) -> Optional[int]:
        """
        Find an open validation issue.
        
        Returns:
            Issue number if found, None otherwise
        """
        success, output = self._run_gh_command([
            "issue", "list",
            "--label", "url-validation",
            "--state", "open",
            "--limit", "1",
            "--json", "number",
            "--jq", ".[0].number"
        ])

        if success and output:
            try:
                return int(output)
            except ValueError:
                return None

        return None
