"""Tests for the post rules shared by digest drafting and posting."""

from __future__ import annotations

from src.lib.digest_drafts import (
    MAX_POST_CHARS,
    URL_CHARS,
    extract_draft,
    find_mentions,
    post_length,
    post_problems,
    posted_marker,
    render_draft,
)


class TestPostLength:
    def test_links_count_as_23_characters_however_long(self) -> None:
        url = "https://github.com/owner/repo/blob/main/docs/data/digest/2026-11-08.json"
        assert post_length(f"See {url}") == len("See ") + URL_CHARS

    def test_trailing_punctuation_is_not_part_of_the_link(self) -> None:
        assert post_length("https://example.org/page.") == URL_CHARS + 1

    def test_plain_text_counts_every_character(self) -> None:
        assert post_length("é" * 10) == 10


class TestMentions:
    def test_finds_local_and_remote_mentions(self) -> None:
        text = "Thanks @agency and @press@social.example for this"
        assert find_mentions(text) == ["@agency", "@press@social.example"]

    def test_ignores_email_addresses_and_profile_links(self) -> None:
        text = "Write to info@agency.example or see https://social.example/@agency"
        assert find_mentions(text) == []


class TestProblems:
    def test_a_clean_post_has_none(self) -> None:
        assert post_problems("Weekly scan: 3 pages changed.") == []

    def test_empty_long_and_mentioning_posts_are_refused(self) -> None:
        assert post_problems("   ")
        assert post_problems("x" * (MAX_POST_CHARS + 1))
        assert any("mention" in p for p in post_problems("Hello @agency"))


class TestDraftMarkers:
    def test_round_trip(self) -> None:
        body = "Intro\n\n" + render_draft(1, "First post") + "\n\n" + render_draft(2, "Second\n\npost")
        assert extract_draft(body, 1) == "First post"
        assert extract_draft(body, 2) == "Second\n\npost"

    def test_reviewer_edits_inside_the_markers_are_kept(self) -> None:
        body = render_draft(1, "Original").replace("Original", "Edited by a reviewer")
        assert extract_draft(body, 1) == "Edited by a reviewer"

    def test_windows_line_endings_and_a_removed_fence_still_parse(self) -> None:
        body = "<!-- digest-draft:1 -->\r\nEdited text\r\n<!-- /digest-draft:1 -->"
        assert extract_draft(body, 1) == "Edited text"

    def test_missing_markers_return_none(self) -> None:
        assert extract_draft("no drafts here", 1) is None
        assert extract_draft("<!-- digest-draft:1 -->\nunterminated", 1) is None

    def test_posted_marker_is_specific_to_the_draft(self) -> None:
        assert posted_marker(1) != posted_marker(2)
        assert posted_marker(1) not in render_draft(1, "text")
