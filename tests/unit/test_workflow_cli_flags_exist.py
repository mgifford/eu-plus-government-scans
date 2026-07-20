"""Regression guard: every CLI flag a workflow_dispatch conditionally appends
to a scanner invocation must actually exist in that scanner's argparse.

This directly targets the bug found during the GitHub Actions orchestration
audit (WORKFLOW_ORCHESTRATION_AUDIT.md Section 1.4/14.4): scan-technology.yml
appended `--limit <value>` to the CLI call, but scan_technology.py had no
`--limit` argument defined at all -- any manual dispatch with `limit` set
would fail immediately with an argparse error.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOWS_DIR = REPO_ROOT / ".github" / "workflows"
CLI_DIR = REPO_ROOT / "src" / "cli"

# Maps a workflow file to the CLI module it invokes, for every scanner
# workflow that builds its argument list dynamically (ARGS+=(--flag ...)).
WORKFLOW_TO_CLI_MODULE = {
    "scan-accessibility.yml": "scan_accessibility.py",
    "scan-lighthouse.yml": "scan_lighthouse.py",
    "scan-social-media.yml": "scan_social_media.py",
    "scan-technology.yml": "scan_technology.py",
    "scan-third-party-js.yml": "scan_third_party_js.py",
    "scan-overlays.yml": "scan_overlays.py",
    "scan-relationships.yml": "scan_relationships.py",
    "validate-urls-batch.yml": "validate_urls_batch.py",
    "validate-urls.yml": "validate_urls.py",
}


def _argparse_flags(cli_path: Path) -> set[str]:
    """Extract every `--flag` string passed to add_argument() in a CLI file."""
    tree = ast.parse(cli_path.read_text(encoding="utf-8"))
    flags: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and getattr(node.func, "attr", None) == "add_argument":
            for arg in node.args:
                if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                    if arg.value.startswith("--"):
                        flags.add(arg.value)
    return flags


def _workflow_conditionally_appended_flags(workflow_path: Path) -> set[str]:
    """Extract every `--flag` appended via `ARGS+=(--flag ...)` in a workflow's
    run: blocks (the dynamic-argument-building pattern used by several
    scanner workflows to support optional inputs)."""
    content = workflow_path.read_text(encoding="utf-8")
    return set(re.findall(r"ARGS\+=\(\s*(--[\w-]+)", content))


def test_every_dynamically_appended_flag_exists_in_its_cli():
    missing: list[str] = []
    for workflow_name, cli_name in WORKFLOW_TO_CLI_MODULE.items():
        workflow_path = WORKFLOWS_DIR / workflow_name
        cli_path = CLI_DIR / cli_name
        if not workflow_path.exists() or not cli_path.exists():
            continue

        appended = _workflow_conditionally_appended_flags(workflow_path)
        if not appended:
            continue

        defined = _argparse_flags(cli_path)
        for flag in appended:
            if flag not in defined:
                missing.append(f"{workflow_name} appends {flag!r} but {cli_name} has no such argument")

    assert not missing, "\n".join(missing)


def test_scan_technology_has_max_urls_flag():
    """Direct regression test for the specific bug found: scan_technology.py
    must define --max-urls (the flag scan-technology.yml now maps its
    `limit` dispatch input onto)."""
    flags = _argparse_flags(CLI_DIR / "scan_technology.py")
    assert "--max-urls" in flags
    assert "--limit" not in flags  # confirms we didn't just rename the bug
