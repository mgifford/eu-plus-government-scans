"""Per-owner metadata artifacts and the merge that reassembles them.

Scan state lives in a SQLite database that is passed between workflow runs as a
GitHub Actions artifact.  Every scan workflow used to download the *same*
``validation-metadata`` artifact, mutate its own copy and re-upload it, which is
a last-writer-wins race: whichever job finished last silently discarded every
result the others had just produced.  Collisions were routine rather than
theoretical -- four writers start together at 00:00 UTC alone.

The fix is to give each writer its own artifact holding only the tables it
owns, so no two workflows ever write the same artifact.  A job that needs
another scanner's data merges the artifacts into one local database at the
start of its run, and uploads only its own tables at the end.

Merging is safe because the result tables are append-only and keyed by
``(url, scan_id)``: two scanners cannot produce the same key, so the union of
their rows is exactly what a single serialized writer would have produced.  The
mutable state tables are all owned by a single artifact for that reason -- see
:data:`ARTIFACT_TABLES`.
"""

from __future__ import annotations

import sqlite3
from collections.abc import Iterable
from pathlib import Path

from src.storage.schema import initialize_schema

# Which tables each artifact owns.  An artifact is written by exactly one
# workflow, or -- for validation-metadata -- by a group of workflows that share
# a concurrency group because they drive the same mutable batch-cycle state.
#
# Every table that is UPDATEd in place rather than only appended to lives in
# validation-metadata, so no mutable row is ever written from two artifacts.
ARTIFACT_TABLES: dict[str, tuple[str, ...]] = {
    "validation-metadata": (
        "url_validation_results",
        "validation_batch_state",
        "issue_trigger_runs",
        "country_scans",
        "domain_records",
    ),
    "social-media-metadata": ("url_social_media_results",),
    "technology-metadata": ("url_tech_results",),
    "accessibility-metadata": ("url_accessibility_results",),
    "lighthouse-metadata": ("url_lighthouse_results",),
    "third-party-js-metadata": ("url_third_party_js_results",),
    "overlay-metadata": ("url_overlay_results",),
    "relationship-scan-metadata": (
        "relationship_scan_state",
        "relationship_scan_results",
    ),
}

# Every table any artifact may carry; used to reject unknown table names before
# they reach a SQL statement.
KNOWN_TABLES = frozenset(
    table for tables in ARTIFACT_TABLES.values() for table in tables
)


class UnknownArtifactError(ValueError):
    """Raised for an artifact name that owns no tables."""


def owned_tables(artifact_name: str) -> tuple[str, ...]:
    """Return the tables *artifact_name* is responsible for.

    Args:
        artifact_name: Artifact name, e.g. ``"social-media-metadata"``.

    Returns:
        The table names that artifact owns.

    Raises:
        UnknownArtifactError: If the artifact is not in :data:`ARTIFACT_TABLES`.
    """
    try:
        return ARTIFACT_TABLES[artifact_name]
    except KeyError as exc:
        known = ", ".join(sorted(ARTIFACT_TABLES))
        raise UnknownArtifactError(
            f"unknown artifact {artifact_name!r}; expected one of: {known}"
        ) from exc


def _table_columns(conn: sqlite3.Connection, table: str, schema: str = "main") -> list[str]:
    """Return *table*'s column names, or an empty list when it does not exist."""
    rows = conn.execute(f"PRAGMA {schema}.table_info({table})").fetchall()
    return [row[1] for row in rows]


def _assert_known(table: str) -> None:
    """Guard table names before they are interpolated into SQL."""
    if table not in KNOWN_TABLES:
        raise ValueError(f"refusing to operate on unknown table {table!r}")


def merge_into(
    target: Path,
    sources: Iterable[Path],
    tables: Iterable[str] | None = None,
) -> dict[str, int]:
    """Merge rows from each source database into *target*.

    The target's schema is created first, so a missing or empty target is a
    valid starting point rather than an error.  Sources are applied in the order
    given; a source that does not exist is skipped, because an artifact is
    legitimately absent until its workflow has run once.

    Only columns present in *both* databases are copied.  An artifact produced
    before a migration added a column therefore still merges, with the new
    column taking its schema default.

    Args:
        target: Database to merge into; created when absent.
        sources: Databases to merge from.
        tables: Restrict the merge to these tables.  Defaults to every table in
            :data:`KNOWN_TABLES`.

    Returns:
        Rows merged per table, omitting tables that contributed nothing.

    Raises:
        ValueError: If *tables* names a table outside :data:`KNOWN_TABLES`.
    """
    wanted = tuple(tables) if tables is not None else tuple(sorted(KNOWN_TABLES))
    for table in wanted:
        _assert_known(table)

    initialize_schema(f"sqlite:///{target}")

    merged: dict[str, int] = {}
    conn = sqlite3.connect(target)
    try:
        for source in sources:
            source = Path(source)
            if not source.is_file():
                continue

            conn.execute("ATTACH DATABASE ? AS src", (str(source),))
            try:
                for table in wanted:
                    src_cols = _table_columns(conn, table, schema="src")
                    if not src_cols:
                        continue
                    dst_cols = _table_columns(conn, table)
                    shared = [col for col in dst_cols if col in src_cols]
                    if not shared:
                        continue

                    column_list = ", ".join(shared)
                    before = conn.execute(
                        f"SELECT COUNT(*) FROM main.{table}"
                    ).fetchone()[0]
                    conn.execute(
                        f"INSERT OR REPLACE INTO main.{table} ({column_list}) "
                        f"SELECT {column_list} FROM src.{table}"
                    )
                    after = conn.execute(
                        f"SELECT COUNT(*) FROM main.{table}"
                    ).fetchone()[0]
                    if after != before:
                        merged[table] = merged.get(table, 0) + (after - before)
                conn.commit()
            finally:
                conn.execute("DETACH DATABASE src")
    finally:
        conn.close()

    return merged


def extract_tables(
    source: Path,
    target: Path,
    tables: Iterable[str],
) -> dict[str, int]:
    """Copy only *tables* out of *source* into a fresh database at *target*.

    This is what a workflow uploads: a database holding the tables it owns and
    nothing else.  Uploading the full merged database instead would let one
    scanner republish a stale snapshot of another's tables.

    Args:
        source: Database to read from.
        target: Database to create.  Replaced when it already exists.
        tables: Tables to copy.

    Returns:
        Row count per copied table.

    Raises:
        FileNotFoundError: If *source* does not exist.
        ValueError: If *tables* names a table outside :data:`KNOWN_TABLES`.
    """
    source = Path(source)
    if not source.is_file():
        raise FileNotFoundError(f"no metadata database at {source}")

    wanted = tuple(tables)
    for table in wanted:
        _assert_known(table)

    target = Path(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.unlink(missing_ok=True)

    initialize_schema(f"sqlite:///{target}")

    counts: dict[str, int] = {}
    conn = sqlite3.connect(target)
    try:
        conn.execute("ATTACH DATABASE ? AS src", (str(source),))
        try:
            for table in wanted:
                src_cols = _table_columns(conn, table, schema="src")
                if not src_cols:
                    continue
                dst_cols = _table_columns(conn, table)
                shared = [col for col in dst_cols if col in src_cols]
                if not shared:
                    continue

                column_list = ", ".join(shared)
                conn.execute(
                    f"INSERT OR REPLACE INTO main.{table} ({column_list}) "
                    f"SELECT {column_list} FROM src.{table}"
                )
                counts[table] = conn.execute(
                    f"SELECT COUNT(*) FROM main.{table}"
                ).fetchone()[0]
            conn.commit()
        finally:
            conn.execute("DETACH DATABASE src")
    finally:
        conn.close()

    return counts
