"""Tests for the weekly Mastodon digest drafter."""

from __future__ import annotations

import json
import sqlite3
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import pytest

import src.cli.generate_weekly_digest as digest
from src.lib.digest_drafts import extract_draft, post_problems
from src.storage.schema import initialize_schema

WEEK = digest.Week(date(2026, 11, 8))
WEEK_ARGS = ["--week-ending", "2026-11-08"]


@pytest.fixture(autouse=True)
def _small_corpus(monkeypatch: pytest.MonkeyPatch) -> None:
    """Let a handful of fixture pages stand in for a week's re-checks."""
    monkeypatch.setattr(digest, "MIN_PAGES_RECHECKED", 1)


def _db(tmp_path: Path) -> Path:
    path = tmp_path / "metadata.db"
    initialize_schema(f"sqlite:///{path}")
    return path


def _statement(conn: sqlite3.Connection, url: str, country: str, day: str,
               has: bool, links: list[str] | None = None, reachable: bool = True) -> None:
    conn.execute(
        "INSERT INTO url_accessibility_results (url, country_code, scan_id, is_reachable, "
        "has_statement, statement_links, scanned_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (url, country, f"scan-{day}", int(reachable), int(has),
         json.dumps(links or []), f"{day}T10:00:00.000000+00:00"),
    )


def _social(conn: sqlite3.Connection, url: str, country: str, day: str,
            version: int = 3, **links: list[str]) -> None:
    columns = {f"{name}_links": json.dumps(value) for name, value in links.items()}
    names = ", ".join(columns)
    marks = ", ".join("?" for _ in columns)
    conn.execute(
        "INSERT INTO url_social_media_results (url, country_code, scan_id, is_reachable, "
        f"scanned_at, platforms_version{', ' + names if names else ''}) "
        f"VALUES (?, ?, ?, 1, ?, ?{', ' + marks if marks else ''})",
        (url, country, f"scan-{day}", f"{day}T10:00:00.000000+00:00", version,
         *columns.values()),
    )


def _statement_fixture(conn: sqlite3.Connection) -> None:
    """Pages A-F, each covering one rule.  Only A gains and only B loses."""
    for day in ("2026-09-01", "2026-10-01"):
        _statement(conn, "https://a.example.fr/", "FRANCE", day, False)
        _statement(conn, "https://b.example.fr/", "FRANCE", day, True)
        _statement(conn, "https://e.example.it/", "ITALY", day, False)
        _statement(conn, "https://f.example.it/", "ITALY", day, False)
    _statement(conn, "https://a.example.fr/", "FRANCE", "2026-11-05", True,
               ["https://a.example.fr/accessibilite?key=sekrit"])
    # B's scan on the week's last day also keeps the data fresh.
    _statement(conn, "https://b.example.fr/", "FRANCE", "2026-11-08", False)
    # C: one earlier scan only, so it is not compared.
    _statement(conn, "https://c.example.es/", "SPAIN", "2026-10-01", False)
    _statement(conn, "https://c.example.es/", "SPAIN", "2026-11-04", True)
    # D: had a statement in one earlier scan, so finding it again is no gain.
    _statement(conn, "https://d.example.es/", "SPAIN", "2026-09-01", False)
    _statement(conn, "https://d.example.es/", "SPAIN", "2026-10-01", True)
    _statement(conn, "https://d.example.es/", "SPAIN", "2026-11-03", True)
    # E: latest scan is before the week.
    _statement(conn, "https://e.example.it/", "ITALY", "2026-10-20", True)
    # F: the only scan this week was unreachable, so it says nothing.
    _statement(conn, "https://f.example.it/", "ITALY", "2026-11-07", False, reachable=False)


def _social_fixture(conn: sqlite3.Connection) -> None:
    """Pages S1-S5.  S2 gains AT Protocol, S3 gains Mastodon, S4 loses Mastodon."""
    # S1: version 2 filed a YouTube /@ link under Mastodon.  Must be ignored.
    _social(conn, "https://s1.example.ca/", "CANADA", "2026-10-01", version=2)
    _social(conn, "https://s1.example.ca/", "CANADA", "2026-11-05", version=2,
            mastodon=["https://www.youtube.com/@agency"])
    _social(conn, "https://s2.example.ca/", "CANADA", "2026-10-10")
    _social(conn, "https://s2.example.ca/", "CANADA", "2026-11-05",
            gander=["https://gander.social/@agency"])
    _social(conn, "https://www.s3.example.de/", "GERMANY", "2026-10-10")
    _social(conn, "https://www.s3.example.de/", "GERMANY", "2026-11-06",
            mastodon=["https://social.example.de/@agency"])
    _social(conn, "https://s4.example.de/", "GERMANY", "2026-10-10",
            mastodon=["https://social.example.de/@other"])
    _social(conn, "https://s4.example.de/", "GERMANY", "2026-11-07")
    # S5: its only earlier scan is version 2, so the two are not compared.
    _social(conn, "https://s5.example.de/", "GERMANY", "2026-10-01", version=2)
    _social(conn, "https://s5.example.de/", "GERMANY", "2026-11-05",
            bluesky=["https://bsky.app/profile/agency.example"])


@pytest.fixture
def full_db(tmp_path: Path) -> Path:
    path = _db(tmp_path)
    conn = sqlite3.connect(path)
    _statement_fixture(conn)
    _social_fixture(conn)
    conn.commit()
    conn.close()
    return path


def _run(tmp_path: Path, db: Path, *extra: str) -> tuple[int, dict, Path]:
    out = tmp_path / "out"
    evidence = tmp_path / "evidence"
    code = digest.main(["--db", str(db), "--output-dir", str(out),
                        "--evidence-dir", str(evidence), *WEEK_ARGS, *extra])
    summary = json.loads((out / "drafts.json").read_text(encoding="utf-8")) if code == 0 else {}
    return code, summary, evidence


class TestWeek:
    def test_label_within_a_month(self) -> None:
        assert WEEK.label() == "2 to 8 November 2026"

    def test_label_across_months_and_years(self) -> None:
        assert digest.Week(date(2026, 11, 1)).label() == "26 October to 1 November 2026"
        assert digest.Week(date(2027, 1, 3)).label() == "28 December 2026 to 3 January 2027"

    def test_bounds_cover_seven_whole_utc_days(self) -> None:
        assert WEEK.contains(datetime(2026, 11, 2, 0, 0, tzinfo=timezone.utc))
        assert WEEK.contains(datetime(2026, 11, 8, 23, 59, tzinfo=timezone.utc))
        assert not WEEK.contains(datetime(2026, 11, 9, 0, 0, tzinfo=timezone.utc))
        assert not WEEK.contains(datetime(2026, 11, 1, 23, 59, tzinfo=timezone.utc))


class TestClassifyChange:
    def test_gain_needs_every_earlier_scan_to_lack_it(self) -> None:
        assert digest.classify_change([False, False, True], 2) == "gained"
        assert digest.classify_change([True, False, True], 2) is None

    def test_loss_needs_every_earlier_scan_to_have_it(self) -> None:
        assert digest.classify_change([True, True, False], 2) == "lost"
        assert digest.classify_change([False, True, False], 2) is None

    def test_too_little_history_is_no_change(self) -> None:
        assert digest.classify_change([False, True], 2) is None
        assert digest.classify_change([True], 1) is None


class TestStatementSection:
    def _section(self, db: Path) -> digest.Section:
        conn = sqlite3.connect(db)
        try:
            return digest.statement_section(conn, WEEK, "https://example.org/evidence.json")
        finally:
            conn.close()

    def test_only_stable_changes_in_the_week_count(self, full_db: Path) -> None:
        evidence = self._section(full_db).evidence

        assert evidence["status"] == "drafted"
        assert evidence["pages_rechecked"] == 3  # A, B and D
        assert [r["url"] for r in evidence["gained"]["statement"]] == ["https://a.example.fr/"]
        assert [r["url"] for r in evidence["lost"]["statement"]] == ["https://b.example.fr/"]

    def test_post_numbers_match_the_evidence(self, full_db: Path) -> None:
        section = self._section(full_db)

        assert section.post is not None
        assert post_problems(section.post) == []
        assert "re-checked 3 public sector web pages in 2 countries" in section.post
        assert "1 page on 1 website now links" in section.post
        assert "On 1 page (1 website), a statement link" in section.post
        assert "https://example.org/evidence.json" in section.post

    def test_credentials_in_harvested_links_are_masked(self, full_db: Path) -> None:
        row = self._section(full_db).evidence["gained"]["statement"][0]

        assert "sekrit" not in json.dumps(row)
        assert row["links"] == ["https://a.example.fr/accessibilite?key=REDACTED"]

    def test_stale_data_is_skipped(self, tmp_path: Path) -> None:
        db = _db(tmp_path)
        conn = sqlite3.connect(db)
        for day in ("2026-09-01", "2026-10-01", "2026-11-03"):
            _statement(conn, "https://a.example.fr/", "FRANCE", day, day == "2026-11-03")
        conn.commit()
        conn.close()

        section = self._section(db)

        assert section.post is None
        assert "stale" in (section.reason or "")
        assert "gained" not in section.evidence

    def test_too_few_pages_are_skipped(self, full_db: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(digest, "MIN_PAGES_RECHECKED", 500)

        section = self._section(full_db)

        assert section.post is None
        assert "only 3 pages" in (section.reason or "")


class TestSocialSection:
    def _section(self, db: Path) -> digest.Section:
        conn = sqlite3.connect(db)
        try:
            return digest.social_section(conn, WEEK, "https://example.org/evidence.json")
        finally:
            conn.close()

    def test_scans_before_detection_version_3_are_never_compared(self, full_db: Path) -> None:
        evidence = self._section(full_db).evidence
        urls = {r["url"] for rows in evidence["gained"].values() for r in rows}

        assert "https://s1.example.ca/" not in urls  # YouTube /@ link under v2
        assert "https://s5.example.de/" not in urls  # v2 then v3
        assert evidence["pages_rechecked"] == 3  # S2, S3 and S4

    def test_gander_counts_as_at_protocol_and_hosts_drop_www(self, full_db: Path) -> None:
        evidence = self._section(full_db).evidence

        assert [r["host"] for r in evidence["gained"]["atproto"]] == ["s2.example.ca"]
        assert [r["host"] for r in evidence["gained"]["mastodon"]] == ["s3.example.de"]
        assert [r["url"] for r in evidence["lost"]["mastodon"]] == ["https://s4.example.de/"]

    def test_post_links_rather_than_mentions(self, full_db: Path) -> None:
        post = self._section(full_db).post

        assert post is not None
        assert post_problems(post) == []
        assert "@" not in post
        assert "2 pages on 2 government websites in 2 countries" in post
        assert "(1 to Mastodon, 1 to Bluesky or another AT Protocol app)" in post
        assert "Among them: s2.example.ca, s3.example.de." in post

    def test_no_version_3_scans_means_no_social_post(self, tmp_path: Path) -> None:
        db = _db(tmp_path)
        conn = sqlite3.connect(db)
        _social(conn, "https://s1.example.ca/", "CANADA", "2026-10-01", version=2)
        _social(conn, "https://s1.example.ca/", "CANADA", "2026-11-05", version=2,
                mastodon=["https://www.youtube.com/@agency"])
        conn.commit()
        conn.close()

        section = self._section(db)

        assert section.post is None
        assert "version 3" in (section.reason or "")


class TestMain:
    def test_writes_drafts_evidence_and_issue(self, tmp_path: Path, full_db: Path) -> None:
        code, summary, evidence_dir = _run(tmp_path, full_db)

        assert code == 0
        assert [d["key"] for d in summary["drafts"]] == ["open_social_platforms", "accessibility_statements"]
        evidence = json.loads((evidence_dir / "2026-11-08.json").read_text(encoding="utf-8"))
        assert set(evidence["sections"]) == {"open_social_platforms", "accessibility_statements"}
        assert summary["evidence_url"].endswith("/blob/main/docs/data/digest/2026-11-08.json")

        issue = (tmp_path / "out" / "issue.md").read_text(encoding="utf-8")
        for draft in summary["drafts"]:
            assert extract_draft(issue, draft["number"]) == draft["text"]
            assert draft["length"] <= 500

    def test_no_drafts_writes_no_evidence_file(self, tmp_path: Path) -> None:
        code, summary, evidence_dir = _run(tmp_path, _db(tmp_path))

        assert code == 0
        assert summary["drafts"] == []
        assert summary["evidence_file"] is None
        assert {s["key"] for s in summary["skipped"]} == {"open_social_platforms", "accessibility_statements"}
        assert not evidence_dir.exists()
        assert not (tmp_path / "out" / "issue.md").exists()

    def test_a_week_that_has_not_ended_is_refused(self, tmp_path: Path, full_db: Path) -> None:
        today = datetime.now(timezone.utc).date().isoformat()
        assert digest.main(["--db", str(full_db), "--week-ending", today]) == 2

    def test_a_missing_database_is_an_error(self, tmp_path: Path) -> None:
        yesterday = (datetime.now(timezone.utc).date() - timedelta(days=1)).isoformat()
        assert digest.main(["--db", str(tmp_path / "missing.db"), "--week-ending", yesterday]) == 1


def test_overlong_wording_falls_back_to_the_shorter_variant() -> None:
    long = "x" * 600
    assert digest.first_postable((long, "short")) == "short"
    assert digest.first_postable((long,)) is None


def test_country_names_read_naturally_mid_sentence() -> None:
    rows = [{"country": "United Kingdom"}] * 3 + [{"country": "Netherlands"}]
    assert digest.leading_countries(rows) == ", most in the United Kingdom (3) and the Netherlands (1)"
    assert digest.leading_countries([{"country": "Spain"}]) == ", all in Spain"


def test_a_big_week_still_fits_in_one_post() -> None:
    """Long numbers and long host names must not push a post over the limit."""
    countries = [f"COUNTRY_{i:02d}" for i in range(33)]
    gained = [
        {
            "url": f"https://a-very-long-regional-government-host-{i % 456}.example.eu/page-{i}",
            "host": f"a-very-long-regional-government-host-{i % 456}.example.eu",
            "country_code": countries[i % 33],
            "country": f"Republic of Country {i % 33}",
        }
        for i in range(12_345)
    ]
    rechecked = {row["url"]: row["country_code"] for row in gained}
    statements = digest.Changes(
        rechecked, {"statement": gained}, {"statement": gained[:5000]}
    )
    social = digest.Changes(
        rechecked,
        {"mastodon": gained[:9000], "atproto": gained[9000:]},
        {"mastodon": gained[:3000], "atproto": []},
    )
    url = "https://github.com/mgifford/eu-plus-government-scans/blob/main/docs/data/digest/2026-11-08.json"

    for text in (digest.statement_post(WEEK, statements, url), digest.social_post(WEEK, social, url)):
        assert text is not None
        assert post_problems(text) == []
