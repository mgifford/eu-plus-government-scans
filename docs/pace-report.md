---
title: Scanner Cycle Pace Report
layout: page
---

_Generated: 2026-09-17 20:47 UTC_

Whether each scanner is on pace to complete its target cycle (30 days for most
covered in the last 7 days projected forward against the full eligible corpus.
For Relationships, coverage means a successful source-page scan; failed attempts
do not count toward relationship coverage. See
[WORKFLOW_ORCHESTRATION_AUDIT.md](https://github.com/mgifford/eu-plus-government-scans/blob/main/WORKFLOW_ORCHESTRATION_AUDIT.md)
Section 11 for the methodology.

| Scanner | Target cycle | Eligible URLs | Corpus covered | Covered (window) | Daily throughput | Projected cycle | Status |
|---|---|---|---|---|---|---|---|
| accessibility | 30d | 87,696 | 100.0% (87,690) | 2,720 (last 7d) | 388.6/day | 225.7d | 🟢 Caught up |
| social_media | 30d | 87,696 | 100.0% (87,690) | 25,272 (last 7d) | 3,610.3/day | 24.3d | 🟢 On pace |
| technology | 30d | 87,696 | 100.0% (87,690) | 33,161 (last 7d) | 4,737.3/day | 18.5d | 🟢 Ahead |
| third_party_js | 30d | 87,696 | 100.0% (87,690) | 18,711 (last 7d) | 2,673.0/day | 32.8d | 🟡 Marginal |
| overlays | 30d | 87,696 | 1.7% (1,523) | 0 (last 7d) | 0.0/day | —d | ⚪ No data |
| relationships | 60d | 87,696 | 93.3% (81,831) | 2,879 (last 7d) | 411.3/day | 213.2d | 🔴 Behind |
| lighthouse | 60d | 87,696 | 29.7% (26,067) | 13,065 (last 7d) | 1,866.4/day | 47.0d | 🟢 Ahead |

_Projection method: `effective daily throughput = distinct URLs covered in the last 7 days ÷ 7`;
`projected cycle days = eligible URLs ÷ effective daily throughput`. The 7-day measurement
window reflects recent scan velocity and is independent of each scanner's own target cycle
length. Relationships measures successful source-page coverage using
`relationship_scan_state.last_successful_at`; other scanners use their configured scan
timestamp. See src/services/cycle_pace_tracker.py's module docstring for why. 'No data' means
the scanner has no rows in its metadata.db within the window (never run against this database,
or the database doesn't cover this scanner)._
