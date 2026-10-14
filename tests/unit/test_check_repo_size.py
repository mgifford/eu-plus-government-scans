"""Tests for src/cli/check_repo_size.py."""

from __future__ import annotations

from datetime import date
from pathlib import Path

from src.cli.check_repo_size import check, main, read_history

TODAY = date(2026, 10, 14)


def test_steady_growth_over_a_week_warns() -> None:
    """Small per-run growth that adds up over a week is the case to catch."""
    history = {"2026-10-07": 700 * 1024, "2026-10-10": 740 * 1024}
    warnings = check(history, TODAY, 760 * 1024, weekly_limit_mb=50, ceiling_mb=2000)
    assert len(warnings) == 1
    assert "since 2026-10-07" in warnings[0]


def test_growth_within_limit_is_quiet() -> None:
    history = {"2026-10-07": 700 * 1024}
    assert check(history, TODAY, 720 * 1024, weekly_limit_mb=50, ceiling_mb=2000) == []


def test_no_week_old_reading_skips_weekly_check() -> None:
    """Readings newer than seven days are not a valid weekly baseline."""
    history = {"2026-10-12": 100 * 1024}
    assert check(history, TODAY, 900 * 1024, weekly_limit_mb=50, ceiling_mb=2000) == []


def test_ceiling_warns_without_history() -> None:
    warnings = check({}, TODAY, 1200 * 1024, weekly_limit_mb=50, ceiling_mb=1000)
    assert len(warnings) == 1
    assert "ceiling" in warnings[0]


def test_main_records_one_reading_per_day(tmp_path: Path) -> None:
    """A second run on the same day must not rewrite the file."""
    history = tmp_path / "sizes.tsv"
    args = ["--history", str(history), "--ceiling-mb", "2000", "--today", "2026-10-14"]

    assert main(["--size-kib", "1000", *args]) == 0
    assert main(["--size-kib", "2000", *args]) == 0

    assert read_history(history) == {"2026-10-14": 1000}


def test_main_exits_zero_when_warning(tmp_path: Path, capsys) -> None:
    """A size warning must never fail the report job."""
    history = tmp_path / "sizes.tsv"
    history.write_text("2026-10-01\t1024\n", encoding="utf-8")

    code = main(["--size-kib", str(500 * 1024), "--history", str(history),
                 "--ceiling-mb", "100", "--today", "2026-10-14"])

    assert code == 0
    assert capsys.readouterr().out.count("::warning") == 2
