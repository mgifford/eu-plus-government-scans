---
title: Scanner Cycle Pace Report
layout: page
---

_Generated: 2026-11-23 09:11 UTC_

Whether each scanner is on pace to complete its target cycle (30 days for most
covered in the last 7 days projected forward against the full eligible corpus.
For Relationships, coverage means a successful source-page scan; failed attempts
do not count toward relationship coverage. See
[WORKFLOW_ORCHESTRATION_AUDIT.md](https://github.com/mgifford/eu-plus-government-scans/blob/main/WORKFLOW_ORCHESTRATION_AUDIT.md)
Section 11 for the methodology.

| Scanner | Target cycle | Eligible URLs | Corpus covered | Covered (window) | Daily throughput | Projected cycle | Status |
|---|---|---|---|---|---|---|---|
| accessibility | 30d | 87,696 | 100.0% (87,690) | 12,303 (last 7d) | 1,757.6/day | 49.9d | 🟢 Caught up |
| social_media | 30d | 87,696 | 100.0% (87,690) | 15,939 (last 7d) | 2,277.0/day | 38.5d | 🟡 Marginal |
| technology | 30d | 87,696 | 100.0% (87,690) | 17,787 (last 7d) | 2,541.0/day | 34.5d | 🟡 Marginal |
| third_party_js | 30d | 87,696 | 100.0% (87,690) | 12,431 (last 7d) | 1,775.9/day | 49.4d | 🟢 Caught up |
| overlays | 30d | 87,696 | 1.7% (1,523) | 0 (last 7d) | 0.0/day | —d | ⚪ No data |
| preferences | 90d | 87,696 | 10.0% (8,751) | 1,572 (last 7d) | 224.6/day | 390.5d | 🔴 Behind |
| relationships | 60d | 87,696 | 94.6% (82,959) | 17,729 (last 7d) | 2,532.7/day | 34.6d | 🟢 Ahead |
| lighthouse | 60d | 87,696 | 100.0% (87,690) | 12,961 (last 7d) | 1,851.6/day | 47.4d | 🟢 Ahead |

_Projection method: `effective daily throughput = distinct URLs covered in the last 7 days ÷ 7`;
`projected cycle days = eligible URLs ÷ effective daily throughput`. The 7-day measurement
window reflects recent scan velocity and is independent of each scanner's own target cycle
length. Relationships measures successful source-page coverage using
`relationship_scan_state.last_successful_at`; other scanners use their configured scan
timestamp. See src/services/cycle_pace_tracker.py's module docstring for why. 'No data' means
the scanner has no rows in its metadata.db within the window (never run against this database,
or the database doesn't cover this scanner)._
