---
title: Scanner Cycle Pace Report
layout: page
---

_Generated: 2026-09-05 11:24 UTC_

Whether each scanner is on pace to complete its target cycle (30 days for most
covered in the last 7 days projected forward against the full eligible corpus.
For Relationships, coverage means a successful source-page scan; failed attempts
do not count toward relationship coverage. See
[WORKFLOW_ORCHESTRATION_AUDIT.md](https://github.com/mgifford/eu-plus-government-scans/blob/main/WORKFLOW_ORCHESTRATION_AUDIT.md)
Section 11 for the methodology.

| Scanner | Target cycle | Eligible URLs | Covered (window) | Daily throughput | Projected cycle | Status |
|---|---|---|---|---|---|---|
| accessibility | 30d | 87,696 | 24,975 (last 7d) | 3,567.9/day | 24.6d | 🟢 On pace |
| social_media | 30d | 87,696 | 25,089 (last 7d) | 3,584.1/day | 24.5d | 🟢 On pace |
| technology | 30d | 87,696 | 16,101 (last 7d) | 2,300.1/day | 38.1d | 🟡 Marginal |
| third_party_js | 30d | 87,696 | 27,749 (last 7d) | 3,964.1/day | 22.1d | 🟢 Ahead |
| overlays | 30d | 87,696 | 0 (last 7d) | 0.0/day | —d | ⚪ No data |
| relationships | 60d | 87,696 | 23,091 (last 7d) | 3,298.7/day | 26.6d | 🟢 Ahead |
| lighthouse | 60d | 87,696 | 3,808 (last 7d) | 544.0/day | 161.2d | 🔴 Behind |

_Projection method: `effective daily throughput = distinct URLs covered in the last 7 days ÷ 7`;
`projected cycle days = eligible URLs ÷ effective daily throughput`. The 7-day measurement
window reflects recent scan velocity and is independent of each scanner's own target cycle
length. Relationships measures successful source-page coverage using
`relationship_scan_state.last_successful_at`; other scanners use their configured scan
timestamp. See src/services/cycle_pace_tracker.py's module docstring for why. 'No data' means
the scanner has no rows in its metadata.db within the window (never run against this database,
or the database doesn't cover this scanner)._
