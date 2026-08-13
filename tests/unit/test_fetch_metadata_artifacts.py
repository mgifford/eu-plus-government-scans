"""Tests for scripts/fetch-metadata-artifacts.sh.

This script gates every scan workflow: it runs before the scan and aborts the
job on failure, so a defect here stops all scanning rather than degrading it.
It has already done so once -- ``sort -rk1 | head -1`` left ``sort`` writing
into a pipe that ``head`` had closed, and under ``set -euo pipefail`` the
resulting SIGPIPE aborted every collecting workflow.

The stub below therefore emits a listing large enough to exceed the pipe
buffer. That detail is the whole point: an earlier stub returned a single line,
``sort`` fitted its output into the buffer before ``head`` exited, and the bug
did not reproduce even though the script was broken in production.
"""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "fetch-metadata-artifacts.sh"

# Comfortably past the 64 KiB pipe buffer at ~32 bytes per line.
LISTING_LINES = 6000

pytestmark = pytest.mark.skipif(
    not SCRIPT.is_file() or shutil.which("bash") is None,
    reason="script or bash not available in this checkout",
)


def _stub_gh(tmp_path: Path, *, api_lines: int = LISTING_LINES,
             api_fails: bool = False, download_fails: bool = False) -> Path:
    """Write a fake `gh` onto PATH and return its directory."""
    bindir = tmp_path / "bin"
    bindir.mkdir(parents=True, exist_ok=True)
    gh = bindir / "gh"
    gh.write_text(
        "#!/usr/bin/env bash\n"
        'if [ "$1" = "api" ]; then\n'
        f"  {'exit 1' if api_fails else ''}\n"
        f"  for i in $(seq 1 {api_lines}); do\n"
        "    printf '2026-01-%02dT00:00:00Z %d\\n' $((i % 28 + 1)) $((31700000000 + i))\n"
        "  done\n"
        "  exit 0\n"
        "fi\n"
        'if [ "$1" = "run" ]; then\n'
        f"  {'exit 1' if download_fails else ''}\n"
        '  mkdir -p "${@: -1}"; : > "${@: -1}/metadata.db"; exit 0\n'
        "fi\n"
        "exit 0\n",
        encoding="utf-8",
    )
    gh.chmod(0o755)
    return bindir


def _run(tmp_path: Path, bindir: Path) -> subprocess.CompletedProcess:
    """Run the script with the stub on PATH."""
    env = dict(os.environ)
    env["PATH"] = f"{bindir}{os.pathsep}{env['PATH']}"
    env["GITHUB_REPOSITORY"] = "owner/repo"
    env["FETCH_ARTIFACT_ATTEMPTS"] = "1"
    return subprocess.run(
        ["bash", str(SCRIPT), str(tmp_path / "dest")],
        capture_output=True, text=True, env=env,
        cwd=SCRIPT.parents[1], timeout=120,
    )


def test_script_is_executable() -> None:
    """The workflows invoke the path directly, not via `bash <path>`.

    Losing the exec bit -- easy to do by rewriting the file through a
    temporary copy -- fails every collecting job with "Permission denied".
    The tests below run it through bash explicitly and so cannot see that,
    which is exactly why this check is separate.
    """
    assert os.access(SCRIPT, os.X_OK), f"{SCRIPT} is not executable"


class TestLargeListing:
    """The regression that stopped every scan."""

    def test_a_large_artifact_listing_does_not_abort_the_run(
        self, tmp_path: Path
    ) -> None:
        result = _run(tmp_path, _stub_gh(tmp_path))

        assert result.returncode == 0, (
            f"exit {result.returncode}; stderr:\n{result.stderr}"
        )
        assert "write error" not in result.stderr

    def test_the_newest_run_is_selected(self, tmp_path: Path) -> None:
        """Selecting the wrong row would merge a stale database."""
        result = _run(tmp_path, _stub_gh(tmp_path))

        # Highest date in the stub is 2026-01-28; the largest run id on it wins.
        assert "from run 31700005991" in result.stdout


class TestFailureHandling:
    """Failing loudly is the point; failing silently is what loses data."""

    def test_unreadable_listing_aborts(self, tmp_path: Path) -> None:
        """A 403 looks identical to 'nothing published' and must not pass."""
        result = _run(tmp_path, _stub_gh(tmp_path, api_fails=True))

        assert result.returncode == 1
        assert "actions: read" in result.stderr

    def test_failed_download_aborts(self, tmp_path: Path) -> None:
        result = _run(tmp_path, _stub_gh(tmp_path, download_fails=True))

        assert result.returncode == 1
        assert "download failed" in result.stderr

    def test_never_published_artifact_is_not_an_error(self, tmp_path: Path) -> None:
        result = _run(tmp_path, _stub_gh(tmp_path, api_lines=0))

        assert result.returncode == 0
        assert "none published yet" in result.stdout
