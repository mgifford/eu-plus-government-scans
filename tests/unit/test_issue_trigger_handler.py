"""Tests for the schedule-aware IssueTriggerHandler."""

from __future__ import annotations

import sqlite3
import tempfile
from datetime import datetime, timezone, timedelta
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from src.services.issue_trigger_handler import (
    IssueTriggerHandler,
    TriggerConfig,
    TRIGGER_CONFIGS,
)
from src.storage.schema import initialize_schema


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def temp_db():
    """Temporary SQLite database with schema applied."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = Path(f.name)
    initialize_schema(f"sqlite:///{db_path}")
    yield db_path
    db_path.unlink(missing_ok=True)


@pytest.fixture
def handler(temp_db):
    """IssueTriggerHandler wired to a temporary database."""
    scanner = MagicMock()
    issue_manager = MagicMock()
    return IssueTriggerHandler(scanner, issue_manager, temp_db)


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------


def _insert_completed_run(db_path: Path, issue_number: int, prefix: str, completed_at: datetime):
    """Insert a completed trigger run directly into the database."""
    started_at = (completed_at - timedelta(minutes=5)).isoformat()
    conn = sqlite3.connect(db_path)
    conn.execute(
        """
        INSERT INTO issue_trigger_runs
            (issue_number, trigger_prefix, started_at, completed_at, status)
        VALUES (?, ?, ?, ?, 'completed')
        """,
        (issue_number, prefix, started_at, completed_at.isoformat()),
    )
    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# TriggerConfig sanity checks
# ---------------------------------------------------------------------------


def test_all_trigger_configs_have_prefix():
    for config in TRIGGER_CONFIGS:
        assert config.prefix.endswith(":")


def test_scan_has_no_cooldown():
    scan_cfg = next(c for c in TRIGGER_CONFIGS if c.prefix == "SCAN:")
    assert scan_cfg.cooldown_hours is None
    assert not scan_cfg.is_periodic


def test_weekly_has_6_day_cooldown():
    cfg = next(c for c in TRIGGER_CONFIGS if c.prefix == "WEEKLY:")
    assert cfg.cooldown_hours == 6 * 24
    assert cfg.is_periodic


def test_quarterly_has_85_day_cooldown():
    cfg = next(c for c in TRIGGER_CONFIGS if c.prefix == "QUARTERLY:")
    assert cfg.cooldown_hours == 85 * 24


def test_monday_config():
    cfg = next(c for c in TRIGGER_CONFIGS if c.prefix == "MONDAYS:")
    assert cfg.day_of_week == 0  # Monday
    assert cfg.cooldown_hours == 23


# ---------------------------------------------------------------------------
# is_due_for_run: SCAN prefix
# ---------------------------------------------------------------------------


def test_scan_always_due(handler):
    """SCAN: is always due (no cooldown, no day restriction)."""
    cfg = next(c for c in TRIGGER_CONFIGS if c.prefix == "SCAN:")
    assert handler.is_due_for_run(1, cfg) is True


# ---------------------------------------------------------------------------
# is_due_for_run: periodic without day-of-week restriction
# ---------------------------------------------------------------------------


def test_weekly_due_when_never_run(handler):
    cfg = next(c for c in TRIGGER_CONFIGS if c.prefix == "WEEKLY:")
    assert handler.is_due_for_run(1, cfg) is True


def test_weekly_not_due_when_recently_run(handler, temp_db):
    """WEEKLY: should not run if last completed run was 2 days ago."""
    cfg = next(c for c in TRIGGER_CONFIGS if c.prefix == "WEEKLY:")
    two_days_ago = datetime.now(timezone.utc) - timedelta(days=2)
    _insert_completed_run(temp_db, issue_number=10, prefix="WEEKLY:", completed_at=two_days_ago)

    assert handler.is_due_for_run(10, cfg) is False


def test_weekly_due_after_full_week(handler, temp_db):
    """WEEKLY: should run if last completed run was more than 6 days ago."""
    cfg = next(c for c in TRIGGER_CONFIGS if c.prefix == "WEEKLY:")
    # Use exactly 6 days + 1 hour to be safely past the 6*24 = 144 h cooldown.
    old_run = datetime.now(timezone.utc) - timedelta(days=6, hours=1)
    _insert_completed_run(temp_db, issue_number=10, prefix="WEEKLY:", completed_at=old_run)

    assert handler.is_due_for_run(10, cfg) is True


def test_monthly_not_due_when_run_10_days_ago(handler, temp_db):
    cfg = next(c for c in TRIGGER_CONFIGS if c.prefix == "MONTHLY:")
    ten_days_ago = datetime.now(timezone.utc) - timedelta(days=10)
    _insert_completed_run(temp_db, issue_number=20, prefix="MONTHLY:", completed_at=ten_days_ago)

    assert handler.is_due_for_run(20, cfg) is False


def test_monthly_due_after_28_days(handler, temp_db):
    cfg = next(c for c in TRIGGER_CONFIGS if c.prefix == "MONTHLY:")
    old_run = datetime.now(timezone.utc) - timedelta(days=28, hours=1)
    _insert_completed_run(temp_db, issue_number=20, prefix="MONTHLY:", completed_at=old_run)

    assert handler.is_due_for_run(20, cfg) is True


# ---------------------------------------------------------------------------
# is_due_for_run: day-of-week restriction (injectable `now`)
# ---------------------------------------------------------------------------


def _make_weekday_now(weekday: int) -> datetime:
    """Build a UTC datetime whose weekday() matches the requested value."""
    # Start from a known date and adjust.
    base = datetime(2024, 1, 1, tzinfo=timezone.utc)  # Monday = 0
    offset = (weekday - base.weekday()) % 7
    return base + timedelta(days=offset)


def test_mondays_only_fires_on_monday(handler):
    cfg = next(c for c in TRIGGER_CONFIGS if c.prefix == "MONDAYS:")

    monday = _make_weekday_now(0)  # Monday
    tuesday = _make_weekday_now(1)  # Tuesday

    assert handler.is_due_for_run(30, cfg, now=monday) is True
    assert handler.is_due_for_run(30, cfg, now=tuesday) is False


def test_fridays_only_fires_on_friday(handler):
    cfg = next(c for c in TRIGGER_CONFIGS if c.prefix == "FRIDAYS:")

    friday = _make_weekday_now(4)
    saturday = _make_weekday_now(5)

    assert handler.is_due_for_run(31, cfg, now=friday) is True
    assert handler.is_due_for_run(31, cfg, now=saturday) is False


def test_mondays_respects_cooldown(handler, temp_db):
    """If MONDAYS: ran 2 hours ago (on a Monday), it should not run again."""
    cfg = next(c for c in TRIGGER_CONFIGS if c.prefix == "MONDAYS:")
    two_hours_ago = _make_weekday_now(0) - timedelta(hours=2)
    _insert_completed_run(temp_db, issue_number=40, prefix="MONDAYS:", completed_at=two_hours_ago)

    # Ask on the same Monday, passing `now` explicitly.
    monday_now = _make_weekday_now(0)
    assert handler.is_due_for_run(40, cfg, now=monday_now) is False


def test_mondays_due_after_full_week(handler, temp_db):
    """MONDAYS: should fire again the following Monday."""
    cfg = next(c for c in TRIGGER_CONFIGS if c.prefix == "MONDAYS:")
    # Last run: previous Monday (8 days ago)
    last_monday = _make_weekday_now(0) - timedelta(days=7)
    _insert_completed_run(temp_db, issue_number=40, prefix="MONDAYS:", completed_at=last_monday)

    monday_now = _make_weekday_now(0)
    assert handler.is_due_for_run(40, cfg, now=monday_now) is True


# ---------------------------------------------------------------------------
# _record_run_start / _record_run_complete round-trip
# ---------------------------------------------------------------------------


def test_record_run_start_creates_running_row(handler, temp_db):
    started_at = handler._record_run_start(issue_number=99, prefix="SCAN:")

    conn = sqlite3.connect(temp_db)
    row = conn.execute(
        "SELECT status FROM issue_trigger_runs WHERE issue_number = 99 AND started_at = ?",
        (started_at,),
    ).fetchone()
    conn.close()

    assert row is not None
    assert row[0] == "running"


def test_record_run_complete_updates_status(handler, temp_db):
    started_at = handler._record_run_start(issue_number=99, prefix="SCAN:")
    handler._record_run_complete(issue_number=99, started_at=started_at, status="completed")

    conn = sqlite3.connect(temp_db)
    row = conn.execute(
        "SELECT status, completed_at FROM issue_trigger_runs WHERE issue_number = 99",
    ).fetchone()
    conn.close()

    assert row[0] == "completed"
    assert row[1] is not None


def test_completed_run_is_visible_to_cooldown_check(handler, temp_db):
    """After recording a completed run, is_due_for_run should respect the cooldown."""
    cfg = next(c for c in TRIGGER_CONFIGS if c.prefix == "WEEKLY:")

    # Simulate a run that just finished.
    started_at = handler._record_run_start(issue_number=50, prefix="WEEKLY:")
    handler._record_run_complete(issue_number=50, started_at=started_at, status="completed")

    # Immediately checking should return False (just ran).
    assert handler.is_due_for_run(50, cfg) is False


# ---------------------------------------------------------------------------
# process_trigger_issue: skipping logic
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_process_trigger_issue_skips_when_not_due(handler, temp_db):
    """process_trigger_issue returns skipped=True when cooldown not elapsed."""
    cfg = next(c for c in TRIGGER_CONFIGS if c.prefix == "WEEKLY:")

    # Record a run from 1 day ago so it is NOT yet due.
    one_day_ago = datetime.now(timezone.utc) - timedelta(days=1)
    _insert_completed_run(temp_db, issue_number=100, prefix="WEEKLY:", completed_at=one_day_ago)

    issue = {
        "number": 100,
        "title": "WEEKLY: Validate URL",
        "body": "",
        "trigger_config": cfg,
    }

    result = await handler.process_trigger_issue(issue)

    assert result["success"] is True
    assert result["skipped"] is True
    assert result["closed"] is False


@pytest.mark.asyncio
async def test_process_trigger_issue_unknown_action(handler):
    """process_trigger_issue returns failure for unknown action types."""
    cfg = next(c for c in TRIGGER_CONFIGS if c.prefix == "SCAN:")

    issue = {
        "number": 101,
        "title": "SCAN: Check something unrelated",
        "body": "",
        "trigger_config": cfg,
    }

    result = await handler.process_trigger_issue(issue)

    assert result["success"] is False
    assert "error" in result
