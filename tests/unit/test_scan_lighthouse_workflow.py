"""Tests for the Lighthouse scan workflow defaults."""

from pathlib import Path


def test_scan_lighthouse_workflow_concurrency_default() -> None:
    """Workflow should document and use its configured Lighthouse concurrency.

    The default was raised from 3 to 5 in the "ci: fix scan progress commit and
    lighthouse pace guard" change; this test guards that the documentation,
    input default, and both invocation/summary uses stay in sync.
    """
    workflow_path = Path(".github/workflows/scan-lighthouse.yml")
    content = workflow_path.read_text(encoding="utf-8")

    assert "Maximum parallel Lighthouse processes (default: 5)" in content
    assert "default: '5'" in content
    assert '--concurrency "${{ github.event.inputs.concurrency || \'5\' }}" \\' in content
    assert "- Concurrency: ${{ github.event.inputs.concurrency || '5' }} parallel processes" in content
