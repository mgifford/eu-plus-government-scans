---
title: Scanner Cycle Pace Report
layout: page
---

_Generated: 2026-10-13 23:57 UTC_

Whether each scanner is on pace to complete its target cycle (30 days for most
covered in the last 7 days projected forward against the full eligible corpus.
For Relationships, coverage means a successful source-page scan; failed attempts
do not count toward relationship coverage. See
[WORKFLOW_ORCHESTRATION_AUDIT.md](https://github.com/mgifford/eu-plus-government-scans/blob/main/WORKFLOW_ORCHESTRATION_AUDIT.md)
Section 11 for the methodology.

| Scanner | Target cycle | Eligible URLs | Corpus covered | Covered (window) | Daily throughput | Projected cycle | Status |
|---|---|---|---|---|---|---|---|
| accessibility | 30d | 87,696 | 100.0% (87,690) | 21,362 (last 7d) | 3,051.7/day | 28.7d | 🟢 On pace |
| social_media | 30d | 87,696 | 100.0% (87,690) | 14,953 (last 7d) | 2,136.1/day | 41.1d | 🟢 Caught up |
| technology | 30d | 87,696 | 100.0% (87,690) | 10,027 (last 7d) | 1,432.4/day | 61.2d | 🟢 Caught up |
| third_party_js | 30d | 87,696 | 100.0% (87,690) | 17,866 (last 7d) | 2,552.3/day | 34.4d | 🟡 Marginal |
| overlays | 30d | 87,696 | 1.7% (1,523) | 0 (last 7d) | 0.0/day | —d | ⚪ No data |
| relationships | 60d | 87,696 | 94.0% (82,403) | 16,354 (last 7d) | 2,336.3/day | 37.5d | 🟢 Ahead |
| lighthouse | 60d | 87,696 | 78.0% (68,371) | 19,488 (last 7d) | 2,784.0/day | 31.5d | 🟢 Ahead |

_Projection method: `effective daily throughput = distinct URLs covered in the last 7 days ÷ 7`;
`projected cycle days = eligible URLs ÷ effective daily throughput`. The 7-day measurement
window reflects recent scan velocity and is independent of each scanner's own target cycle
length. Relationships measures successful source-page coverage using
`relationship_scan_state.last_successful_at`; other scanners use their configured scan
timestamp. See src/services/cycle_pace_tracker.py's module docstring for why. 'No data' means
the scanner has no rows in its metadata.db within the window (never run against this database,
or the database doesn't cover this scanner)._
