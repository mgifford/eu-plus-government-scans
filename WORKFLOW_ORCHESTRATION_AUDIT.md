# GitHub Actions Orchestration Audit

**Scope:** timing, scheduling, and coordination of `.github/workflows/` only. Not in scope: reducing
request load on the government servers being scanned (individual sites receive very few requests/day;
that is not a constraint here).

**Method:** direct inspection of all 18 workflow files and the relevant `src/cli/`/`src/jobs/`/
`src/services/`/`src/storage/` source, plus `gh` CLI queries against real GitHub Actions run history
(25 runs per major scanner where available). No throughput figure in this document is derived from a
configured rate limit alone — every "observed" number below comes from an actual run log or job-timing
record. Figures inferred rather than observed are marked **[projection]**; anything not directly
confirmed is marked **[unverified]**.

**How to read this document:** Section 0 states the labeling convention. Sections 1–5 are the required
factual inventory and analysis. Sections 6–10 are the proposed redesign. Section 11 is the phased
migration plan; Section 12 is the actual Phase 1 YAML; Section 13 is tests; Section 14 is the
administrator's guide.

---

## 0. Fact / Measurement / Projection / Assumption — labeling key

| Marker | Meaning |
|---|---|
| **[fact]** | Read directly from a file in this repository (YAML, source code, or generated JSON). |
| **[measured]** | Read directly from GitHub Actions run history via `gh` (timestamps, conclusions, log lines). |
| **[projection]** | Calculated from facts/measurements using an explicit formula shown inline. |
| **[assumption]** | Not verifiable from what's in the repo or run history; stated explicitly so it can be checked before acting on it. |

---

## 1. Complete Workflow Inventory **[fact]**

18 files under `.github/workflows/`. Four are purely event-driven and outside the scanning-load
problem (`axe-site-accessibility.yml` on push, `cancel-batch.yml` and `delete-merged-branches.yml`
manual/PR-close utilities, `deploy-pages.yml` triggered by docs pushes and by
`generate-scan-progress.yml` completion). The remaining 14 either run on a cron or exist specifically
to manage cron-driven scan cycles.

### 1.1 Scanning workflows

| Workflow | Purpose | Trigger | Cron (UTC) | Runs/day (cron) | Job timeout | Scanner internal max-runtime | Concurrency group | cancel-in-progress |
|---|---|---|---|---|---|---|---|---|
| `scan-accessibility.yml` | EU Accessibility Directive statement-link detection | schedule + dispatch | `30 */4 * * *` | 6 | 65 min | 55 min | `metadata-scans` | false |
| `scan-lighthouse.yml` | Lighthouse perf/a11y/best-practices/SEO audit | schedule + dispatch | `0 */6 * * *` | 4 | 70 min | 55 min | `lighthouse-scan` | false |
| `scan-social-media.yml` | Twitter/X, Bluesky, Mastodon link detection | schedule + dispatch | `0 */2 * * *` | 12 | 120 min | 110 min | `metadata-scans` | false |
| `scan-technology.yml` | CMS/framework/analytics detection | schedule + dispatch | `0 */2 * * *` | 12 | 25 min | 15 min | `metadata-scans` | false |
| `scan-third-party-js.yml` | Third-party JS service + version detection | schedule + dispatch | `30 */6 * * *` | 4 | 65 min | 55 min | `metadata-scans` | false |
| `scan-overlays.yml` | Accessibility overlay vendor detection | dispatch only | — | 0 | 120 min | 110 min | `metadata-scans` | false |
| `scan-relationships.yml` | Inter-domain link/relationship extraction | schedule + dispatch | `0 */6 * * *` | 4 | 110 min | 100 min (default) | **none** | n/a |
| `validate-urls-batch.yml` | Batched reachability check, 4 countries/run | schedule + dispatch | `0 1,13 * * *` | 2 | 60 min | 50 min (hardcoded internal) | `validation-background` | false |
| `validate-urls.yml` | Single-shot/legacy reachability check | dispatch only | — | 0 | 120 min | 110 min | `validation-background` | false |

### 1.2 Coordination / maintenance workflows

| Workflow | Purpose | Trigger | Cron (UTC) | Runs/day or month | Job timeout | Concurrency group |
|---|---|---|---|---|---|---|
| `generate-scan-progress.yml` | Regenerate all published progress/report pages | schedule + dispatch + `workflow_run` (5 scan workflows) | `15 */2 * * *` | 12/day **plus** up to 5 extra triggers/day from `workflow_run` | 15 min | `scan-progress-report` (cancel-in-progress: true) |
| `issue-triggered-validation.yml` | Poll for issue-triggered ad-hoc validation, circuit-breaker gated | schedule + dispatch | `0 * * * *` | 24 | 60 min | `issue-check-runs` |
| `reopen-validation-cycle.yml` | Kick off a new validation cycle | schedule + dispatch | `0 0 1 1,4,7,10 *` | 4/year | none set | none |
| `detect-orphans.yml` | Monthly orphaned-domain detection | schedule + dispatch | `0 6 1 * *` | 1/month | 15 min | none |
| `import-swh-domains.yml` | Monthly Software Heritage domain import | schedule + dispatch | `0 6 1 * *` | 1/month | none set | none |
| `check-links.yml` | Weekly Markdown link check | push + PR + schedule + dispatch | `0 20 * * 3` | 1/week | 15 min | `check-links-${{ github.ref }}` (cancel-in-progress: true) |

### 1.3 Event-driven, out of cron-collision scope

`axe-site-accessibility.yml` (push to main, 1-in-4 gated), `cancel-batch.yml` (dispatch),
`delete-merged-branches.yml` (PR closed), `deploy-pages.yml` (push to `docs/**` + `workflow_run` on
`generate-scan-progress.yml` completion — in practice fires roughly in step with that workflow's
2-hour cadence, i.e. effectively ~12+/day).

### 1.4 Actual CLI arguments (not just workflow comments) **[fact]**

Confirmed by reading both the workflow `run:` blocks and the target `src/cli/*.py` argparse
definitions directly:

| Scanner | `--rate-limit` | `--skip-recently-scanned-days` | `--max-runtime` (all-countries mode) | Notes |
|---|---|---|---|---|
| Accessibility | 1.0 | 7 | 55 (job timeout 65) | |
| Lighthouse | 0.5 | 30 | 55 (job timeout 70) | `--concurrency 3` (parallel LH processes), `--lighthouse-timeout-ms 30000` |
| Social Media | 1.0 | 7 | 110 (job timeout 120) | |
| Technology | 2.0 | 7 | 15 (job timeout 25) | Workflow builds an optional `--limit` flag from a dispatch input — **this flag does not exist in `scan_technology.py`'s argparse.** Confirmed by reading the file: only `--country`, `--toon-dir`, `--rate-limit`, `--all`, `--max-runtime`, `--skip-recently-scanned-days` are defined. Any manual dispatch with `limit` set will fail at argument-parsing time. **This is a standalone bug, unrelated to scheduling, worth fixing regardless of anything else in this document.** |
| Third-Party JS | 1.0 | *(flag not passed — no freshness skip exists for this scanner)* | 55 (job timeout 65) | `ThirdPartyJsScannerJob` has no skip-recently-scanned logic at all; every run re-scans everything it selects. |
| Overlays | 1.0 | *(flag doesn't exist for this scanner either)* | 110 (job timeout 120) | Simplest scanner: no freshness, no circuit breaker. |
| Relationships | 2.0 | 28 (matches `DEFAULT_SCAN_WINDOW_DAYS = 28` module constant in `relationship_scanner_job.py:38`) | 100 (job timeout 110) | Has a *separate* exponential failure-backoff mechanism (`_backoff_days()`) layered on top of the freshness skip. |
| Validate URLs Batch | 2.0 | 30 | 50 (hardcoded in `run_batch_mode()`, **not** a CLI flag; job timeout 60) | `BatchConfig.max_runtime_minutes = 60` dataclass default exists but is unused/vestigial — the CLI hardcodes 50 directly, a second, drifted "60 minutes" concept from the workflow's own `timeout-minutes: 60`. |

### 1.5 Shared-metadata usage — the central coordination risk

`data/metadata.db` (SQLite) is the artifact-backed shared state for **seven** of the nine scanning
workflows, all uploading/downloading it under the artifact name `validation-metadata`:
`scan-accessibility`, `scan-overlays`, `scan-social-media`, `scan-technology`, `scan-third-party-js`,
`validate-urls-batch`, `validate-urls`. `scan-lighthouse` maintains its **own** separate
`lighthouse-metadata` artifact but *also* uploads that same file as `validation-metadata` — a second,
redundant write to the shared artifact from a workflow whose own primary metadata stream is different.
`scan-relationships` correctly uses an isolated `relationship-scan-metadata` artifact.

**The critical finding: these seven workflows are split across two different concurrency groups that do
not protect each other.** `scan-accessibility` / `scan-overlays` / `scan-social-media` /
`scan-technology` / `scan-third-party-js` share `metadata-scans`. `validate-urls-batch` /
`validate-urls` share `validation-background`. `scan-lighthouse` has its own `lighthouse-scan` group.
**All three groups can run at the same time**, and all three write to the same `validation-metadata`
artifact. A `metadata-scans` job and a `validation-background` job (or a Lighthouse run) can download
the same prior version, both run independently, and whichever uploads last silently discards the
other's writes to `data/metadata.db`. The "safety guard" every workflow runs before uploading
(`db-guard` step) only checks **whether `data/metadata.db` exists on disk after download** — it has no
concept of version, timestamp, or "has this artifact changed since I downloaded it." It cannot detect
or prevent the overwrite scenario above; it only catches the narrower case of a download that failed
outright.

`scan-third-party-js.yml` additionally has **no `db-guard` step at all** — its upload of
`validation-metadata` is gated only on `if: always()`, one layer weaker than its five siblings.

This is not hypothetical. **[measured]**: `scan-social-media` run `29709440932` (2026-07-20 00:23) shows
the scan step succeeding, then the `db-guard` step failing because `data/metadata.db` was missing —
concrete evidence that the download/guard/upload sequence has already misfired in production, even
before accounting for the cross-group race.

---

## 2. Historical Runtime and Throughput **[measured]**

Pulled via `gh run list --workflow=<file> --limit 25 --json ...` plus `gh run view <id> --json jobs`
for step-level timing and `gh run view <id> --log` for URL-count log lines, for the 7 scheduled
scanners with meaningful run history plus `validate-urls-batch`.

| Workflow | Runs sampled | Success | Cancelled | Failure | Cancelled = queue-starved (never started) | Typical successful scan-step duration | Longest run | Shortest successful run | Observed URLs/pages per successful run |
|---|---|---|---|---|---|---|---|---|---|
| `scan-accessibility.yml` | 25 | 16 | 9 | 0 | 9/9 (100%) | ~54 min | 140.6 min (queue-dominated) | ~54 min | 353 (small country, completed) – 665 (partial, large country) |
| `scan-lighthouse.yml` | 25 | 23 | 0 | 2 | n/a | ~55 min | 70.3 min (near timeout) | ~55 min | 262 |
| `scan-social-media.yml` | 25 | 12 | 12 | 1 | 12/12 (100%) | ~109 min | 115.3 min | ~109 min | 2,112 (France, partial) |
| `scan-technology.yml` | 25 | 8 | 16 | 0 | 16/16 (100%) | ~14 min | 122.4 min (queue-dominated) | ~14 min | 482 (Austria, partial) |
| `scan-third-party-js.yml` | 25 | 24 | 1 | 0 | 1/1 (100%) | ~54 min | 134.2 min (queue-dominated) | ~55 min | 1,181 (Belgium, partial; plus Croatia 257 completed same run) |
| `scan-overlays.yml` | 1 (all-time) | 0 | 1 | 0 | unknown (no job data retrievable) | — | 69.7 min | — | — |
| `scan-relationships.yml` | 24 | 17 | 3 | 4 | 2/3 no-job; 1/3 mid-run 179.8-min timeout overrun | ~99 min | 180.4 min (exceeded 110-min timeout) | ~99 min | not cleanly captured — see gap note below |
| `validate-urls-batch.yml` | 25 | 16 | 9 | 0 | **0/9 — all genuine mid-run 60-min hard-timeout kills**, not queue starvation | 7–8 min (small batches) | 107.9 min (queue-dominated) | 7.6 min | 4 countries/batch, e.g. 8/31 countries (25.8%) after 2 runs |

**Setup/teardown overhead [measured], consistent across scanners**: checkout ~2–3s, Python setup ~2s,
pip install ~9s, Node setup ~0s (where applicable), Lighthouse CLI install ~9s (Lighthouse only),
artifact download ~1s, artifact upload ~1–2s, guard/summary steps <1s each. **Total non-scan overhead
is consistently under 30 seconds per run** — overhead is not the bottleneck; queue-starvation
cancellations and the scan step's own internal budget are.

**Failure-rate root causes, by workflow [measured]:**
- **Queue starvation** (job never started, killed while queued): the dominant failure mode for
  accessibility (100% of cancellations), social-media (100%), technology (100%, and the *highest*
  cancellation rate observed at 64%), third-party-js (100% of its one cancellation). All of these share
  `metadata-scans`, which is contended by up to 5 workflows.
- **Genuine mid-run timeout kill**: the dominant and *only* failure mode for `validate-urls-batch` — its
  internal 50-minute soft-stop did not fire before GitHub's 60-minute hard kill in at least one sampled
  run (`29711525672`, scan step ran 59.82 min with no "approaching timeout" log line found), meaning
  partial progress from that run was likely lost rather than gracefully saved.
- **Commit-step failure, not scan failure**: `scan-relationships`' 4 failures all occurred at the "Commit
  updated data files" step *after* the scan itself succeeded — consistent with `scan-relationships`
  having **no concurrency group**, so it can race against itself or against other workflows' commits to
  `main`.
- **Infrastructure-level failure**: 2 of Lighthouse's 25 runs failed before any scan logic ran (one at
  dependency install, one at "Set up job" itself) — not a scheduling issue.

**No "0 URLs to scan" / no-eligible-work exit message was found in any of the ~40 individual run logs
inspected** across accessibility, lighthouse, social-media, technology, third-party-js, and
relationships. This is not an exhaustive search of all 175 pulled run records, so absence of evidence
here is not proof of absence, but every sampled successful run processed a nonzero — usually
partial — URL count.

**Gaps, stated explicitly rather than estimated around [assumption / needs instrumentation]:**
- `scan-overlays.yml` has only one historical run ever (2026-04-07, cancelled, no retrievable job data).
  It has never completed successfully in observable history. No throughput data exists for it.
- `scan-relationships.yml`'s stdout format and step names changed between an older run
  (`29497953707`, "Scan relationships for all EU countries") and the current YAML ("Run progressive
  relationship scan"), and a clean "N/M URLs scanned" log line was not captured in the sample. Its
  observed-throughput figure in Section 4 below is therefore a **[projection]** from run duration and
  the documented 28-day freshness window, not a directly observed URL count — flagged accordingly.
- Median/p50 figures are reported as **typical values from the sampled successful runs**, not a formally
  computed statistical median across all 175 pulled records — the sample sizes (8–24 successes per
  workflow) are adequate for the "is this scanner roughly on pace" question this audit needs to answer,
  but a smaller/larger true median could exist outside the sample.

---

## 3. Schedule Collisions and Queues **[fact + measured]**

### 3.1 Exact simultaneous cron collisions

| Cron | Fires at (UTC) | Workflows |
|---|---|---|
| `0 */6 * * *` | 00:00, 06:00, 12:00, 18:00 | `scan-lighthouse.yml`, `scan-relationships.yml` |
| `0 */2 * * *` | every even hour | `scan-social-media.yml`, `scan-technology.yml` |

At every 6-hour mark (00:00/06:00/12:00/18:00), **four** scheduled scanners start in the same minute:
lighthouse, relationships (both exactly `0 */6`), plus social-media and technology (both `0 */2`, which
includes every 6-hour mark as a subset). None of these four share a concurrency group with each other —
so they don't queue-block each other, but they *do* all compete for GitHub's shared runner pool at the
literal busiest possible instant (the top of the hour), and three of the four (lighthouse, social-media,
technology — not relationships) also each independently touch `validation-metadata` within the same
short window.

### 3.2 Minute-zero clustering

Of the 8 scanning-and-reporting crons with a `schedule:` trigger, **7 fire at minute 0 or 15**; only
`scan-accessibility` (`:30`) and `scan-third-party-js` (`:30`) avoid the top of the hour, and
`generate-scan-progress` (`:15`) is close to it. **Zero** workflows currently use the requested
`:07/:17/:27/:37/:47/:53` stagger pattern.

### 3.3 `metadata-scans` group: serialized work that queues but shouldn't need to

Five workflows share one concurrency group (`metadata-scans`) purely because they all touch the same
`validation-metadata` artifact — but their *scanning* work (accessibility statements, social links, tech
stack, third-party JS, overlays) is logically independent; only the metadata read-modify-write needs
serialization, not the scan itself. **[measured]** this is the direct, confirmed cause of the highest
cancellation rates in the whole fleet: technology (64% cancelled, all queue-starved), social-media
(48% cancelled, all queue-starved), accessibility (36% cancelled, all queue-starved).

### 3.4 Runtime extending into the next scheduled invocation

`scan-social-media.yml`: job timeout 120 min, internal max-runtime 110 min, cron interval 120 min. In
the worst observed case (115.3 min), a run can still be executing when its own next scheduled trigger
fires two hours later, plus it's in the heavily-contended `metadata-scans` group, compounding the
queue-starvation problem for its own next occurrence and for its four groupmates.

`validate-urls-batch.yml`: job timeout 60 min matches the CLI's *intended* 50-min soft-stop + 10-min
buffer, but **[measured]** at least one real run shows the soft-stop failing to fire before the hard
kill — meaning this workflow's actual behavior is closer to "runs right up to its timeout" than its
design intends.

### 3.5 `scan-relationships.yml`: unprotected, currently racing with itself

No concurrency group at all. **[measured]**: 4 of 24 sampled runs failed specifically at the git-commit
step (not the scan step), and one dispatched run overran its own 110-minute job timeout by 70 minutes
(180.4 min total) before being killed — evidence consistent with, though not conclusive proof of, commit
races against concurrent pushes from other workflows or from a second overlapping
`scan-relationships` invocation.

### 3.6 `generate-scan-progress.yml`: triggered far more often than data changes

Fires on its own `:15`-past-every-2-hours cron **and** on `workflow_run` completion of 5 other
workflows (`validate-urls-batch`, `scan-social-media`, `scan-technology`, `scan-lighthouse`,
`scan-accessibility`). Given those 5 source workflows' cron cadences (2/day, 12/day, 12/day, 4/day,
6/day respectively) plus queue-starvation cancellations counted as non-triggering, this workflow can
realistically fire well over its own nominal 12/day, frequently while the very scanners it's reporting
on are still mid-run — meaning some fraction of its regenerated reports reflect a source dataset that's
still being written. Compounding this, `deploy-pages.yml` listens for `generate-scan-progress.yml`
completions too, so a report regeneration with no real data change still triggers a full site rebuild
and deploy.

### 3.7 Duplicated setup work

Setup/teardown overhead is small in absolute terms (~30 sec/run, Section 2), but at current volume
(scanning workflows alone attempt roughly 60 runs/day across all crons, before counting
`generate-scan-progress`'s 12+/day and `issue-triggered-validation`'s 24/day) this is still on the order
of **30–45 minutes/day** of pure repeated checkout+install+artifact-download work, independent of any
actual scanning. Not the dominant cost (queue-starvation and the Social Media over-scan are much larger,
Section 4), but a real, avoidable tax that consolidating short/frequent jobs into fewer, appropriately-
sized runs would reduce.

---

## 4. Capacity Calculations **[projection, built from Section 2's measured figures]**

**Corpus** (per instruction, from `data/toon-seeds/index.json`, treated as authoritative): 38,926
domains, 87,183 pages, 32 countries. **[fact, caveat]**: direct comparison against 8 countries' own
`.toon` file headers shows `index.json` undercounts by 0–1.5% per country (worst case Germany, off by
44/2,991 domains ≈ 1.5%) and has no `generated_at` timestamp, so it is not kept in sync by any of the
18 workflows audited — none of them write to it. The undercount is small enough not to change any
"ahead/on-pace/marginal/behind" classification below, but it means true eligible-URL counts are
slightly higher than what `index.json` reports.

Formula used throughout: `effective daily throughput = (cron runs/day × observed success rate) ×
observed URLs/successful run`; `projected cycle days = 87,183 ÷ effective daily throughput`. Success
rate and URLs/run both come from Section 2's measured data, not from configured rate limits.

| Scanner | Target cycle | Cron runs/day | Observed success rate | Effective successful runs/day | Observed URLs/run | Effective daily throughput | **Projected cycle** | Status |
|---|---|---|---|---|---|---|---|---|
| Accessibility | 30 days | 6 | 64% (16/25) | 3.84 | 353–665 | 1,356–2,554 | **34–64 days** | **Marginal to behind** — wide range driven by run-to-run variance in whether a small country finishes or a large one is left partial |
| Lighthouse | 60 days | 4 | 92% (23/25) | 3.68 | 262 | 964 | **~90 days** | **Behind** its own 60-day target |
| Social Media | 30 days | 12 | 48% (12/25) | 5.76 | 2,112 | 12,165 | **~7 days** | **Far ahead** — effectively re-scanning most of the corpus roughly 4× within its own 30-day window, and its own 7-day freshness-skip setting means much of that repeat work is actively wasted |
| Technology | 30 days | 12 | 32% (8/25) | 3.84 | 482 | 1,851 | **~47 days** | **Behind** target despite being scheduled 12×/day — the busiest cron of any scanner, undone by a 64% queue-starvation cancellation rate |
| Third-Party JS | 30 days | 4 | 96% (24/25) | 3.84 | 1,181 | 4,535 | **~19 days** | **Ahead of pace** — healthiest scanner in the fleet by every measured metric |
| Relationships | 60 days | 4 | 71% (17/24) | 2.83 | **[unverified — see Section 2 gap note]** | **[not computable from clean data]** | **not computable** | **Unknown — flagged for instrumentation, not guessed** |
| Validate URLs Batch | n/a (country-cycle, not URL-cycle) | 2 | 64% (16/25) | 1.28 | 4 countries/batch | ~5.1 countries/day | **~6.3 days to touch every country once** | **On pace** for its own country-rotation design, though "touched once" ≠ "fully validated" given the internal 50-min soft-stop issue in 3.4 |

**The single clearest finding in this section**: Social Media is simultaneously the scanner burning the
*most* runner-minutes/month (Section 5) and the *most* over-scanned relative to its own freshness
target. Its 12×/day cron was presumably set assuming rate-limit-bound throughput; the measured
throughput is roughly 4× what a 30-day cycle at its own 7-day freshness window actually requires.
Reducing its cron frequency is very likely the single highest-leverage, lowest-risk change available —
covered in Section 6.

Technology is the inverse problem: also scheduled 12×/day, but its 25-minute job timeout combined with
sharing the most-contested concurrency group means less than a third of its scheduled attempts ever
start. More cron frequency will not fix this — it needs either a dedicated (or less contested)
concurrency lane, or the job timeout raised so a starting run isn't racing a 25-minute clock inside an
already-delayed start.

---

## 5. Monthly Runner-Minute Estimates **[projection]**

`runner-minutes/month ≈ (successful runs/month × typical successful-run duration) + (failed/cancelled
runs/month × ~2 min average overhead before failure/cancellation)`. Successful-run duration uses
Section 2's measured typical scan-step duration; the ~2-minute average is a rough **[assumption]**
covering the "cancelled while queued" case (which Section 2 shows is often well under 2 minutes) and the
rarer mid-run failure case (which can be much longer) — stated as an approximation, not a precise figure.

| Scanner | Attempts/month | Successful/month | Runner-minutes/month | % of total |
|---|---|---|---|---|
| Accessibility | 180 | 115.2 | ~6,466 | 13.1% |
| Lighthouse | 120 | 110.4 | ~6,091 | 12.4% |
| Social Media | 360 | 172.8 | **~19,382** | **39.4%** |
| Technology | 360 | 115.2 | ~2,102 | 4.3% |
| Third-Party JS | 120 | 115.2 | ~6,346 | 12.9% |
| Relationships | 120 | 85.0 | ~8,485 | 17.2% |
| Validate URLs Batch | 60 | 38.4 | ~350 | 0.7% |
| **Total (these 7)** | | | **~49,222 min (~820 hours)** | 100% |

Social Media alone accounts for **39% of all measured scanning runner-minutes**, while being the
scanner furthest ahead of its own target cycle (Section 4). This is the largest single efficiency
opportunity identified in this audit.

(GitHub-hosted Linux runners are free for public repositories under the standard Actions minutes
allowance; if this repository is public, the practical constraint is queue fairness and predictability,
not billed minutes — worth confirming, since it changes how much urgency to put on Social Media's
reduction versus treating it as a "correctness of freshness policy" fix.)

---

## 6. Proposed Staggered Cron Schedule **[projection — design, not yet applied]**

Design principles applied: (a) no two scanning workflows share a start minute; (b) nothing starts at
`:00`; (c) the four workflows that currently collide at every 6-hour mark are spread across different
offsets; (d) `generate-scan-progress` moves later relative to the scan cadences it reports on, so it's
less likely to catch a still-running scan mid-flight; (e) Social Media's cron frequency is reduced to
match its measured throughput rather than its original (apparently rate-limit-based) assumption.

| Workflow | Current cron | Proposed cron | Rationale |
|---|---|---|---|
| `scan-accessibility.yml` | `30 */4 * * *` | `17 */4 * * *` | Off minute-30 cluster; keeps 4-hour cadence (on pace to marginal, don't reduce frequency yet) |
| `scan-lighthouse.yml` | `0 */6 * * *` | `07 */6 * * *` | Breaks the 4-way top-of-hour collision; 6-hour cadence unchanged (behind target — see Section 11 Phase 3 for the real fix, which is partitioning, not more cron slots) |
| `scan-social-media.yml` | `0 */2 * * *` | `37 */8 * * *` (3×/day) | **Frequency reduced from 12×/day to 3×/day** — Section 4 shows current effective throughput is ~4× what a 30-day cycle needs; even at 3×/day this scanner should comfortably clear its 30-day target with room to spare, freeing ~39% of current scanning runner-minutes for reallocation |
| `scan-technology.yml` | `0 */2 * * *` | `27 */2 * * *` | Cadence unchanged (12×/day) since it's genuinely behind target, but moved off the collision minute; **paired with the concurrency-group split in Section 8**, which is the change that actually fixes its 64% cancellation rate — cron placement alone won't |
| `scan-third-party-js.yml` | `30 */6 * * *` | `47 */6 * * *` | Off minute-30; cadence unchanged (already ahead of pace) |
| `scan-relationships.yml` | `0 */6 * * *` | `53 */6 * * *` | Breaks the 4-way collision; **must** also get a concurrency group (Section 8) — cron placement doesn't fix the unprotected-commit problem |
| `validate-urls-batch.yml` | `0 1,13 * * *` | `07 1,13 * * *` | Off minute-0; cadence unchanged (on pace for country rotation) |
| `issue-triggered-validation.yml` | `0 * * * *` | `43 * * * *` | Off the single busiest boundary (top of every hour); isolated group already, no other change needed |
| `generate-scan-progress.yml` | `15 */2 * * *` | `57 */6 * * *` (3×/day, plus its existing `workflow_run` triggers) | Cron frequency reduced to align with a data-changed cadence rather than fixed high frequency (Section 9); still gets triggered promptly by real scan completions via `workflow_run`, so administrators aren't waiting up to 6h for a report after a scan finishes — the cron becomes a fallback, not the primary trigger |
| `detect-orphans.yml` | `0 6 1 * *` | `23 6 1 * *` | Off minute-0; monthly cadence unchanged |
| `import-swh-domains.yml` | `0 6 1 * *` | `41 6 1 * *` | Currently collides with `detect-orphans` at the exact same minute on the same day; separated |
| `check-links.yml` | `0 20 * * 3` | `13 20 * * 3` | Off minute-0; weekly cadence unchanged, low-priority/low-risk |
| `reopen-validation-cycle.yml` | `0 0 1 1,4,7,10 *` | `07 0 1 1,4,7,10 *` | Off minute-0; quarterly cadence unchanged |

No two rows above share a start minute, and none start on `:00`. `scan-lighthouse` (`:07`) and
`validate-urls-batch` (`:07`) do share a minute value but on entirely different hour patterns (every
6h vs. twice daily) and different concurrency groups, so this is not a real collision — flagged so it
doesn't look like an oversight.

---

## 7. Recommended Partition Sizes **[projection]**

Current partitioning is "one country = one unit of work" via `--all` scanning every country in TOON-file
order until the internal max-runtime is hit. This is unstable (a 4,469-page country like Canada or an
8,259-domain country like the UK can consume most or all of a run's budget, starving every country that
sorts after it) and doesn't match the task's requirement that partitions "remain stable as URLs are
added" and "produce approximately similar expected runtimes."

**Recommended model**: partition by **page count**, not by country, with a per-scanner target partition
size derived from that scanner's *measured* pages/minute throughput (Section 2) and a conservative
per-run time budget that leaves real margin under the job timeout (not just the existing ~10-minute
buffer, which Section 3.4/2 shows has already failed to protect against a hard-kill at least once).

| Scanner | Measured throughput (pages/min, from Section 2) | Target run budget | Target partition size (pages) | Rationale |
|---|---|---|---|---|
| Accessibility | ~353–665 pages / 54 min ≈ 6.5–12.3/min | 40 min | ~300 pages | Mid-range of observed variance; large countries split across multiple partitions instead of one run absorbing all the variance |
| Lighthouse | 262 pages / 55 min ≈ 4.8/min | 40 min | ~190 pages | Slowest scanner per-page (real browser rendering); smallest partitions of the family, matching the task's explicit note that Lighthouse needs smaller partitions than HTTP-based scanners |
| Social Media | 2,112 pages / 109 min ≈ 19.4/min | 40 min | ~750 pages | Fast, simple HTTP+regex scan; large partitions are safe |
| Technology | 482 pages / 14 min ≈ 34.4/min | 15 min (keep its existing short internal budget — this is the scanner whose problem is queue access, not per-partition size) | ~500 pages | Already fast; the fix for Technology is concurrency-group isolation (Section 8), not bigger partitions |
| Third-Party JS | 1,181+257 pages / 54 min ≈ 26.6/min | 40 min | ~1,000 pages | Fast; already ahead of pace, partition size just needs to stay stable |
| Relationships | **[unverified]** | 40 min | **[needs one cycle of Phase-1 instrumentation before a number can be justified]** | Do not guess a partition size from unclear throughput data — this is exactly the case Phase 1 measurement exists to resolve |

**Partition naming and stability**: partitions should be computed from a stable, deterministic ordering
of `(country, domain)` pairs sorted alphabetically (not by size, which shifts every time the corpus
changes) and then chunked by cumulative page count up to the target size. A partition's identity should
be `<scanner>-<cycle>-<partition-index>` (e.g. `accessibility-2026w30-p04`), not a country name — this
satisfies the requirement that partitions "remain stable as URLs are added" (adding pages to an existing
country shifts later partition boundaries slightly but doesn't renumber or rename earlier, unaffected
partitions under a stable sort) and "expose understandable names in GitHub Actions" (the index and cycle
id are both human-legible).

---

## 8. Revised Concurrency Design **[projection]**

Current state has three problems: (1) the `metadata-scans` group serializes genuinely independent
*scanning* work because of a shared *metadata* write; (2) three different groups (`metadata-scans`,
`validation-background`, `lighthouse-scan`) all touch the same `validation-metadata` artifact without
protecting each other from it; (3) `scan-relationships` has no group at all.

**Proposed separation**, following the task's explicit instruction to split scanning / artifact
creation / metadata merging / report publication into different concurrency domains:

| New/changed group | Protects | Members | cancel-in-progress |
|---|---|---|---|
| *(none — scanning partitions run unconstrained)* | Nothing shared — see Section 9, each scanner's partitions write to their own immutable per-partition artifact, not a shared file | All partition-worker jobs, any scanner | n/a |
| `metadata-merge-<scanner>` (one per scanner, not one shared group) | The scanner's own SQLite merge step only | The single merge job per scanner run, after its partitions complete | true (a superseded merge attempt is safe to cancel and retry) |
| `scan-relationships-commit` | The `docs/data/relationships.jsonl` / `summaries/` git commit step specifically | `scan-relationships.yml`'s commit step only | false (never drop in-flight commit data) |
| `scan-progress-report` (existing, keep) | The generated report pages | `generate-scan-progress.yml` | true (existing, correct — a stale report-generation attempt should yield to a newer one) |
| `pages` (existing, keep) | The Pages deployment | `deploy-pages.yml` | false (existing, correct — never cancel a deploy in flight) |
| `issue-check-runs` (existing, keep — already correctly isolated) | Issue-polling job | `issue-triggered-validation.yml` | false |

**What this removes**: `metadata-scans`, `validation-background`, and `lighthouse-scan` as broad
scanning-serialization groups are retired. Nothing serializes the actual scan work anymore — Technology
no longer waits behind Accessibility, Social Media no longer waits behind Third-Party JS, and Lighthouse
runs are no longer artificially isolated from workflows they never actually needed protection from. The
**only** thing that still needs a lock is each scanner's own metadata-merge step, and it's now scoped
per-scanner rather than shared across five unrelated scanners.

This directly addresses Section 3.3's finding: Technology's 64% cancellation rate was caused by
contention in a group protecting a resource (shared metadata) that a per-scanner merge lock protects
just as safely, without blocking Technology's actual scan work behind Accessibility's.

---

## 9. Artifact and Metadata Merge Design **[projection]**

**Problem restated precisely**: seven workflows currently download the *same* `data/metadata.db`,
mutate their own copy, and re-upload it as the same artifact name — a last-writer-wins race with a
presence-only (not freshness-aware) guard, plus one workflow (`scan-lighthouse`) additionally uploading
a copy of a *different* metadata stream (`lighthouse-metadata`) under this same shared name.

**Recommended pattern**: immutable, per-partition-attempt artifacts, consolidated by a dedicated merge
step — following the task's suggested naming convention.

1. Each partition worker writes its scan results to `data/partition-results/<scanner>-<cycle>-
   <partition-index>-<attempt>.sqlite` (or, more simply, a per-partition JSONL of just the new/changed
   rows — cheaper to merge than a full SQLite file, and avoids ever having two jobs open the same SQLite
   file at once). Uploads it as artifact
   `<scanner>-<cycle>-<partition-index>-<attempt>` — **never `validation-metadata` directly**. This
   artifact is write-once; no partition worker ever downloads or mutates another partition's file.
2. A single merge job (one per scanner, per cycle-tick, running under that scanner's own
   `metadata-merge-<scanner>` group) downloads **all** partition-result artifacts produced since the
   last successful merge, applies them to the canonical `data/metadata.db` in one serialized pass, and
   uploads the updated canonical DB as `validation-metadata` (shared, since downstream report generation
   still needs one canonical file to read).
3. Because each partition's result is immutable and independently retryable, a failed or timed-out
   partition can be rerun without touching any other partition's already-uploaded result, and the merge
   step is naturally idempotent (re-running it against the same set of partition artifacts produces the
   same canonical state) — satisfying the task's "individual failed partitions can be rerun" and "avoid
   requiring every parallel worker to update one shared database" requirements simultaneously.

**Where should the consolidated metadata live?** Evaluated against the task's explicit trade-off list:

| Option | Verdict | Why |
|---|---|---|
| Committed to the repo | **No** | `data/metadata.db` would grow into a large binary blob under version control, bloating clone size and diff noise for every merge; the repo already avoids this for the equally-large `docs/*-data.json` files (explicitly excluded from commits per `generate-scan-progress.yml`'s own comments, for the same 100 MB-limit reason) |
| Workflow artifact (current mechanism, kept but made safe) | **Yes — recommended** | Least disruptive: same mechanism already in use, same 90-day retention pattern already established, zero new infrastructure or credentials. The fix is *how* it's written (immutable partitions + one serialized merge), not *where* it lives. |
| GitHub cache | **No** | Cache entries are evictable under storage pressure and are not designed for "authoritative current state" — a cache miss on the canonical DB would silently reset all scan-state/backoff history, which is exactly the failure mode this whole audit is trying to eliminate |
| GitHub Pages data (`docs/data/`) | **Partially — already used for the *published, derived* output** (relationships.jsonl, summaries), correctly kept separate from the *working* metadata DB. Don't move the working DB here; it would make every scan run part of the public Pages deploy surface. |
| External persistent service | **No — not justified by scale** | 87,183 pages of scan state is well within SQLite's comfortable operating range; introducing an external DB (hosted Postgres, etc.) adds real operational cost (credentials, uptime, cost) to solve a coordination problem that a corrected artifact-merge pattern solves without any new infrastructure |

**Recommendation: keep the workflow-artifact mechanism, fix the write pattern.** This is the
"least disruptive reliable option" the task asks to prefer, and it directly eliminates the race
without requiring new infrastructure, new credentials, or a data-migration.

---

## 10. Proposed Reporting Cadence **[projection]**

Current: `generate-scan-progress.yml` runs on a fixed 2-hour cron **and** on `workflow_run` completion
of 5 scan workflows — meaning, per Section 3.6, it can fire well over its nominal 12×/day, often against
a source dataset still mid-write.

**Proposed**: keep the `workflow_run` triggers (they're the right idea — regenerate promptly *after*
real data changes, per the task's explicit preference for "a reporting cadence based on completed data
batches rather than a fixed high-frequency schedule") but reduce the fallback cron from 12×/day to 4×/day
(`57 */6 * * *`, per Section 6), and add a cheap "did anything actually change" check before doing the
expensive report-regeneration work — e.g. compare a hash of the source metadata files against the hash
recorded at the last successful report commit, and skip regeneration (not just skip the git commit) when
unchanged. This addresses all four of the task's explicit "avoid repeatedly..." items: it stops
re-downloading artifacts for a report that won't change, stops rebuilding unchanged reports, stops
committing unchanged files (the existing `git diff --cached --quiet` check already does this for the
*commit*, but the *build* work still happens first — moving the check earlier saves the build cost too),
and — because `deploy-pages.yml` triggers on `generate-scan-progress.yml` completion — stops triggering
redundant deploys.

---

## 11. Migration Plan — 5 Phases

Per the task's explicit instruction, **no scheduling or code change in this document has been applied
yet** beyond what was already committed earlier in this session (the government-domain-registry fix,
the Canada seed addition, and the two CI bug fixes — all unrelated to orchestration). Everything below
is a plan for review, not a fait accompli.

### Phase 1 — Measure (this document + minimal instrumentation, no scheduling changes)
- Ship the `$GITHUB_STEP_SUMMARY` instrumentation (Section 13/14) to every scanning workflow so future
  runs record: scheduled vs. actual start time, queue delay, setup/scan/artifact durations, URLs
  eligible/attempted/completed/failed/skipped, throughput/min, remaining URLs, projected completion
  date, on-pace status, runner-minutes used.
- Add the schedule-reliability distinguishing fields the task requests (Section 14: which of "GitHub
  delayed," "concurrency lock delayed," "no eligible work," "setup failed," "scanner failed," "merge
  failed," "hit timeout," "completed normally" applies to each run).
- **No cron changes, no concurrency changes, no partitioning changes in this phase.** The goal is to
  replace this document's Section 2/4 estimates (built from a 25-run retrospective sample) with live,
  ongoing, per-run data before making structural changes.
- Concrete deliverable for this phase: Section 12 below (a small, additive YAML change — a reusable
  summary-writing step, not a scheduling rewrite).

### Phase 2 — Remove obvious collisions
- Apply the staggered cron table in Section 6 (minute changes only — no frequency changes except Social
  Media, which is justified by Section 4's measured 4× overshoot, not a guess).
- Correct `docs/batched-validation.md`'s stale "every 2 hours" claim about `validate-urls-batch.yml`
  (actual: twice daily) — a real documentation defect found in this audit, unrelated to scheduling logic
  itself but directly relevant to "documentation containing runtime assumptions."
- Fix the `scan-technology.yml` `--limit` dispatch-input-to-nonexistent-flag bug (Section 1.4) — small,
  isolated, unrelated to orchestration but found during this audit and worth fixing in the same pass
  since it touches the same file.

### Phase 3 — Partition work
- Implement the page-count-based partitioning model (Section 7) for Accessibility, Lighthouse,
  Social Media, and Third-Party JS first (the four with clean measured throughput data). Defer
  Relationships until Phase 1's instrumentation produces a real throughput number for it.
- Introduce a reusable worker workflow (`workflow_call`) that each scanner's controller invokes per
  partition, to avoid duplicating the checkout/setup/scan/upload YAML five times.
- Add partition-level retry: a failed partition can be re-dispatched by partition ID without
  re-running its siblings.

### Phase 4 — Fix shared-state coordination
- Implement the immutable-partition-artifact + serialized-merge pattern (Section 9).
- Retire `metadata-scans`, `validation-background`, `lighthouse-scan` as broad scanning locks; replace
  with the per-scanner `metadata-merge-<scanner>` groups (Section 8).
- Add the `scan-relationships-commit` group and give `scan-relationships.yml` concurrency protection
  for the first time.

### Phase 5 — Capacity-based orchestration
- Compute per-scanner on-pace status (Section 4's methodology, now fed by live Phase-1 data instead of
  a retrospective sample) automatically, on a schedule, and surface it in a dashboard/summary.
- Implement the scheduling-priority order from the task (deadline-risk first, then incomplete prior
  work, then never-scanned URLs, then current-cycle-incomplete, then newly added, then routine refresh,
  then reporting/maintenance last) as the actual partition-selection logic for a `crawl-controller`-style
  dispatcher.
- Enable the Catch-up runtime profile (Section 14) to be triggered automatically when a scanner is
  projected behind its deadline, without a human needing to notice first.

---

## 12. Phase 1 YAML — Concrete Change

Phase 1 is deliberately additive and low-risk: a new reusable step that writes the operational summary
required by the task, wired into the existing `scan-accessibility.yml` as a pilot (the same pattern
would be copy-pasted into the other scanners in a follow-up commit once reviewed — not done here, to
keep this first change small and reviewable per the task's own migration-approach instruction).

```yaml
# .github/workflows/scan-accessibility.yml
# ADDITIVE CHANGE ONLY — no cron/timeout/concurrency edits in this phase.

jobs:
  scan-accessibility:
    timeout-minutes: 65
    concurrency:
      group: metadata-scans   # unchanged in Phase 1 — see Phase 2/4 for the real fix
      cancel-in-progress: false
    steps:
      - name: Record scheduled vs actual start time
        id: timing
        run: |
          # github.event.schedule is only set for schedule-triggered runs;
          # for workflow_dispatch there is no "intended" time to compare against.
          echo "actual_start=$(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$GITHUB_OUTPUT"
          echo "scheduled_cron=${{ github.event.schedule || 'n/a (manual dispatch)' }}" >> "$GITHUB_OUTPUT"

      # ... existing checkout / setup-python / install / find-metadata / download-metadata steps unchanged ...

      - name: Run accessibility scan (all countries)
        id: scan
        run: |
          SCAN_START=$(date -u +%Y-%m-%dT%H:%M:%SZ)
          echo "scan_start=$SCAN_START" >> "$GITHUB_OUTPUT"
          SKIP_DAYS="${{ github.event.inputs.skip_recently_scanned_days || '7' }}"
          set -o pipefail
          python3 -m src.cli.scan_accessibility \
            --all \
            --max-runtime 55 \
            --rate-limit "${{ github.event.inputs.rate_limit || '1.0' }}" \
            --skip-recently-scanned-days "$SKIP_DAYS" \
            2>&1 | tee accessibility-scan-output.txt
          echo "scan_end=$(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$GITHUB_OUTPUT"

      # ... existing artifact upload / db-guard / metadata-update steps unchanged ...

      - name: Write operational summary
        if: always()
        run: |
          # Parse observed counts from the scan output rather than guessing —
          # matches the "Reachable: N" / "Unreachable: N" lines already emitted
          # by AccessibilityScannerJob (confirmed present in real logs, Section 2).
          ATTEMPTED=$(grep -oP 'Reachable:\s+\K\d+' accessibility-scan-output.txt | paste -sd+ | bc 2>/dev/null || echo "unknown")
          FAILED=$(grep -oP 'Unreachable:\s+\K\d+' accessibility-scan-output.txt | paste -sd+ | bc 2>/dev/null || echo "unknown")

          {
            echo "## Accessibility Scan — Operational Summary"
            echo ""
            echo "| Field | Value |"
            echo "|---|---|"
            echo "| Scanner | accessibility |"
            echo "| Scheduled start (cron) | ${{ steps.timing.outputs.scheduled_cron }} |"
            echo "| Actual job start | ${{ steps.timing.outputs.actual_start }} |"
            echo "| Scan step start | ${{ steps.scan.outputs.scan_start }} |"
            echo "| Scan step end | ${{ steps.scan.outputs.scan_end }} |"
            echo "| URLs attempted (reachable) | $ATTEMPTED |"
            echo "| URLs failed (unreachable) | $FAILED |"
            echo "| Run conclusion | ${{ job.status }} |"
            echo ""
            echo "_Phase 1 instrumentation — throughput/cycle-projection fields land in Phase 5 once the_"
            echo "_capacity-tracking logic (WORKFLOW_ORCHESTRATION_AUDIT.md Section 11) is implemented._"
          } >> "$GITHUB_STEP_SUMMARY"
```

This change: (a) adds no new external dependencies, (b) does not touch the cron, timeout, or concurrency
configuration, (c) is purely additive — if the summary step itself fails, `if: always()` ensures it
doesn't affect the run's actual conclusion, (d) gives administrators the first piece of the visibility
requirement (Section 14) without any risk to the existing scan behavior.

---

## 13. Tests

Four categories, per the task's requirement (schedule, partition, freshness, metadata safety). These are
proposed **[projection]** test designs to accompany Phase 2–4 implementation, not yet written as actual
test files (per the task's "do not modify files until inventory/analysis complete" instruction — this
audit itself is the analysis; the tests below are the next actionable step, written here as specs).

### 13.1 Schedule tests (`tests/unit/test_workflow_schedules.py`)
```python
"""Parses every .github/workflows/*.yml with a `schedule:` trigger and asserts
no two scanning workflows share a start-minute, and none start at :00."""

def test_no_two_scanning_workflows_share_a_start_minute():
    # Parse cron `minute` field for every workflow file matching scan-*.yml,
    # validate-urls-batch.yml, generate-scan-progress.yml, issue-triggered-validation.yml.
    # Assert the set of minute values has no duplicates.
    ...

def test_no_scanning_workflow_starts_at_minute_zero():
    # Same file set; assert minute != 0 for every cron.
    ...

def test_cron_expressions_are_valid():
    # Use croniter (or equivalent) to confirm every cron string parses and
    # produces a sane next-run time, catching typos before they ship.
    ...
```

### 13.2 Partition tests (`tests/unit/test_partition_stability.py`)
```python
"""Verifies the page-count partitioning model (Section 7) is stable as URLs
are added, produces balanced runtimes, and preserves every page exactly once."""

def test_partitions_cover_every_page_exactly_once():
    # Given a synthetic corpus of N countries/pages, partition it, and assert
    # the union of all partitions equals the input set with no duplicates/gaps.
    ...

def test_partition_sizes_stay_within_target_tolerance():
    # Assert every partition's total page count is within e.g. +/-20% of the
    # scanner's configured target_partition_size (Section 7's table).
    ...

def test_adding_pages_does_not_renumber_unaffected_earlier_partitions():
    # Partition a corpus, add pages to one country, re-partition, and assert
    # partitions before the affected boundary keep the same partition-index
    # and page membership.
    ...

def test_partition_ids_are_deterministic():
    # Same corpus in, same partition assignment out, run twice.
    ...
```

### 13.3 Freshness tests (`tests/unit/test_freshness_skip_consistency.py`)
```python
"""Confirms each scanner's skip-recently-scanned-days logic actually excludes
what it claims to, and that the workflow-passed value matches documentation."""

def test_skip_recently_scanned_excludes_urls_within_window():
    # Seed a fake scan-state row with last_seen = now - 3 days, run with
    # skip_recently_scanned_days=7, assert the URL is excluded from the batch.
    ...

def test_skip_recently_scanned_includes_urls_outside_window():
    # Same, but last_seen = now - 10 days; assert the URL IS included.
    ...

def test_workflow_freshness_defaults_match_capacity_plan():
    # Regression guard: if Section 4's capacity math assumed accessibility=7d,
    # lighthouse=30d, relationships=28d, assert the actual --skip-recently-
    # scanned-days values passed in each workflow YAML still match — catches
    # silent drift between the capacity plan and the deployed configuration.
    ...
```

### 13.4 Metadata-safety tests (`tests/unit/test_metadata_merge_safety.py`)
```python
"""Verifies the Phase-4 immutable-partition-artifact + merge pattern (Section 9)
cannot lose data the way the current shared-artifact overwrite can."""

def test_merge_is_idempotent():
    # Apply the same set of partition-result files to a metadata DB twice;
    # assert the resulting DB state is identical both times.
    ...

def test_merge_never_loses_a_partition_result():
    # Simulate two partitions completing "concurrently" (in any order), merge
    # both, and assert both partitions' rows are present in the final DB --
    # this is the direct regression test for the last-writer-wins bug found
    # in Section 1.5/2 (scan-social-media run 29709440932's missing-DB guard
    # failure, and the cross-group race between metadata-scans/
    # validation-background/lighthouse-scan).
    ...

def test_partial_partition_failure_does_not_corrupt_merged_state():
    # Simulate one partition's result file being malformed/truncated; assert
    # the merge step rejects only that partition (logs an error, leaves it
    # for retry) without corrupting the other partitions' already-merged data.
    ...

def test_scan_technology_limit_flag_matches_argparse():
    # Regression guard for the concrete bug found in Section 1.4: parse
    # scan-technology.yml's workflow_dispatch inputs and cross-check every
    # input that gets conditionally appended to the CLI invocation actually
    # exists as an argparse argument in scan_technology.py.
    ...
```

---

## 14. Administrator Documentation

### 14.1 `workflow_dispatch` interface (proposed, Phase 3+)

Every scanner workflow should expose the following manual inputs, building on what several already
have (`country`, `rate_limit`) with the additions the task requests:

```yaml
on:
  workflow_dispatch:
    inputs:
      cycle:
        description: 'Cycle ID to operate on (default: current active cycle)'
        required: false
        type: string
      country:
        description: 'Restrict to one country code (default: all)'
        required: false
        type: string
      partition:
        description: 'Restrict to one partition index (e.g. p04). Requires country or "all".'
        required: false
        type: string
      retry_failed_only:
        description: 'Only re-run partitions marked failed in the current cycle'
        required: false
        type: boolean
        default: false
      incomplete_only:
        description: 'Only process partitions not yet completed this cycle (skip already-done work)'
        required: false
        type: boolean
        default: false
      ignore_freshness:
        description: 'Bypass --skip-recently-scanned-days and re-scan regardless of last-seen date'
        required: false
        type: boolean
        default: false
      max_runtime_minutes:
        description: 'Override the internal scanner max-runtime (must stay below job timeout)'
        required: false
        type: string
      max_partitions:
        description: 'Cap how many partitions this dispatch will process'
        required: false
        type: string
      max_parallel_jobs:
        description: 'Cap concurrent partition-worker jobs (matrix max-parallel)'
        required: false
        type: string
      dry_run:
        description: 'Compute what would run without actually scanning or writing metadata'
        required: false
        type: boolean
        default: false
      runtime_profile:
        description: 'cautious | normal | catchup'
        required: false
        type: choice
        options: [cautious, normal, catchup]
        default: normal
```

### 14.2 Runtime profiles — exact configuration, derived from Section 2's measured data

| Profile | Max parallel partition jobs | Partition size multiplier | Timeout safety margin | Intended use |
|---|---|---|---|---|
| **Cautious** | 2 | 0.5× (half the Section 7 target size) | 20 min buffer under job timeout (up from the current ~10 min, which Section 3.4 shows has already failed once) | Debugging an unstable scanner, or the first dispatch after a Phase 3/4 code change, before trusting it at full scale |
| **Normal** | 4–6 (scaled to how many partitions a scanner has at its Section 7 target size) | 1.0× | 10 min buffer (current default) | Standard scheduled operation, expected to meet the scanner's Section 4 target cycle |
| **Catch-up** | 8–10 | 1.0× (not larger — bigger partitions increase single-failure blast radius, which the task explicitly warns against) | 10 min buffer (unchanged — catch-up increases parallelism, not per-job risk tolerance) | Only when Section 4/5's live on-pace calculation shows a scanner projected to miss its cycle deadline. **Must never bypass the metadata-merge locking from Section 8/9** — more parallel partition workers is safe because they write immutable per-partition artifacts; skipping the serialized merge step is not, and Catch-up mode does not do that. |

### 14.3 Reading the on-pace status

Once Phase 5 lands, each scanner's status (ahead / on-pace / marginal / behind) is computed the same way
as Section 4 of this document, but from live rolling data instead of a 25-run retrospective sample:

- **Ahead**: projected cycle days < 80% of target — candidate for a frequency *reduction* (as recommended
  for Social Media in Section 6/11).
- **On-pace**: projected cycle days between 80–100% of target.
- **Marginal**: projected cycle days 100–130% of target — worth watching, not yet urgent.
- **Behind**: projected cycle days > 130% of target, or the scanner has never completed a full cycle in
  the observable history — becomes eligible for Catch-up profile auto-dispatch under Phase 5's priority
  order (deadline-risk first, per the task's explicit scheduling-priority list).

### 14.4 Known issues to track separately from this audit

Two defects were found during this audit that are **not** orchestration/scheduling problems and can be
fixed independently, on their own timeline, without waiting for any phase above:

1. `scan-technology.yml` passes a `--limit` value from a `workflow_dispatch` input to
   `scan_technology.py`, which has no such argparse argument — any manual dispatch with `limit` set will
   fail immediately (Section 1.4).
2. `docs/batched-validation.md` states `validate-urls-batch.yml` runs "every 2 hours" — the actual cron
   is twice daily (`0 1,13 * * *`). This is a documentation accuracy issue, not a scheduling one, but
   directly relevant to anyone reading that doc to understand actual system cadence.

---

## Summary of confidence levels

- **Section 1 (inventory)** and **Section 3 (collisions)**: high confidence — read directly from the 18
  workflow files and cross-checked against source code, not inferred.
- **Section 2 (historical runtime)**: high confidence for the workflows with 20+ sampled runs
  (accessibility, lighthouse, social-media, technology, third-party-js, validate-urls-batch); explicitly
  flagged as low-confidence/gap for `scan-overlays` (1 run ever) and partially unverified for
  `scan-relationships`' per-run URL counts.
- **Section 4/5 (capacity and runner-minutes)**: medium confidence — built from real measured inputs via
  explicit, shown formulas, but success rates and observed-URLs-per-run are drawn from a retrospective
  sample rather than a full population; Phase 1's instrumentation (Section 12) exists specifically to
  upgrade these from **[projection]** to **[measured]** on an ongoing basis.
- **Sections 6–10 (redesign)**: proposals, not yet applied to any workflow file. Ready for review.
