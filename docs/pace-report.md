---
title: Scanner Cycle Pace Report
layout: page
---

_Generated: 2026-08-31 16:56 UTC_

Whether each scanner is on pace to complete its target cycle (30 days for most
covered in the last 7 days projected forward against the full eligible corpus.
For Relationships, coverage means a successful source-page scan; failed attempts
do not count toward relationship coverage. See
[WORKFLOW_ORCHESTRATION_AUDIT.md](https://github.com/mgifford/eu-plus-government-scans/blob/main/WORKFLOW_ORCHESTRATION_AUDIT.md)
Section 11 for the methodology.

| Scanner | Target cycle | Eligible URLs | Covered (window) | Daily throughput | Projected cycle | Status |
|---|---|---|---|---|---|---|
| accessibility | 30d | 87,696 | 25,748 (last 7d) | 3,678.3/day | 23.8d | 🟢 Ahead |
| social_media | 30d | 87,696 | 18,944 (last 7d) | 2,706.3/day | 32.4d | 🟡 Marginal |
| technology | 30d | 87,696 | 26,708 (last 7d) | 3,815.4/day | 23.0d | 🟢 Ahead |
| third_party_js | 30d | 87,696 | 23,683 (last 7d) | 3,383.3/day | 25.9d | 🟢 On pace |
| overlays | 30d | 87,696 | 1,469 (last 7d) | 209.9/day | 417.9d | 🔴 Behind |
| relationships | 60d | 87,696 | 13,582 (last 7d) | 1,940.3/day | 45.2d | 🟢 Ahead |
| lighthouse | 60d | 87,696 | 4,359 (last 7d) | 622.7/day | 140.8d | 🔴 Behind |

_Projection method: `effective daily throughput = distinct URLs covered in the last 7 days ÷ 7`;
`projected cycle days = eligible URLs ÷ effective daily throughput`. The 7-day measurement
window reflects recent scan velocity and is independent of each scanner's own target cycle
length. Relationships measures successful source-page coverage using
`relationship_scan_state.last_successful_at`; other scanners use their configured scan
timestamp. See src/services/cycle_pace_tracker.py's module docstring for why. 'No data' means
the scanner has no rows in its metadata.db within the window (never run against this database,
or the database doesn't cover this scanner)._
