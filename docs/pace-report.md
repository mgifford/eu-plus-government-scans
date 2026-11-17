---
title: Scanner Cycle Pace Report
layout: page
---

_Generated: 2026-11-17 17:16 UTC_

Whether each scanner is on pace to complete its target cycle (30 days for most
covered in the last 7 days projected forward against the full eligible corpus.
For Relationships, coverage means a successful source-page scan; failed attempts
do not count toward relationship coverage. See
[WORKFLOW_ORCHESTRATION_AUDIT.md](https://github.com/mgifford/eu-plus-government-scans/blob/main/WORKFLOW_ORCHESTRATION_AUDIT.md)
Section 11 for the methodology.

| Scanner | Target cycle | Eligible URLs | Corpus covered | Covered (window) | Daily throughput | Projected cycle | Status |
|---|---|---|---|---|---|---|---|
| accessibility | 30d | 87,696 | 100.0% (87,690) | 20,139 (last 7d) | 2,877.0/day | 30.5d | 🟡 Marginal |
| social_media | 30d | 87,696 | 100.0% (87,690) | 20,020 (last 7d) | 2,860.0/day | 30.7d | 🟡 Marginal |
| technology | 30d | 87,696 | 100.0% (87,690) | 25,121 (last 7d) | 3,588.7/day | 24.4d | 🟢 On pace |
| third_party_js | 30d | 87,696 | 100.0% (87,690) | 14,361 (last 7d) | 2,051.6/day | 42.7d | 🟢 Caught up |
| overlays | 30d | 87,696 | 1.7% (1,523) | 0 (last 7d) | 0.0/day | —d | ⚪ No data |
| preferences | 90d | 87,696 | 8.2% (7,180) | 2,149 (last 7d) | 307.0/day | 285.7d | 🔴 Behind |
| relationships | 60d | 87,696 | 94.6% (82,957) | 17,199 (last 7d) | 2,457.0/day | 35.7d | 🟢 Ahead |
| lighthouse | 60d | 87,696 | 100.0% (87,690) | 11,598 (last 7d) | 1,656.9/day | 52.9d | 🟢 On pace |

_Projection method: `effective daily throughput = distinct URLs covered in the last 7 days ÷ 7`;
`projected cycle days = eligible URLs ÷ effective daily throughput`. The 7-day measurement
window reflects recent scan velocity and is independent of each scanner's own target cycle
length. Relationships measures successful source-page coverage using
`relationship_scan_state.last_successful_at`; other scanners use their configured scan
timestamp. See src/services/cycle_pace_tracker.py's module docstring for why. 'No data' means
the scanner has no rows in its metadata.db within the window (never run against this database,
or the database doesn't cover this scanner)._
