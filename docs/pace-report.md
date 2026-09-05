---
title: Scanner Cycle Pace Report
layout: page
---

_Generated: 2026-09-05 05:50 UTC_

Whether each scanner is on pace to complete its target cycle (30 days for most
covered in the last 7 days projected forward against the full eligible corpus.
For Relationships, coverage means a successful source-page scan; failed attempts
do not count toward relationship coverage. See
[WORKFLOW_ORCHESTRATION_AUDIT.md](https://github.com/mgifford/eu-plus-government-scans/blob/main/WORKFLOW_ORCHESTRATION_AUDIT.md)
Section 11 for the methodology.

| Scanner | Target cycle | Eligible URLs | Covered (window) | Daily throughput | Projected cycle | Status |
|---|---|---|---|---|---|---|
| accessibility | 30d | 87,696 | 25,789 (last 7d) | 3,684.1/day | 23.8d | 🟢 Ahead |
| social_media | 30d | 87,696 | 25,917 (last 7d) | 3,702.4/day | 23.7d | 🟢 Ahead |
| technology | 30d | 87,696 | 17,168 (last 7d) | 2,452.6/day | 35.8d | 🟡 Marginal |
| third_party_js | 30d | 87,696 | 28,303 (last 7d) | 4,043.3/day | 21.7d | 🟢 Ahead |
| overlays | 30d | 87,696 | 0 (last 7d) | 0.0/day | —d | ⚪ No data |
| relationships | 60d | 87,696 | 23,234 (last 7d) | 3,319.1/day | 26.4d | 🟢 Ahead |
| lighthouse | 60d | 87,696 | 3,896 (last 7d) | 556.6/day | 157.6d | 🔴 Behind |

_Projection method: `effective daily throughput = distinct URLs covered in the last 7 days ÷ 7`;
`projected cycle days = eligible URLs ÷ effective daily throughput`. The 7-day measurement
window reflects recent scan velocity and is independent of each scanner's own target cycle
length. Relationships measures successful source-page coverage using
`relationship_scan_state.last_successful_at`; other scanners use their configured scan
timestamp. See src/services/cycle_pace_tracker.py's module docstring for why. 'No data' means
the scanner has no rows in its metadata.db within the window (never run against this database,
or the database doesn't cover this scanner)._
