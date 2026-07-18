"""CLI entry point for progressive relationship scanning."""

from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

from src.jobs.relationship_scanner_job import RelationshipScannerJob
from src.lib.country_utils import country_code_to_filename
from src.lib.settings import load_settings


def main() -> None:
    """Main CLI entry point for relationship scanning."""
    parser = argparse.ArgumentParser(
        description="Extract and aggregate relationships from government web pages."
    )
    parser.add_argument(
        "--country",
        help="Specific country code to scan (e.g., ICELAND, FRANCE)",
        type=str,
    )
    parser.add_argument(
        "--all",
        help="Scan all countries (progressive, fairness-ordered)",
        action="store_true",
    )
    parser.add_argument(
        "--toon-dir",
        help="Directory containing TOON files",
        type=Path,
        default=Path("data/toon-seeds/countries"),
    )
    parser.add_argument(
        "--rate-limit",
        help="Maximum requests per second (default: 2.0)",
        type=float,
        default=2.0,
    )
    parser.add_argument(
        "--max-runtime",
        help=(
            "Maximum runtime in minutes before stopping gracefully. "
            "0 = no limit (default).  For --all mode in GitHub Actions "
            "set this to ~10 minutes less than the workflow timeout."
        ),
        type=int,
        default=0,
        dest="max_runtime",
    )
    parser.add_argument(
        "--skip-recently-scanned-days",
        help=(
            "Skip URLs successfully scanned within the last N days "
            "(default: 0 = always re-scan).  Set to 28 for a monthly cycle."
        ),
        type=int,
        default=0,
        dest="skip_recently_scanned_days",
    )

    args = parser.parse_args()

    if not args.all and not args.country:
        print("Error: Must specify either --country or --all")
        parser.print_help()
        sys.exit(1)

    if not args.toon_dir.exists():
        print(f"Error: TOON directory not found: {args.toon_dir}")
        sys.exit(1)

    max_runtime_seconds = args.max_runtime * 60 if args.max_runtime > 0 else None

    settings = load_settings()
    job = RelationshipScannerJob(settings)

    try:
        if args.all:
            if max_runtime_seconds is not None:
                print(
                    f"Running relationship scans for all countries "
                    f"(max runtime: {args.max_runtime} minutes)..."
                )
            else:
                print("Running relationship scans for all countries...")

            all_stats = asyncio.run(
                job.scan_all_countries(
                    args.toon_dir,
                    rate_limit_per_second=args.rate_limit,
                    max_runtime_seconds=max_runtime_seconds,
                    skip_recently_scanned_days=args.skip_recently_scanned_days,
                )
            )

            print("\n" + "=" * 80)
            print("RELATIONSHIP SCAN SUMMARY (all countries)")
            print("=" * 80)
            for stats in all_stats:
                if "error" in stats:
                    print(f"{stats.get('country_code', '?')}: ERROR - {stats['error']}")
                else:
                    complete = "" if stats.get("is_complete", True) else " (partial)"
                    print(
                        f"{stats['country_code']}{complete}: "
                        f"{stats['urls_scanned']} scanned, "
                        f"{stats['relationships_extracted']} rel observations, "
                        f"{stats['unique_edges']} unique edges"
                    )
        else:
            country_code = args.country.upper()
            toon_file = args.toon_dir / f"{country_code_to_filename(country_code)}.toon"

            if not toon_file.exists():
                print(
                    f"Error: TOON file not found: {toon_file}\n"
                    f"Expected '{toon_file.name}' in {args.toon_dir}"
                )
                sys.exit(1)

            print(f"Scanning {country_code} for relationships...")
            stats = asyncio.run(
                job.scan_country(
                    country_code,
                    toon_file,
                    rate_limit_per_second=args.rate_limit,
                    max_runtime_seconds=max_runtime_seconds,
                    skip_recently_scanned_days=args.skip_recently_scanned_days,
                )
            )

            print("\n" + "=" * 80)
            print("RELATIONSHIP SCAN COMPLETE")
            print("=" * 80)
            print(f"Scan ID:               {stats['scan_id']}")
            print(f"Total URLs:            {stats['total_urls']}")
            print(f"Scanned:               {stats['urls_scanned']}")
            print(f"Skipped:               {stats['urls_skipped']}")
            print(f"Complete:              {'Yes' if stats.get('is_complete', True) else 'No'}")
            print(f"Relationships Found:   {stats['relationships_extracted']}")
            print(f"Unique Edges:          {stats['unique_edges']}")

    except KeyboardInterrupt:
        print("\nScan interrupted by user")
        sys.exit(1)
    except Exception as exc:
        print(f"Error: {exc}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
