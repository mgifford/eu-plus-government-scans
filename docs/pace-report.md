---
title: Scanner Cycle Pace Report
layout: page
---

_Generated: 2026-11-12 18:41 UTC_

Whether each scanner is on pace to complete its target cycle (30 days for most
covered in the last 7 days projected forward against the full eligible corpus.
For Relationships, coverage means a successful source-page scan; failed attempts
do not count toward relationship coverage. See
[WORKFLOW_ORCHESTRATION_AUDIT.md](https://github.com/mgifford/eu-plus-government-scans/blob/main/WORKFLOW_ORCHESTRATION_AUDIT.md)
Section 11 for the methodology.

| Scanner | Target cycle | Eligible URLs | Corpus covered | Covered (window) | Daily throughput | Projected cycle | Status |
|---|---|---|---|---|---|---|---|
| accessibility | 30d | 87,696 | 100.0% (87,690) | 17,625 (last 7d) | 2,517.9/day | 34.8d | 🟡 Marginal |
| social_media | 30d | 87,696 | 100.0% (87,690) | 25,029 (last 7d) | 3,575.6/day | 24.5d | 🟢 On pace |
| technology | 30d | 87,696 | 100.0% (87,690) | 7,556 (last 7d) | 1,079.4/day | 81.2d | 🟢 Caught up |
| third_party_js | 30d | 87,696 | 100.0% (87,690) | 15,893 (last 7d) | 2,270.4/day | 38.6d | 🟡 Marginal |
| overlays | 30d | 87,696 | 1.7% (1,523) | 1,269 (last 7d) | 181.3/day | 483.7d | 🔴 Behind |
| preferences | 90d | 87,696 | 8.2% (7,180) | 2,149 (last 7d) | 307.0/day | 285.7d | 🔴 Behind |
| relationships | 60d | 87,696 | 94.6% (82,955) | 14,105 (last 7d) | 2,015.0/day | 43.5d | 🟢 Ahead |
| lighthouse | 60d | 87,696 | 100.0% (87,690) | 5,038 (last 7d) | 719.7/day | 121.8d | 🟢 Caught up |

_Projection method: `effective daily throughput = distinct URLs covered in the last 7 days ÷ 7`;
`projected cycle days = eligible URLs ÷ effective daily throughput`. The 7-day measurement
window reflects recent scan velocity and is independent of each scanner's own target cycle
length. Relationships measures successful source-page coverage using
`relationship_scan_state.last_successful_at`; other scanners use their configured scan
timestamp. See src/services/cycle_pace_tracker.py's module docstring for why. 'No data' means
the scanner has no rows in its metadata.db within the window (never run against this database,
or the database doesn't cover this scanner)._
