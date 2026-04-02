"""Unit tests for the GitHub issue manager service."""

from __future__ import annotations

import subprocess
from unittest.mock import MagicMock, patch

import pytest

from src.services.github_issue_manager import (
    GH_CLI_CHECK_TIMEOUT,
    GH_CLI_COMMAND_TIMEOUT,
    GitHubIssueManager,
)


# ---------------------------------------------------------------------------
# _check_gh_cli
# ---------------------------------------------------------------------------


def test_check_gh_cli_available():
    """Returns True when 'gh --version' exits with code 0."""
    mock_result = MagicMock()
    mock_result.returncode = 0

    with patch("subprocess.run", return_value=mock_result) as mock_run:
        manager = GitHubIssueManager()

    mock_run.assert_called_once_with(
        ["gh", "--version"],
        capture_output=True,
        text=True,
        timeout=GH_CLI_CHECK_TIMEOUT,
    )
    assert manager._has_gh_cli is True


def test_check_gh_cli_not_available_nonzero():
    """Returns False when 'gh --version' exits with non-zero code."""
    mock_result = MagicMock()
    mock_result.returncode = 1

    with patch("subprocess.run", return_value=mock_result):
        manager = GitHubIssueManager()

    assert manager._has_gh_cli is False


def test_check_gh_cli_not_found():
    """Returns False when the 'gh' binary is not installed (FileNotFoundError)."""
    with patch("subprocess.run", side_effect=FileNotFoundError):
        manager = GitHubIssueManager()

    assert manager._has_gh_cli is False


def test_check_gh_cli_timeout():
    """Returns False when the version check times out."""
    with patch("subprocess.run", side_effect=subprocess.TimeoutExpired("gh", 5)):
        manager = GitHubIssueManager()

    assert manager._has_gh_cli is False


# ---------------------------------------------------------------------------
# _run_gh_command
# ---------------------------------------------------------------------------


def _make_manager_with_cli(available: bool = True) -> GitHubIssueManager:
    """Return a GitHubIssueManager bypassing the real _check_gh_cli."""
    check_result = MagicMock()
    check_result.returncode = 0 if available else 1
    with patch("subprocess.run", return_value=check_result):
        return GitHubIssueManager()


def test_run_gh_command_no_cli():
    """Returns (False, 'GitHub CLI not available') when CLI is absent."""
    manager = _make_manager_with_cli(available=False)
    success, output = manager._run_gh_command(["issue", "list"])
    assert success is False
    assert "not available" in output


def test_run_gh_command_success():
    """Returns (True, stdout) on a successful command."""
    manager = _make_manager_with_cli(available=True)

    cmd_result = MagicMock()
    cmd_result.returncode = 0
    cmd_result.stdout = "https://github.com/owner/repo/issues/42\n"

    with patch("subprocess.run", return_value=cmd_result):
        success, output = manager._run_gh_command(["issue", "create"])

    assert success is True
    assert output == "https://github.com/owner/repo/issues/42"


def test_run_gh_command_failure():
    """Returns (False, stdout) when command returns non-zero."""
    manager = _make_manager_with_cli(available=True)

    cmd_result = MagicMock()
    cmd_result.returncode = 1
    cmd_result.stdout = "error message"

    with patch("subprocess.run", return_value=cmd_result):
        success, output = manager._run_gh_command(["issue", "create"])

    assert success is False


def test_run_gh_command_timeout():
    """Returns (False, 'Command timed out') on TimeoutExpired."""
    manager = _make_manager_with_cli(available=True)

    with patch("subprocess.run", side_effect=subprocess.TimeoutExpired("gh", GH_CLI_COMMAND_TIMEOUT)):
        success, output = manager._run_gh_command(["issue", "list"])

    assert success is False
    assert "timed out" in output


def test_run_gh_command_generic_exception():
    """Returns (False, str(e)) on unexpected exceptions."""
    manager = _make_manager_with_cli(available=True)

    with patch("subprocess.run", side_effect=RuntimeError("some error")):
        success, output = manager._run_gh_command(["issue", "list"])

    assert success is False
    assert "some error" in output


# ---------------------------------------------------------------------------
# create_validation_issue
# ---------------------------------------------------------------------------


def test_create_validation_issue_success():
    """Returns the parsed issue number on success."""
    manager = _make_manager_with_cli(available=True)

    cmd_result = MagicMock()
    cmd_result.returncode = 0
    cmd_result.stdout = "https://github.com/mgifford/eu-plus-government-scans/issues/123\n"

    with patch("subprocess.run", return_value=cmd_result):
        issue_number = manager.create_validation_issue("cycle-2024-01")

    assert issue_number == 123


def test_create_validation_issue_bad_url_format():
    """Returns None when stdout cannot be parsed as an issue URL."""
    manager = _make_manager_with_cli(available=True)

    cmd_result = MagicMock()
    cmd_result.returncode = 0
    cmd_result.stdout = "not-a-url\n"

    with patch("subprocess.run", return_value=cmd_result):
        issue_number = manager.create_validation_issue("cycle-2024-01")

    assert issue_number is None


def test_create_validation_issue_command_fails():
    """Returns None when the CLI command fails."""
    manager = _make_manager_with_cli(available=True)

    cmd_result = MagicMock()
    cmd_result.returncode = 1
    cmd_result.stdout = ""

    with patch("subprocess.run", return_value=cmd_result):
        issue_number = manager.create_validation_issue("cycle-2024-01")

    assert issue_number is None


def test_create_validation_issue_no_cli():
    """Returns None when the CLI is not available."""
    manager = _make_manager_with_cli(available=False)
    issue_number = manager.create_validation_issue("cycle-2024-01")
    assert issue_number is None


# ---------------------------------------------------------------------------
# update_issue_progress
# ---------------------------------------------------------------------------


def test_update_issue_progress_calls_gh():
    """update_issue_progress invokes 'gh issue edit' with the correct issue number."""
    manager = _make_manager_with_cli(available=True)

    calls = []

    def _fake_run(cmd, **kwargs):
        calls.append(cmd)
        result = MagicMock()
        result.returncode = 0
        result.stdout = ""
        return result

    with patch("subprocess.run", side_effect=_fake_run):
        manager.update_issue_progress(
            issue_number=42,
            cycle_id="cycle-1",
            total=10,
            completed=5,
            processing=1,
            pending=4,
            failed=0,
        )

    assert any("42" in str(c) for c in calls)
    assert any("edit" in c for c in calls[0])


def test_update_issue_progress_complete_status():
    """When all countries are done the status emoji becomes 🟢."""
    manager = _make_manager_with_cli(available=True)
    captured_body = []

    def _fake_run(cmd, **kwargs):
        # Capture the body argument
        if "--body" in cmd:
            idx = cmd.index("--body")
            captured_body.append(cmd[idx + 1])
        result = MagicMock()
        result.returncode = 0
        result.stdout = ""
        return result

    with patch("subprocess.run", side_effect=_fake_run):
        manager.update_issue_progress(
            issue_number=42,
            cycle_id="cycle-1",
            total=10,
            completed=10,
            processing=0,
            pending=0,
            failed=0,
        )

    assert len(captured_body) == 1
    assert "🟢" in captured_body[0]


def test_update_issue_progress_zero_total():
    """With total=0 the progress percentage is 0% (no ZeroDivisionError)."""
    manager = _make_manager_with_cli(available=True)

    result = MagicMock()
    result.returncode = 0
    result.stdout = ""

    with patch("subprocess.run", return_value=result):
        # Should not raise
        manager.update_issue_progress(
            issue_number=1,
            cycle_id="c",
            total=0,
            completed=0,
            processing=0,
            pending=0,
            failed=0,
        )


# ---------------------------------------------------------------------------
# close_validation_issue
# ---------------------------------------------------------------------------


def test_close_validation_issue_calls_edit_then_close():
    """close_validation_issue first edits the body then closes the issue."""
    manager = _make_manager_with_cli(available=True)

    verbs_seen = []

    def _fake_run(cmd, **kwargs):
        verbs_seen.append(cmd[1])  # 'issue'
        verbs_seen.append(cmd[2])  # 'edit' or 'close'
        result = MagicMock()
        result.returncode = 0
        result.stdout = ""
        return result

    with patch("subprocess.run", side_effect=_fake_run):
        manager.close_validation_issue(
            issue_number=99,
            cycle_id="cycle-x",
            total=5,
            completed=5,
            failed=0,
        )

    # Both 'edit' and 'close' should have been called
    assert "edit" in verbs_seen
    assert "close" in verbs_seen


# ---------------------------------------------------------------------------
# add_comment / reopen_issue
# ---------------------------------------------------------------------------


def test_add_comment_calls_gh():
    """add_comment calls 'gh issue comment'."""
    manager = _make_manager_with_cli(available=True)
    calls = []

    def _fake_run(cmd, **kwargs):
        calls.append(cmd)
        r = MagicMock()
        r.returncode = 0
        r.stdout = ""
        return r

    with patch("subprocess.run", side_effect=_fake_run):
        manager.add_comment(7, "Hello from test!")

    assert any("comment" in c for c in calls[0])
    assert any("7" in str(c) for c in calls[0])


def test_reopen_issue_calls_gh():
    """reopen_issue calls 'gh issue reopen'."""
    manager = _make_manager_with_cli(available=True)
    calls = []

    def _fake_run(cmd, **kwargs):
        calls.append(cmd)
        r = MagicMock()
        r.returncode = 0
        r.stdout = ""
        return r

    with patch("subprocess.run", side_effect=_fake_run):
        manager.reopen_issue(7)

    assert any("reopen" in c for c in calls[0])
    assert any("7" in str(c) for c in calls[0])


# ---------------------------------------------------------------------------
# find_open_validation_issue
# ---------------------------------------------------------------------------


def test_find_open_validation_issue_returns_number():
    """Returns the issue number when one is found."""
    manager = _make_manager_with_cli(available=True)

    cmd_result = MagicMock()
    cmd_result.returncode = 0
    cmd_result.stdout = "55\n"

    with patch("subprocess.run", return_value=cmd_result):
        number = manager.find_open_validation_issue()

    assert number == 55


def test_find_open_validation_issue_empty_output():
    """Returns None when command succeeds but output is empty."""
    manager = _make_manager_with_cli(available=True)

    cmd_result = MagicMock()
    cmd_result.returncode = 0
    cmd_result.stdout = ""

    with patch("subprocess.run", return_value=cmd_result):
        number = manager.find_open_validation_issue()

    assert number is None


def test_find_open_validation_issue_non_numeric_output():
    """Returns None when output cannot be parsed as an integer."""
    manager = _make_manager_with_cli(available=True)

    cmd_result = MagicMock()
    cmd_result.returncode = 0
    cmd_result.stdout = "null"

    with patch("subprocess.run", return_value=cmd_result):
        number = manager.find_open_validation_issue()

    assert number is None


def test_find_open_validation_issue_command_fails():
    """Returns None when the CLI command fails."""
    manager = _make_manager_with_cli(available=True)

    cmd_result = MagicMock()
    cmd_result.returncode = 1
    cmd_result.stdout = ""

    with patch("subprocess.run", return_value=cmd_result):
        number = manager.find_open_validation_issue()

    assert number is None


def test_find_open_validation_issue_no_cli():
    """Returns None when CLI is not available."""
    manager = _make_manager_with_cli(available=False)
    number = manager.find_open_validation_issue()
    assert number is None


# ---------------------------------------------------------------------------
# Custom repo argument
# ---------------------------------------------------------------------------


def test_custom_repo_is_stored():
    """The repo argument is stored on the instance."""
    check_result = MagicMock()
    check_result.returncode = 0
    with patch("subprocess.run", return_value=check_result):
        manager = GitHubIssueManager(repo="other/repo")
    assert manager.repo == "other/repo"
