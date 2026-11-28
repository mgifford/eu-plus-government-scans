---
title: Scanner Cycle Pace Report
layout: page
---

_Generated: 2026-11-28 08:52 UTC_

Whether each scanner is on pace to complete its target cycle (30 days for most
covered in the last 7 days projected forward against the full eligible corpus.
For Relationships, coverage means a successful source-page scan; failed attempts
do not count toward relationship coverage. See
[WORKFLOW_ORCHESTRATION_AUDIT.md](https://github.com/mgifford/eu-plus-government-scans/blob/main/WORKFLOW_ORCHESTRATION_AUDIT.md)
Section 11 for the methodology.

| Scanner | Target cycle | Eligible URLs | Corpus covered | Covered (window) | Daily throughput | Projected cycle | Status |
|---|---|---|---|---|---|---|---|
| accessibility | 30d | 87,696 | 100.0% (87,690) | 14,005 (last 7d) | 2,000.7/day | 43.8d | 🟢 Caught up |
| social_media | 30d | 87,696 | 100.0% (87,690) | 14,719 (last 7d) | 2,102.7/day | 41.7d | 🟢 Caught up |
| technology | 30d | 87,696 | 100.0% (87,690) | 15,865 (last 7d) | 2,266.4/day | 38.7d | 🟡 Marginal |
| third_party_js | 30d | 87,696 | 100.0% (87,690) | 16,201 (last 7d) | 2,314.4/day | 37.9d | 🟡 Marginal |
| overlays | 30d | 87,696 | 1.7% (1,523) | 0 (last 7d) | 0.0/day | —d | ⚪ No data |
| preferences | 90d | 87,696 | 11.8% (10,343) | 1,592 (last 7d) | 227.4/day | 385.6d | 🔴 Behind |
| relationships | 60d | 87,696 | 94.6% (82,967) | 16,899 (last 7d) | 2,414.1/day | 36.3d | 🟢 Ahead |
| lighthouse | 60d | 87,696 | 100.0% (87,690) | 11,576 (last 7d) | 1,653.7/day | 53.0d | 🟢 On pace |

_Projection method: `effective daily throughput = distinct URLs covered in the last 7 days ÷ 7`;
`projected cycle days = eligible URLs ÷ effective daily throughput`. The 7-day measurement
window reflects recent scan velocity and is independent of each scanner's own target cycle
length. Relationships measures successful source-page coverage using
`relationship_scan_state.last_successful_at`; other scanners use their configured scan
timestamp. See src/services/cycle_pace_tracker.py's module docstring for why. 'No data' means
the scanner has no rows in its metadata.db within the window (never run against this database,
or the database doesn't cover this scanner)._
