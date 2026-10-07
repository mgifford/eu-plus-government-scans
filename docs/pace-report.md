---
title: Scanner Cycle Pace Report
layout: page
---

_Generated: 2026-10-07 12:31 UTC_

Whether each scanner is on pace to complete its target cycle (30 days for most
covered in the last 7 days projected forward against the full eligible corpus.
For Relationships, coverage means a successful source-page scan; failed attempts
do not count toward relationship coverage. See
[WORKFLOW_ORCHESTRATION_AUDIT.md](https://github.com/mgifford/eu-plus-government-scans/blob/main/WORKFLOW_ORCHESTRATION_AUDIT.md)
Section 11 for the methodology.

| Scanner | Target cycle | Eligible URLs | Corpus covered | Covered (window) | Daily throughput | Projected cycle | Status |
|---|---|---|---|---|---|---|---|
| accessibility | 30d | 87,696 | 100.0% (87,690) | 18,959 (last 7d) | 2,708.4/day | 32.4d | 🟡 Marginal |
| social_media | 30d | 87,696 | 100.0% (87,690) | 23,899 (last 7d) | 3,414.1/day | 25.7d | 🟢 On pace |
| technology | 30d | 87,696 | 100.0% (87,690) | 8,468 (last 7d) | 1,209.7/day | 72.5d | 🟢 Caught up |
| third_party_js | 30d | 87,696 | 100.0% (87,690) | 21,556 (last 7d) | 3,079.4/day | 28.5d | 🟢 On pace |
| overlays | 30d | 87,696 | 1.7% (1,523) | 0 (last 7d) | 0.0/day | —d | ⚪ No data |
| relationships | 60d | 87,696 | 93.9% (82,311) | 19,615 (last 7d) | 2,802.1/day | 31.3d | 🟢 Ahead |
| lighthouse | 60d | 87,696 | 70.8% (62,093) | 21,684 (last 7d) | 3,097.7/day | 28.3d | 🟢 Ahead |

_Projection method: `effective daily throughput = distinct URLs covered in the last 7 days ÷ 7`;
`projected cycle days = eligible URLs ÷ effective daily throughput`. The 7-day measurement
window reflects recent scan velocity and is independent of each scanner's own target cycle
length. Relationships measures successful source-page coverage using
`relationship_scan_state.last_successful_at`; other scanners use their configured scan
timestamp. See src/services/cycle_pace_tracker.py's module docstring for why. 'No data' means
the scanner has no rows in its metadata.db within the window (never run against this database,
or the database doesn't cover this scanner)._
