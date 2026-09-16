"""Tests for the pace-report CLI."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path

from src.cli.generate_pace_report import (
    main,
    render_console,
    render_markdown,
    render_markdown_table,
)
from src.services.cycle_pace_tracker import PaceStatus, ScannerConfig, compute_pace_status
from src.storage.schema import SCHEMA_SQL


def _make_toon_dir(tmp_path: Path) -> Path:
    d = tmp_path / "countries"
    d.mkdir()
    data = {"domains": [{"canonical_domain": "a.gov", "pages": [{"url": "https://a.gov/x"}]}]}
    (d / "alpha.toon").write_text(json.dumps(data), encoding="utf-8")
    return d


def test_main_with_missing_db_still_reports_no_data(tmp_path: Path, capsys):
    toon_dir = _make_toon_dir(tmp_path)
    exit_code = main(
        [
            "--db",
            str(tmp_path / "nope.db"),
            "--seeds-dir",
            str(toon_dir),
            "--scanner",
            "technology",
        ]
    )
    assert exit_code == 0
    captured = capsys.readouterr()
    assert "technology" in captured.out
    assert "No data" in captured.out


def test_main_rejects_unknown_scanner(tmp_path: Path, capsys):
    toon_dir = _make_toon_dir(tmp_path)
    exit_code = main(
        [
            "--db",
            str(tmp_path / "nope.db"),
            "--seeds-dir",
            str(toon_dir),
            "--scanner",
            "not-a-real-scanner",
        ]
    )
    assert exit_code == 2


def test_main_fail_on_behind_exits_nonzero(tmp_path: Path):
    toon_dir = tmp_path / "countries"
    toon_dir.mkdir()
    data = {
        "domains": [
            {"canonical_domain": "a.gov", "pages": [{"url": f"https://a.gov/{i}"} for i in range(100)]}
        ]
    }
    (toon_dir / "alpha.toon").write_text(json.dumps(data), encoding="utf-8")

    db_path = tmp_path / "metadata.db"
    conn = sqlite3.connect(db_path)
    conn.executescript(SCHEMA_SQL)
    now = datetime.now(timezone.utc)
    # Only 1 of 100 URLs scanned recently -- clearly behind.
    conn.execute(
        "INSERT INTO url_tech_results (url, country_code, scan_id, technologies, scanned_at) "
        "VALUES ('https://a.gov/0', 'ALPHA', 'scan-1', '{}', ?)",
        ((now - timedelta(days=1)).isoformat(),),
    )
    conn.commit()
    conn.close()

    exit_code = main(
        [
            "--db",
            str(db_path),
            "--seeds-dir",
            str(toon_dir),
            "--scanner",
            "technology",
            "--fail-on-behind",
        ]
    )
    assert exit_code == 1


def test_main_writes_to_output_file(tmp_path: Path):
    toon_dir = _make_toon_dir(tmp_path)
    output = tmp_path / "report.md"
    exit_code = main(
        [
            "--db",
            str(tmp_path / "nope.db"),
            "--seeds-dir",
            str(toon_dir),
            "--format",
            "markdown",
            "--output",
            str(output),
        ]
    )
    assert exit_code == 0
    assert output.exists()
    content = output.read_text(encoding="utf-8")
    assert "Scanner Cycle Pace Report" in content


def test_render_markdown_includes_all_scanners(tmp_path: Path):
    toon_dir = _make_toon_dir(tmp_path)
    statuses = compute_pace_status(
        tmp_path / "nope.db", toon_dir, configs=(ScannerConfig("technology", "url_tech_results", 30),)
    )
    md = render_markdown(statuses)
    assert "technology" in md
    assert "|" in md  # is a markdown table


def test_render_console_produces_aligned_output(tmp_path: Path):
    toon_dir = _make_toon_dir(tmp_path)
    statuses = compute_pace_status(
        tmp_path / "nope.db", toon_dir, configs=(ScannerConfig("technology", "url_tech_results", 30),)
    )
    out = render_console(statuses)
    assert "SCANNER" in out
    assert "technology" in out


def _caught_up_status() -> PaceStatus:
    return PaceStatus(
        scanner="accessibility",
        target_cycle_days=30,
        eligible_urls=87696,
        urls_scanned_in_window=0,
        window_days=7,
        effective_daily_throughput=0.0,
        projected_cycle_days=None,
        status="caught_up",
        covered_urls=87412,
        coverage_ratio=0.99676,
    )


def test_markdown_table_has_corpus_covered_column_and_caught_up_label():
    table = render_markdown_table([_caught_up_status()])
    assert "Corpus covered" in table  # new column header
    assert "99.7% (87,412)" in table  # coverage cell
    assert "🟢 Caught up" in table  # caught_up status label


def test_console_shows_coverage_percent():
    out = render_console([_caught_up_status()])
    assert "COVERED%" in out
    assert "99.7%" in out
    assert "Caught up" in out
