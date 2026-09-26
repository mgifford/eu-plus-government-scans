---
title: Scanner Cycle Pace Report
layout: page
---

_Generated: 2026-09-26 11:32 UTC_

Whether each scanner is on pace to complete its target cycle (30 days for most
covered in the last 7 days projected forward against the full eligible corpus.
For Relationships, coverage means a successful source-page scan; failed attempts
do not count toward relationship coverage. See
[WORKFLOW_ORCHESTRATION_AUDIT.md](https://github.com/mgifford/eu-plus-government-scans/blob/main/WORKFLOW_ORCHESTRATION_AUDIT.md)
Section 11 for the methodology.

| Scanner | Target cycle | Eligible URLs | Corpus covered | Covered (window) | Daily throughput | Projected cycle | Status |
|---|---|---|---|---|---|---|---|
| accessibility | 30d | 87,696 | 100.0% (87,690) | 24,033 (last 7d) | 3,433.3/day | 25.5d | 🟢 On pace |
| social_media | 30d | 87,696 | 100.0% (87,690) | 20,715 (last 7d) | 2,959.3/day | 29.6d | 🟢 On pace |
| technology | 30d | 87,696 | 100.0% (87,690) | 23,940 (last 7d) | 3,420.0/day | 25.6d | 🟢 On pace |
| third_party_js | 30d | 87,696 | 100.0% (87,690) | 11,310 (last 7d) | 1,615.7/day | 54.3d | 🟢 Caught up |
| overlays | 30d | 87,696 | 1.7% (1,523) | 0 (last 7d) | 0.0/day | —d | ⚪ No data |
| relationships | 60d | 87,696 | 93.7% (82,174) | 24,817 (last 7d) | 3,545.3/day | 24.7d | 🟢 Ahead |
| lighthouse | 60d | 87,696 | 50.8% (44,575) | 15,817 (last 7d) | 2,259.6/day | 38.8d | 🟢 Ahead |

_Projection method: `effective daily throughput = distinct URLs covered in the last 7 days ÷ 7`;
`projected cycle days = eligible URLs ÷ effective daily throughput`. The 7-day measurement
window reflects recent scan velocity and is independent of each scanner's own target cycle
length. Relationships measures successful source-page coverage using
`relationship_scan_state.last_successful_at`; other scanners use their configured scan
timestamp. See src/services/cycle_pace_tracker.py's module docstring for why. 'No data' means
the scanner has no rows in its metadata.db within the window (never run against this database,
or the database doesn't cover this scanner)._
