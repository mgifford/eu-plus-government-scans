---
title: Scanner Cycle Pace Report
layout: page
---

_Generated: 2026-10-13 07:30 UTC_

Whether each scanner is on pace to complete its target cycle (30 days for most
covered in the last 7 days projected forward against the full eligible corpus.
For Relationships, coverage means a successful source-page scan; failed attempts
do not count toward relationship coverage. See
[WORKFLOW_ORCHESTRATION_AUDIT.md](https://github.com/mgifford/eu-plus-government-scans/blob/main/WORKFLOW_ORCHESTRATION_AUDIT.md)
Section 11 for the methodology.

| Scanner | Target cycle | Eligible URLs | Corpus covered | Covered (window) | Daily throughput | Projected cycle | Status |
|---|---|---|---|---|---|---|---|
| accessibility | 30d | 87,696 | 100.0% (87,690) | 20,766 (last 7d) | 2,966.6/day | 29.6d | 🟢 On pace |
| social_media | 30d | 87,696 | 100.0% (87,690) | 15,404 (last 7d) | 2,200.6/day | 39.9d | 🟢 Caught up |
| technology | 30d | 87,696 | 100.0% (87,690) | 7,631 (last 7d) | 1,090.1/day | 80.4d | 🟢 Caught up |
| third_party_js | 30d | 87,696 | 100.0% (87,690) | 18,181 (last 7d) | 2,597.3/day | 33.8d | 🟡 Marginal |
| overlays | 30d | 87,696 | 1.7% (1,523) | 0 (last 7d) | 0.0/day | —d | ⚪ No data |
| relationships | 60d | 87,696 | 94.0% (82,403) | 17,170 (last 7d) | 2,452.9/day | 35.8d | 🟢 Ahead |
| lighthouse | 60d | 87,696 | 77.3% (67,789) | 19,094 (last 7d) | 2,727.7/day | 32.1d | 🟢 Ahead |

_Projection method: `effective daily throughput = distinct URLs covered in the last 7 days ÷ 7`;
`projected cycle days = eligible URLs ÷ effective daily throughput`. The 7-day measurement
window reflects recent scan velocity and is independent of each scanner's own target cycle
length. Relationships measures successful source-page coverage using
`relationship_scan_state.last_successful_at`; other scanners use their configured scan
timestamp. See src/services/cycle_pace_tracker.py's module docstring for why. 'No data' means
the scanner has no rows in its metadata.db within the window (never run against this database,
or the database doesn't cover this scanner)._
