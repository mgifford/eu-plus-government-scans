"""CLI entry point for issue-triggered validation."""

from __future__ import annotations

import asyncio
import sys
from datetime import datetime, timezone
from pathlib import Path

from src.jobs.url_validation_scanner import UrlValidationScanner
from src.lib.settings import load_settings
from src.services.github_issue_manager import GitHubIssueManager
from src.services.issue_trigger_handler import IssueTriggerHandler
from src.storage.schema import initialize_schema


def main():
    """Main CLI entry point for issue-triggered validation."""
    print("=" * 80)
    print("ISSUE-TRIGGERED VALIDATION CHECKER")
    print("=" * 80)
    print(f"Timestamp: {datetime.now(timezone.utc).isoformat()}")
    print("")
    
    # Initialize services
    settings = load_settings()
    db_path = initialize_schema(settings.metadata_db_url)
    scanner = UrlValidationScanner(settings)
    issue_manager = GitHubIssueManager()
    trigger_handler = IssueTriggerHandler(scanner, issue_manager, db_path)
    
    # Check for trigger issues
    print("Checking for open trigger issues...")
    issues = trigger_handler.find_trigger_issues()
    
    if not issues:
        print("✓ No trigger issues found")
        return
    
    print(f"Found {len(issues)} trigger issue(s):")
    for issue in issues:
        print(f"  - Issue #{issue['number']}: {issue['title']}")
    print("")
    
    # Process each trigger issue
    for issue in issues:
        try:
            print("=" * 80)
            print(f"Processing Issue #{issue['number']}: {issue['title']}")
            print("=" * 80)
            
            result = asyncio.run(
                trigger_handler.process_trigger_issue(issue)
            )
            
            if result["success"]:
                print(f"✓ Issue #{issue['number']} processed successfully")
                if result.get("closed"):
                    print(f"  Issue closed (one-time scan)")
            else:
                print(f"✗ Issue #{issue['number']} processing failed: {result.get('error')}")
        
        except Exception as e:
            print(f"❌ Error processing issue #{issue['number']}: {e}")
            import traceback
            traceback.print_exc()
    
    print("")
    print("=" * 80)
    print("ISSUE PROCESSING COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
