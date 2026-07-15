"""CLI for generating classification reports.

Generates classification reports in `docs/data/classification/` for static publishing via GitHub Pages.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from ..services.classification_engine import ClassificationEngine
from ..services.classification_report_generator import ClassificationReportGenerator


def main(args: list[str] | None = None) -> int:
    """Main entry point for the classification report generator."""
    parsed = parse_args(args)

    # Initialize engine
    engine = ClassificationEngine()

    # Initialize report generator
    generator = ClassificationReportGenerator(engine)

    # Output directory
    output_dir = Path(parsed.output_dir)

    if parsed.country:
        # Generate report for a specific country
        generator.save_country_report(parsed.country.upper(), output_dir)
        print(f"Generated report for {parsed.country.upper()} in {output_dir}")
    else:
        # Generate global report
        generator.save_global_report(output_dir)
        print(f"Generated global report in {output_dir}")

    return 0


def parse_args(args: list[str] | None = None) -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate classification reports for static publishing."
    )
    parser.add_argument(
        "--country",
        type=str,
        help="Generate report for a specific country (ISO-3166-1 alpha-2 code)",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="docs/data/classification",
        help="Output directory for reports (default: docs/data/classification)",
    )
    return parser.parse_args(args)


if __name__ == "__main__":
    sys.exit(main())
