---
title: Scanner Cycle Pace Report
layout: page
---

_Generated: 2026-08-30 12:39 UTC_

Whether each scanner is on pace to complete its target cycle (30 days for most
covered in the last 7 days projected forward against the full eligible corpus.
For Relationships, coverage means a successful source-page scan; failed attempts
do not count toward relationship coverage. See
[WORKFLOW_ORCHESTRATION_AUDIT.md](https://github.com/mgifford/eu-plus-government-scans/blob/main/WORKFLOW_ORCHESTRATION_AUDIT.md)
Section 11 for the methodology.

| Scanner | Target cycle | Eligible URLs | Covered (window) | Daily throughput | Projected cycle | Status |
|---|---|---|---|---|---|---|
| accessibility | 30d | 87,696 | 28,952 (last 7d) | 4,136.0/day | 21.2d | 🟢 Ahead |
| social_media | 30d | 87,696 | 17,825 (last 7d) | 2,546.4/day | 34.4d | 🟡 Marginal |
| technology | 30d | 87,696 | 24,697 (last 7d) | 3,528.1/day | 24.9d | 🟢 On pace |
| third_party_js | 30d | 87,696 | 21,879 (last 7d) | 3,125.6/day | 28.1d | 🟢 On pace |
| overlays | 30d | 87,696 | 1,469 (last 7d) | 209.9/day | 417.9d | 🔴 Behind |
| relationships | 60d | 87,696 | 15,345 (last 7d) | 2,192.1/day | 40.0d | 🟢 Ahead |
| lighthouse | 60d | 87,696 | 4,653 (last 7d) | 664.7/day | 131.9d | 🔴 Behind |

_Projection method: `effective daily throughput = distinct URLs covered in the last 7 days ÷ 7`;
`projected cycle days = eligible URLs ÷ effective daily throughput`. The 7-day measurement
window reflects recent scan velocity and is independent of each scanner's own target cycle
length. Relationships measures successful source-page coverage using
`relationship_scan_state.last_successful_at`; other scanners use their configured scan
timestamp. See src/services/cycle_pace_tracker.py's module docstring for why. 'No data' means
the scanner has no rows in its metadata.db within the window (never run against this database,
or the database doesn't cover this scanner)._
