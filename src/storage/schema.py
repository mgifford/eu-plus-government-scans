"""Metadata schema and migration bootstrap for scan lifecycle state."""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class CountryScan:
    scan_id: str
    country_code: str
    run_month: str
    status: str
    started_at: str | None = None
    finished_at: str | None = None
    artifact_path: str | None = None
    artifact_checksum: str | None = None
    host_total: int = 0
    host_processed: int = 0
    error_summary: str | None = None


@dataclass(slots=True)
class DomainRecord:
    country_code: str
    canonical_hostname: str
    input_hostname: str
    alias_hostnames: str = ""
    in_scope_wad: int = 1
    source_type: str = "other"
    source_reference_url: str = ""
    last_seen_scan_id: str | None = None
    stale: int = 0
    unreachable_streak: int = 0
    active: int = 1


@dataclass(slots=True)
class UrlValidationResult:
    url: str
    country_code: str
    scan_id: str
    status_code: int | None = None
    error_message: str | None = None
    redirected_to: str | None = None
    redirect_chain: str | None = None
    is_valid: int = 0
    failure_count: int = 0
    validated_at: str | None = None


@dataclass(slots=True)
class ValidationBatchState:
    """Tracks progress of batch validation cycles."""
    cycle_id: str
    country_code: str
    status: str  # pending, processing, completed, failed
    started_at: str | None = None
    completed_at: str | None = None
    github_issue_number: int | None = None
    error_message: str | None = None


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS country_scans (
    scan_id TEXT PRIMARY KEY,
    country_code TEXT NOT NULL,
    run_month TEXT NOT NULL,
    status TEXT NOT NULL,
    started_at TEXT,
    finished_at TEXT,
    artifact_path TEXT,
    artifact_checksum TEXT,
    host_total INTEGER NOT NULL DEFAULT 0,
    host_processed INTEGER NOT NULL DEFAULT 0,
    error_summary TEXT,
    UNIQUE(country_code, run_month, scan_id)
);

CREATE TABLE IF NOT EXISTS domain_records (
    country_code TEXT NOT NULL,
    canonical_hostname TEXT NOT NULL,
    input_hostname TEXT NOT NULL,
    alias_hostnames TEXT NOT NULL DEFAULT '',
    in_scope_wad INTEGER NOT NULL DEFAULT 1,
    source_type TEXT NOT NULL,
    source_reference_url TEXT NOT NULL,
    last_seen_scan_id TEXT,
    stale INTEGER NOT NULL DEFAULT 0,
    unreachable_streak INTEGER NOT NULL DEFAULT 0,
    active INTEGER NOT NULL DEFAULT 1,
    PRIMARY KEY (country_code, canonical_hostname)
);

CREATE TABLE IF NOT EXISTS url_validation_results (
    url TEXT NOT NULL,
    country_code TEXT NOT NULL,
    scan_id TEXT NOT NULL,
    status_code INTEGER,
    error_message TEXT,
    redirected_to TEXT,
    redirect_chain TEXT,
    is_valid INTEGER NOT NULL DEFAULT 0,
    failure_count INTEGER NOT NULL DEFAULT 0,
    validated_at TEXT,
    PRIMARY KEY (url, scan_id)
);

CREATE INDEX IF NOT EXISTS idx_url_validation_country ON url_validation_results(country_code);
CREATE INDEX IF NOT EXISTS idx_url_validation_scan ON url_validation_results(scan_id);
CREATE INDEX IF NOT EXISTS idx_url_validation_failures ON url_validation_results(failure_count);

CREATE TABLE IF NOT EXISTS validation_batch_state (
    cycle_id TEXT NOT NULL,
    country_code TEXT NOT NULL,
    status TEXT NOT NULL,
    started_at TEXT,
    completed_at TEXT,
    github_issue_number INTEGER,
    error_message TEXT,
    PRIMARY KEY (cycle_id, country_code)
);

CREATE INDEX IF NOT EXISTS idx_batch_state_cycle ON validation_batch_state(cycle_id);
CREATE INDEX IF NOT EXISTS idx_batch_state_status ON validation_batch_state(status);
CREATE INDEX IF NOT EXISTS idx_batch_state_issue ON validation_batch_state(github_issue_number);
"""


def _db_path_from_url(db_url: str) -> Path:
    if db_url.startswith("sqlite:///"):
        return Path(db_url.replace("sqlite:///", "", 1))
    return Path(db_url)


def initialize_schema(db_url: str) -> Path:
    """Create required schema tables and return resolved db path."""
    db_path = _db_path_from_url(db_url)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    try:
        conn.executescript(SCHEMA_SQL)
        conn.commit()
    finally:
        conn.close()
    return db_path
