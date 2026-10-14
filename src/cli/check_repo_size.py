"""Warn when the repository's git history grows too fast or too large.

Committed scan data makes history grow on every bot commit, and history never
shrinks on its own.  A check that only compares against the previous run misses
steady growth: a few megabytes per run never looks alarming, yet adds up to
gigabytes over a few months.  This tool therefore keeps one size reading per
day in a small history file and compares today's size against the reading from
about a week ago, as well as against an absolute ceiling.

The size comes from the GitHub API (``repos/{owner}/{repo}`` ``size`` field, in
KiB), which measures the full server-side history rather than the shallow
checkout a workflow runs in.

Warnings are printed as GitHub Actions ``::warning::`` annotations.  The tool
always exits 0 so a size warning never blocks report publishing.
"""

from __future__ import annotations

import argparse
import sys
from datetime import date, timedelta
from pathlib import Path

DEFAULT_HISTORY = Path("data/repo-size-history.tsv")


def read_history(path: Path) -> dict[str, int]:
    """Read ``YYYY-MM-DD<TAB>KiB`` lines into a date-to-size mapping.

    Args:
        path: History file; a missing file yields an empty mapping.

    Returns:
        Mapping of ISO date string to size in KiB.
    """
    if not path.is_file():
        return {}
    history: dict[str, int] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        parts = line.split("\t")
        if len(parts) == 2 and parts[1].isdigit():
            history[parts[0]] = int(parts[1])
    return history


def write_history(path: Path, history: dict[str, int]) -> None:
    """Write the history mapping back, one line per day in date order."""
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [f"{day}\t{kib}" for day, kib in sorted(history.items())]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def check(
    history: dict[str, int],
    today: date,
    size_kib: int,
    weekly_limit_mb: int,
    ceiling_mb: int,
) -> list[str]:
    """Return warning messages for the given reading; empty when healthy.

    Args:
        history: Earlier daily readings (today's entry, if any, is ignored).
        today: Date of this reading.
        size_kib: Current repository size in KiB.
        weekly_limit_mb: Maximum acceptable growth over about seven days.
        ceiling_mb: Absolute size above which to warn.

    Returns:
        Human-readable warning strings.
    """
    warnings: list[str] = []
    size_mb = size_kib // 1024
    cutoff = (today - timedelta(days=7)).isoformat()
    older = [day for day in history if day <= cutoff]
    if older:
        base_day = max(older)
        growth_mb = (size_kib - history[base_day]) // 1024
        print(f"Growth since {base_day}: ~{growth_mb} MB")
        if growth_mb > weekly_limit_mb:
            warnings.append(
                f"Repository grew ~{growth_mb} MB since {base_day} (limit "
                f"{weekly_limit_mb} MB per week; now ~{size_mb} MB). Find the "
                "path being committed repeatedly with `git rev-list --objects "
                "--all | git cat-file --batch-check`."
            )
    else:
        print("No reading from 7+ days ago yet; weekly check starts once one exists.")
    if size_mb > ceiling_mb:
        warnings.append(
            f"Repository is ~{size_mb} MB, over the {ceiling_mb} MB ceiling."
        )
    return warnings


def main(argv: list[str] | None = None) -> int:
    """Record today's size, print any warnings, and always return 0."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--size-kib", type=int, required=True,
                        help="Current repository size in KiB (GitHub API `size`)")
    parser.add_argument("--history", type=Path, default=DEFAULT_HISTORY,
                        help=f"Daily size history file (default: {DEFAULT_HISTORY})")
    parser.add_argument("--weekly-limit-mb", type=int, default=50)
    parser.add_argument("--ceiling-mb", type=int, required=True)
    parser.add_argument("--today", type=date.fromisoformat, default=date.today(),
                        help="Override today's date (for tests)")
    args = parser.parse_args(argv)

    print(f"Repository size (server-side, full history): ~{args.size_kib // 1024} MB")
    history = read_history(args.history)
    for message in check(history, args.today, args.size_kib,
                         args.weekly_limit_mb, args.ceiling_mb):
        print(f"::warning title=Repository size::{message}")

    # One reading per day keeps the file small and the daily diff to one line.
    key = args.today.isoformat()
    if key not in history:
        history[key] = args.size_kib
        write_history(args.history, history)
    return 0


if __name__ == "__main__":
    sys.exit(main())
