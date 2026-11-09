"""Guards on the two weekly-digest workflows.

Drafting and posting are split so that nothing reaches Mastodon without a
maintainer choosing it.  These tests pin the properties that split relies on.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

import yaml

from src.lib.metadata_merge import ARTIFACT_TABLES

REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOWS = REPO_ROOT / ".github" / "workflows"
DRAFT = WORKFLOWS / "weekly-digest.yml"
POST = WORKFLOWS / "post-digest.yml"


def _load(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _triggers(workflow: dict) -> dict:
    # PyYAML reads a bare `on:` key as the boolean True.
    return workflow.get("on") or workflow.get(True) or {}


def _steps(workflow: dict) -> list[dict]:
    return [step for job in workflow["jobs"].values() for step in job["steps"]]


def _argparse_flags(module: str) -> set[str]:
    tree = ast.parse((REPO_ROOT / "src" / "cli" / f"{module}.py").read_text(encoding="utf-8"))
    return {
        arg.value
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and getattr(node.func, "attr", "") == "add_argument"
        for arg in node.args
        if isinstance(arg, ast.Constant) and str(arg.value).startswith("--")
    }


class TestPostingWorkflow:
    def test_runs_only_when_started_by_hand(self) -> None:
        assert set(_triggers(_load(POST))) == {"workflow_dispatch"}

    def test_previews_unless_told_otherwise(self) -> None:
        dry_run = _triggers(_load(POST))["workflow_dispatch"]["inputs"]["dry_run"]
        assert dry_run["type"] == "boolean"
        assert dry_run["default"] is True

    def test_only_the_posting_step_sees_the_mastodon_secrets(self) -> None:
        holders = [
            step["name"] for step in _steps(_load(POST))
            if "MASTODON_" in yaml.safe_dump(step)
        ]
        assert holders == ["Check and post the draft"]

    def test_flags_exist(self) -> None:
        run = next(s["run"] for s in _steps(_load(POST)) if s.get("name") == "Check and post the draft")
        assert set(re.findall(r"--[a-z][a-z-]+", run)) <= _argparse_flags("post_digest")


class TestDraftWorkflow:
    def test_never_touches_mastodon(self) -> None:
        assert "MASTODON" not in DRAFT.read_text(encoding="utf-8")
        assert "post_digest" not in DRAFT.read_text(encoding="utf-8")

    def test_fetches_known_artifacts_and_uploads_none_it_does_not_own(self) -> None:
        steps = _steps(_load(DRAFT))
        names = {
            name
            for step in steps
            for name in step.get("env", {}).get("FETCH_ARTIFACT_NAMES", "").split()
        }
        assert names == {"accessibility-metadata", "social-media-metadata"}
        assert names <= set(ARTIFACT_TABLES)

        uploads = [
            step["with"]["name"] for step in steps
            if str(step.get("uses", "")).startswith("actions/upload-artifact")
        ]
        assert uploads and not set(uploads) & set(ARTIFACT_TABLES)

    def test_flags_exist(self) -> None:
        run = next(s["run"] for s in _steps(_load(DRAFT)) if s.get("name") == "Draft posts")
        assert set(re.findall(r"--[a-z][a-z-]+", run)) <= _argparse_flags("generate_weekly_digest")


def test_inputs_reach_scripts_only_through_the_environment() -> None:
    """Interpolating an input into a script lets its text run as shell."""
    for path in (DRAFT, POST):
        for step in _steps(_load(path)):
            assert "${{ inputs." not in step.get("run", ""), (path.name, step.get("name"))
