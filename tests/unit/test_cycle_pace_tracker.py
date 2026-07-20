"""Tests for the on-pace capacity tracker (pulled-forward Phase 5 slice of
WORKFLOW_ORCHESTRATION_AUDIT.md).
"""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from src.services.cycle_pace_tracker import (
    ScannerConfig,
    _classify,
    _count_eligible_urls,
    compute_pace_status,
)
from src.storage.schema import SCHEMA_SQL


@pytest.fixture
def db_path(tmp_path: Path) -> Path:
    path = tmp_path / "metadata.db"
    conn = sqlite3.connect(path)
    conn.executescript(SCHEMA_SQL)
    conn.commit()
    conn.close()
    return path


@pytest.fixture
def toon_dir(tmp_path: Path) -> Path:
    d = tmp_path / "countries"
    d.mkdir()
    # 100 pages total across 2 countries -- the "eligible URLs" denominator.
    # Using a round number makes the throughput math easy to verify by hand.
    data_a = {
        "domains": [
            {"canonical_domain": "a.gov", "pages": [{"url": f"https://a.gov/{i}"} for i in range(60)]}
        ]
    }
    data_b = {
        "domains": [
            {"canonical_domain": "b.gov", "pages": [{"url": f"https://b.gov/{i}"} for i in range(40)]}
        ]
    }
    (d / "alpha.toon").write_text(json.dumps(data_a), encoding="utf-8")
    (d / "beta.toon").write_text(json.dumps(data_b), encoding="utf-8")
    return d


def _insert_tech_results(db_path: Path, urls: list[str], scanned_at: datetime, country="ALPHA"):
    conn = sqlite3.connect(db_path)
    for i, url in enumerate(urls):
        conn.execute(
            "INSERT INTO url_tech_results (url, country_code, scan_id, technologies, scanned_at) "
            "VALUES (?, ?, ?, '{}', ?)",
            (url, country, f"scan-{i}", scanned_at.isoformat()),
        )
    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# _classify
# ---------------------------------------------------------------------------


def test_classify_no_data_when_projected_none():
    assert _classify(None, 30) == "no_data"


def test_classify_ahead_when_well_under_target():
    assert _classify(15, 30) == "ahead"  # ratio 0.5


def test_classify_on_pace_at_boundary():
    assert _classify(24, 30) == "on_pace"  # ratio 0.8
    assert _classify(30, 30) == "on_pace"  # ratio 1.0


def test_classify_marginal_slightly_over():
    assert _classify(35, 30) == "marginal"  # ratio ~1.17


def test_classify_behind_well_over_target():
    assert _classify(50, 30) == "behind"  # ratio ~1.67


# ---------------------------------------------------------------------------
# compute_pace_status
# ---------------------------------------------------------------------------


def test_no_data_when_db_missing(tmp_path: Path, toon_dir: Path):
    missing_db = tmp_path / "does-not-exist.db"
    statuses = compute_pace_status(
        missing_db, toon_dir, configs=(ScannerConfig("technology", "url_tech_results", 30),)
    )
    assert len(statuses) == 1
    assert statuses[0].status == "no_data"
    assert statuses[0].eligible_urls == 100  # toon_dir still readable


def test_no_data_when_zero_urls_scanned(db_path: Path, toon_dir: Path):
    statuses = compute_pace_status(
        db_path, toon_dir, configs=(ScannerConfig("technology", "url_tech_results", 30),)
    )
    assert statuses[0].status == "no_data"
    assert statuses[0].urls_scanned_in_window == 0


def test_ahead_when_recent_throughput_would_finish_well_early(db_path: Path, toon_dir: Path):
    now = datetime(2026, 7, 20, tzinfo=timezone.utc)
    # 100 eligible URLs. In the last 7 measurement days, 50 distinct URLs
    # were scanned -> throughput 50/7 ~= 7.14/day -> projected cycle =
    # 100 / 7.14 ~= 14 days. Target is 30 days -> ratio ~0.47 -> ahead.
    urls = [f"https://a.gov/{i}" for i in range(50)]
    _insert_tech_results(db_path, urls, now - timedelta(days=2))

    statuses = compute_pace_status(
        db_path,
        toon_dir,
        configs=(ScannerConfig("technology", "url_tech_results", 30),),
        now=now,
        measurement_window_days=7,
    )
    s = statuses[0]
    assert s.urls_scanned_in_window == 50
    assert s.status == "ahead"
    assert s.projected_cycle_days == pytest.approx(14.0, rel=0.01)


def test_on_pace_when_projected_matches_target(db_path: Path, toon_dir: Path):
    now = datetime(2026, 7, 20, tzinfo=timezone.utc)
    # 100 eligible, 7-day window: need 100/30*7 ~= 23.33 scanned in-window
    # to project exactly a 30-day cycle. Use 23 (slightly under, still
    # rounds into the on_pace band per _classify's 0.8-1.0 threshold isn't
    # violated -- verify the boundary precisely instead with a value chosen
    # to land at ratio ~1.0).
    urls = [f"https://a.gov/{i}" for i in range(23)] + [f"https://b.gov/{i}" for i in range(1)]
    _insert_tech_results(db_path, urls, now - timedelta(days=3))

    statuses = compute_pace_status(
        db_path,
        toon_dir,
        configs=(ScannerConfig("technology", "url_tech_results", 30),),
        now=now,
        measurement_window_days=7,
    )
    s = statuses[0]
    assert s.urls_scanned_in_window == 24
    # throughput = 24/7 ~= 3.43/day; projected = 100/3.43 ~= 29.2 days;
    # ratio ~0.97 -> on_pace.
    assert s.status == "on_pace"


def test_behind_when_recent_throughput_is_too_slow(db_path: Path, toon_dir: Path):
    now = datetime(2026, 7, 20, tzinfo=timezone.utc)
    # 100 eligible, only 3 scanned in the last 7 days -> throughput 3/7 per
    # day -> projected = 100 / (3/7) ~= 233 days, way past a 30-day target.
    urls = [f"https://a.gov/{i}" for i in range(3)]
    _insert_tech_results(db_path, urls, now - timedelta(days=1))

    statuses = compute_pace_status(
        db_path,
        toon_dir,
        configs=(ScannerConfig("technology", "url_tech_results", 30),),
        now=now,
        measurement_window_days=7,
    )
    s = statuses[0]
    assert s.urls_scanned_in_window == 3
    assert s.status == "behind"
    assert s.projected_cycle_days == pytest.approx(233.3, rel=0.01)


def test_urls_outside_measurement_window_are_excluded(db_path: Path, toon_dir: Path):
    now = datetime(2026, 7, 20, tzinfo=timezone.utc)
    # Scanned 8 days ago -- outside a 7-day measurement window, must not count.
    _insert_tech_results(db_path, ["https://a.gov/0"], now - timedelta(days=8))

    statuses = compute_pace_status(
        db_path,
        toon_dir,
        configs=(ScannerConfig("technology", "url_tech_results", 30),),
        now=now,
        measurement_window_days=7,
    )
    assert statuses[0].urls_scanned_in_window == 0
    assert statuses[0].status == "no_data"


def test_duplicate_scans_of_same_url_count_once(db_path: Path, toon_dir: Path):
    now = datetime(2026, 7, 20, tzinfo=timezone.utc)
    conn = sqlite3.connect(db_path)
    # Two rows for the same URL (append-only history, PRIMARY KEY (url, scan_id))
    conn.execute(
        "INSERT INTO url_tech_results (url, country_code, scan_id, technologies, scanned_at) "
        "VALUES (?, 'ALPHA', 'scan-1', '{}', ?)",
        ("https://a.gov/0", (now - timedelta(days=5)).isoformat()),
    )
    conn.execute(
        "INSERT INTO url_tech_results (url, country_code, scan_id, technologies, scanned_at) "
        "VALUES (?, 'ALPHA', 'scan-2', '{}', ?)",
        ("https://a.gov/0", (now - timedelta(days=1)).isoformat()),
    )
    conn.commit()
    conn.close()

    statuses = compute_pace_status(
        db_path,
        toon_dir,
        configs=(ScannerConfig("technology", "url_tech_results", 30),),
        now=now,
        measurement_window_days=7,
    )
    assert statuses[0].urls_scanned_in_window == 1  # DISTINCT url, not 2 rows


def test_missing_table_treated_as_no_data_not_error(tmp_path: Path, toon_dir: Path):
    # An empty (schema-less) DB file -- table genuinely doesn't exist.
    db_path = tmp_path / "empty.db"
    sqlite3.connect(db_path).close()

    statuses = compute_pace_status(
        db_path, toon_dir, configs=(ScannerConfig("technology", "url_tech_results", 30),)
    )
    assert statuses[0].status == "no_data"


def test_evaluates_all_configured_scanners_independently(db_path: Path, toon_dir: Path):
    now = datetime(2026, 7, 20, tzinfo=timezone.utc)
    _insert_tech_results(db_path, ["https://a.gov/0"], now - timedelta(hours=1))
    # No lighthouse rows inserted at all.

    configs = (
        ScannerConfig("technology", "url_tech_results", 30),
        ScannerConfig("lighthouse", "url_lighthouse_results", 60),
    )
    statuses = compute_pace_status(db_path, toon_dir, configs=configs, now=now)

    by_name = {s.scanner: s for s in statuses}
    assert by_name["technology"].urls_scanned_in_window == 1
    assert by_name["lighthouse"].urls_scanned_in_window == 0
    assert by_name["lighthouse"].status == "no_data"
    assert by_name["lighthouse"].target_cycle_days == 60


def test_measurement_window_is_independent_of_target_cycle_days(db_path: Path, toon_dir: Path):
    """Regression guard for the modeling bug found while writing these tests:
    an earlier version measured throughput over target_cycle_days itself,
    which made 'ahead' unreachable once the full corpus had been scanned at
    least once (eligible / (eligible / target) always equals target,
    regardless of how quickly the corpus was actually covered). The
    measurement window must stay fixed (default 7 days) and independent of
    each scanner's own target_cycle_days."""
    now = datetime(2026, 7, 20, tzinfo=timezone.utc)
    # Scan the entire 100-URL corpus within the last 2 days.
    all_urls = [f"https://a.gov/{i}" for i in range(60)] + [f"https://b.gov/{i}" for i in range(40)]
    _insert_tech_results(db_path, all_urls, now - timedelta(days=2))

    statuses = compute_pace_status(
        db_path,
        toon_dir,
        configs=(ScannerConfig("technology", "url_tech_results", 30),),
        now=now,
        measurement_window_days=7,
    )
    s = statuses[0]
    assert s.urls_scanned_in_window == 100
    # throughput = 100/7 ~= 14.3/day; projected = 100/14.3 = 7 days; target
    # 30 days -> ratio ~0.23 -> clearly ahead, correctly distinguishable
    # from "on pace."
    assert s.status == "ahead"
    assert s.projected_cycle_days == pytest.approx(7.0, rel=0.01)


def test_eligible_urls_reads_all_toon_files(toon_dir: Path):
    assert _count_eligible_urls(toon_dir) == 100


def test_eligible_urls_missing_dir_returns_zero(tmp_path: Path):
    assert _count_eligible_urls(tmp_path / "does-not-exist") == 0


def test_pace_ratio_property():
    from src.services.cycle_pace_tracker import PaceStatus

    s = PaceStatus(
        scanner="x",
        target_cycle_days=30,
        eligible_urls=100,
        urls_scanned_in_window=10,
        window_days=7,
        effective_daily_throughput=10 / 7,
        projected_cycle_days=45.0,
        status="marginal",
    )
    assert s.pace_ratio == pytest.approx(1.5)


def test_pace_ratio_none_when_no_data():
    from src.services.cycle_pace_tracker import PaceStatus

    s = PaceStatus(
        scanner="x",
        target_cycle_days=30,
        eligible_urls=100,
        urls_scanned_in_window=0,
        window_days=7,
        effective_daily_throughput=0.0,
        projected_cycle_days=None,
        status="no_data",
    )
    assert s.pace_ratio is None
