---
title: Weekly Mastodon Digest
layout: page
---

Once a week this project drafts short Mastodon posts about what changed on the government websites it scans. The posts support two campaigns: public bodies using open social media, and public sector websites publishing accessibility statements.

A person reviews every post before it is published. Nothing is posted automatically.

## What the posts report

There are two kinds of post.

- **Open social media links.** Pages that now link to Mastodon, or to Bluesky or another AT Protocol app (Blacksky, Gander), where earlier scans of the same page found no such link.
- **Accessibility statements.** Pages that now link to an accessibility statement where earlier scans found none.

Each post also reports the opposite change: pages where a link that earlier scans found is now missing. Scans flicker, because a timeout or a bot block can hide a link that is still there, so in a typical week the losses are about as large as the gains. Reporting only the gains would overstate progress.

### What counts as a change

A page is compared only when its most recent successful scan falls within the week (Monday to Sunday, UTC).

- A page has **gained** a link when its latest scan found it and every earlier scan did not.
- A page has **lost** a link when every earlier scan found it and the latest scan did not.

Accessibility statement changes need at least two earlier scans of the page. Social media changes need at least one.

Social media scans are compared only when they were made with detection version 3 or later. Earlier versions counted TikTok and YouTube links as Mastodon, and did not detect Blacksky or Gander. Comparing across versions would report changes to the scanner as changes on the website. Until enough pages have two version 3 scans, the social media post is skipped.

### When a week is skipped

A post is not drafted when:

- its scanner has not run in the last two days of the week;
- fewer than 500 pages could be compared that week; or
- no page gained a link.

A skipped week is better than a post built on stale numbers.

## Checking a post

Each post links to an evidence file for its week in [`docs/data/digest/`](https://github.com/mgifford/eu-plus-government-scans/tree/main/docs/data/digest). The file is JSON and lists:

- every page counted as gained or lost, with its country, scan time, how many earlier scans it was compared with, and the links found;
- the number of pages compared, in total and per country; and
- the source data and the rule applied.

Every number in a post can be recounted from that file.

## How drafting and posting work

1. Every Monday the **Draft Weekly Mastodon Digest** workflow reads the latest scan data and writes one draft for each kind of post that has something to report.
2. It commits the evidence file and opens an issue labelled `digest-draft` with the drafts.
3. A maintainer checks each draft against its evidence file and edits the text in the issue if needed.
4. The maintainer runs the **Post weekly digest to Mastodon** workflow by hand, giving the issue number and draft number. It previews by default; the maintainer unticks *dry run* to publish.
5. The workflow records the link to the published post on the issue, and will not post the same draft twice.

The posting step refuses a draft that is longer than 500 characters or that mentions an account with `@`. Posts link to websites by name instead, because a mention sends a notification to a real account.

## Setting up the account

A maintainer does this once. No one else should handle the account's token.

1. On the Mastodon account, turn on **This is an automated account** in the profile settings. Posting is refused until this is set, so readers can always see the account is a bot.
2. Create an application in the account's development settings with the scopes `write:statuses` and `profile`. On servers older than Mastodon 4.3, use `read:accounts` instead of `profile`.
3. Add two repository secrets: `MASTODON_INSTANCE_URL` (for example `https://mastodon.example`) and `MASTODON_ACCESS_TOKEN`.
4. Optionally, add required reviewers to the `mastodon` environment in the repository settings. Every posting run then waits for a second approval.

Posts are text only. If images are added later, each one must have alt text (Mastodon's media `description` field).
