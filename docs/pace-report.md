---
title: Scanner Cycle Pace Report
layout: page
---

_Generated: 2026-11-21 07:45 UTC_

Whether each scanner is on pace to complete its target cycle (30 days for most
covered in the last 7 days projected forward against the full eligible corpus.
For Relationships, coverage means a successful source-page scan; failed attempts
do not count toward relationship coverage. See
[WORKFLOW_ORCHESTRATION_AUDIT.md](https://github.com/mgifford/eu-plus-government-scans/blob/main/WORKFLOW_ORCHESTRATION_AUDIT.md)
Section 11 for the methodology.

| Scanner | Target cycle | Eligible URLs | Corpus covered | Covered (window) | Daily throughput | Projected cycle | Status |
|---|---|---|---|---|---|---|---|
| accessibility | 30d | 87,696 | 100.0% (87,690) | 15,290 (last 7d) | 2,184.3/day | 40.1d | 🟢 Caught up |
| social_media | 30d | 87,696 | 100.0% (87,690) | 18,372 (last 7d) | 2,624.6/day | 33.4d | 🟡 Marginal |
| technology | 30d | 87,696 | 100.0% (87,690) | 21,238 (last 7d) | 3,034.0/day | 28.9d | 🟢 On pace |
| third_party_js | 30d | 87,696 | 100.0% (87,690) | 14,170 (last 7d) | 2,024.3/day | 43.3d | 🟢 Caught up |
| overlays | 30d | 87,696 | 1.7% (1,523) | 0 (last 7d) | 0.0/day | —d | ⚪ No data |
| preferences | 90d | 87,696 | 10.0% (8,751) | 1,572 (last 7d) | 224.6/day | 390.5d | 🔴 Behind |
| relationships | 60d | 87,696 | 94.6% (82,959) | 16,668 (last 7d) | 2,381.1/day | 36.8d | 🟢 Ahead |
| lighthouse | 60d | 87,696 | 100.0% (87,690) | 17,028 (last 7d) | 2,432.6/day | 36.1d | 🟢 Ahead |

_Projection method: `effective daily throughput = distinct URLs covered in the last 7 days ÷ 7`;
`projected cycle days = eligible URLs ÷ effective daily throughput`. The 7-day measurement
window reflects recent scan velocity and is independent of each scanner's own target cycle
length. Relationships measures successful source-page coverage using
`relationship_scan_state.last_successful_at`; other scanners use their configured scan
timestamp. See src/services/cycle_pace_tracker.py's module docstring for why. 'No data' means
the scanner has no rows in its metadata.db within the window (never run against this database,
or the database doesn't cover this scanner)._
