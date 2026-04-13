"""Tests for GitHub Pages deployment workflow safeguards."""

from pathlib import Path


def test_deploy_pages_workflow_validates_required_drilldown_json_files() -> None:
    """Deploy workflow should fail fast if required drilldown JSON files are missing."""
    workflow_path = Path(".github/workflows/deploy-pages.yml")
    content = workflow_path.read_text(encoding="utf-8")

    assert "Validate required drilldown JSON files" in content
    assert "docs/social-media-data.json" in content
    assert "docs/technology-data.json" in content
    assert "docs/accessibility-data.json" in content
    assert "docs/third-party-tools-data.json" in content
    assert "docs/scan-progress-data.json" in content
    assert "GitHub Pages build stopped because one or more drilldown JSON files are missing." in content


def test_deploy_pages_workflow_hydrates_scan_progress_artifacts() -> None:
    """Deploy workflow should hydrate JSON files from scan-progress artifacts."""
    workflow_path = Path(".github/workflows/deploy-pages.yml")
    content = workflow_path.read_text(encoding="utf-8")

    assert "Download scan-progress artifact from triggering workflow run" in content
    assert "Find latest scan-progress artifact run ID" in content
    assert "Download latest scan-progress artifact" in content
    assert "pattern: scan-progress-report-*" in content
    assert "Hydrate drilldown JSON files for site build" in content
