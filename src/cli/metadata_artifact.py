"""CLI for assembling and splitting per-owner metadata artifacts.

Used by the scan workflows either side of a scan:

``merge``
    Combine every downloaded artifact into the local working database before
    scanning, so cross-scanner skip logic sees all results.

``extract``
    Write out just the tables this workflow owns, ready to upload as its own
    artifact.

See :mod:`src.lib.metadata_merge` for why the split exists.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from src.lib.metadata_merge import (
    ARTIFACT_TABLES,
    UnknownArtifactError,
    extract_tables,
    merge_into,
    owned_tables,
)


def _add_merge_parser(subparsers: argparse._SubParsersAction) -> None:
    """Register the ``merge`` subcommand."""
    parser = subparsers.add_parser(
        "merge",
        help="Merge downloaded artifact databases into the working database.",
    )
    parser.add_argument(
        "--into",
        type=Path,
        default=Path("data/metadata.db"),
        help="Working database to merge into (created when absent).",
    )
    parser.add_argument(
        "--from-dir",
        type=Path,
        default=Path("data/artifacts"),
        help=(
            "Directory holding one subdirectory per downloaded artifact, each "
            "containing a metadata.db."
        ),
    )


def _add_extract_parser(subparsers: argparse._SubParsersAction) -> None:
    """Register the ``extract`` subcommand."""
    parser = subparsers.add_parser(
        "extract",
        help="Write out only the tables this workflow owns, for upload.",
    )
    parser.add_argument(
        "--artifact",
        required=True,
        choices=sorted(ARTIFACT_TABLES),
        help="Artifact whose tables should be written out.",
    )
    parser.add_argument(
        "--source",
        type=Path,
        default=Path("data/metadata.db"),
        help="Working database to read from.",
    )
    parser.add_argument(
        "--into",
        type=Path,
        default=Path("data/upload/metadata.db"),
        help="Database to create for upload.",
    )


def parse_args(args: list[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Assemble or split per-owner scan metadata artifacts.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    _add_merge_parser(subparsers)
    _add_extract_parser(subparsers)
    return parser.parse_args(args)


def _run_merge(args: argparse.Namespace) -> int:
    """Merge every artifact database found under ``--from-dir``."""
    sources = sorted(args.from_dir.glob("*/metadata.db"))
    if not sources:
        print(f"No artifact databases under {args.from_dir}; starting fresh.")
        merge_into(args.into, [])
        return 0

    print(f"Merging {len(sources)} artifact database(s) into {args.into}")
    for source in sources:
        print(f"  - {source.parent.name}")

    merged = merge_into(args.into, sources)
    if merged:
        for table, count in sorted(merged.items()):
            print(f"  {table}: +{count} row(s)")
    else:
        print("  no new rows")
    return 0


def _run_extract(args: argparse.Namespace) -> int:
    """Write the artifact's own tables to a standalone database."""
    try:
        tables = owned_tables(args.artifact)
    except UnknownArtifactError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    if not args.source.is_file():
        print(
            f"Error: no working database at {args.source}; refusing to upload "
            "an empty artifact over existing data.",
            file=sys.stderr,
        )
        return 1

    counts = extract_tables(args.source, args.into, tables)
    print(f"Wrote {args.artifact} to {args.into}")
    for table in tables:
        print(f"  {table}: {counts.get(table, 0)} row(s)")
    return 0


def main(args: list[str] | None = None) -> int:
    """Entry point."""
    parsed = parse_args(args)
    if parsed.command == "merge":
        return _run_merge(parsed)
    return _run_extract(parsed)


if __name__ == "__main__":
    raise SystemExit(main())
