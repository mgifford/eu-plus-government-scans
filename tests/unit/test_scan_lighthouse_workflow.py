"""Tests for the Lighthouse scan workflow defaults."""

from pathlib import Path


def test_scan_lighthouse_workflow_uses_safer_ci_concurrency_default() -> None:
    """Workflow should default to the documented Lighthouse CI concurrency."""
    workflow_path = Path(".github/workflows/scan-lighthouse.yml")
    content = workflow_path.read_text(encoding="utf-8")

    assert "Maximum parallel Lighthouse processes (default: 3)" in content
    assert "default: '3'" in content
    assert '--concurrency "${{ github.event.inputs.concurrency || \'3\' }}" \\' in content
    assert "- Concurrency: ${{ github.event.inputs.concurrency || '3' }} parallel processes" in content
