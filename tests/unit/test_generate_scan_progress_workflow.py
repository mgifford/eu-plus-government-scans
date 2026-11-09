"""Tests for Generate Scan Progress workflow artifact contents."""

from pathlib import Path

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
