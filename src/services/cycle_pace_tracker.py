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

Reads directly from data/metadata.db's per-scanner result tables (each has
a scanned_at column) and from the TOON seed files for the eligible-URL
denominator, rather than estimating from configured rate limits.
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


# Table/target-cycle mapping per scanner. Target days are the values already
# documented in each workflow's CLI defaults and in the audit (Section 1.4/4):
# accessibility=7d freshness window but 30d cycle target; lighthouse and
# relationships are the two scanners explicitly allowed a 60-day cycle per
# the task's own instructions (monthly completion not practical for them).
SCANNER_CONFIGS: tuple[ScannerConfig, ...] = (
    ScannerConfig("accessibility", "url_accessibility_results", 30),
    ScannerConfig("lighthouse", "url_lighthouse_results", 60),
    ScannerConfig("social_media", "url_social_media_results", 30),
    ScannerConfig("technology", "url_tech_results", 30),
    ScannerConfig("third_party_js", "url_third_party_js_results", 30),
    ScannerConfig("overlays", "url_overlay_results", 30),
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
    projected_cycle_days: float | None  # None when zero throughput observed
    status: str  # "ahead" | "on_pace" | "marginal" | "behind" | "no_data"

    @property
    def pace_ratio(self) -> float | None:
        """projected_cycle_days as a fraction of target_cycle_days.

        <0.8 = ahead, 0.8-1.0 = on_pace, 1.0-1.3 = marginal, >1.3 = behind.
        Matches WORKFLOW_ORCHESTRATION_AUDIT.md Section 14.3's thresholds.
        """
        if self.projected_cycle_days is None:
            return None
        return self.projected_cycle_days / self.target_cycle_days


def _classify(projected_days: float | None, target_days: int) -> str:
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


def _count_eligible_urls(toon_dir: Path) -> int:
    """Total page count across every country's TOON seed file.

    Reads each file's own domain_count/page_count-bearing structure rather
    than a possibly-stale index.json (see WORKFLOW_ORCHESTRATION_AUDIT.md
    Section 5's finding that data/toon-seeds/index.json can undercount by
    up to ~1.5%).
    """
    import json

    total = 0
    if not toon_dir.exists():
        return 0
    for toon_path in iter_seed_toon_files(toon_dir):
        try:
            data = json.loads(toon_path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        for domain_entry in data.get("domains", []):
            total += len(domain_entry.get("pages", []))
    return total


def _count_urls_scanned_since(
    conn: sqlite3.Connection, table: str, cutoff_iso: str
) -> int:
    """Distinct URLs with at least one row in `table` scanned since cutoff.

    Uses the same >= scanned_at pattern as each job's own
    _get_recently_scanned_urls() (e.g. src/jobs/tech_scanner.py) rather than
    inventing a different freshness definition.
    """
    try:
        cursor = conn.execute(
            f"SELECT COUNT(DISTINCT url) FROM {table} WHERE scanned_at >= ?",  # noqa: S608
            (cutoff_iso,),
        )
        row = cursor.fetchone()
        return row[0] if row else 0
    except sqlite3.OperationalError:
        # Table doesn't exist yet (e.g. scanner has never run) -- zero data,
        # not an error.
        return 0


DEFAULT_MEASUREMENT_WINDOW_DAYS = 7
"""How far back to look when measuring *current* throughput. Deliberately
much shorter than any scanner's target cycle (30 or 60 days) so the
projection reflects recent velocity rather than "has the whole corpus been
touched at least once during the target window," which cannot distinguish
ahead-of-pace from exactly-on-pace (see module docstring)."""


def compute_pace_status(
    db_path: Path,
    toon_dir: Path,
    configs: tuple[ScannerConfig, ...] = SCANNER_CONFIGS,
    now: datetime | None = None,
    measurement_window_days: int = DEFAULT_MEASUREMENT_WINDOW_DAYS,
) -> list[PaceStatus]:
    """Compute on-pace status for every configured scanner.

    Args:
        db_path: Path to metadata.db (the downloaded validation-metadata
            artifact in CI, or a local copy for ad-hoc inspection).
        toon_dir: Directory of country TOON seed files, for the eligible-URL
            denominator.
        configs: Which scanners to evaluate (defaults to all of them).
        now: Injectable clock for testing; defaults to real UTC now.
        measurement_window_days: How many recent days of scan activity to
            measure throughput from. Independent of each scanner's own
            target_cycle_days -- see module docstring for why.

    Returns:
        One PaceStatus per config, in the same order as `configs`.
    """
    now = now or datetime.now(timezone.utc)
    eligible = _count_eligible_urls(toon_dir)
    cutoff = now - timedelta(days=measurement_window_days)

    results: list[PaceStatus] = []
    conn = sqlite3.connect(db_path) if db_path.exists() else None
    try:
        for config in configs:
            scanned = (
                _count_urls_scanned_since(conn, config.result_table, cutoff.isoformat())
                if conn is not None
                else 0
            )
            effective_daily = scanned / measurement_window_days if measurement_window_days else 0.0

            if scanned <= 0 or eligible <= 0:
                projected_days: float | None = None
            else:
                projected_days = eligible / effective_daily

            results.append(
                PaceStatus(
                    scanner=config.name,
                    target_cycle_days=config.target_cycle_days,
                    eligible_urls=eligible,
                    urls_scanned_in_window=scanned,
                    window_days=measurement_window_days,
                    effective_daily_throughput=effective_daily,
                    projected_cycle_days=projected_days,
                    status=_classify(projected_days, config.target_cycle_days),
                )
            )
    finally:
        if conn is not None:
            conn.close()

    return results
