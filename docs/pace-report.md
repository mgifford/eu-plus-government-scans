---
title: Scanner Cycle Pace Report
layout: page
---

_Generated: 2026-09-24 11:51 UTC_

Whether each scanner is on pace to complete its target cycle (30 days for most
covered in the last 7 days projected forward against the full eligible corpus.
For Relationships, coverage means a successful source-page scan; failed attempts
do not count toward relationship coverage. See
[WORKFLOW_ORCHESTRATION_AUDIT.md](https://github.com/mgifford/eu-plus-government-scans/blob/main/WORKFLOW_ORCHESTRATION_AUDIT.md)
Section 11 for the methodology.

| Scanner | Target cycle | Eligible URLs | Corpus covered | Covered (window) | Daily throughput | Projected cycle | Status |
|---|---|---|---|---|---|---|---|
| accessibility | 30d | 87,696 | 100.0% (87,690) | 24,839 (last 7d) | 3,548.4/day | 24.7d | 🟢 On pace |
| social_media | 30d | 87,696 | 100.0% (87,690) | 20,238 (last 7d) | 2,891.1/day | 30.3d | 🟡 Marginal |
| technology | 30d | 87,696 | 100.0% (87,690) | 26,711 (last 7d) | 3,815.9/day | 23.0d | 🟢 Ahead |
| third_party_js | 30d | 87,696 | 100.0% (87,690) | 4,544 (last 7d) | 649.1/day | 135.1d | 🟢 Caught up |
| overlays | 30d | 87,696 | 1.7% (1,523) | 0 (last 7d) | 0.0/day | —d | ⚪ No data |
| relationships | 60d | 87,696 | 93.3% (81,842) | 26,890 (last 7d) | 3,841.4/day | 22.8d | 🟢 Ahead |
| lighthouse | 60d | 87,696 | 47.7% (41,867) | 19,930 (last 7d) | 2,847.1/day | 30.8d | 🟢 Ahead |

_Projection method: `effective daily throughput = distinct URLs covered in the last 7 days ÷ 7`;
`projected cycle days = eligible URLs ÷ effective daily throughput`. The 7-day measurement
window reflects recent scan velocity and is independent of each scanner's own target cycle
length. Relationships measures successful source-page coverage using
`relationship_scan_state.last_successful_at`; other scanners use their configured scan
timestamp. See src/services/cycle_pace_tracker.py's module docstring for why. 'No data' means
the scanner has no rows in its metadata.db within the window (never run against this database,
or the database doesn't cover this scanner)._
