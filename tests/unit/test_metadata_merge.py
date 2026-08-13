"""Unit tests for per-owner metadata artifacts and their merge."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from src.lib.metadata_merge import (
    ARTIFACT_TABLES,
    KNOWN_TABLES,
    UnknownArtifactError,
    extract_tables,
    merge_into,
    owned_tables,
)
from src.storage.schema import initialize_schema


def _db(path: Path) -> Path:
    """Create an empty database with the full schema applied."""
    initialize_schema(f"sqlite:///{path}")
    return path


def _insert(path: Path, table: str, columns: tuple[str, ...], rows: list[tuple]) -> None:
    """Insert rows into *table*."""
    conn = sqlite3.connect(path)
    try:
        placeholders = ",".join("?" * len(columns))
        conn.executemany(
            f"INSERT OR REPLACE INTO {table} ({','.join(columns)}) VALUES ({placeholders})",
            rows,
        )
        conn.commit()
    finally:
        conn.close()


def _count(path: Path, table: str) -> int:
    """Return the row count of *table*."""
    conn = sqlite3.connect(path)
    try:
        return conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    finally:
        conn.close()


VALIDATION_COLS = ("url", "country_code", "scan_id", "is_valid")
SOCIAL_COLS = ("url", "country_code", "scan_id", "is_reachable")
TECH_COLS = ("url", "country_code", "scan_id", "technologies")


class TestOwnership:
    """Each table belongs to exactly one artifact."""

    def test_no_table_is_owned_twice(self) -> None:
        """Two artifacts owning one table would reintroduce the race."""
        seen: dict[str, str] = {}
        for artifact, tables in ARTIFACT_TABLES.items():
            for table in tables:
                assert table not in seen, (
                    f"{table} owned by both {seen.get(table)} and {artifact}"
                )
                seen[table] = artifact

    def test_owned_tables_returns_the_mapping(self) -> None:
        assert owned_tables("social-media-metadata") == ("url_social_media_results",)

    def test_unknown_artifact_is_rejected(self) -> None:
        with pytest.raises(UnknownArtifactError):
            owned_tables("not-a-real-artifact")

    def test_every_owned_table_exists_in_the_schema(self, tmp_path: Path) -> None:
        """Ownership cannot drift from the actual schema."""
        db = _db(tmp_path / "schema.db")
        conn = sqlite3.connect(db)
        try:
            actual = {
                row[0]
                for row in conn.execute(
                    "SELECT name FROM sqlite_master WHERE type = 'table'"
                )
            }
        finally:
            conn.close()

        assert KNOWN_TABLES <= actual, f"missing from schema: {KNOWN_TABLES - actual}"


class TestMerge:
    """Merging reassembles what concurrent writers produced."""

    def test_rows_from_every_source_are_kept(self, tmp_path: Path) -> None:
        """The defect: whichever writer finished last discarded the others."""
        social = _db(tmp_path / "social.db")
        _insert(social, "url_social_media_results", SOCIAL_COLS,
                [("https://a.gov", "X", "soc1", 1)])

        tech = _db(tmp_path / "tech.db")
        _insert(tech, "url_tech_results", TECH_COLS,
                [("https://a.gov", "X", "tech1", "{}")])

        target = tmp_path / "merged.db"
        merge_into(target, [social, tech])

        assert _count(target, "url_social_media_results") == 1
        assert _count(target, "url_tech_results") == 1

    def test_merge_is_idempotent(self, tmp_path: Path) -> None:
        """Re-running a merge must not duplicate rows."""
        source = _db(tmp_path / "source.db")
        _insert(source, "url_validation_results", VALIDATION_COLS,
                [("https://a.gov", "X", "s1", 1)])

        target = tmp_path / "merged.db"
        merge_into(target, [source])
        merge_into(target, [source])

        assert _count(target, "url_validation_results") == 1

    def test_missing_source_is_skipped(self, tmp_path: Path) -> None:
        """An artifact is legitimately absent until its workflow first runs."""
        source = _db(tmp_path / "present.db")
        _insert(source, "url_validation_results", VALIDATION_COLS,
                [("https://a.gov", "X", "s1", 1)])

        target = tmp_path / "merged.db"
        merge_into(target, [tmp_path / "absent.db", source])

        assert _count(target, "url_validation_results") == 1

    def test_target_is_created_when_absent(self, tmp_path: Path) -> None:
        target = tmp_path / "nested" / "new.db"
        merge_into(target, [])
        assert target.is_file()

    def test_distinct_scan_ids_both_survive(self, tmp_path: Path) -> None:
        """Same URL, different scans: the union keeps both rows."""
        first = _db(tmp_path / "first.db")
        _insert(first, "url_validation_results", VALIDATION_COLS,
                [("https://a.gov", "X", "scan-1", 1)])

        second = _db(tmp_path / "second.db")
        _insert(second, "url_validation_results", VALIDATION_COLS,
                [("https://a.gov", "X", "scan-2", 0)])

        target = tmp_path / "merged.db"
        merge_into(target, [first, second])

        assert _count(target, "url_validation_results") == 2

    def test_source_missing_a_column_still_merges(self, tmp_path: Path) -> None:
        """An artifact predating a migration must not block the merge."""
        source = _db(tmp_path / "old.db")
        _insert(source, "url_social_media_results", SOCIAL_COLS,
                [("https://a.gov", "X", "soc1", 1)])
        conn = sqlite3.connect(source)
        try:
            conn.execute("ALTER TABLE url_social_media_results DROP COLUMN platforms_version")
            conn.commit()
        finally:
            conn.close()

        target = tmp_path / "merged.db"
        merge_into(target, [source])

        assert _count(target, "url_social_media_results") == 1

    def test_unknown_table_is_refused(self, tmp_path: Path) -> None:
        """Table names reach SQL by interpolation, so they are allowlisted."""
        with pytest.raises(ValueError):
            merge_into(tmp_path / "t.db", [], tables=["sqlite_master"])


class TestExtract:
    """A workflow uploads only the tables it owns."""

    def test_only_owned_tables_are_written(self, tmp_path: Path) -> None:
        """Uploading the merged database would republish stale foreign rows."""
        working = _db(tmp_path / "working.db")
        _insert(working, "url_social_media_results", SOCIAL_COLS,
                [("https://a.gov", "X", "soc1", 1)])
        _insert(working, "url_tech_results", TECH_COLS,
                [("https://a.gov", "X", "tech1", "{}")])

        out = tmp_path / "upload" / "metadata.db"
        extract_tables(working, out, owned_tables("social-media-metadata"))

        assert _count(out, "url_social_media_results") == 1
        assert _count(out, "url_tech_results") == 0

    def test_extract_replaces_an_existing_target(self, tmp_path: Path) -> None:
        working = _db(tmp_path / "working.db")
        _insert(working, "url_tech_results", TECH_COLS,
                [("https://a.gov", "X", "tech1", "{}")])

        out = tmp_path / "out.db"
        extract_tables(working, out, owned_tables("technology-metadata"))
        extract_tables(working, out, owned_tables("technology-metadata"))

        assert _count(out, "url_tech_results") == 1

    def test_missing_source_raises(self, tmp_path: Path) -> None:
        with pytest.raises(FileNotFoundError):
            extract_tables(tmp_path / "absent.db", tmp_path / "out.db", ("url_tech_results",))

    def test_round_trip_preserves_rows(self, tmp_path: Path) -> None:
        """extract then merge is what the workflows actually do."""
        working = _db(tmp_path / "working.db")
        _insert(working, "url_overlay_results",
                ("url", "country_code", "scan_id", "overlay_count"),
                [("https://a.gov", "X", "ov1", 2)])

        artifact = tmp_path / "artifacts" / "overlay-metadata" / "metadata.db"
        extract_tables(working, artifact, owned_tables("overlay-metadata"))

        rebuilt = tmp_path / "rebuilt.db"
        merge_into(rebuilt, [artifact])

        assert _count(rebuilt, "url_overlay_results") == 1


class TestWorkflowWiring:
    """The workflows must keep the one-writer-per-artifact invariant.

    These read the committed workflow files, so the ownership map and the YAML
    cannot drift apart silently.
    """

    @staticmethod
    def _workflows() -> list[Path]:
        root = Path(__file__).resolve().parents[2] / ".github" / "workflows"
        return sorted(root.glob("*.yml")) if root.is_dir() else []

    @staticmethod
    def _load(path: Path) -> dict:
        import yaml

        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}

    def _uploaders(self) -> dict[str, list[Path]]:
        """Map each known artifact to the workflows that upload it."""
        uploaders: dict[str, list[Path]] = {}
        for path in self._workflows():
            for job in (self._load(path).get("jobs") or {}).values():
                for step in job.get("steps", []):
                    if "upload-artifact" not in str(step.get("uses", "")):
                        continue
                    name = (step.get("with") or {}).get("name")
                    if name in ARTIFACT_TABLES:
                        uploaders.setdefault(name, []).append(path)
        return uploaders

    def test_each_artifact_has_a_single_writer_or_a_shared_lock(self) -> None:
        """Two workflows may share an artifact only if they serialize on it.

        This is the regression guard for the original defect: several workflows
        in different concurrency groups overwriting one artifact.
        """
        if not self._workflows():
            pytest.skip("workflow directory not present in this checkout")

        for artifact, paths in self._uploaders().items():
            if len(paths) == 1:
                continue
            groups = {
                (self._load(p).get("concurrency") or {}).get("group")
                for p in paths
            }
            assert len(groups) == 1 and None not in groups, (
                f"{artifact} is written by {[p.name for p in paths]} "
                f"across concurrency groups {groups}"
            )

    def test_no_workflow_uploads_an_artifact_it_does_not_own(self) -> None:
        """A workflow must not republish another scanner's tables."""
        if not self._workflows():
            pytest.skip("workflow directory not present in this checkout")

        for artifact, paths in self._uploaders().items():
            for path in paths:
                text = path.read_text(encoding="utf-8")
                assert f"--artifact {artifact}" in text, (
                    f"{path.name} uploads {artifact} without extracting it first"
                )

    def test_every_collector_can_read_artifacts(self) -> None:
        """Fetching artifacts needs ``actions: read``, and failing is silent.

        Without the permission the artifact listing 403s, the merge starts from
        an empty database, and the upload -- which runs with ``overwrite:
        true`` -- replaces the accumulated state with nothing.  Nothing in the
        run turns red, so this has to be caught here.
        """
        if not self._workflows():
            pytest.skip("workflow directory not present in this checkout")

        for path in self._workflows():
            if "fetch-metadata-artifacts" not in path.read_text(encoding="utf-8"):
                continue
            for name, job in (self._load(path).get("jobs") or {}).items():
                steps = " ".join(str(s.get("run", "")) for s in job.get("steps", []))
                if "fetch-metadata-artifacts" not in steps:
                    continue
                permissions = job.get("permissions") or {}
                assert permissions.get("actions") == "read", (
                    f"{path.name} job {name!r} downloads metadata artifacts but "
                    f"has permissions {permissions}"
                )

    def test_every_uploader_merges_before_scanning(self) -> None:
        """Skip logic reads other scanners' results, so the merge must run."""
        if not self._workflows():
            pytest.skip("workflow directory not present in this checkout")

        for paths in self._uploaders().values():
            for path in paths:
                assert "metadata_artifact merge" in path.read_text(encoding="utf-8"), (
                    f"{path.name} uploads metadata but never merges it in"
                )
