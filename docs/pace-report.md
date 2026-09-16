---
title: Scanner Cycle Pace Report
layout: page
---

_Generated: 2026-09-16 14:15 UTC_

Whether each scanner is on pace to complete its target cycle (30 days for most
covered in the last 7 days projected forward against the full eligible corpus.
For Relationships, coverage means a successful source-page scan; failed attempts
do not count toward relationship coverage. See
[WORKFLOW_ORCHESTRATION_AUDIT.md](https://github.com/mgifford/eu-plus-government-scans/blob/main/WORKFLOW_ORCHESTRATION_AUDIT.md)
Section 11 for the methodology.

| Scanner | Target cycle | Eligible URLs | Covered (window) | Daily throughput | Projected cycle | Status |
|---|---|---|---|---|---|---|
| accessibility | 30d | 87,696 | 275 (last 7d) | 39.3/day | 2,232.3d | 🔴 Behind |
| social_media | 30d | 87,696 | 21,015 (last 7d) | 3,002.1/day | 29.2d | 🟢 On pace |
| technology | 30d | 87,696 | 27,314 (last 7d) | 3,902.0/day | 22.5d | 🟢 Ahead |
| third_party_js | 30d | 87,696 | 23,773 (last 7d) | 3,396.1/day | 25.8d | 🟢 On pace |
| overlays | 30d | 87,696 | 0 (last 7d) | 0.0/day | —d | ⚪ No data |
| relationships | 60d | 87,696 | 314 (last 7d) | 44.9/day | 1,955.0d | 🔴 Behind |
| lighthouse | 60d | 87,696 | 7,172 (last 7d) | 1,024.6/day | 85.6d | 🔴 Behind |

_Projection method: `effective daily throughput = distinct URLs covered in the last 7 days ÷ 7`;
`projected cycle days = eligible URLs ÷ effective daily throughput`. The 7-day measurement
window reflects recent scan velocity and is independent of each scanner's own target cycle
length. Relationships measures successful source-page coverage using
`relationship_scan_state.last_successful_at`; other scanners use their configured scan
timestamp. See src/services/cycle_pace_tracker.py's module docstring for why. 'No data' means
the scanner has no rows in its metadata.db within the window (never run against this database,
or the database doesn't cover this scanner)._
