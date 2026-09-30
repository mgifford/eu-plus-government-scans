---
title: Scanner Cycle Pace Report
layout: page
---

_Generated: 2026-09-30 23:10 UTC_

Whether each scanner is on pace to complete its target cycle (30 days for most
covered in the last 7 days projected forward against the full eligible corpus.
For Relationships, coverage means a successful source-page scan; failed attempts
do not count toward relationship coverage. See
[WORKFLOW_ORCHESTRATION_AUDIT.md](https://github.com/mgifford/eu-plus-government-scans/blob/main/WORKFLOW_ORCHESTRATION_AUDIT.md)
Section 11 for the methodology.

| Scanner | Target cycle | Eligible URLs | Corpus covered | Covered (window) | Daily throughput | Projected cycle | Status |
|---|---|---|---|---|---|---|---|
| accessibility | 30d | 87,696 | 100.0% (87,690) | 19,874 (last 7d) | 2,839.1/day | 30.9d | 🟡 Marginal |
| social_media | 30d | 87,696 | 100.0% (87,690) | 20,559 (last 7d) | 2,937.0/day | 29.9d | 🟢 On pace |
| technology | 30d | 87,696 | 100.0% (87,690) | 24,761 (last 7d) | 3,537.3/day | 24.8d | 🟢 On pace |
| third_party_js | 30d | 87,696 | 100.0% (87,690) | 21,056 (last 7d) | 3,008.0/day | 29.2d | 🟢 On pace |
| overlays | 30d | 87,696 | 1.7% (1,523) | 0 (last 7d) | 0.0/day | —d | ⚪ No data |
| relationships | 60d | 87,696 | 93.8% (82,216) | 20,524 (last 7d) | 2,932.0/day | 29.9d | 🟢 Ahead |
| lighthouse | 60d | 87,696 | 60.5% (53,071) | 23,147 (last 7d) | 3,306.7/day | 26.5d | 🟢 Ahead |

_Projection method: `effective daily throughput = distinct URLs covered in the last 7 days ÷ 7`;
`projected cycle days = eligible URLs ÷ effective daily throughput`. The 7-day measurement
window reflects recent scan velocity and is independent of each scanner's own target cycle
length. Relationships measures successful source-page coverage using
`relationship_scan_state.last_successful_at`; other scanners use their configured scan
timestamp. See src/services/cycle_pace_tracker.py's module docstring for why. 'No data' means
the scanner has no rows in its metadata.db within the window (never run against this database,
or the database doesn't cover this scanner)._
