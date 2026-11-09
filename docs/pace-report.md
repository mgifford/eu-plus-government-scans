---
title: Scanner Cycle Pace Report
layout: page
---

_Generated: 2026-11-09 23:22 UTC_

Whether each scanner is on pace to complete its target cycle (30 days for most
covered in the last 7 days projected forward against the full eligible corpus.
For Relationships, coverage means a successful source-page scan; failed attempts
do not count toward relationship coverage. See
[WORKFLOW_ORCHESTRATION_AUDIT.md](https://github.com/mgifford/eu-plus-government-scans/blob/main/WORKFLOW_ORCHESTRATION_AUDIT.md)
Section 11 for the methodology.

| Scanner | Target cycle | Eligible URLs | Corpus covered | Covered (window) | Daily throughput | Projected cycle | Status |
|---|---|---|---|---|---|---|---|
| accessibility | 30d | 87,696 | 100.0% (87,690) | 18,080 (last 7d) | 2,582.9/day | 34.0d | 🟡 Marginal |
| social_media | 30d | 87,696 | 100.0% (87,690) | 23,139 (last 7d) | 3,305.6/day | 26.5d | 🟢 On pace |
| technology | 30d | 87,696 | 100.0% (87,690) | 0 (last 7d) | 0.0/day | —d | 🟢 Caught up |
| third_party_js | 30d | 87,696 | 100.0% (87,690) | 15,757 (last 7d) | 2,251.0/day | 39.0d | 🟡 Marginal |
| overlays | 30d | 87,696 | 1.7% (1,523) | 1,269 (last 7d) | 181.3/day | 483.7d | 🔴 Behind |
| preferences | 90d | 87,696 | 5.7% (5,031) | 2,346 (last 7d) | 335.1/day | 261.7d | 🔴 Behind |
| relationships | 60d | 87,696 | 94.5% (82,874) | 14,896 (last 7d) | 2,128.0/day | 41.2d | 🟢 Ahead |
| lighthouse | 60d | 87,696 | 100.0% (87,690) | 5,629 (last 7d) | 804.1/day | 109.1d | 🟢 Caught up |

_Projection method: `effective daily throughput = distinct URLs covered in the last 7 days ÷ 7`;
`projected cycle days = eligible URLs ÷ effective daily throughput`. The 7-day measurement
window reflects recent scan velocity and is independent of each scanner's own target cycle
length. Relationships measures successful source-page coverage using
`relationship_scan_state.last_successful_at`; other scanners use their configured scan
timestamp. See src/services/cycle_pace_tracker.py's module docstring for why. 'No data' means
the scanner has no rows in its metadata.db within the window (never run against this database,
or the database doesn't cover this scanner)._
