---
title: Scanner Cycle Pace Report
layout: page
---

_Generated: 2026-11-26 10:40 UTC_

Whether each scanner is on pace to complete its target cycle (30 days for most
covered in the last 7 days projected forward against the full eligible corpus.
For Relationships, coverage means a successful source-page scan; failed attempts
do not count toward relationship coverage. See
[WORKFLOW_ORCHESTRATION_AUDIT.md](https://github.com/mgifford/eu-plus-government-scans/blob/main/WORKFLOW_ORCHESTRATION_AUDIT.md)
Section 11 for the methodology.

| Scanner | Target cycle | Eligible URLs | Corpus covered | Covered (window) | Daily throughput | Projected cycle | Status |
|---|---|---|---|---|---|---|---|
| accessibility | 30d | 87,696 | 100.0% (87,690) | 15,556 (last 7d) | 2,222.3/day | 39.5d | 🟢 Caught up |
| social_media | 30d | 87,696 | 100.0% (87,690) | 14,684 (last 7d) | 2,097.7/day | 41.8d | 🟢 Caught up |
| technology | 30d | 87,696 | 100.0% (87,690) | 17,176 (last 7d) | 2,453.7/day | 35.7d | 🟡 Marginal |
| third_party_js | 30d | 87,696 | 100.0% (87,690) | 16,050 (last 7d) | 2,292.9/day | 38.2d | 🟡 Marginal |
| overlays | 30d | 87,696 | 1.7% (1,523) | 0 (last 7d) | 0.0/day | —d | ⚪ No data |
| preferences | 90d | 87,696 | 10.0% (8,751) | 1,572 (last 7d) | 224.6/day | 390.5d | 🔴 Behind |
| relationships | 60d | 87,696 | 94.6% (82,962) | 19,634 (last 7d) | 2,804.9/day | 31.3d | 🟢 Ahead |
| lighthouse | 60d | 87,696 | 100.0% (87,690) | 12,601 (last 7d) | 1,800.1/day | 48.7d | 🟢 On pace |

_Projection method: `effective daily throughput = distinct URLs covered in the last 7 days ÷ 7`;
`projected cycle days = eligible URLs ÷ effective daily throughput`. The 7-day measurement
window reflects recent scan velocity and is independent of each scanner's own target cycle
length. Relationships measures successful source-page coverage using
`relationship_scan_state.last_successful_at`; other scanners use their configured scan
timestamp. See src/services/cycle_pace_tracker.py's module docstring for why. 'No data' means
the scanner has no rows in its metadata.db within the window (never run against this database,
or the database doesn't cover this scanner)._
