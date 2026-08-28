---
title: Scanner Cycle Pace Report
layout: page
---

_Generated: 2026-08-28 01:44 UTC_

Whether each scanner is on pace to complete its target cycle (30 days for most
covered in the last 7 days projected forward against the full eligible corpus.
For Relationships, coverage means a successful source-page scan; failed attempts
do not count toward relationship coverage. See
[WORKFLOW_ORCHESTRATION_AUDIT.md](https://github.com/mgifford/eu-plus-government-scans/blob/main/WORKFLOW_ORCHESTRATION_AUDIT.md)
Section 11 for the methodology.

| Scanner | Target cycle | Eligible URLs | Covered (window) | Daily throughput | Projected cycle | Status |
|---|---|---|---|---|---|---|
| accessibility | 30d | 87,696 | 39,702 (last 7d) | 5,671.7/day | 15.5d | 🟢 Ahead |
| social_media | 30d | 87,696 | 21,810 (last 7d) | 3,115.7/day | 28.1d | 🟢 On pace |
| technology | 30d | 87,696 | 24,268 (last 7d) | 3,466.9/day | 25.3d | 🟢 On pace |
| third_party_js | 30d | 87,696 | 15,750 (last 7d) | 2,250.0/day | 39.0d | 🟡 Marginal |
| overlays | 30d | 87,696 | 1,469 (last 7d) | 209.9/day | 417.9d | 🔴 Behind |
| relationships | 60d | 87,696 | 19,886 (last 7d) | 2,840.9/day | 30.9d | 🟢 Ahead |
| lighthouse | 60d | 87,696 | 5,291 (last 7d) | 755.9/day | 116.0d | 🔴 Behind |

_Projection method: `effective daily throughput = distinct URLs covered in the last 7 days ÷ 7`;
`projected cycle days = eligible URLs ÷ effective daily throughput`. The 7-day measurement
window reflects recent scan velocity and is independent of each scanner's own target cycle
length. Relationships measures successful source-page coverage using
`relationship_scan_state.last_successful_at`; other scanners use their configured scan
timestamp. See src/services/cycle_pace_tracker.py's module docstring for why. 'No data' means
the scanner has no rows in its metadata.db within the window (never run against this database,
or the database doesn't cover this scanner)._
