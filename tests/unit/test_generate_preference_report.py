"""Unit tests for the user-preferences report generator."""

from __future__ import annotations

import csv
import io
import json
import sqlite3
from pathlib import Path

import pytest
import yaml

from src.cli.generate_preference_report import generate_preference_report
from src.storage.schema import initialize_schema

_MARKER_START = "<!-- USER_PREFERENCES_STATS_START -->"
_MARKER_END = "<!-- USER_PREFERENCES_STATS_END -->"

_PAGE_TEMPLATE = f"""---
title: Browser User Preferences
layout: page
---

Intro text before the block.

{_MARKER_START}

stale content that must be replaced

{_MARKER_END}

Footer text after the block.
"""


def _insert(
    conn,
    *,
    url: str,
    country: str = "ESTONIA",
    scan_id: str,
    reachable: int = 1,
    features: list[str] | None = None,
    feature_sources: dict | None = None,
    override_signals: list[str] | None = None,
    design_systems: list[str] | None = None,
    checked: int = 0,
    total: int = 0,
    error: str | None = None,
    scanned_at: str = "2026-10-01T00:00:00+00:00",
) -> None:
    """Insert one scan result row."""
    conn.execute(
        """
        INSERT INTO url_preference_results
        (url, country_code, scan_id, is_reachable, meta_color_scheme,
         features, feature_sources, theme_toggle_hints, override_signals,
         design_systems, stylesheets_checked, stylesheets_total,
         error_message, scanned_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, '[]', ?, ?, ?, ?, ?, ?)
        """,
        (
            url,
            country,
            scan_id,
            reachable,
            None,
            json.dumps(features or []),
            json.dumps(feature_sources or {}),
            json.dumps(override_signals or []),
            json.dumps(design_systems or []),
            checked,
            total,
            error,
            scanned_at,
        ),
    )


def _make_db(tmp_path: Path) -> Path:
    """Create a database with multi-batch rows exercising every aggregate."""
    db_path = initialize_schema(f"sqlite:///{tmp_path / 'metadata.db'}")
    conn = sqlite3.connect(db_path)
    try:
        # URL A: signal in scan 1, a second signal only in scan 2.
        _insert(
            conn,
            url="https://a.example.gov/",
            scan_id="preference-1",
            features=["prefers-color-scheme"],
            feature_sources={"prefers-color-scheme": {"html": 1}},
            checked=1,
            total=2,
            scanned_at="2026-10-01T00:00:00+00:00",
        )
        _insert(
            conn,
            url="https://a.example.gov/",
            scan_id="preference-2",
            features=["forced-colors"],
            feature_sources={"forced-colors": {"first_party_css": 3}},
            checked=2,
            total=2,
            scanned_at="2026-10-08T00:00:00+00:00",
        )
        # URL B: reachable, override risk, design-system adoption, no features.
        _insert(
            conn,
            url="https://b.example.gov/",
            scan_id="preference-1",
            features=[],
            override_signals=["forced-color-adjust: none"],
            design_systems=["Example Design System"],
            checked=1,
            total=1,
            scanned_at="2026-10-01T00:00:00+00:00",
        )
        # URL C: unreachable.
        _insert(
            conn,
            url="https://dead.example.gov/",
            scan_id="preference-1",
            reachable=0,
            error="Connection error: refused",
            scanned_at="2026-10-01T00:00:00+00:00",
        )
        conn.commit()
    finally:
        conn.close()
    return db_path


def _make_registry(tmp_path: Path) -> Path:
    """Write a one-entry design-system registry for adoption matching."""
    path = tmp_path / "design-systems.yaml"
    path.write_text(
        yaml.safe_dump({
            "design_systems": [{
                "name": "Example Design System",
                "country_code": "ESTONIA",
                "type": "design_system",
                "scope": "national",
                "url": "https://example.gov/design",
                "adoption_signatures": ["example-ds"],
                "confidence": "high",
                "needs_review": False,
            }, {
                "name": "Uncurated System",
                "country_code": "LATVIA",
                "type": "design_system",
                "scope": "national",
                "url": "https://lv.example/",
                "adoption_signatures": [],
                "confidence": "medium",
                "needs_review": True,
            }]
        }),
        encoding="utf-8",
    )
    return path


def _generate(tmp_path: Path, with_markers: bool = True, db_exists: bool = True):
    """Run the generator against temp inputs; return (ok, page, data, csv)."""
    db_path = _make_db(tmp_path) if db_exists else tmp_path / "missing.db"
    page_path = tmp_path / "user-preferences.md"
    page_path.write_text(_PAGE_TEMPLATE if with_markers else "no markers here", "utf-8")
    data_path = tmp_path / "user-preferences-data.json"
    csv_path = tmp_path / "user-preferences-data.csv"

    ok = generate_preference_report(
        db_path, page_path, data_path, csv_path,
        toon_seeds_dir=None, registry_path=_make_registry(tmp_path),
    )
    return ok, page_path, data_path, csv_path


class TestPageUpdate:
    """Marker injection into the Markdown page."""

    def test_success_replaces_stale_block(self, tmp_path: Path) -> None:
        ok, page_path, _, _ = _generate(tmp_path)
        content = page_path.read_text(encoding="utf-8")

        assert ok is True
        assert "stale content that must be replaced" not in content
        assert content.startswith("---")  # front matter untouched
        assert "Footer text after the block." in content  # text after END untouched
        assert content.count(_MARKER_START) == 1
        assert content.count(_MARKER_END) == 1

    def test_stats_block_reports_headline_counts(self, tmp_path: Path) -> None:
        _, page_path, _, _ = _generate(tmp_path)
        content = page_path.read_text(encoding="utf-8")

        # 3 scanned, 2 reachable, 2 CSS-checked, 1 signal page (URL A only:
        # URL B carries an override risk but no positive feature), 1 override.
        assert "**3** pages scanned" in content
        assert "**2** of **3** scanned pages were reachable" in content
        assert "**2** of **2** reachable pages had at least one stylesheet checked" in content
        assert "**1** of **2** reachable pages show at least one user-preference signal" in content
        assert "(`forced-color-adjust: none`)" in content

    def test_feature_table_lists_detection_counts(self, tmp_path: Path) -> None:
        _, page_path, _, _ = _generate(tmp_path)
        content = page_path.read_text(encoding="utf-8")

        assert "`prefers-color-scheme`" in content
        assert "`forced-colors`" in content
        # URL A shows prefers-color-scheme across its two scan batches.
        assert "| Dark/light colour scheme (`prefers-color-scheme`) | 1 |" in content

    def test_design_system_table_includes_adoption_and_gaps(self, tmp_path: Path) -> None:
        _, page_path, _, _ = _generate(tmp_path)
        content = page_path.read_text(encoding="utf-8")

        assert "Example Design System" in content
        assert "Uncurated System" in content
        assert "not curated" in content
        assert "1 |" in content  # one page matched the example system

    def test_missing_markers_returns_false(self, tmp_path: Path) -> None:
        ok, page_path, data_path, _ = _generate(tmp_path, with_markers=False)

        assert ok is False
        assert page_path.read_text(encoding="utf-8") == "no markers here"
        # Data files are still written so the artifacts stay available.
        assert data_path.exists()

    def test_missing_database_yields_empty_state(self, tmp_path: Path) -> None:
        ok, page_path, data_path, _ = _generate(tmp_path, db_exists=False)
        content = page_path.read_text(encoding="utf-8")

        assert ok is True
        assert "_No scan data yet" in content
        payload = json.loads(data_path.read_text(encoding="utf-8"))
        assert payload["summary"]["total_scanned"] == 0
        assert payload["by_url"] == []


class TestDataAggregates:
    """JSON aggregates must be recomputable from the by_url array."""

    @pytest.fixture()
    def payload(self, tmp_path: Path) -> dict:
        _, _, data_path, _ = _generate(tmp_path)
        return json.loads(data_path.read_text(encoding="utf-8"))

    def test_summary_matches_by_url_recomputation(self, payload: dict) -> None:
        rows = payload["by_url"]
        summary = payload["summary"]

        assert summary["total_scanned"] == len(rows)
        assert summary["total_reachable"] == sum(1 for r in rows if r["is_reachable"])
        assert summary["total_with_signals"] == sum(1 for r in rows if r["features"])
        assert summary["total_css_checked"] == sum(
            1 for r in rows if r["stylesheets_checked"] > 0
        )
        assert summary["total_with_override_risk"] == sum(
            1 for r in rows if r["override_signals"]
        )
        assert summary["total_with_design_system"] == sum(
            1 for r in rows if r["design_systems"]
        )

    def test_feature_counts_recompute_from_by_url(self, payload: dict) -> None:
        recomputed: dict[str, int] = {}
        for row in payload["by_url"]:
            for feature in row["features"]:
                recomputed[feature] = recomputed.get(feature, 0) + 1

        assert payload["summary"]["feature_counts"] == recomputed
        assert recomputed["prefers-color-scheme"] == 1
        assert recomputed["forced-colors"] == 1

    def test_multi_batch_merge_unions_signals(self, payload: dict) -> None:
        """URL A must show both signals across its two scan batches."""
        url_a = next(r for r in payload["by_url"] if r["url"].endswith("a.example.gov/"))
        assert sorted(url_a["features"]) == ["forced-colors", "prefers-color-scheme"]
        assert url_a["stylesheets_checked"] == 2  # max, not sum
        assert url_a["last_scanned"] == "2026-10-08T00:00:00+00:00"

    def test_by_country_aggregates(self, payload: dict) -> None:
        estonia = next(
            r for r in payload["by_country"] if r["country_code"] == "ESTONIA"
        )
        assert estonia["total_scanned"] == 3
        assert estonia["total_reachable"] == 2
        # Only URL A carries positive preference features; URL B has an
        # override risk without any positive signal.
        assert estonia["total_with_signals"] == 1
        assert estonia["total_with_override_risk"] == 1

    def test_registry_coverage_is_published(self, payload: dict) -> None:
        coverage = payload["design_system_registry"]["coverage"]
        assert coverage["total"] == 2
        assert coverage["with_adoption_signatures"] == 1
        assert coverage["needs_review"] == 1

        entries = {e["name"]: e for e in payload["design_system_registry"]["entries"]}
        assert entries["Example Design System"]["pages_matched"] == 1
        assert entries["Uncurated System"]["pages_matched"] == 0


class TestCsvOutput:
    """The CSV mirrors by_url with per-signal boolean columns."""

    @pytest.fixture()
    def rows(self, tmp_path: Path) -> list[dict]:
        _, _, _, csv_path = _generate(tmp_path)
        raw = csv_path.read_bytes()
        assert raw.startswith(b"\xef\xbb\xbf"), "CSV must carry a UTF-8 BOM"
        text = raw.decode("utf-8-sig")
        return list(csv.DictReader(io.StringIO(text)))

    def test_one_row_per_url(self, rows: list[dict]) -> None:
        assert len(rows) == 3

    def test_boolean_columns_support_recomputation(self, rows: list[dict]) -> None:
        row_a = next(r for r in rows if r["url"].endswith("a.example.gov/"))
        assert row_a["prefers-color-scheme"] == "1"
        assert row_a["forced-colors"] == "1"
        assert row_a["forced-color-adjust-none"] == "0"

        row_b = next(r for r in rows if r["url"].endswith("b.example.gov/"))
        assert row_b["forced-color-adjust-none"] == "1"
        assert row_b["design_systems"] == "Example Design System"
        assert row_b["prefers-color-scheme"] == "0"

    def test_signal_total_matches_json_summary(self, rows: list[dict]) -> None:
        feature = "prefers-color-scheme"
        csv_total = sum(int(r[feature]) for r in rows)
        assert csv_total == 1
