---
title: Scanner Cycle Pace Report
layout: page
---

_Generated: 2026-11-16 06:05 UTC_

Whether each scanner is on pace to complete its target cycle (30 days for most
covered in the last 7 days projected forward against the full eligible corpus.
For Relationships, coverage means a successful source-page scan; failed attempts
do not count toward relationship coverage. See
[WORKFLOW_ORCHESTRATION_AUDIT.md](https://github.com/mgifford/eu-plus-government-scans/blob/main/WORKFLOW_ORCHESTRATION_AUDIT.md)
Section 11 for the methodology.

| Scanner | Target cycle | Eligible URLs | Corpus covered | Covered (window) | Daily throughput | Projected cycle | Status |
|---|---|---|---|---|---|---|---|
| accessibility | 30d | 87,696 | 100.0% (87,690) | 20,022 (last 7d) | 2,860.3/day | 30.7d | 🟡 Marginal |
| social_media | 30d | 87,696 | 100.0% (87,690) | 21,810 (last 7d) | 3,115.7/day | 28.1d | 🟢 On pace |
| technology | 30d | 87,696 | 100.0% (87,690) | 21,068 (last 7d) | 3,009.7/day | 29.1d | 🟢 On pace |
| third_party_js | 30d | 87,696 | 100.0% (87,690) | 15,631 (last 7d) | 2,233.0/day | 39.3d | 🟢 Caught up |
| overlays | 30d | 87,696 | 1.7% (1,523) | 1,269 (last 7d) | 181.3/day | 483.7d | 🔴 Behind |
| preferences | 90d | 87,696 | 8.2% (7,180) | 2,149 (last 7d) | 307.0/day | 285.7d | 🔴 Behind |
| relationships | 60d | 87,696 | 94.6% (82,957) | 16,610 (last 7d) | 2,372.9/day | 37.0d | 🟢 Ahead |
| lighthouse | 60d | 87,696 | 100.0% (87,690) | 9,581 (last 7d) | 1,368.7/day | 64.1d | 🟡 Marginal |

_Projection method: `effective daily throughput = distinct URLs covered in the last 7 days ÷ 7`;
`projected cycle days = eligible URLs ÷ effective daily throughput`. The 7-day measurement
window reflects recent scan velocity and is independent of each scanner's own target cycle
length. Relationships measures successful source-page coverage using
`relationship_scan_state.last_successful_at`; other scanners use their configured scan
timestamp. See src/services/cycle_pace_tracker.py's module docstring for why. 'No data' means
the scanner has no rows in its metadata.db within the window (never run against this database,
or the database doesn't cover this scanner)._
