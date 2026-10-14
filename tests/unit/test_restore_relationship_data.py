"""Tests for scripts/restore-relationship-data.sh.

The relationship scan commits at most once a day and hands its output to the
next run through the ``relationship-data`` artifact.  If restoring that
artifact silently fell back to the committed files, the run would scan from
stale data and then upload it over the newer artifact, losing results.  These
tests pin down when the script restores, when it leaves the committed files
alone, and that every failure aborts.
"""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "restore-relationship-data.sh"

pytestmark = pytest.mark.skipif(
    not SCRIPT.is_file() or shutil.which("bash") is None,
    reason="script or bash not available in this checkout",
)

ARTIFACT_AT = "2026-10-14T06:30:00Z"


def _stub_gh(tmp_path: Path, *, artifact_at: str | None = ARTIFACT_AT,
             committed_at: str = "2026-10-14T00:30:00Z",
             list_fails: bool = False, download_fails: bool = False) -> Path:
    """Write a fake `gh` onto PATH and return its directory."""
    bindir = tmp_path / "bin"
    bindir.mkdir()
    listing = f"echo '{artifact_at} 42'" if artifact_at else ":"
    (bindir / "gh").write_text(
        "#!/usr/bin/env bash\n"
        'if [ "$1" = "api" ]; then\n'
        '  case "$*" in\n'
        f"    *artifacts*) {'exit 1' if list_fails else listing} ;;\n"
        f"    *commits*) echo '{committed_at}' ;;\n"
        "  esac\n"
        "  exit 0\n"
        "fi\n"
        'if [ "$1" = "run" ]; then\n'
        f"  {'exit 1' if download_fails else ''}\n"
        '  dir="${@: -1}"\n'
        '  mkdir -p "$dir/relationships" "$dir/summaries"\n'
        '  echo new > "$dir/relationships/index.json"\n'
        '  echo new > "$dir/relationships/fr.001.jsonl"\n'
        '  echo new > "$dir/summaries/fr.json"\n'
        '  echo new > "$dir/dependency-matrix.json"\n'
        "  exit 0\n"
        "fi\n"
        "exit 0\n",
        encoding="utf-8",
    )
    (bindir / "gh").chmod(0o755)
    return bindir


def _data_dir(tmp_path: Path) -> Path:
    """Create committed-looking data, including a shard the artifact lacks."""
    data = tmp_path / "data"
    (data / "relationships").mkdir(parents=True)
    (data / "relationships" / "index.json").write_text("old\n")
    (data / "relationships" / "uk.001.jsonl").write_text("old\n")
    (data / "summaries").mkdir()
    (data / "summaries" / "de.json").write_text("old\n")
    return data


def _run(tmp_path: Path, bindir: Path, data: Path) -> subprocess.CompletedProcess:
    env = dict(os.environ)
    env["PATH"] = f"{bindir}{os.pathsep}{env['PATH']}"
    env["GITHUB_REPOSITORY"] = "owner/repo"
    return subprocess.run(["bash", str(SCRIPT), str(data)],
                          capture_output=True, text=True, env=env, timeout=60)


def test_script_is_executable() -> None:
    """The workflow invokes the path directly, not via `bash <path>`."""
    assert os.access(SCRIPT, os.X_OK), f"{SCRIPT} is not executable"


def test_newer_artifact_replaces_shards_and_merges_summaries(tmp_path: Path) -> None:
    data = _data_dir(tmp_path)
    result = _run(tmp_path, _stub_gh(tmp_path), data)

    assert result.returncode == 0, result.stderr
    assert (data / "relationships" / "index.json").read_text() == "new\n"
    # Shards are replaced outright, so a shard the artifact lacks is gone.
    assert not (data / "relationships" / "uk.001.jsonl").exists()
    # Summaries are merged, not replaced.
    assert (data / "summaries" / "de.json").read_text() == "old\n"
    assert (data / "summaries" / "fr.json").read_text() == "new\n"
    assert (data / "dependency-matrix.json").read_text() == "new\n"


def test_newer_commit_keeps_committed_data(tmp_path: Path) -> None:
    """A deliberate reset committed after the artifact must not be undone."""
    data = _data_dir(tmp_path)
    bindir = _stub_gh(tmp_path, committed_at="2026-10-14T09:00:00Z")
    result = _run(tmp_path, bindir, data)

    assert result.returncode == 0, result.stderr
    assert (data / "relationships" / "index.json").read_text() == "old\n"
    assert "using committed data" in result.stdout


def test_no_artifact_keeps_committed_data(tmp_path: Path) -> None:
    data = _data_dir(tmp_path)
    result = _run(tmp_path, _stub_gh(tmp_path, artifact_at=None), data)

    assert result.returncode == 0, result.stderr
    assert (data / "relationships" / "index.json").read_text() == "old\n"
    assert "none published" in result.stdout


@pytest.mark.parametrize("failure", ["list_fails", "download_fails"])
def test_failures_abort_and_leave_data_untouched(tmp_path: Path, failure: str) -> None:
    data = _data_dir(tmp_path)
    result = _run(tmp_path, _stub_gh(tmp_path, **{failure: True}), data)

    assert result.returncode == 1
    assert (data / "relationships" / "uk.001.jsonl").read_text() == "old\n"
