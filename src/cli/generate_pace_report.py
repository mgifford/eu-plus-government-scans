"""CLI tool to report whether each scanner is on pace for its target cycle.

Pulled forward from WORKFLOW_ORCHESTRATION_AUDIT.md's Phase 5 (capacity-based
orchestration) because it's independently useful before Phases 2-4 land: it
reads whatever scan data currently exists in metadata.db and reports ahead/
on_pace/marginal/behind/no_data per scanner, using the same eligible-URLs /
effective-daily-throughput / projected-cycle-days formulas as the audit's
Section 4.

Usage:
    python3 -m src.cli.generate_pace_report --db data/metadata.db

Typically run against a metadata.db downloaded from the shared
validation-metadata artifact (see the "Download previous metadata DB" steps
already present in every scan-*.yml workflow) or from local Lighthouse/
relationship-specific metadata artifacts, since coverage is scanner-specific.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from src.services.cycle_pace_tracker import SCANNER_CONFIGS, PaceStatus, compute_pace_status

_STATUS_LABELS = {
    "ahead": "🟢 Ahead",
    "on_pace": "🟢 On pace",
    "marginal": "🟡 Marginal",
    "behind": "🔴 Behind",
    "no_data": "⚪ No data",
}


def _format_days(value: float | None) -> str:
    if value is None:
        return "—"
    return f"{value:,.1f}"


def render_markdown_table(statuses: list[PaceStatus]) -> str:
    """Just the table rows (header + data), no title or footnote -- meant to
    be composed with other invocations covering different scanners/DBs, e.g.
    when Lighthouse's metadata lives in a separate artifact from every other
    scanner's shared validation-metadata DB."""
    lines = [
        "| Scanner | Target cycle | Eligible URLs | Covered (window) | Daily throughput | Projected cycle | Status |",
        "|---|---|---|---|---|---|---|",
    ]
    for s in statuses:
        lines.append(
            f"| {s.scanner} | {s.target_cycle_days}d | {s.eligible_urls:,} | "
            f"{s.urls_scanned_in_window:,} (last {s.window_days}d) | "
            f"{s.effective_daily_throughput:,.1f}/day | "
            f"{_format_days(s.projected_cycle_days)}d | "
            f"{_STATUS_LABELS.get(s.status, s.status)} |"
        )
    return "\n".join(lines)


def render_markdown(statuses: list[PaceStatus]) -> str:
    window = statuses[0].window_days if statuses else 7
    lines = [
        "# Scanner Cycle Pace Report",
        "",
        render_markdown_table(statuses),
        "",
        f"_Projection method: `effective daily throughput = distinct URLs scanned in the "
        f"last {window} days ÷ {window}`; `projected cycle days = eligible URLs ÷ effective "
        f"daily throughput`. The {window}-day measurement window reflects recent scan "
        f"velocity and is independent of each scanner's own target cycle length -- see "
        f"src/services/cycle_pace_tracker.py's module docstring for why. "
        f"'No data' means the scanner has no rows in this metadata.db within its window "
        f"(never run against this database, or the database doesn't cover this scanner)._",
    ]
    return "\n".join(lines)


def render_console(statuses: list[PaceStatus]) -> str:
    lines = []
    name_width = max(len(s.scanner) for s in statuses) if statuses else 8
    header = (
        f"{'SCANNER':<{name_width}}  {'TARGET':>8}  {'ELIGIBLE':>10}  "
        f"{'SCANNED':>10}  {'DAILY':>10}  {'PROJECTED':>11}  STATUS"
    )
    lines.append(header)
    lines.append("-" * len(header))
    for s in statuses:
        lines.append(
            f"{s.scanner:<{name_width}}  {s.target_cycle_days:>6}d  "
            f"{s.eligible_urls:>10,}  {s.urls_scanned_in_window:>10,}  "
            f"{s.effective_daily_throughput:>10,.1f}  "
            f"{_format_days(s.projected_cycle_days):>10}d  "
            f"{_STATUS_LABELS.get(s.status, s.status)}"
        )
    return "\n".join(lines)


def parse_args(args: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Report whether each scanner is on pace to complete its target "
            "scan cycle, based on distinct URLs scanned in metadata.db "
            "within each scanner's own cycle window."
        )
    )
    parser.add_argument(
        "--db",
        type=Path,
        default=Path("data/metadata.db"),
        help="Path to the metadata SQLite database (default: data/metadata.db)",
    )
    parser.add_argument(
        "--seeds-dir",
        type=Path,
        default=Path("data/toon-seeds/countries"),
        help="Directory of country TOON seed files (default: data/toon-seeds/countries)",
        dest="toon_dir",
    )
    parser.add_argument(
        "--measurement-window-days",
        type=int,
        default=7,
        help=(
            "How many recent days of scan activity to measure current "
            "throughput from (default: 7). Deliberately independent of each "
            "scanner's own target cycle length -- see "
            "src/services/cycle_pace_tracker.py's module docstring for why."
        ),
    )
    parser.add_argument(
        "--scanner",
        action="append",
        dest="scanners",
        help=(
            "Restrict to one scanner (repeatable). Default: all configured "
            "scanners. Valid names: " + ", ".join(c.name for c in SCANNER_CONFIGS)
        ),
    )
    parser.add_argument(
        "--format",
        choices=["console", "markdown"],
        default="console",
        help="Output format (default: console)",
    )
    parser.add_argument(
        "--table-only",
        action="store_true",
        help=(
            "With --format markdown, emit just the table rows (no title or "
            "footnote). Meant for composing multiple invocations that cover "
            "different scanners/databases, e.g. Lighthouse's separate "
            "metadata artifact -- append the outputs together for one "
            "combined report instead of duplicating the title/footnote."
        ),
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Write output to this file instead of stdout",
    )
    parser.add_argument(
        "--fail-on-behind",
        action="store_true",
        help=(
            "Exit with a non-zero status if any evaluated scanner is "
            "classified 'behind'. Useful for a scheduled CI check that "
            "should visibly fail rather than silently report."
        ),
    )
    return parser.parse_args(args)


def main(args: list[str] | None = None) -> int:
    parsed = parse_args(args)

    configs = SCANNER_CONFIGS
    if parsed.scanners:
        by_name = {c.name: c for c in SCANNER_CONFIGS}
        unknown = [name for name in parsed.scanners if name not in by_name]
        if unknown:
            print(
                f"Error: unknown scanner(s) {unknown}. "
                f"Valid: {sorted(by_name)}",
                file=sys.stderr,
            )
            return 2
        configs = tuple(by_name[name] for name in parsed.scanners)

    statuses = compute_pace_status(
        parsed.db,
        parsed.toon_dir,
        configs=configs,
        measurement_window_days=parsed.measurement_window_days,
    )

    if not parsed.db.exists():
        print(
            f"Warning: {parsed.db} does not exist -- all scanners will show "
            f"'no_data'. Download the relevant metadata artifact first.",
            file=sys.stderr,
        )

    if parsed.format == "markdown":
        output = render_markdown_table(statuses) if parsed.table_only else render_markdown(statuses)
    else:
        output = render_console(statuses)

    if parsed.output:
        parsed.output.parent.mkdir(parents=True, exist_ok=True)
        parsed.output.write_text(output + "\n", encoding="utf-8")
        print(f"Wrote pace report to {parsed.output}")
    else:
        print(output)

    if parsed.fail_on_behind and any(s.status == "behind" for s in statuses):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
