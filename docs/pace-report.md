---
title: Scanner Cycle Pace Report
layout: page
---

_Generated: 2026-09-03 21:04 UTC_

Whether each scanner is on pace to complete its target cycle (30 days for most
covered in the last 7 days projected forward against the full eligible corpus.
For Relationships, coverage means a successful source-page scan; failed attempts
do not count toward relationship coverage. See
[WORKFLOW_ORCHESTRATION_AUDIT.md](https://github.com/mgifford/eu-plus-government-scans/blob/main/WORKFLOW_ORCHESTRATION_AUDIT.md)
Section 11 for the methodology.

| Scanner | Target cycle | Eligible URLs | Covered (window) | Daily throughput | Projected cycle | Status |
|---|---|---|---|---|---|---|
| accessibility | 30d | 87,696 | 22,739 (last 7d) | 3,248.4/day | 27.0d | 🟢 On pace |
| social_media | 30d | 87,696 | 22,974 (last 7d) | 3,282.0/day | 26.7d | 🟢 On pace |
| technology | 30d | 87,696 | 21,448 (last 7d) | 3,064.0/day | 28.6d | 🟢 On pace |
| third_party_js | 30d | 87,696 | 24,511 (last 7d) | 3,501.6/day | 25.0d | 🟢 On pace |
| overlays | 30d | 87,696 | 0 (last 7d) | 0.0/day | —d | ⚪ No data |
| relationships | 60d | 87,696 | 17,254 (last 7d) | 2,464.9/day | 35.6d | 🟢 Ahead |
| lighthouse | 60d | 87,696 | 3,965 (last 7d) | 566.4/day | 154.8d | 🔴 Behind |

_Projection method: `effective daily throughput = distinct URLs covered in the last 7 days ÷ 7`;
`projected cycle days = eligible URLs ÷ effective daily throughput`. The 7-day measurement
window reflects recent scan velocity and is independent of each scanner's own target cycle
length. Relationships measures successful source-page coverage using
`relationship_scan_state.last_successful_at`; other scanners use their configured scan
timestamp. See src/services/cycle_pace_tracker.py's module docstring for why. 'No data' means
the scanner has no rows in its metadata.db within the window (never run against this database,
or the database doesn't cover this scanner)._
