"""Computes whether each scanner is on pace to complete its target scan
cycle, using the same method as WORKFLOW_ORCHESTRATION_AUDIT.md Section 4:

    effective daily throughput = distinct URLs scanned in a recent
                                  measurement window / that window's length
    projected cycle days       = eligible URLs / effective daily throughput

The measurement window is deliberately short and fixed (default 7 days),
independent of each scanner's target cycle length. This matters: measuring
throughput over a window as long as the target itself would make "projected
cycle days" collapse to exactly the target whenever the full eligible set
has been covered even once (eligible / (eligible / target) == target,
always) -- which would make "ahead of pace" undetectable by construction.
A short, recent window instead reflects *current velocity*, matching the
audit's own methodology (cron runs/day x observed URLs/run is a rate, not
"did we finish the whole corpus").

Reads directly from data/metadata.db's per-scanner result or state tables
and from the TOON seed files for the eligible-URL denominator, rather than
estimating from configured rate limits.

Most scanners measure recent work using a ``scanned_at`` timestamp.
Relationships is different: it uses ``relationship_scan_state`` and
``last_successful_at`` so attempted but failed page fetches do not count as
completed relationship coverage.
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

from src.lib.country_utils import iter_seed_toon_files


@dataclass(frozen=True, slots=True)
class ScannerConfig:
    """Static configuration for one scanner's pace calculation."""

    name: str
    result_table: str
    target_cycle_days: int
    timestamp_column: str = "scanned_at"


# Table/target-cycle mapping per scanner.
#
# Most scanners have a 30-day cycle target. Lighthouse and Relationships
# are allowed a 60-day cycle because full-corpus completion is significantly
# more expensive.
#
# Relationships is measured from relationship_scan_state.last_successful_at
# rather than relationship_scan_results.scanned_at. This measures successful
# source-page coverage and avoids treating failed fetch attempts as completed
# graph coverage.
SCANNER_CONFIGS: tuple[ScannerConfig, ...] = (
    ScannerConfig(
        "accessibility",
        "url_accessibility_results",
        30,
    ),
    ScannerConfig(
        "lighthouse",
        "url_lighthouse_results",
        60,
    ),
    ScannerConfig(
        "social_media",
        "url_social_media_results",
        30,
    ),
    ScannerConfig(
        "technology",
        "url_tech_results",
        30,
    ),
    ScannerConfig(
        "third_party_js",
        "url_third_party_js_results",
        30,
    ),
    ScannerConfig(
        "overlays",
        "url_overlay_results",
        30,
    ),
    ScannerConfig(
        "relationships",
        "relationship_scan_state",
        60,
        "last_successful_at",
    ),
)


@dataclass(frozen=True, slots=True)
class PaceStatus:
    """On-pace evaluation for a single scanner."""

    scanner: str
    target_cycle_days: int
    eligible_urls: int
    urls_scanned_in_window: int
    window_days: int
    effective_daily_throughput: float
    projected_cycle_days: float | None
    status: str

    @property
    def pace_ratio(self) -> float | None:
        """Return projected cycle length as a fraction of the target cycle.

        Classification thresholds:

        * <0.8 = ahead
        * 0.8-1.0 = on pace
        * 1.0-1.3 = marginal
        * >1.3 = behind

        Matches WORKFLOW_ORCHESTRATION_AUDIT.md Section 14.3.
        """
        if self.projected_cycle_days is None:
            return None

        return (
            self.projected_cycle_days
            / self.target_cycle_days
        )


def _classify(
    projected_days: float | None,
    target_days: int,
) -> str:
    """Classify projected scan-cycle performance."""
    if projected_days is None:
        return "no_data"

    ratio = projected_days / target_days

    if ratio < 0.8:
        return "ahead"

    if ratio <= 1.0:
        return "on_pace"

    if ratio <= 1.3:
        return "marginal"

    return "behind"


def _count_eligible_urls(
    toon_dir: Path,
) -> int:
    """Return total page count across all country TOON seed files.

    Reads each file's own domain/page structure rather than relying on a
    potentially stale aggregate index.
    """
    import json

    total = 0

    if not toon_dir.exists():
        return 0

    for toon_path in iter_seed_toon_files(
        toon_dir
    ):
        try:
            data = json.loads(
                toon_path.read_text(
                    encoding="utf-8"
                )
            )
        except (OSError, ValueError):
            continue

        for domain_entry in data.get(
            "domains",
            [],
        ):
            total += len(
                domain_entry.get(
                    "pages",
                    [],
                )
            )

    return total


def _count_urls_scanned_since(
    conn: sqlite3.Connection,
    table: str,
    timestamp_column: str,
    cutoff_iso: str,
) -> int:
    """Return distinct URLs successfully covered since the cutoff.

    Most scanners use ``scanned_at`` from their result table.

    Relationships uses ``last_successful_at`` from
    ``relationship_scan_state`` so failed attempts do not count as completed
    relationship coverage.

    The table and timestamp column values come only from the static
    ``SCANNER_CONFIGS`` configuration above.
    """
    try:
        cursor = conn.execute(
            f"""
            SELECT COUNT(DISTINCT url)
            FROM {table}
            WHERE {timestamp_column} >= ?
            """,  # noqa: S608
            (cutoff_iso,),
        )

        row = cursor.fetchone()

        return row[0] if row else 0

    except sqlite3.OperationalError:
        # The table may not exist yet if the scanner has never run against
        # this database. Treat that as zero data rather than an error.
        return 0


DEFAULT_MEASUREMENT_WINDOW_DAYS = 7
"""How far back to look when measuring current scanner throughput.

The window is deliberately much shorter than any scanner's target cycle
(30 or 60 days). This ensures the projection reflects recent velocity rather
than merely answering whether the corpus has been touched at least once
during the target interval.
"""


def compute_pace_status(
    db_path: Path,
    toon_dir: Path,
    configs: tuple[
        ScannerConfig,
        ...,
    ] = SCANNER_CONFIGS,
    now: datetime | None = None,
    measurement_window_days: int = (
        DEFAULT_MEASUREMENT_WINDOW_DAYS
    ),
) -> list[PaceStatus]:
    """Compute on-pace status for every configured scanner.

    Args:
        db_path:
            Path to metadata.db.

        toon_dir:
            Directory containing country TOON seed files. These supply the
            eligible source-page denominator.

        configs:
            Scanner configurations to evaluate. Defaults to all configured
            scanners.

        now:
            Injectable clock for testing. Defaults to current UTC time.

        measurement_window_days:
            Number of recent days used to measure current scan throughput.
            This is independent of each scanner's target cycle.

    Returns:
        One ``PaceStatus`` for each scanner configuration, preserving the
        configuration order.
    """
    now = now or datetime.now(
        timezone.utc
    )

    eligible = _count_eligible_urls(
        toon_dir
    )

    cutoff = now - timedelta(
        days=measurement_window_days
    )
    cutoff_iso = cutoff.isoformat()

    results: list[PaceStatus] = []

    conn = (
        sqlite3.connect(db_path)
        if db_path.exists()
        else None
    )

    try:
        for config in configs:
            if conn is not None:
                scanned = (
                    _count_urls_scanned_since(
                        conn,
                        config.result_table,
                        config.timestamp_column,
                        cutoff_iso,
                    )
                )
            else:
                scanned = 0

            effective_daily = (
                scanned
                / measurement_window_days
                if measurement_window_days
                else 0.0
            )

            if (
                scanned <= 0
                or eligible <= 0
                or effective_daily <= 0
            ):
                projected_days: (
                    float | None
                ) = None
            else:
                projected_days = (
                    eligible
                    / effective_daily
                )

            results.append(
                PaceStatus(
                    scanner=config.name,
                    target_cycle_days=(
                        config.target_cycle_days
                    ),
                    eligible_urls=eligible,
                    urls_scanned_in_window=(
                        scanned
                    ),
                    window_days=(
                        measurement_window_days
                    ),
                    effective_daily_throughput=(
                        effective_daily
                    ),
                    projected_cycle_days=(
                        projected_days
                    ),
                    status=_classify(
                        projected_days,
                        config.target_cycle_days,
                    ),
                )
            )

    finally:
        if conn is not None:
            conn.close()

    return results
