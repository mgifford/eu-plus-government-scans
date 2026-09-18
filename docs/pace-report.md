---
title: Scanner Cycle Pace Report
layout: page
---

_Generated: 2026-09-18 16:56 UTC_

Whether each scanner is on pace to complete its target cycle (30 days for most
covered in the last 7 days projected forward against the full eligible corpus.
For Relationships, coverage means a successful source-page scan; failed attempts
do not count toward relationship coverage. See
[WORKFLOW_ORCHESTRATION_AUDIT.md](https://github.com/mgifford/eu-plus-government-scans/blob/main/WORKFLOW_ORCHESTRATION_AUDIT.md)
Section 11 for the methodology.

| Scanner | Target cycle | Eligible URLs | Corpus covered | Covered (window) | Daily throughput | Projected cycle | Status |
|---|---|---|---|---|---|---|---|
| accessibility | 30d | 87,696 | 100.0% (87,690) | 5,092 (last 7d) | 727.4/day | 120.6d | 🟢 Caught up |
| social_media | 30d | 87,696 | 100.0% (87,690) | 24,570 (last 7d) | 3,510.0/day | 25.0d | 🟢 On pace |
| technology | 30d | 87,696 | 100.0% (87,690) | 33,377 (last 7d) | 4,768.1/day | 18.4d | 🟢 Ahead |
| third_party_js | 30d | 87,696 | 100.0% (87,690) | 15,172 (last 7d) | 2,167.4/day | 40.5d | 🟢 Caught up |
| overlays | 30d | 87,696 | 1.7% (1,523) | 0 (last 7d) | 0.0/day | —d | ⚪ No data |
| relationships | 60d | 87,696 | 93.3% (81,831) | 7,178 (last 7d) | 1,025.4/day | 85.5d | 🔴 Behind |
| lighthouse | 60d | 87,696 | 35.4% (31,062) | 17,918 (last 7d) | 2,559.7/day | 34.3d | 🟢 Ahead |

_Projection method: `effective daily throughput = distinct URLs covered in the last 7 days ÷ 7`;
`projected cycle days = eligible URLs ÷ effective daily throughput`. The 7-day measurement
window reflects recent scan velocity and is independent of each scanner's own target cycle
length. Relationships measures successful source-page coverage using
`relationship_scan_state.last_successful_at`; other scanners use their configured scan
timestamp. See src/services/cycle_pace_tracker.py's module docstring for why. 'No data' means
the scanner has no rows in its metadata.db within the window (never run against this database,
or the database doesn't cover this scanner)._
