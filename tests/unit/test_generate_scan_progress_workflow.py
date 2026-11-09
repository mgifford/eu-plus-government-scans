"""Tests for Generate Scan Progress workflow artifact contents."""

import re
import subprocess
from pathlib import Path

import pytest
import yaml


def test_generate_scan_progress_workflow_uploads_scan_progress_data_json() -> None:
    """Workflow artifact should include scan-progress drilldown JSON."""
    workflow_path = Path(".github/workflows/generate-scan-progress.yml")
    workflow = yaml.safe_load(workflow_path.read_text(encoding="utf-8"))

    jobs = workflow.get("jobs", {})
    steps = jobs.get("generate-progress-report", {}).get("steps", [])
    upload_step = next(
        (step for step in steps if step.get("name") == "Upload progress report artifact"),
        None,
    )

    assert upload_step is not None, "Upload progress report artifact step is missing."

    upload_path = upload_step.get("with", {}).get("path", "")
    assert "docs/scan-progress-data.json" in upload_path


def test_generate_scan_progress_workflow_installs_dependencies_with_pip() -> None:
    """Workflow should use setup-python and pip install for dependencies."""
    workflow_path = Path(".github/workflows/generate-scan-progress.yml")
    workflow = yaml.safe_load(workflow_path.read_text(encoding="utf-8"))

    steps = workflow.get("jobs", {}).get("generate-progress-report", {}).get("steps", [])
    setup_python_step = next((step for step in steps if step.get("name") == "Set up Python"), None)
    install_step = next((step for step in steps if step.get("name") == "Install dependencies"), None)

    assert setup_python_step is not None, "Set up Python step is missing."
    assert setup_python_step.get("uses") == "actions/setup-python@v6"
    assert setup_python_step.get("with", {}).get("cache") == "pip"
    assert install_step is not None, "Install dependencies step is missing."
    assert install_step.get("run", "").strip() == "pip install -r requirements.txt"


def test_correlation_report_cannot_block_other_reports() -> None:
    """The slow correlation step must be capped and allowed to fail.

    Its growth froze every published report from 2026-10-18 to 2026-11-08,
    because the whole job timed out before the commit step.  The step cap
    must sit below the job timeout, and a later step must warn when the
    report did not finish.
    """
    workflow_path = Path(".github/workflows/generate-scan-progress.yml")
    workflow = yaml.safe_load(workflow_path.read_text(encoding="utf-8"))

    job = workflow.get("jobs", {}).get("generate-progress-report", {})
    steps = job.get("steps", [])
    step = next((s for s in steps if s.get("id") == "tech_lighthouse"), None)

    assert step is not None, "Correlation report step (id: tech_lighthouse) is missing."
    assert step.get("continue-on-error") is True
    assert 0 < step.get("timeout-minutes", 0) < job.get("timeout-minutes", 0)
    assert any(
        "steps.tech_lighthouse.outcome" in str(s.get("if", ""))
        for s in steps[steps.index(step) + 1:]
    ), "No later step warns when the correlation report did not finish."


def _commit_step_paths(steps: list[dict]) -> list[str]:
    """Return the paths the commit step passes to ``git add``."""
    step = next((s for s in steps if s.get("name") == "Commit progress report to repository"), None)
    assert step is not None, "Commit progress report to repository step is missing."
    match = re.search(r"git add ((?:[^\n]*\\\n)*[^\n]*)", step.get("run", ""))
    assert match is not None, "The commit step no longer runs git add."
    return match.group(1).replace("\\\n", " ").split()


def test_commit_step_stages_every_tracked_file_the_workflow_writes() -> None:
    """A tracked report left out of ``git add`` blocks the push.

    The commit step runs ``git pull --rebase`` after committing, and git
    refuses to rebase while a tracked file has unstaged changes.  That is how
    docs/user-preferences.md, regenerated on every run but never staged, failed
    the first run to reach the commit step after the 2026-11 freeze.
    """
    workflow_path = Path(".github/workflows/generate-scan-progress.yml")
    workflow = yaml.safe_load(workflow_path.read_text(encoding="utf-8"))
    steps = workflow.get("jobs", {}).get("generate-progress-report", {}).get("steps", [])

    written = {
        path
        for step in steps
        for path in re.findall(
            r"(?:--(?:page|output|update-index|index|data|csv)\s+|>\s*)(docs/[^\s\;]+)",
            step.get("run", ""),
        )
    }
    assert "docs/user-preferences.md" in written, "Output paths are no longer found."

    try:
        listed = subprocess.run(
            ["git", "ls-files", "--", *sorted(written)],
            capture_output=True, check=True, text=True,
        ).stdout.split()
    except (OSError, subprocess.CalledProcessError):
        pytest.skip("needs a git checkout to tell which reports are tracked")

    staged = _commit_step_paths(steps)
    missing = [
        path for path in listed
        if not any(path == entry or path.startswith(entry.rstrip("/") + "/") for entry in staged)
    ]
    assert missing == [], f"Tracked reports the commit step never stages: {missing}"
