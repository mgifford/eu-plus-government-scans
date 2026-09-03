---
title: Scanner Cycle Pace Report
layout: page
---

_Generated: 2026-09-03 13:39 UTC_

Whether each scanner is on pace to complete its target cycle (30 days for most
covered in the last 7 days projected forward against the full eligible corpus.
For Relationships, coverage means a successful source-page scan; failed attempts
do not count toward relationship coverage. See
[WORKFLOW_ORCHESTRATION_AUDIT.md](https://github.com/mgifford/eu-plus-government-scans/blob/main/WORKFLOW_ORCHESTRATION_AUDIT.md)
Section 11 for the methodology.

| Scanner | Target cycle | Eligible URLs | Covered (window) | Daily throughput | Projected cycle | Status |
|---|---|---|---|---|---|---|
| accessibility | 30d | 87,696 | 21,178 (last 7d) | 3,025.4/day | 29.0d | 🟢 On pace |
| social_media | 30d | 87,696 | 21,801 (last 7d) | 3,114.4/day | 28.2d | 🟢 On pace |
| technology | 30d | 87,696 | 21,448 (last 7d) | 3,064.0/day | 28.6d | 🟢 On pace |
| third_party_js | 30d | 87,696 | 23,464 (last 7d) | 3,352.0/day | 26.2d | 🟢 On pace |
| overlays | 30d | 87,696 | 991 (last 7d) | 141.6/day | 619.4d | 🔴 Behind |
| relationships | 60d | 87,696 | 16,884 (last 7d) | 2,412.0/day | 36.4d | 🟢 Ahead |
| lighthouse | 60d | 87,696 | 3,930 (last 7d) | 561.4/day | 156.2d | 🔴 Behind |

_Projection method: `effective daily throughput = distinct URLs covered in the last 7 days ÷ 7`;
`projected cycle days = eligible URLs ÷ effective daily throughput`. The 7-day measurement
window reflects recent scan velocity and is independent of each scanner's own target cycle
length. Relationships measures successful source-page coverage using
`relationship_scan_state.last_successful_at`; other scanners use their configured scan
timestamp. See src/services/cycle_pace_tracker.py's module docstring for why. 'No data' means
the scanner has no rows in its metadata.db within the window (never run against this database,
or the database doesn't cover this scanner)._
