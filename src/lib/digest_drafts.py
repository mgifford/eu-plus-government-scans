"""Rules every weekly-digest post must meet, shared by drafting and posting.

Drafts are written by :mod:`src.cli.generate_weekly_digest` into a GitHub issue,
reviewed and possibly edited there by a maintainer, and read back from the issue
by :mod:`src.cli.post_digest`.  Both sides check the same rules, so a draft that
was edited into breaking one is refused at posting time rather than published.

The markers below delimit each draft inside the issue body.  They are HTML
comments, so they do not render, and they survive ordinary edits to the text
between them.
"""

from __future__ import annotations

import re

# Mastodon's default status limit.  Instances can raise it; none lower it.
MAX_POST_CHARS = 500

# Mastodon counts every link as 23 characters, however long the URL is.
URL_CHARS = 23

# A URL as Mastodon's counter sees it: trailing punctuation is not part of it.
_URL_RE = re.compile(r"https?://\S*[^\s.,;:!?)\]'\"]")

# An @-mention: "@" that does not follow a word character (so e-mail addresses
# and "/@user" URL paths do not match), then a username.
_MENTION_RE = re.compile(r"(?<![\w/])@[A-Za-z0-9_]+(?:@[A-Za-z0-9.-]+)?")

_DRAFT_START = "<!-- digest-draft:{n} -->"
_DRAFT_END = "<!-- /digest-draft:{n} -->"
_POSTED = "<!-- digest-posted:{n} -->"


def post_length(text: str) -> int:
    """Return the length Mastodon will count for *text*.

    Args:
        text: Post text.

    Returns:
        Character count with every link counted as :data:`URL_CHARS`.
    """
    return len(_URL_RE.sub("x" * URL_CHARS, text))


def find_mentions(text: str) -> list[str]:
    """Return every @-mention in *text*, ignoring those inside links.

    Mentions notify real accounts, so digest posts link to agencies instead.

    Args:
        text: Post text.

    Returns:
        The mentions found, in order.
    """
    return _MENTION_RE.findall(_URL_RE.sub(" ", text))


def post_problems(text: str) -> list[str]:
    """Return the reasons *text* cannot be posted, or an empty list.

    Args:
        text: Post text.

    Returns:
        Human-readable problems; empty when the text may be posted.
    """
    problems: list[str] = []
    if not text.strip():
        problems.append("the draft is empty")
    length = post_length(text)
    if length > MAX_POST_CHARS:
        problems.append(f"the draft is {length} characters; the limit is {MAX_POST_CHARS}")
    mentions = find_mentions(text)
    if mentions:
        problems.append(
            "the draft mentions accounts, which would notify them: " + ", ".join(mentions)
        )
    return problems


def render_draft(number: int, text: str) -> str:
    """Wrap *text* in the markers that let it be read back from an issue.

    The text sits in a fenced block so GitHub shows it verbatim.

    Args:
        number: Draft number within the issue, starting at 1.
        text: Post text.

    Returns:
        Markdown for the issue body.
    """
    return "\n".join(
        (_DRAFT_START.format(n=number), "```text", text, "```", _DRAFT_END.format(n=number))
    )


def extract_draft(body: str, number: int) -> str | None:
    """Read draft *number* back out of an issue body.

    Args:
        body: Issue body, possibly edited by a reviewer.
        number: Draft number.

    Returns:
        The draft text, or None if the markers are missing.
    """
    start = _DRAFT_START.format(n=number)
    end = _DRAFT_END.format(n=number)
    _, sep, rest = body.partition(start)
    if not sep:
        return None
    inner, sep, _ = rest.partition(end)
    if not sep:
        return None
    lines = inner.replace("\r\n", "\n").strip("\n").split("\n")
    if lines and lines[0].strip().startswith("```"):
        lines = lines[1:]
    if lines and lines[-1].strip().startswith("```"):
        lines = lines[:-1]
    return "\n".join(lines).strip()


def posted_marker(number: int) -> str:
    """Return the marker recorded on the issue once draft *number* is posted.

    Args:
        number: Draft number.

    Returns:
        An HTML comment unique to that draft.
    """
    return _POSTED.format(n=number)
