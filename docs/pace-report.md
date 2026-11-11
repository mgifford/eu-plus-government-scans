---
title: Scanner Cycle Pace Report
layout: page
---

_Generated: 2026-11-11 18:00 UTC_

Whether each scanner is on pace to complete its target cycle (30 days for most
covered in the last 7 days projected forward against the full eligible corpus.
For Relationships, coverage means a successful source-page scan; failed attempts
do not count toward relationship coverage. See
[WORKFLOW_ORCHESTRATION_AUDIT.md](https://github.com/mgifford/eu-plus-government-scans/blob/main/WORKFLOW_ORCHESTRATION_AUDIT.md)
Section 11 for the methodology.

| Scanner | Target cycle | Eligible URLs | Corpus covered | Covered (window) | Daily throughput | Projected cycle | Status |
|---|---|---|---|---|---|---|---|
| accessibility | 30d | 87,696 | 100.0% (87,690) | 17,524 (last 7d) | 2,503.4/day | 35.0d | 🟡 Marginal |
| social_media | 30d | 87,696 | 100.0% (87,690) | 23,346 (last 7d) | 3,335.1/day | 26.3d | 🟢 On pace |
| technology | 30d | 87,696 | 100.0% (87,690) | 4,749 (last 7d) | 678.4/day | 129.3d | 🟢 Caught up |
| third_party_js | 30d | 87,696 | 100.0% (87,690) | 16,424 (last 7d) | 2,346.3/day | 37.4d | 🟡 Marginal |
| overlays | 30d | 87,696 | 1.7% (1,523) | 1,269 (last 7d) | 181.3/day | 483.7d | 🔴 Behind |
| preferences | 90d | 87,696 | 5.7% (5,031) | 2,346 (last 7d) | 335.1/day | 261.7d | 🔴 Behind |
| relationships | 60d | 87,696 | 94.6% (82,935) | 14,803 (last 7d) | 2,114.7/day | 41.5d | 🟢 Ahead |
| lighthouse | 60d | 87,696 | 100.0% (87,690) | 5,316 (last 7d) | 759.4/day | 115.5d | 🟢 Caught up |

_Projection method: `effective daily throughput = distinct URLs covered in the last 7 days ÷ 7`;
`projected cycle days = eligible URLs ÷ effective daily throughput`. The 7-day measurement
window reflects recent scan velocity and is independent of each scanner's own target cycle
length. Relationships measures successful source-page coverage using
`relationship_scan_state.last_successful_at`; other scanners use their configured scan
timestamp. See src/services/cycle_pace_tracker.py's module docstring for why. 'No data' means
the scanner has no rows in its metadata.db within the window (never run against this database,
or the database doesn't cover this scanner)._
