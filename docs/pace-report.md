---
title: Scanner Cycle Pace Report
layout: page
---

_Generated: 2026-09-30 09:36 UTC_

Whether each scanner is on pace to complete its target cycle (30 days for most
covered in the last 7 days projected forward against the full eligible corpus.
For Relationships, coverage means a successful source-page scan; failed attempts
do not count toward relationship coverage. See
[WORKFLOW_ORCHESTRATION_AUDIT.md](https://github.com/mgifford/eu-plus-government-scans/blob/main/WORKFLOW_ORCHESTRATION_AUDIT.md)
Section 11 for the methodology.

| Scanner | Target cycle | Eligible URLs | Corpus covered | Covered (window) | Daily throughput | Projected cycle | Status |
|---|---|---|---|---|---|---|---|
| accessibility | 30d | 87,696 | 100.0% (87,690) | 20,802 (last 7d) | 2,971.7/day | 29.5d | 🟢 On pace |
| social_media | 30d | 87,696 | 100.0% (87,690) | 19,574 (last 7d) | 2,796.3/day | 31.4d | 🟡 Marginal |
| technology | 30d | 87,696 | 100.0% (87,690) | 23,893 (last 7d) | 3,413.3/day | 25.7d | 🟢 On pace |
| third_party_js | 30d | 87,696 | 100.0% (87,690) | 21,221 (last 7d) | 3,031.6/day | 28.9d | 🟢 On pace |
| overlays | 30d | 87,696 | 1.7% (1,523) | 0 (last 7d) | 0.0/day | —d | ⚪ No data |
| relationships | 60d | 87,696 | 93.7% (82,204) | 20,655 (last 7d) | 2,950.7/day | 29.7d | 🟢 Ahead |
| lighthouse | 60d | 87,696 | 59.6% (52,290) | 22,615 (last 7d) | 3,230.7/day | 27.1d | 🟢 Ahead |

_Projection method: `effective daily throughput = distinct URLs covered in the last 7 days ÷ 7`;
`projected cycle days = eligible URLs ÷ effective daily throughput`. The 7-day measurement
window reflects recent scan velocity and is independent of each scanner's own target cycle
length. Relationships measures successful source-page coverage using
`relationship_scan_state.last_successful_at`; other scanners use their configured scan
timestamp. See src/services/cycle_pace_tracker.py's module docstring for why. 'No data' means
the scanner has no rows in its metadata.db within the window (never run against this database,
or the database doesn't cover this scanner)._
