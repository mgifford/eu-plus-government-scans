"""CLI entry point for batched URL validation scanner."""

from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

from src.jobs.url_validation_scanner import UrlValidationScanner
from src.lib.country_utils import country_code_to_filename
from src.lib.settings import load_settings
from src.services.batch_coordinator import BatchCoordinator, BatchConfig
from src.services.github_issue_manager import GitHubIssueManager
from src.storage.schema import initialize_schema


def main():
    """Main CLI entry point for batched validation."""
    parser = argparse.ArgumentParser(
        description="Validate URLs in government TOON files with batch processing"
    )
    
    # Batch mode arguments
    parser.add_argument(
        "--batch-mode",
        help="Enable batch processing mode",
        action="store_true",
    )
    parser.add_argument(
        "--batch-size",
        help="Number of countries to process per batch (default: 5)",
        type=int,
        default=5,
    )
    parser.add_argument(
        "--github-issue",
        help="GitHub issue number to track this validation cycle",
        type=int,
    )
    parser.add_argument(
        "--create-issue",
        help="Create a GitHub issue to track progress",
        action="store_true",
    )
    
    # Single country mode (original)
    parser.add_argument(
        "--country",
        help="Specific country code to scan (e.g., ICELAND, FRANCE)",
        type=str,
    )
    
    # Common arguments
    parser.add_argument(
        "--toon-dir",
        help="Directory containing TOON files",
        type=Path,
        default=Path("data/toon-seeds/countries"),
    )
    parser.add_argument(
        "--rate-limit",
        help="Maximum requests per second",
        type=float,
        default=2.0,
    )
    parser.add_argument(
        "--all",
        help="Scan all countries (legacy mode, use --batch-mode instead)",
        action="store_true",
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if not args.batch_mode and not args.all and not args.country:
        print("Error: Must specify --batch-mode, --country, or --all")
        parser.print_help()
        sys.exit(1)
    
    if not args.toon_dir.exists():
        print(f"Error: TOON directory not found: {args.toon_dir}")
        sys.exit(1)
    
    # Load settings and initialize
    settings = load_settings()
    db_path = initialize_schema(settings.metadata_db_url)
    scanner = UrlValidationScanner(settings)
    
    try:
        if args.batch_mode:
            # Batch processing mode
            run_batch_mode(
                scanner=scanner,
                db_path=db_path,
                toon_dir=args.toon_dir,
                batch_size=args.batch_size,
                rate_limit=args.rate_limit,
                github_issue=args.github_issue,
                create_issue=args.create_issue,
            )
        elif args.all:
            # Legacy mode: scan all countries
            print("⚠️  Warning: --all mode will process all countries sequentially.")
            print("   This may take longer than 2 hours. Consider using --batch-mode instead.")
            print("")
            stats = asyncio.run(
                scanner.scan_all_countries(
                    args.toon_dir,
                    rate_limit_per_second=args.rate_limit,
                )
            )
            print_summary(stats)
        else:
            # Single country mode
            country_code = args.country.upper()
            toon_file = args.toon_dir / f"{country_code_to_filename(country_code)}.toon"
            
            if not toon_file.exists():
                print(f"Error: TOON file not found: {toon_file}")
                sys.exit(1)
            
            print(f"Scanning {country_code}...")
            stats = asyncio.run(
                scanner.scan_country(
                    country_code,
                    toon_file,
                    rate_limit_per_second=args.rate_limit,
                )
            )
            print_country_stats(stats)
    
    except KeyboardInterrupt:
        print("\nScan interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def run_batch_mode(
    scanner: UrlValidationScanner,
    db_path: Path,
    toon_dir: Path,
    batch_size: int,
    rate_limit: float,
    github_issue: int | None,
    create_issue: bool,
):
    """Run validation in batch mode."""
    import time
    
    # Track start time for timeout handling
    start_time = time.time()
    # Leave 10 minutes buffer before the 110 minute GitHub Actions timeout
    max_runtime_seconds = (110 - 10) * 60  # 100 minutes
    
    print("=" * 80)
    print("BATCH VALIDATION MODE")
    print("=" * 80)
    print(f"Batch size: {batch_size} countries")
    print(f"Rate limit: {rate_limit} requests/second")
    print(f"Max runtime: {max_runtime_seconds // 60} minutes")
    print("")
    
    # Initialize coordinators
    coordinator = BatchCoordinator(db_path)
    issue_manager = GitHubIssueManager()
    
    # Get or create cycle
    cycle_id = coordinator.get_or_create_cycle(github_issue)
    print(f"Cycle ID: {cycle_id}")
    
    # Handle GitHub issue
    if create_issue and not github_issue:
        print("Creating GitHub issue to track progress...")
        github_issue = issue_manager.create_validation_issue(cycle_id)
        if github_issue:
            print(f"✓ Created issue #{github_issue}")
            # Update cycle with issue number
            coordinator.get_or_create_cycle(github_issue)
        else:
            print("⚠️  Could not create GitHub issue (gh CLI may not be available)")
    elif github_issue:
        print(f"Tracking progress in issue #{github_issue}")
    
    # Get initial progress
    progress = coordinator.get_cycle_progress(cycle_id)
    print("")
    print_progress(progress)
    
    if progress["is_complete"]:
        print("")
        print("✓ Cycle is already complete!")
        if github_issue:
            issue_manager.close_validation_issue(
                github_issue,
                cycle_id,
                progress["total"],
                progress["completed"],
                progress["failed"],
            )
        return
    
    # Get next batch
    countries = coordinator.get_next_batch(cycle_id, batch_size)
    
    if not countries:
        print("")
        print("No pending countries to process in this batch.")
        return
    
    print("")
    print(f"Processing batch: {', '.join(countries)}")
    print("")
    
    # Mark as processing
    coordinator.mark_batch_processing(cycle_id, countries)
    
    # Process each country with timeout check
    completed_countries = []
    stopped_early = False
    
    for country_code in countries:
        # Check if we're approaching timeout
        elapsed = time.time() - start_time
        remaining = max_runtime_seconds - elapsed
        
        if remaining < 300:  # Less than 5 minutes remaining
            print("")
            print("⏱️  Approaching timeout limit - stopping batch processing")
            print(f"   Elapsed: {elapsed / 60:.1f} minutes")
            print(f"   Remaining countries will be processed in next run")
            stopped_early = True
            
            # Mark unprocessed countries as pending again
            unprocessed = [c for c in countries if c not in completed_countries]
            for country in unprocessed:
                coordinator.mark_batch_pending(cycle_id, country)
            break
        
        try:
            toon_file = toon_dir / f"{country_code_to_filename(country_code)}.toon"
            
            if not toon_file.exists():
                print(f"⚠️  Skipping {country_code}: TOON file not found")
                coordinator.mark_batch_failed(
                    cycle_id,
                    country_code,
                    "TOON file not found"
                )
                continue
            
            print(f"\n{'=' * 80}")
            print(f"Processing: {country_code}")
            print(f"Elapsed time: {elapsed / 60:.1f} minutes, Remaining: {remaining / 60:.1f} minutes")
            print('=' * 80)
            
            stats = asyncio.run(
                scanner.scan_country(
                    country_code,
                    toon_file,
                    rate_limit_per_second=rate_limit,
                )
            )
            
            print_country_stats(stats)
            
            # Mark as completed
            coordinator.mark_batch_completed(cycle_id, [country_code])
            completed_countries.append(country_code)
            
        except Exception as e:
            print(f"❌ Error processing {country_code}: {e}")
            coordinator.mark_batch_failed(cycle_id, country_code, str(e))
    
    # Get final progress
    progress = coordinator.get_cycle_progress(cycle_id)
    
    print("")
    print("=" * 80)
    if stopped_early:
        print("BATCH STOPPED EARLY (TIMEOUT PREVENTION)")
    else:
        print("BATCH COMPLETE")
    print("=" * 80)
    print_progress(progress)
    
    if stopped_early:
        print("")
        print("⚠️  Batch processing stopped early to avoid GitHub Actions timeout")
        print("   The next scheduled run will continue with remaining countries")
    
    # Update GitHub issue
    if github_issue:
        issue_manager.update_issue_progress(
            github_issue,
            cycle_id,
            progress["total"],
            progress["completed"],
            progress["processing"],
            progress["pending"],
            progress["failed"],
        )
        
        # Close issue if cycle is complete
        if progress["is_complete"]:
            print("")
            print(f"✓ Closing GitHub issue #{github_issue} (cycle complete)")
            issue_manager.close_validation_issue(
                github_issue,
                cycle_id,
                progress["total"],
                progress["completed"],
                progress["failed"],
            )


def print_progress(progress: dict):
    """Print progress statistics."""
    total = progress["total"]
    completed = progress["completed"]
    pending = progress["pending"]
    processing = progress["processing"]
    failed = progress["failed"]
    
    pct = (completed / total * 100) if total > 0 else 0
    
    print(f"Progress: {completed}/{total} ({pct:.1f}%)")
    print(f"  Completed: {completed}")
    print(f"  Processing: {processing}")
    print(f"  Pending: {pending}")
    print(f"  Failed: {failed}")


def print_country_stats(stats: dict):
    """Print statistics for a single country."""
    print("")
    print(f"Scan ID: {stats['scan_id']}")
    print(f"Total URLs: {stats['total_urls']}")
    print(f"Validated: {stats['urls_validated']}")
    print(f"Skipped: {stats['urls_skipped']}")
    print(f"Valid: {stats['valid_urls']}")
    print(f"Invalid: {stats['invalid_urls']}")
    print(f"Redirected: {stats['redirected_urls']}")
    print(f"Removed: {stats['urls_removed']}")


def print_summary(all_stats: list[dict]):
    """Print summary for all countries."""
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    for country_stats in all_stats:
        if "error" in country_stats:
            print(f"{country_stats['country_code']}: ERROR - {country_stats['error']}")
        else:
            print(
                f"{country_stats['country_code']}: "
                f"{country_stats['valid_urls']} valid, "
                f"{country_stats['invalid_urls']} invalid, "
                f"{country_stats['urls_removed']} removed"
            )


if __name__ == "__main__":
    main()
