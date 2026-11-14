---
title: Scanner Cycle Pace Report
layout: page
---

_Generated: 2026-11-14 22:28 UTC_

Whether each scanner is on pace to complete its target cycle (30 days for most
covered in the last 7 days projected forward against the full eligible corpus.
For Relationships, coverage means a successful source-page scan; failed attempts
do not count toward relationship coverage. See
[WORKFLOW_ORCHESTRATION_AUDIT.md](https://github.com/mgifford/eu-plus-government-scans/blob/main/WORKFLOW_ORCHESTRATION_AUDIT.md)
Section 11 for the methodology.

| Scanner | Target cycle | Eligible URLs | Corpus covered | Covered (window) | Daily throughput | Projected cycle | Status |
|---|---|---|---|---|---|---|---|
| accessibility | 30d | 87,696 | 100.0% (87,690) | 18,387 (last 7d) | 2,626.7/day | 33.4d | 🟡 Marginal |
| social_media | 30d | 87,696 | 100.0% (87,690) | 22,014 (last 7d) | 3,144.9/day | 27.9d | 🟢 On pace |
| technology | 30d | 87,696 | 100.0% (87,690) | 15,265 (last 7d) | 2,180.7/day | 40.2d | 🟢 Caught up |
| third_party_js | 30d | 87,696 | 100.0% (87,690) | 15,440 (last 7d) | 2,205.7/day | 39.8d | 🟢 Caught up |
| overlays | 30d | 87,696 | 1.7% (1,523) | 1,269 (last 7d) | 181.3/day | 483.7d | 🔴 Behind |
| preferences | 90d | 87,696 | 8.2% (7,180) | 2,149 (last 7d) | 307.0/day | 285.7d | 🔴 Behind |
| relationships | 60d | 87,696 | 94.6% (82,955) | 16,077 (last 7d) | 2,296.7/day | 38.2d | 🟢 Ahead |
| lighthouse | 60d | 87,696 | 100.0% (87,690) | 6,044 (last 7d) | 863.4/day | 101.6d | 🟢 Caught up |

_Projection method: `effective daily throughput = distinct URLs covered in the last 7 days ÷ 7`;
`projected cycle days = eligible URLs ÷ effective daily throughput`. The 7-day measurement
window reflects recent scan velocity and is independent of each scanner's own target cycle
length. Relationships measures successful source-page coverage using
`relationship_scan_state.last_successful_at`; other scanners use their configured scan
timestamp. See src/services/cycle_pace_tracker.py's module docstring for why. 'No data' means
the scanner has no rows in its metadata.db within the window (never run against this database,
or the database doesn't cover this scanner)._
