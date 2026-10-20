"""CLI entry point for the user-preference signal scanner."""

from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

from src.jobs.preference_scanner import PreferenceScannerJob
from src.lib.country_utils import country_code_to_filename
from src.lib.settings import load_settings


def main():
    """Main CLI entry point for user-preference signal scanning."""
    parser = argparse.ArgumentParser(
        description=(
            "Scan government website pages for evidence that they respond to "
            "browser/OS user preferences (prefers-color-scheme, "
            "prefers-reduced-motion, prefers-contrast, forced-colors, the "
            "color-scheme property) as described by EN 301 549 clause 9.7, "
            "and for adoption of curated government design systems. "
            "Signals are evidence of effort, not conformance verdicts."
        )
    )
    parser.add_argument(
        "--country",
        help="Specific country code to scan (e.g., ICELAND, FRANCE)",
        type=str,
    )
    parser.add_argument(
        "--toon-dir",
        help="Directory containing TOON files",
        type=Path,
        default=Path("data/toon-seeds/countries"),
    )
    parser.add_argument(
        "--rate-limit",
        help="Maximum requests per second (default: 1.0 for polite crawling)",
        type=float,
        default=1.0,
    )
    parser.add_argument(
        "--all",
        help="Scan all countries",
        action="store_true",
    )
    parser.add_argument(
        "--max-runtime",
        help=(
            "Maximum runtime in minutes before stopping gracefully. "
            "0 = no limit (default). For --all mode in GitHub Actions set "
            "this to ~10 minutes less than the workflow timeout-minutes value "
            "so the job can finish cleanly and upload its artifacts."
        ),
        type=int,
        default=0,
        dest="max_runtime",
    )
    parser.add_argument(
        "--skip-recently-scanned-days",
        help=(
            "Skip URLs already scanned by this scanner within the last N days "
            "(default: 90 in --all mode, 0 for a single country). Makes repeat "
            "runs progress through the corpus."
        ),
        type=int,
        default=None,
        dest="skip_recently_scanned_days",
    )
    parser.add_argument(
        "--max-urls",
        help="Maximum URLs to scan per country (default: no limit)",
        type=int,
        default=None,
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
    if args.skip_recently_scanned_days is not None:
        skip_days = args.skip_recently_scanned_days
    else:
        skip_days = 90 if args.all else 0

    settings = load_settings()
    job = PreferenceScannerJob(settings)

    try:
        if args.all:
            if max_runtime_seconds is not None:
                print(
                    f"Scanning all countries for user-preference signals "
                    f"(max runtime: {args.max_runtime} minutes)..."
                )
            else:
                print("Scanning all countries for user-preference signals...")
            all_stats = asyncio.run(
                job.scan_all_countries(
                    args.toon_dir,
                    rate_limit_per_second=args.rate_limit,
                    max_runtime_seconds=max_runtime_seconds,
                    skip_recently_scanned_days=skip_days,
                    max_urls=args.max_urls,
                )
            )

            print("\n" + "=" * 80)
            print("USER-PREFERENCE SCAN SUMMARY")
            print("=" * 80)
            for country_stats in all_stats:
                if "error" in country_stats:
                    print(
                        f"{country_stats['country_code']}: "
                        f"ERROR - {country_stats['error']}"
                    )
                else:
                    complete_flag = (
                        "" if country_stats.get("is_complete", True) else " (partial)"
                    )
                    print(
                        f"{country_stats['country_code']}{complete_flag}: "
                        f"{country_stats['urls_scanned']} scanned, "
                        f"{country_stats['urls_with_signals']} with signals, "
                        f"{country_stats['urls_with_override_risk']} with override risk"
                    )
        else:
            country_code = args.country.upper()
            toon_file = args.toon_dir / f"{country_code_to_filename(country_code)}.toon"

            if not toon_file.exists():
                print(
                    f"Error: TOON file not found: {toon_file}\n"
                    f"Expected a file named '{toon_file.name}' in {args.toon_dir}"
                )
                sys.exit(1)

            print(f"Scanning {country_code} for user-preference signals...")
            stats = asyncio.run(
                job.scan_country(
                    country_code,
                    toon_file,
                    rate_limit_per_second=args.rate_limit,
                    max_runtime_seconds=max_runtime_seconds,
                    skip_recently_scanned_days=skip_days,
                    max_urls=args.max_urls,
                )
            )

            print("\n" + "=" * 80)
            print("USER-PREFERENCE SCAN COMPLETE")
            print("=" * 80)
            print(f"Scan ID:                  {stats['scan_id']}")
            print(f"Total URLs:               {stats['total_urls']}")
            print(f"Skipped (recent):         {stats['urls_skipped_recent']}")
            print(f"Scanned:                  {stats['urls_scanned']}")
            print(
                f"Complete:                 "
                f"{'Yes' if stats.get('is_complete', True) else 'No (stopped early)'}"
            )
            print(f"Reachable:                {stats['reachable_count']}")
            print(f"With preference signals:  {stats['urls_with_signals']}")
            print(f"With CSS tier checked:    {stats['urls_with_css_checked']}")
            print(f"With override risk:       {stats['urls_with_override_risk']}")
            if stats["feature_counts"]:
                print("Features found:")
                for feature, count in sorted(
                    stats["feature_counts"].items(), key=lambda x: -x[1]
                ):
                    print(f"  {feature}: {count}")
            if stats["adoption_counts"]:
                print("Design-system adoption:")
                for system, count in sorted(
                    stats["adoption_counts"].items(), key=lambda x: -x[1]
                ):
                    print(f"  {system}: {count}")
            else:
                print("No design-system adoption signatures matched.")
            print(f"Output:                   {stats['output_path']}")

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
