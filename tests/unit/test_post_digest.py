"""Tests for publishing a reviewed digest draft.

No test talks to a real Mastodon instance: every HTTP request goes to an
``httpx.MockTransport`` that records it, so the checks that must stop a post
can be shown to stop it before any request is made.
"""

from __future__ import annotations

import json
from pathlib import Path

import httpx
import pytest

import src.cli.post_digest as post
from src.lib.digest_drafts import posted_marker, render_draft

TOKEN = "test-token-not-real"
DRAFT_TEXT = "Government web scan: 3 pages changed. All pages: https://example.org/e.json"


def _issue(**overrides: object) -> dict:
    issue = {
        "number": 42,
        "state": "open",
        "user": {"login": "github-actions[bot]"},
        "labels": [{"name": "digest-draft"}],
        "body": "Intro\n\n" + render_draft(1, DRAFT_TEXT) + "\n",
    }
    issue.update(overrides)
    return issue


class FakeInstance:
    """A Mastodon instance that records requests instead of posting."""

    def __init__(self, bot: bool = True, status_code: int = 200) -> None:
        self.bot = bot
        self.status_code = status_code
        self.requests: list[httpx.Request] = []

    def __call__(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        if request.url.path == "/api/v1/accounts/verify_credentials":
            return httpx.Response(200, json={"acct": "digest", "bot": self.bot})
        if request.url.path == "/api/v1/statuses":
            if self.status_code != 200:
                return httpx.Response(self.status_code, json={"error": "Validation failed"})
            return httpx.Response(200, json={"url": "https://social.example/@digest/1"})
        return httpx.Response(404)

    @property
    def transport(self) -> httpx.MockTransport:
        return httpx.MockTransport(self)

    @property
    def posts(self) -> list[httpx.Request]:
        return [r for r in self.requests if r.url.path == "/api/v1/statuses"]


@pytest.fixture
def credentials(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MASTODON_INSTANCE_URL", "https://social.example")
    monkeypatch.setenv("MASTODON_ACCESS_TOKEN", TOKEN)


def _run(tmp_path: Path, issue: dict, instance: FakeInstance, *extra: str,
         comments: str = "") -> int:
    issue_path = tmp_path / "issue.json"
    issue_path.write_text(json.dumps(issue), encoding="utf-8")
    comments_path = tmp_path / "comments.txt"
    comments_path.write_text(comments, encoding="utf-8")
    return post.main(
        ["--issue-json", str(issue_path), "--comments-file", str(comments_path),
         "--draft", "1", "--result-file", str(tmp_path / "result.json"), *extra],
        transport=instance.transport,
    )


class TestPosting:
    def test_posts_the_reviewed_text_once_with_an_idempotency_key(
        self, tmp_path: Path, credentials: None
    ) -> None:
        instance = FakeInstance()

        assert _run(tmp_path, _issue(), instance) == 0

        (request,) = instance.posts
        assert request.headers["Authorization"] == f"Bearer {TOKEN}"
        assert request.headers["Idempotency-Key"] == post.idempotency_key(42, 1, DRAFT_TEXT)
        form = dict(httpx.QueryParams(request.content.decode()))
        assert form == {"status": DRAFT_TEXT, "visibility": "public", "language": "en"}
        result = json.loads((tmp_path / "result.json").read_text(encoding="utf-8"))
        assert result["url"] == "https://social.example/@digest/1"

    def test_reviewer_edits_are_what_gets_posted(self, tmp_path: Path, credentials: None) -> None:
        issue = _issue(body=render_draft(1, "Edited by the maintainer."))
        instance = FakeInstance()

        assert _run(tmp_path, issue, instance) == 0
        form = dict(httpx.QueryParams(instance.posts[0].content.decode()))
        assert form["status"] == "Edited by the maintainer."

    def test_dry_run_sends_nothing_and_needs_no_credentials(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        instance = FakeInstance()

        assert _run(tmp_path, _issue(), instance, "--dry-run") == 0
        assert instance.requests == []
        assert DRAFT_TEXT in capsys.readouterr().out


class TestRefusals:
    """Every refusal must happen before a status is sent."""

    @pytest.mark.parametrize(
        "issue",
        [
            _issue(user={"login": "someone-else"}),
            _issue(labels=[]),
            _issue(state="closed"),
            _issue(pull_request={}),
            _issue(body="no drafts here"),
            _issue(body=render_draft(1, "Thanks @agency@social.example!")),
            _issue(body=render_draft(1, "x" * 501)),
        ],
        ids=["author", "label", "closed", "pull-request", "no-draft", "mention", "too-long"],
    )
    def test_bad_issue_or_draft(self, tmp_path: Path, credentials: None, issue: dict) -> None:
        instance = FakeInstance()

        assert _run(tmp_path, issue, instance) == 1
        assert instance.posts == []

    def test_already_posted(self, tmp_path: Path, credentials: None) -> None:
        instance = FakeInstance()

        code = _run(tmp_path, _issue(), instance, comments=f"{posted_marker(1)}\nPosted")

        assert code == 1
        assert instance.requests == []

    def test_account_not_marked_as_bot(self, tmp_path: Path, credentials: None,
                                       capsys: pytest.CaptureFixture[str]) -> None:
        instance = FakeInstance(bot=False)

        assert _run(tmp_path, _issue(), instance) == 1
        assert instance.posts == []
        assert "automated account" in capsys.readouterr().err

    def test_missing_credentials(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("MASTODON_INSTANCE_URL", raising=False)
        monkeypatch.delenv("MASTODON_ACCESS_TOKEN", raising=False)
        instance = FakeInstance()

        assert _run(tmp_path, _issue(), instance) == 1
        assert instance.requests == []

    def test_plain_http_instance(self, tmp_path: Path, credentials: None,
                                 monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("MASTODON_INSTANCE_URL", "http://social.example")
        instance = FakeInstance()

        assert _run(tmp_path, _issue(), instance) == 1
        assert instance.requests == []

    def test_server_error_is_reported_without_the_token(
        self, tmp_path: Path, credentials: None, capsys: pytest.CaptureFixture[str]
    ) -> None:
        instance = FakeInstance(status_code=422)

        assert _run(tmp_path, _issue(), instance) == 1
        captured = capsys.readouterr()
        assert "HTTP 422 Validation failed" in captured.err
        assert TOKEN not in captured.out + captured.err
        assert not (tmp_path / "result.json").exists()
