---
title: Scanner Cycle Pace Report
layout: page
---

_Generated: 2026-10-05 05:54 UTC_

Whether each scanner is on pace to complete its target cycle (30 days for most
covered in the last 7 days projected forward against the full eligible corpus.
For Relationships, coverage means a successful source-page scan; failed attempts
do not count toward relationship coverage. See
[WORKFLOW_ORCHESTRATION_AUDIT.md](https://github.com/mgifford/eu-plus-government-scans/blob/main/WORKFLOW_ORCHESTRATION_AUDIT.md)
Section 11 for the methodology.

| Scanner | Target cycle | Eligible URLs | Corpus covered | Covered (window) | Daily throughput | Projected cycle | Status |
|---|---|---|---|---|---|---|---|
| accessibility | 30d | 87,696 | 100.0% (87,690) | 17,769 (last 7d) | 2,538.4/day | 34.5d | 🟡 Marginal |
| social_media | 30d | 87,696 | 100.0% (87,690) | 21,640 (last 7d) | 3,091.4/day | 28.4d | 🟢 On pace |
| technology | 30d | 87,696 | 100.0% (87,690) | 17,586 (last 7d) | 2,512.3/day | 34.9d | 🟡 Marginal |
| third_party_js | 30d | 87,696 | 100.0% (87,690) | 22,132 (last 7d) | 3,161.7/day | 27.7d | 🟢 On pace |
| overlays | 30d | 87,696 | 1.7% (1,523) | 0 (last 7d) | 0.0/day | —d | ⚪ No data |
| relationships | 60d | 87,696 | 93.9% (82,307) | 17,583 (last 7d) | 2,511.9/day | 34.9d | 🟢 Ahead |
| lighthouse | 60d | 87,696 | 69.3% (60,768) | 23,432 (last 7d) | 3,347.4/day | 26.2d | 🟢 Ahead |

_Projection method: `effective daily throughput = distinct URLs covered in the last 7 days ÷ 7`;
`projected cycle days = eligible URLs ÷ effective daily throughput`. The 7-day measurement
window reflects recent scan velocity and is independent of each scanner's own target cycle
length. Relationships measures successful source-page coverage using
`relationship_scan_state.last_successful_at`; other scanners use their configured scan
timestamp. See src/services/cycle_pace_tracker.py's module docstring for why. 'No data' means
the scanner has no rows in its metadata.db within the window (never run against this database,
or the database doesn't cover this scanner)._
