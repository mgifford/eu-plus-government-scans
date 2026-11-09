"""Draft the weekly Mastodon digest from the scan metadata database.

The digest turns a week of scan results into short posts for the campaign
account: government websites that start linking to open social media, and
public sector pages that start publishing an accessibility statement.  It only
drafts.  The drafts go into a GitHub issue where a maintainer checks and edits
them, and nothing is published until they run the separate posting workflow
(:mod:`src.cli.post_digest`).

Every number in a draft is backed by an evidence file that lists each page
behind it.  The file is written to ``docs/data/digest/<week-ending>.json``,
committed, and linked from the post, so any reader can check the claim
(AGENTS.md, "Independent Verification").

Three rules keep the numbers honest:

* **A change must hold against the page's history.**  Scans flicker: a timeout
  or a bot wall can hide a link that is still there.  A page has *gained*
  something only if every earlier comparable scan lacked it, and *lost* it only
  if every earlier comparable scan had it.  Losses are always reported next to
  gains, because in a typical week they are of the same order.
* **Stale data is skipped, not reposted.**  A post type is skipped when its
  scanner has not run within two days of the week's end, or re-checked too few
  pages that week.
* **Social links are compared only between scans made with detection version 3
  or later.**  Older scans counted TikTok and YouTube ``/@handle`` links as
  Mastodon and did not know Blacksky or Gander, so comparing across versions
  would report detector changes as adoption.
"""

from __future__ import annotations

import argparse
import json
import sqlite3
from collections import Counter, defaultdict
from collections.abc import Callable, Iterable, Sequence
from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path
from urllib.parse import urlsplit

from src.lib.country_utils import country_code_to_display_name
from src.lib.digest_drafts import MAX_POST_CHARS, post_length, post_problems, render_draft
from src.lib.secret_redaction import redact_url
from src.services.social_media_scanner import SOCIAL_PLATFORMS_VERSION

DEFAULT_DB = Path("data/metadata.db")
DEFAULT_EVIDENCE_DIR = Path("docs/data/digest")
DEFAULT_OUTPUT_DIR = Path("digest-output")
DEFAULT_REPO = "mgifford/eu-plus-government-scans"

# Where the evidence file is published, relative to the repository root.  Posts
# link to it on GitHub, which serves it as soon as it is committed; the Pages
# site only picks it up on its next deploy.
EVIDENCE_REPO_PATH = "docs/data/digest"

# A post type is skipped when its newest scan is older than this at week's end.
MAX_DATA_AGE_DAYS = 2

# Fewer re-checked pages than this and a week's figures say too little to post.
MIN_PAGES_RECHECKED = 500

# Earlier scans a page needs before a change on it counts.  Accessibility
# statement detection flickers enough that one earlier scan is not evidence.
STATEMENT_MIN_PRIOR_SCANS = 2
SOCIAL_MIN_PRIOR_SCANS = 1

# The first social detection version whose Mastodon counts can be published.
MIN_SOCIAL_PLATFORMS_VERSION = 3

# Example websites named in a post.
MAX_EXAMPLES = 2

STATEMENT_GROUPS: dict[str, tuple[str, ...]] = {"statement": ("statement_links",)}

# Open platforms, grouped as a post describes them.
SOCIAL_GROUPS: dict[str, tuple[str, ...]] = {
    "mastodon": ("mastodon_links",),
    "atproto": ("bluesky_links", "blacksky_links", "gander_links"),
}
SOCIAL_GROUP_LABELS: dict[str, str] = {
    "mastodon": "Mastodon",
    "atproto": "Bluesky or another AT Protocol app",
}

# Country names that take "the" in a sentence.
_NAMES_WITH_ARTICLE = frozenset({"United Kingdom", "Netherlands"})

_MONTHS = (
    "January", "February", "March", "April", "May", "June", "July",
    "August", "September", "October", "November", "December",
)


@dataclass(frozen=True)
class Week:
    """Seven whole UTC days ending on ``ending``."""

    ending: date

    @property
    def first_day(self) -> date:
        """Return the first day of the week."""
        return self.ending - timedelta(days=6)

    @property
    def start(self) -> datetime:
        """Return the inclusive lower bound, midnight UTC on the first day."""
        return datetime.combine(self.first_day, time(), timezone.utc)

    @property
    def end(self) -> datetime:
        """Return the exclusive upper bound, midnight UTC after the last day."""
        return datetime.combine(self.ending + timedelta(days=1), time(), timezone.utc)

    def contains(self, moment: datetime) -> bool:
        """Return whether *moment* falls inside the week."""
        return self.start <= moment < self.end

    def label(self) -> str:
        """Return the week as prose, e.g. ``2 to 8 November 2026``."""
        first, last = self.first_day, self.ending
        if first.year != last.year:
            return (
                f"{first.day} {_MONTHS[first.month - 1]} {first.year} "
                f"to {last.day} {_MONTHS[last.month - 1]} {last.year}"
            )
        if first.month != last.month:
            return (
                f"{first.day} {_MONTHS[first.month - 1]} "
                f"to {last.day} {_MONTHS[last.month - 1]} {last.year}"
            )
        return f"{first.day} to {last.day} {_MONTHS[last.month - 1]} {last.year}"


@dataclass(frozen=True, slots=True)
class Scan:
    """One successful scan of a page, reduced to what the digest compares.

    Attributes:
        scanned_at: When the scan ran.
        country_code: Country the page belongs to.
        found: Whether each signal group was found, keyed by group.
        columns: Raw JSON link lists, keyed by database column.
    """

    scanned_at: datetime
    country_code: str
    found: dict[str, bool]
    columns: dict[str, str]


@dataclass
class Changes:
    """Pages re-checked in a week, and which of them gained or lost a signal.

    Attributes:
        rechecked: URL to country code, for every page compared this week.
        gained: Evidence rows per group for pages that gained the signal.
        lost: Evidence rows per group for pages that lost it.
    """

    rechecked: dict[str, str] = field(default_factory=dict)
    gained: dict[str, list[dict]] = field(default_factory=dict)
    lost: dict[str, list[dict]] = field(default_factory=dict)


@dataclass
class Section:
    """One post type's outcome for the week.

    Attributes:
        key: Stable identifier, used in the evidence file.
        title: Heading shown to the reviewer.
        evidence: Machine-readable backing data for the post.
        post: Draft text, or None when the post type was skipped.
        reason: Why it was skipped, when it was.
    """

    key: str
    title: str
    evidence: dict = field(default_factory=dict)
    post: str | None = None
    reason: str | None = None


def parse_timestamp(value: str | None) -> datetime | None:
    """Parse a stored ISO timestamp, treating a naive one as UTC.

    Args:
        value: Timestamp text from the database.

    Returns:
        An aware datetime, or None when the value is missing or malformed.
    """
    if not value:
        return None
    try:
        moment = datetime.fromisoformat(value)
    except ValueError:
        return None
    return moment if moment.tzinfo else moment.replace(tzinfo=timezone.utc)


def json_list(raw: str | None) -> list[str]:
    """Decode a stored JSON list of links, tolerating bad values."""
    try:
        value = json.loads(raw or "[]")
    except (TypeError, json.JSONDecodeError):
        return []
    return [str(item) for item in value] if isinstance(value, list) else []


def site_host(url: str) -> str:
    """Return the host of *url* without a leading ``www.``."""
    return (urlsplit(url).hostname or "").removeprefix("www.")


def table_columns(conn: sqlite3.Connection, table: str) -> set[str]:
    """Return the column names of *table*, empty when it does not exist.

    Args:
        conn: Open database connection.
        table: Table name; callers pass constants only.

    Returns:
        Column names.
    """
    return {row[1] for row in conn.execute(f"PRAGMA table_info({table})")}


def _sorted_history(history: dict[str, list[Scan]]) -> dict[str, list[Scan]]:
    """Order each page's scans oldest first."""
    for scans in history.values():
        scans.sort(key=lambda scan: scan.scanned_at)
    return dict(history)


def load_statement_history(conn: sqlite3.Connection, before: datetime) -> dict[str, list[Scan]]:
    """Load every usable accessibility-statement scan made before *before*.

    A scan is usable when the page was reachable and parsed without error.
    The scanner stores a page it fetched but could not parse as reachable with
    no links, which would otherwise read as a statement link disappearing.

    Args:
        conn: Database holding ``url_accessibility_results``.
        before: Exclusive upper bound, so a past week can be re-drafted.

    Returns:
        URL to its scans, oldest first.
    """
    if not table_columns(conn, "url_accessibility_results"):
        return {}
    history: dict[str, list[Scan]] = defaultdict(list)
    rows = conn.execute(
        "SELECT url, country_code, scanned_at, has_statement, statement_links "
        "FROM url_accessibility_results WHERE is_reachable = 1 AND error_message IS NULL"
    )
    for url, country, stamp, has_statement, links in rows:
        moment = parse_timestamp(stamp)
        if moment is None or moment >= before:
            continue
        history[url].append(
            Scan(moment, country, {"statement": bool(has_statement)}, {"statement_links": links})
        )
    return _sorted_history(history)


def load_social_history(conn: sqlite3.Connection, before: datetime) -> dict[str, list[Scan]]:
    """Load every usable social scan made with detection version 3 or later.

    Usable means reachable and parsed without error, the rule the social media
    report applies (``LATEST_SOCIAL_SCANS_SQL`` in ``_report_common``).  A parse
    error is stored as reachable with no links, which would otherwise read as
    a page dropping its links.

    Args:
        conn: Database holding ``url_social_media_results``.
        before: Exclusive upper bound, so a past week can be re-drafted.

    Returns:
        URL to its comparable scans, oldest first.
    """
    present = table_columns(conn, "url_social_media_results")
    if "platforms_version" not in present:
        return {}
    wanted = [column for columns in SOCIAL_GROUPS.values() for column in columns]
    # Column names come from SOCIAL_GROUPS, never from input.  A database that
    # predates a column has, by definition, no links in it.
    selected = ", ".join(column if column in present else "'[]'" for column in wanted)
    rows = conn.execute(
        f"SELECT url, country_code, scanned_at, {selected} "
        "FROM url_social_media_results "
        "WHERE is_reachable = 1 AND error_message IS NULL AND platforms_version >= ?",
        (MIN_SOCIAL_PLATFORMS_VERSION,),
    )
    history: dict[str, list[Scan]] = defaultdict(list)
    for url, country, stamp, *raw in rows:
        moment = parse_timestamp(stamp)
        if moment is None or moment >= before:
            continue
        columns = dict(zip(wanted, raw))
        found = {
            group: any(json_list(columns[column]) for column in group_columns)
            for group, group_columns in SOCIAL_GROUPS.items()
        }
        history[url].append(Scan(moment, country, found, columns))
    return _sorted_history(history)


def classify_change(flags: Sequence[bool], min_prior: int) -> str | None:
    """Return ``"gained"``, ``"lost"`` or None for a page's scan history.

    Args:
        flags: Whether each scan found the signal, oldest first.
        min_prior: Earlier scans needed before any change counts.

    Returns:
        ``"gained"`` when only the latest scan found it, ``"lost"`` when every
        scan but the latest found it, otherwise None.
    """
    *prior, latest = flags
    if len(prior) < min_prior:
        return None
    if latest and not any(prior):
        return "gained"
    if not latest and all(prior):
        return "lost"
    return None


def _evidence_row(url: str, scan: Scan, columns: Sequence[str], earlier: int) -> dict:
    """Build one evidence-file row for a page that changed."""
    links = sorted(
        {redact_url(link) for column in columns for link in json_list(scan.columns.get(column))}
    )
    row = {
        "url": url,
        "host": site_host(url),
        "country_code": scan.country_code,
        "country": country_code_to_display_name(scan.country_code),
        "scanned_at": scan.scanned_at.isoformat(),
        "earlier_checks": earlier,
    }
    if links:
        row["links"] = links
    return row


def find_changes(
    history: dict[str, list[Scan]],
    week: Week,
    groups: dict[str, tuple[str, ...]],
    min_prior: int,
) -> Changes:
    """Compare each page re-checked during *week* against its earlier scans.

    Args:
        history: URL to its scans, oldest first.
        week: Week whose re-checks are reported.
        groups: Signal group to the columns holding its links.
        min_prior: Earlier scans a page needs to be compared at all.

    Returns:
        The pages compared and the changes found, in URL order.
    """
    changes = Changes(gained={g: [] for g in groups}, lost={g: [] for g in groups})
    for url in sorted(history):
        scans = history[url]
        latest = scans[-1]
        earlier = len(scans) - 1
        if earlier < min_prior or not week.contains(latest.scanned_at):
            continue
        changes.rechecked[url] = latest.country_code
        for group, columns in groups.items():
            kind = classify_change([scan.found[group] for scan in scans], min_prior)
            if kind == "gained":
                changes.gained[group].append(_evidence_row(url, latest, columns, earlier))
            elif kind == "lost":
                changes.lost[group].append(_evidence_row(url, latest, (), earlier))
    return changes


def newest_scan(history: dict[str, list[Scan]]) -> datetime | None:
    """Return the most recent scan time in *history*."""
    return max((scans[-1].scanned_at for scans in history.values()), default=None)


def data_problem(history: dict[str, list[Scan]], week: Week, changes: Changes, empty: str) -> str | None:
    """Return why a week's data cannot support a post, or None.

    Args:
        history: The scans loaded for this post type.
        week: Week being drafted.
        changes: The comparison for that week.
        empty: Reason to give when there are no scans at all.

    Returns:
        A reason to skip, or None when the data is fresh and broad enough.
    """
    newest = newest_scan(history)
    if newest is None:
        return empty
    if newest < week.end - timedelta(days=MAX_DATA_AGE_DAYS):
        return (
            f"the data is stale: the newest scan is from {newest:%Y-%m-%d %H:%M} UTC, "
            f"more than {MAX_DATA_AGE_DAYS} days before the week ended"
        )
    if len(changes.rechecked) < MIN_PAGES_RECHECKED:
        return (
            f"only {len(changes.rechecked):,} pages could be compared with earlier scans "
            f"this week; at least {MIN_PAGES_RECHECKED:,} are needed"
        )
    return None


def country_breakdown(changes: Changes) -> list[dict]:
    """Return per-country counts behind a post, in country order.

    Args:
        changes: The week's comparison.

    Returns:
        One row per country re-checked, with pages compared, gained and lost.
    """
    rechecked = Counter(changes.rechecked.values())
    gained = {g: Counter(r["country_code"] for r in rows) for g, rows in changes.gained.items()}
    lost = {g: Counter(r["country_code"] for r in rows) for g, rows in changes.lost.items()}
    return [
        {
            "country_code": country,
            "country": country_code_to_display_name(country),
            "pages_rechecked": rechecked[country],
            "gained": {g: counts[country] for g, counts in gained.items()},
            "lost": {g: counts[country] for g, counts in lost.items()},
        }
        for country in sorted(rechecked)
    ]


def section_evidence(changes: Changes, history: dict[str, list[Scan]], source: dict, rule: str) -> dict:
    """Assemble the evidence-file entry for one post type.

    Args:
        changes: The week's comparison.
        history: Scans loaded for this post type.
        source: Where the data came from.
        rule: Plain-language statement of what counted as a change.

    Returns:
        Evidence for the post, before its status is set.
    """
    newest = newest_scan(history)
    return {
        "source": {**source, "newest_scan": newest.isoformat() if newest else None},
        "rule": rule,
        "pages_rechecked": len(changes.rechecked),
        "countries_rechecked": len(set(changes.rechecked.values())),
        "by_country": country_breakdown(changes),
        "gained": changes.gained,
        "lost": changes.lost,
    }


def _count(n: int, singular: str, plural: str | None = None) -> str:
    """Return ``"1 page"`` or ``"3 pages"``."""
    return f"{n:,} {singular if n == 1 else plural or singular + 's'}"


def in_prose(country: str) -> str:
    """Return a country name as it reads mid-sentence, e.g. ``the Netherlands``."""
    return f"the {country}" if country in _NAMES_WITH_ARTICLE else country


def leading_countries(rows: Sequence[dict]) -> str:
    """Describe where most of *rows* are, e.g. ``", most in France (31) and Spain (4)"``."""
    counts = Counter(row["country"] for row in rows)
    if not counts:
        return ""
    if len(counts) == 1:
        return f", all in {in_prose(next(iter(counts)))}"
    (first, n1), (second, n2) = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))[:2]
    return f", most in {in_prose(first)} ({n1:,}) and {in_prose(second)} ({n2:,})"


def example_hosts(rows: Sequence[dict], limit: int = MAX_EXAMPLES) -> list[str]:
    """Return the hosts with the most changed pages, ties broken by name."""
    counts = Counter(row["host"] for row in rows if row["host"])
    return [host for host, _ in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))[:limit]]


def first_postable(variants: Sequence[str]) -> str | None:
    """Return the first variant that may be posted, longest wording first."""
    for text in variants:
        if not post_problems(text):
            return text
    return None


def _hosts(rows: Iterable[dict]) -> set[str]:
    """Return the distinct hosts among evidence rows."""
    return {row["host"] for row in rows}


def _flatten(rows_by_group: dict[str, list[dict]]) -> list[dict]:
    """Return every group's rows as one list."""
    return [row for rows in rows_by_group.values() for row in rows]


def _missing_text(lost: Sequence[dict], noun: str) -> str:
    """Report the pages that lost something, so gains are read against them."""
    if not lost:
        return f"No {noun} that earlier checks found has gone missing."
    article = "an" if noun[0] in "aeiou" else "a"
    return (
        f"On {_count(len(lost), 'page')} ({_count(len(_hosts(lost)), 'website')}), "
        f"{article} {noun} that every earlier check found is now missing."
    )


def statement_post(week: Week, changes: Changes, evidence_url: str) -> str | None:
    """Write the accessibility-statement post, or None if it cannot fit.

    Args:
        week: Week being reported.
        changes: The week's comparison.
        evidence_url: Link to the evidence file.

    Returns:
        Post text within Mastodon's limit, or None.
    """
    gained = changes.gained["statement"]
    countries = len(set(changes.rechecked.values()))
    verb = "links" if len(gained) == 1 else "link"
    missing = _missing_text(changes.lost["statement"], "statement link")

    def compose(where: str) -> str:
        return "\n\n".join((
            f"Government web scan, {week.label()}: we re-checked "
            f"{_count(len(changes.rechecked), 'public sector web page')} in "
            f"{_count(countries, 'country', 'countries')}.",
            f"{_count(len(gained), 'page')} on {_count(len(_hosts(gained)), 'website')} "
            f"now {verb} to an accessibility statement that earlier checks never "
            f"found{where}. {missing}",
            f"All pages: {evidence_url}",
            "The EU Web Accessibility Directive requires public sector websites to "
            "publish one.",
            "#a11y #Accessibility #OpenData",
        ))

    return first_postable((compose(leading_countries(gained)), compose("")))


def social_post(week: Week, changes: Changes, evidence_url: str) -> str | None:
    """Write the open-platform adoption post, or None if it cannot fit.

    Counts are of pages, not websites adopting a platform: a site may already
    have linked to it from pages that were not re-checked this week.

    Args:
        week: Week being reported.
        changes: The week's comparison.
        evidence_url: Link to the evidence file.

    Returns:
        Post text within Mastodon's limit, or None.
    """
    gained = _flatten(changes.gained)
    pages = {row["url"] for row in gained}
    countries = {row["country_code"] for row in gained}
    verb = "links" if len(pages) == 1 else "link"
    parts = ", ".join(
        f"{len(rows):,} to {SOCIAL_GROUP_LABELS[group]}"
        for group, rows in changes.gained.items() if rows
    )
    missing = _missing_text(_flatten(changes.lost), "open social media link")

    def compose(examples: Sequence[str]) -> str:
        among = f" Among them: {', '.join(examples)}." if examples else ""
        return "\n\n".join((
            f"Open social web, {week.label()}: {_count(len(pages), 'page')} on "
            f"{_count(len(_hosts(gained)), 'government website')} in "
            f"{_count(len(countries), 'country', 'countries')} now {verb} to open social "
            f"media where earlier checks found none ({parts}).{among}",
            missing,
            "Open platforms keep public communication out of any single company's hands.",
            f"All pages: {evidence_url}",
            "#Fediverse #DigitalSovereignty",
        ))

    return first_postable((compose(example_hosts(gained)), compose(())))


def build_section(
    key: str,
    title: str,
    history: dict[str, list[Scan]],
    week: Week,
    settings: dict,
    write_post: Callable[[Week, Changes, str], str | None],
    evidence_url: str,
) -> Section:
    """Compare a week's scans and draft one post type, or record why not.

    Args:
        key: Section identifier.
        title: Heading for the reviewer.
        history: Scans for this post type.
        week: Week being drafted.
        settings: ``groups``, ``min_prior``, ``source``, ``rule`` and ``empty``.
        write_post: Turns the comparison into post text.
        evidence_url: Link to the evidence file.

    Returns:
        The drafted or skipped section.
    """
    changes = find_changes(history, week, settings["groups"], settings["min_prior"])
    section = Section(key, title)
    section.evidence = section_evidence(changes, history, settings["source"], settings["rule"])
    reason = data_problem(history, week, changes, settings["empty"])
    if reason is None and not any(changes.gained.values()):
        reason = "no page gained one this week"
    if reason is None:
        section.post = write_post(week, changes, evidence_url)
        if section.post is None:
            reason = f"the post could not be fitted into {MAX_POST_CHARS} characters"
    if reason:
        section.reason = reason
        section.evidence = {"status": "skipped", "reason": reason, "source": section.evidence["source"]}
    else:
        section.evidence = {"status": "drafted", **section.evidence}
    return section


def social_section(conn: sqlite3.Connection, week: Week, evidence_url: str) -> Section:
    """Draft the open-platform adoption post."""
    title = "Government websites newly linking to open social media"
    if SOCIAL_PLATFORMS_VERSION < MIN_SOCIAL_PLATFORMS_VERSION:
        reason = f"social detection is version {SOCIAL_PLATFORMS_VERSION}; version 3 is needed"
        return Section("open_social_platforms", title, {"status": "skipped", "reason": reason}, reason=reason)
    settings = {
        "groups": SOCIAL_GROUPS,
        "min_prior": SOCIAL_MIN_PRIOR_SCANS,
        "source": {
            "artifact": "social-media-metadata",
            "table": "url_social_media_results",
            "min_platforms_version": MIN_SOCIAL_PLATFORMS_VERSION,
        },
        "rule": (
            "A page gained a platform group when its latest successful scan (reachable "
            "and parsed without error) links to it and no earlier successful scan "
            "(detection version 3 or later) did; it lost one when every earlier such "
            "scan linked to it and the latest does not."
        ),
        "empty": (
            "no page has been scanned with social detection version 3 yet; older "
            "scans counted TikTok and YouTube links as Mastodon"
        ),
    }
    history = load_social_history(conn, week.end)
    return build_section("open_social_platforms", title, history, week, settings, social_post, evidence_url)


def statement_section(conn: sqlite3.Connection, week: Week, evidence_url: str) -> Section:
    """Draft the new accessibility statements post."""
    settings = {
        "groups": STATEMENT_GROUPS,
        "min_prior": STATEMENT_MIN_PRIOR_SCANS,
        "source": {"artifact": "accessibility-metadata", "table": "url_accessibility_results"},
        "rule": (
            "A page gained a statement when its latest successful scan (reachable and "
            "parsed without error) found an accessibility statement link and at least "
            f"{STATEMENT_MIN_PRIOR_SCANS} earlier successful scans all found none; it "
            "lost one when all of those "
            "earlier scans found one and the latest does not."
        ),
        "empty": "there are no accessibility statement scans",
    }
    history = load_statement_history(conn, week.end)
    return build_section(
        "accessibility_statements", "New accessibility statements", history, week,
        settings, statement_post, evidence_url,
    )


def build_evidence(week: Week, sections: Sequence[Section]) -> dict:
    """Assemble the evidence file for the week.

    Args:
        week: Week being drafted.
        sections: Every post type, drafted or skipped.

    Returns:
        The evidence payload.
    """
    return {
        "schema": 1,
        "week": {"first_day": week.first_day.isoformat(), "last_day": week.ending.isoformat()},
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "notes": {
            "pages_rechecked": (
                "pages whose latest reachable scan falls in the week and that have "
                "enough earlier comparable scans to compare against"
            ),
            "gained": "pages whose latest scan found the item while every earlier comparable scan did not, per group",
            "lost": "pages whose latest scan did not find the item while every earlier comparable scan did, per group",
            "earlier_checks": "number of earlier comparable scans of the page",
            "links": "links found by the latest scan; credential parameters masked",
            "host": "page host without a leading www., used to count websites",
        },
        "sections": {section.key: section.evidence for section in sections},
    }


def _utc_minute(stamp: str | None) -> str:
    """Format a stored timestamp as ``2026-11-08 21:38 UTC``."""
    moment = parse_timestamp(stamp)
    return f"{moment.astimezone(timezone.utc):%Y-%m-%d %H:%M} UTC" if moment else "unknown"


def render_issue(week: Week, drafts: Sequence[Section], skipped: Sequence[Section], evidence_url: str) -> str:
    """Write the review issue body.

    Args:
        week: Week being drafted.
        drafts: Sections with a post, in draft-number order.
        skipped: Sections without one.
        evidence_url: Link to the evidence file.

    Returns:
        Markdown for the issue.
    """
    lines = [
        f"Weekly digest drafts for **{week.label()}**. Nothing here has been posted.",
        "",
        "Before posting a draft:",
        "",
        "- [ ] Open its evidence file and check that every number in the text matches it.",
        "- [ ] Open three of the listed pages and confirm what the scan reported.",
        "- [ ] Edit the text here if needed, keeping it between its markers. Do not add "
        "@-mentions: they notify real accounts, and the posting step refuses them.",
        "",
        "To post, run the **Post weekly digest to Mastodon** workflow from the Actions tab "
        "with this issue's number and the draft number. It previews by default; untick "
        "*dry run* to publish.",
    ]
    for number, section in enumerate(drafts, start=1):
        evidence = section.evidence
        lines += [
            "",
            f"## Draft {number}: {section.title}",
            "",
            render_draft(number, section.post or ""),
            "",
            f"{post_length(section.post or '')} of {MAX_POST_CHARS} characters "
            "(Mastodon counts each link as 23).",
            f"Data: {evidence['pages_rechecked']:,} pages compared; newest scan "
            f"{_utc_minute(evidence['source']['newest_scan'])} from the "
            f"`{evidence['source']['artifact']}` artifact. Evidence: {evidence_url}",
        ]
    if skipped:
        lines += ["", "## Skipped this week", ""]
        lines += [f"- **{section.title}**: {section.reason}." for section in skipped]
    return "\n".join(lines) + "\n"


def write_outputs(args: argparse.Namespace, week: Week, sections: Sequence[Section], evidence_url: str) -> int:
    """Write the evidence file, the issue body and the drafts summary.

    Args:
        args: Parsed command-line arguments.
        week: Week being drafted.
        sections: Every post type.
        evidence_url: Link to the evidence file.

    Returns:
        Number of drafts written.
    """
    drafts = [section for section in sections if section.post]
    skipped = [section for section in sections if not section.post]
    args.output_dir.mkdir(parents=True, exist_ok=True)
    evidence_path = None
    if drafts:
        args.evidence_dir.mkdir(parents=True, exist_ok=True)
        evidence_path = args.evidence_dir / f"{week.ending.isoformat()}.json"
        evidence_path.write_text(
            json.dumps(build_evidence(week, sections), indent=1, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        (args.output_dir / "issue.md").write_text(
            render_issue(week, drafts, skipped, evidence_url), encoding="utf-8"
        )
    summary = {
        "week_ending": week.ending.isoformat(),
        "title": f"Weekly digest drafts: week ending {week.ending.isoformat()}",
        "evidence_file": evidence_path.as_posix() if evidence_path else None,
        "evidence_url": evidence_url if drafts else None,
        "drafts": [
            {"number": n, "key": s.key, "title": s.title, "text": s.post, "length": post_length(s.post or "")}
            for n, s in enumerate(drafts, start=1)
        ],
        "skipped": [{"key": s.key, "title": s.title, "reason": s.reason} for s in skipped],
    }
    (args.output_dir / "drafts.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return len(drafts)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--db", type=Path, default=DEFAULT_DB, help="Merged metadata database.")
    parser.add_argument(
        "--week-ending",
        type=date.fromisoformat,
        default=None,
        help="Last day of the week to draft, YYYY-MM-DD (default: yesterday, UTC).",
    )
    parser.add_argument("--evidence-dir", type=Path, default=DEFAULT_EVIDENCE_DIR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument(
        "--repo", default=DEFAULT_REPO, help="owner/name, used to link the evidence file."
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """Entry point."""
    args = parse_args(argv)
    today = datetime.now(timezone.utc).date()
    week = Week(args.week_ending or today - timedelta(days=1))
    if week.ending >= today:
        print(f"The week must have ended: {week.ending} is not before {today} (UTC).")
        return 2
    if not args.db.is_file():
        print(f"No metadata database at {args.db}.")
        return 1

    evidence_url = (
        f"https://github.com/{args.repo}/blob/main/{EVIDENCE_REPO_PATH}/{week.ending.isoformat()}.json"
    )
    conn = sqlite3.connect(f"file:{args.db}?mode=ro", uri=True)
    try:
        sections = [
            social_section(conn, week, evidence_url),
            statement_section(conn, week, evidence_url),
        ]
    finally:
        conn.close()

    count = write_outputs(args, week, sections, evidence_url)
    print(f"Week {week.label()}: {count} draft(s).")
    for section in sections:
        print(f"  {section.title}: {'drafted' if section.post else 'skipped, ' + (section.reason or '')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
