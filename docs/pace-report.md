---
title: Scanner Cycle Pace Report
layout: page
---

_Generated: 2026-09-01 19:23 UTC_

Whether each scanner is on pace to complete its target cycle (30 days for most
covered in the last 7 days projected forward against the full eligible corpus.
For Relationships, coverage means a successful source-page scan; failed attempts
do not count toward relationship coverage. See
[WORKFLOW_ORCHESTRATION_AUDIT.md](https://github.com/mgifford/eu-plus-government-scans/blob/main/WORKFLOW_ORCHESTRATION_AUDIT.md)
Section 11 for the methodology.

| Scanner | Target cycle | Eligible URLs | Covered (window) | Daily throughput | Projected cycle | Status |
|---|---|---|---|---|---|---|
| accessibility | 30d | 87,696 | 23,041 (last 7d) | 3,291.6/day | 26.6d | 🟢 On pace |
| social_media | 30d | 87,696 | 18,050 (last 7d) | 2,578.6/day | 34.0d | 🟡 Marginal |
| technology | 30d | 87,696 | 26,462 (last 7d) | 3,780.3/day | 23.2d | 🟢 Ahead |
| third_party_js | 30d | 87,696 | 23,920 (last 7d) | 3,417.1/day | 25.7d | 🟢 On pace |
| overlays | 30d | 87,696 | 1,469 (last 7d) | 209.9/day | 417.9d | 🔴 Behind |
| relationships | 60d | 87,696 | 13,486 (last 7d) | 1,926.6/day | 45.5d | 🟢 Ahead |
| lighthouse | 60d | 87,696 | 3,964 (last 7d) | 566.3/day | 154.9d | 🔴 Behind |

_Projection method: `effective daily throughput = distinct URLs covered in the last 7 days ÷ 7`;
`projected cycle days = eligible URLs ÷ effective daily throughput`. The 7-day measurement
window reflects recent scan velocity and is independent of each scanner's own target cycle
length. Relationships measures successful source-page coverage using
`relationship_scan_state.last_successful_at`; other scanners use their configured scan
timestamp. See src/services/cycle_pace_tracker.py's module docstring for why. 'No data' means
the scanner has no rows in its metadata.db within the window (never run against this database,
or the database doesn't cover this scanner)._
