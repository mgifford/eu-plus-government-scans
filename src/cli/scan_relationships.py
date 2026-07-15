"""CLI entry point for relationship scanner."""

from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

from src.jobs.relationship_scanner_job import RelationshipScannerJob
from src.lib.country_utils import country_code_to_filename
from src.lib.settings import load_settings


def main():
    """Main CLI entry point for relationship scanning."""
    parser = argparse.ArgumentParser(
        description="Extract and aggregate relationships from government web pages."
    )
    parser.add_argument(
        "--country",
        help="Specific country code to scan (e.g., ICELAND, FRANCE)",
        type=str,
        required=True,
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
        help="Maximum runtime in minutes before stopping gracefully.",
        type=int,
        default=0,
    )

    args = parser.parse_args()

    if not args.toon_dir.exists():
        print(f"Error: TOON directory not found: {args.toon_dir}")
        sys.exit(1)

    max_runtime_seconds = args.max_runtime * 60 if args.max_runtime > 0 else None

    settings = load_settings()
    job = RelationshipScannerJob(settings)

    country_code = args.country.upper()
    toon_file = args.toon_dir / f"{country_code_to_filename(country_code)}.toon"

    if not toon_file.exists():
        print(
            f"Error: TOON file not found: {toon_file}\n"
            f"Expected a file named '{toon_file.name}' in {args.toon_dir}"
        )
        sys.exit(1)

    print(f"Scanning {country_code} for relationships...")
    try:
        stats = asyncio.run(
            job.scan_country(
                country_code,
                toon_file,
                rate_limit_per_second=args.rate_limit,
                max_runtime_seconds=max_runtime_seconds,
            )
        )

        print("\n" + "=" * 80)
        print("RELATIONSHIP SCAN COMPLETE")
        print("=" * 80)
        print(f"Scan ID:               {stats['scan_id']}")
        print(f"Total URLs:            {stats['total_urls']}")
        print(f"Scanned:               {stats['urls_scanned']}")
        print(f"Complete:              {'Yes' if stats.get('is_complete', True) else 'No'}")
        print(f"Total Relationships:   {stats['relationships_extracted']}")
        print(f"Unique Edges:          {stats['unique_edges']}")
        print(f"Output:                {stats['output_path']}")

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
