---
title: Scanner Cycle Pace Report
layout: page
---

_Generated: 2026-09-20 14:12 UTC_

Whether each scanner is on pace to complete its target cycle (30 days for most
covered in the last 7 days projected forward against the full eligible corpus.
For Relationships, coverage means a successful source-page scan; failed attempts
do not count toward relationship coverage. See
[WORKFLOW_ORCHESTRATION_AUDIT.md](https://github.com/mgifford/eu-plus-government-scans/blob/main/WORKFLOW_ORCHESTRATION_AUDIT.md)
Section 11 for the methodology.

| Scanner | Target cycle | Eligible URLs | Corpus covered | Covered (window) | Daily throughput | Projected cycle | Status |
|---|---|---|---|---|---|---|---|
| accessibility | 30d | 87,696 | 100.0% (87,690) | 11,966 (last 7d) | 1,709.4/day | 51.3d | 🟢 Caught up |
| social_media | 30d | 87,696 | 100.0% (87,690) | 23,265 (last 7d) | 3,323.6/day | 26.4d | 🟢 On pace |
| technology | 30d | 87,696 | 100.0% (87,690) | 32,048 (last 7d) | 4,578.3/day | 19.2d | 🟢 Ahead |
| third_party_js | 30d | 87,696 | 100.0% (87,690) | 5,782 (last 7d) | 826.0/day | 106.2d | 🟢 Caught up |
| overlays | 30d | 87,696 | 1.7% (1,523) | 0 (last 7d) | 0.0/day | —d | ⚪ No data |
| relationships | 60d | 87,696 | 93.3% (81,831) | 14,699 (last 7d) | 2,099.9/day | 41.8d | 🟢 Ahead |
| lighthouse | 60d | 87,696 | 45.9% (40,264) | 26,302 (last 7d) | 3,757.4/day | 23.3d | 🟢 Ahead |

_Projection method: `effective daily throughput = distinct URLs covered in the last 7 days ÷ 7`;
`projected cycle days = eligible URLs ÷ effective daily throughput`. The 7-day measurement
window reflects recent scan velocity and is independent of each scanner's own target cycle
length. Relationships measures successful source-page coverage using
`relationship_scan_state.last_successful_at`; other scanners use their configured scan
timestamp. See src/services/cycle_pace_tracker.py's module docstring for why. 'No data' means
the scanner has no rows in its metadata.db within the window (never run against this database,
or the database doesn't cover this scanner)._
