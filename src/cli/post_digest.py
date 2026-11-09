"""Publish one reviewed weekly-digest draft to Mastodon.

This runs only from the "Post weekly digest to Mastodon" workflow, which a
maintainer starts by hand after reviewing a digest issue.  The draft is read
from the issue as it stands, so the reviewer's edits are what gets posted.

It refuses to post when:

* the issue was not opened by the digest workflow, lacks the ``digest-draft``
  label, or is closed;
* the draft is missing, longer than Mastodon allows, or @-mentions anyone;
* the issue already records that this draft was posted;
* the account is not marked as automated (Mastodon's "This is an automated
  account" setting), which Mastodon shows as a bot badge.

The instance URL and access token are read from the environment, set from
repository secrets by the workflow, and are never printed.  ``--dry-run`` runs
every check that needs no account and prints the text, without either.

Usage::

    python3 -m src.cli.post_digest --issue-json issue.json --draft 1 --dry-run
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

import httpx

from src.lib.digest_drafts import (
    MAX_POST_CHARS,
    extract_draft,
    post_length,
    post_problems,
    posted_marker,
)

DRAFT_LABEL = "digest-draft"
DRAFT_AUTHOR = "github-actions[bot]"
TIMEOUT_SECONDS = 30.0
USER_AGENT = "eu-plus-government-scans weekly digest"


class PostingError(Exception):
    """Raised when a draft must not, or could not, be posted."""


def load_draft(issue: dict, number: int, comments: str = "") -> str:
    """Return draft *number* from a digest issue, after checking it may be posted.

    Args:
        issue: The issue as returned by the GitHub REST API.
        number: Draft number within the issue.
        comments: Text of the issue's comments, to detect an earlier posting.

    Returns:
        The draft text.

    Raises:
        PostingError: If the issue or the draft fails a check.
    """
    login = (issue.get("user") or {}).get("login")
    if login != DRAFT_AUTHOR:
        raise PostingError(f"the issue was opened by {login!r}, not by the digest workflow")
    if "pull_request" in issue:
        raise PostingError("that number is a pull request, not a digest issue")
    labels = {label.get("name") for label in issue.get("labels", []) if isinstance(label, dict)}
    if DRAFT_LABEL not in labels:
        raise PostingError(f"the issue does not carry the {DRAFT_LABEL!r} label")
    if issue.get("state") != "open":
        raise PostingError("the issue is closed")
    if posted_marker(number) in comments:
        raise PostingError(f"draft {number} has already been posted from this issue")

    text = extract_draft(issue.get("body") or "", number)
    if text is None:
        raise PostingError(f"the issue has no draft {number}, or its markers were edited away")
    problems = post_problems(text)
    if problems:
        raise PostingError("; ".join(problems))
    return text


def idempotency_key(issue_number: object, draft_number: int, text: str) -> str:
    """Return a key that makes Mastodon ignore an accidental repeat of a post."""
    return hashlib.sha256(f"{issue_number}:{draft_number}:{text}".encode()).hexdigest()


def instance_client(
    base_url: str, token: str, transport: httpx.BaseTransport | None = None
) -> httpx.Client:
    """Return an HTTP client for the Mastodon instance.

    Args:
        base_url: Instance URL, e.g. ``https://mastodon.example``.
        token: Access token with the ``write:statuses`` scope, plus
            ``profile`` (Mastodon 4.3 and later) or ``read:accounts``.
        transport: Replacement transport, for tests.

    Returns:
        A configured client.

    Raises:
        PostingError: If the URL is not HTTPS.
    """
    if not base_url.startswith("https://"):
        raise PostingError("MASTODON_INSTANCE_URL must start with https://")
    return httpx.Client(
        base_url=base_url.rstrip("/"),
        headers={"Authorization": f"Bearer {token}", "User-Agent": USER_AGENT},
        timeout=TIMEOUT_SECONDS,
        transport=transport,
    )


def _check_response(response: httpx.Response, action: str) -> dict:
    """Return the JSON body of a successful response, or raise.

    Args:
        response: The instance's response.
        action: What was being attempted, for the error message.

    Returns:
        The decoded body.

    Raises:
        PostingError: If the request failed or the body is not a JSON object.
    """
    try:
        body = response.json()
    except ValueError:
        body = {}
    if not response.is_success:
        detail = body.get("error", "") if isinstance(body, dict) else ""
        raise PostingError(f"could not {action}: HTTP {response.status_code} {detail}".strip())
    if not isinstance(body, dict):
        raise PostingError(f"could not {action}: unexpected response")
    return body


def check_bot_account(client: httpx.Client) -> str:
    """Confirm the account is marked as automated and return its handle.

    Args:
        client: Client for the instance.

    Returns:
        The account's handle.

    Raises:
        PostingError: If the account is not marked as a bot.
    """
    account = _check_response(
        client.get("/api/v1/accounts/verify_credentials"), "check the account"
    )
    if account.get("bot") is not True:
        raise PostingError(
            "the account is not marked as automated; turn on 'This is an automated "
            "account' in its profile settings and run again"
        )
    return str(account.get("acct", ""))


def publish(client: httpx.Client, text: str, key: str) -> str:
    """Post *text* as a public status and return its URL.

    Args:
        client: Client for the instance.
        text: Status text.
        key: Idempotency key, so a retried request cannot post twice.

    Returns:
        URL of the new status.
    """
    status = _check_response(
        client.post(
            "/api/v1/statuses",
            data={"status": text, "visibility": "public", "language": "en"},
            headers={"Idempotency-Key": key},
        ),
        "post the status",
    )
    return str(status.get("url") or status.get("uri") or "")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--issue-json", type=Path, required=True, help="Issue JSON from the GitHub REST API."
    )
    parser.add_argument("--draft", type=int, required=True, help="Draft number in the issue.")
    parser.add_argument(
        "--comments-file", type=Path, default=None, help="Text of the issue's comments."
    )
    parser.add_argument(
        "--result-file", type=Path, default=None, help="Where to write the posted URL as JSON."
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Check and print the draft without posting."
    )
    return parser.parse_args(argv)


def _post(issue_number: object, draft: int, text: str, transport: httpx.BaseTransport | None) -> dict:
    """Post a checked draft with the credentials from the environment."""
    base_url = os.environ.get("MASTODON_INSTANCE_URL", "").strip()
    token = os.environ.get("MASTODON_ACCESS_TOKEN", "").strip()
    if not base_url or not token:
        raise PostingError("MASTODON_INSTANCE_URL and MASTODON_ACCESS_TOKEN must both be set")
    try:
        with instance_client(base_url, token, transport) as client:
            account = check_bot_account(client)
            url = publish(client, text, idempotency_key(issue_number, draft, text))
    except httpx.HTTPError as exc:
        raise PostingError(f"could not reach the instance: {type(exc).__name__}") from exc
    return {"issue": issue_number, "draft": draft, "account": account, "url": url}


def main(argv: list[str] | None = None, transport: httpx.BaseTransport | None = None) -> int:
    """Entry point.

    Args:
        argv: Command-line arguments.
        transport: Replacement HTTP transport, for tests.

    Returns:
        0 when the draft was posted or previewed, 1 when it was refused.
    """
    args = parse_args(argv)
    try:
        issue = json.loads(args.issue_json.read_text(encoding="utf-8"))
        if not isinstance(issue, dict):
            raise PostingError("the issue file does not hold an issue")
        comments = args.comments_file.read_text(encoding="utf-8") if args.comments_file else ""
        text = load_draft(issue, args.draft, comments)
        print(
            f"Draft {args.draft} from issue #{issue.get('number')} "
            f"({post_length(text)} of {MAX_POST_CHARS} characters):\n\n{text}\n"
        )
        if args.dry_run:
            print("Dry run: nothing was posted.")
            return 0
        result = _post(issue.get("number"), args.draft, text, transport)
    except (OSError, json.JSONDecodeError, PostingError) as exc:
        print(f"Not posted: {exc}", file=sys.stderr)
        return 1

    print(f"Posted as {result['account']}: {result['url']}")
    if args.result_file:
        args.result_file.write_text(json.dumps(result) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
