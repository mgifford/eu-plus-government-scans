"""CLI entry point for URL validation scanner."""

from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

from src.jobs.url_validation_scanner import UrlValidationScanner
from src.lib.settings import load_settings


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Validate URLs in government TOON files"
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
        help="Maximum requests per second",
        type=float,
        default=2.0,
    )
    parser.add_argument(
        "--all",
        help="Scan all countries",
        action="store_true",
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if not args.all and not args.country:
        print("Error: Must specify either --country or --all")
        parser.print_help()
        sys.exit(1)
    
    if not args.toon_dir.exists():
        print(f"Error: TOON directory not found: {args.toon_dir}")
        sys.exit(1)
    
    # Load settings
    settings = load_settings()
    scanner = UrlValidationScanner(settings)
    
    # Run scan
    try:
        if args.all:
            print("Scanning all countries...")
            stats = asyncio.run(
                scanner.scan_all_countries(
                    args.toon_dir,
                    rate_limit_per_second=args.rate_limit,
                )
            )
            
            print("\n" + "=" * 80)
            print("SUMMARY")
            print("=" * 80)
            for country_stats in stats:
                if "error" in country_stats:
                    print(f"{country_stats['country_code']}: ERROR - {country_stats['error']}")
                else:
                    print(
                        f"{country_stats['country_code']}: "
                        f"{country_stats['valid_urls']} valid, "
                        f"{country_stats['invalid_urls']} invalid, "
                        f"{country_stats['urls_removed']} removed"
                    )
        else:
            # Scan specific country
            country_code = args.country.upper()
            toon_file = args.toon_dir / f"{args.country.lower().replace('_', '-')}.toon"
            
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
            
            print("\n" + "=" * 80)
            print("SCAN COMPLETE")
            print("=" * 80)
            print(f"Scan ID: {stats['scan_id']}")
            print(f"Total URLs: {stats['total_urls']}")
            print(f"Validated: {stats['urls_validated']}")
            print(f"Skipped: {stats['urls_skipped']}")
            print(f"Valid: {stats['valid_urls']}")
            print(f"Invalid: {stats['invalid_urls']}")
            print(f"Redirected: {stats['redirected_urls']}")
            print(f"Removed: {stats['urls_removed']}")
            print(f"Output: {stats['output_path']}")
    
    except KeyboardInterrupt:
        print("\nScan interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
