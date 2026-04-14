"""Tests for Generate Scan Progress workflow artifact contents."""

from pathlib import Path


def test_generate_scan_progress_workflow_uploads_scan_progress_data_json() -> None:
    """Workflow artifact should include scan-progress drilldown JSON."""
    workflow_path = Path(".github/workflows/generate-scan-progress.yml")
    content = workflow_path.read_text(encoding="utf-8")
    upload_section = content.split("- name: Upload progress report artifact", maxsplit=1)[1]
    upload_path_block = upload_section.split("retention-days:", maxsplit=1)[0]

    assert "Upload progress report artifact" in content
    assert "docs/scan-progress-data.json" in upload_path_block
