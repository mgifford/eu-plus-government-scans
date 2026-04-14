"""Tests for Generate Scan Progress workflow artifact contents."""

from pathlib import Path


def test_generate_scan_progress_workflow_uploads_scan_progress_data_json() -> None:
    """Workflow artifact should include scan-progress drilldown JSON."""
    workflow_path = Path(".github/workflows/generate-scan-progress.yml")
    content = workflow_path.read_text(encoding="utf-8")
    upload_section = content.partition("- name: Upload progress report artifact")[2]
    assert upload_section, "Upload progress report artifact step is missing from workflow."

    upload_path_block = upload_section.partition("retention-days:")[0]
    assert upload_path_block, "Could not find artifact path block before retention-days."

    assert "Upload progress report artifact" in content
    assert "docs/scan-progress-data.json" in upload_path_block
