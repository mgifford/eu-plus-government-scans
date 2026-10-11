---
title: Scanner Cycle Pace Report
layout: page
---

_Generated: 2026-10-11 16:08 UTC_

Whether each scanner is on pace to complete its target cycle (30 days for most
covered in the last 7 days projected forward against the full eligible corpus.
For Relationships, coverage means a successful source-page scan; failed attempts
do not count toward relationship coverage. See
[WORKFLOW_ORCHESTRATION_AUDIT.md](https://github.com/mgifford/eu-plus-government-scans/blob/main/WORKFLOW_ORCHESTRATION_AUDIT.md)
Section 11 for the methodology.

| Scanner | Target cycle | Eligible URLs | Corpus covered | Covered (window) | Daily throughput | Projected cycle | Status |
|---|---|---|---|---|---|---|---|
| accessibility | 30d | 87,696 | 100.0% (87,690) | 19,427 (last 7d) | 2,775.3/day | 31.6d | 🟡 Marginal |
| social_media | 30d | 87,696 | 100.0% (87,690) | 14,828 (last 7d) | 2,118.3/day | 41.4d | 🟢 Caught up |
| technology | 30d | 87,696 | 100.0% (87,690) | 2,385 (last 7d) | 340.7/day | 257.4d | 🟢 Caught up |
| third_party_js | 30d | 87,696 | 100.0% (87,690) | 18,749 (last 7d) | 2,678.4/day | 32.7d | 🟡 Marginal |
| overlays | 30d | 87,696 | 1.7% (1,523) | 0 (last 7d) | 0.0/day | —d | ⚪ No data |
| relationships | 60d | 87,696 | 93.9% (82,389) | 21,634 (last 7d) | 3,090.6/day | 28.4d | 🟢 Ahead |
| lighthouse | 60d | 87,696 | 76.2% (66,852) | 19,499 (last 7d) | 2,785.6/day | 31.5d | 🟢 Ahead |

_Projection method: `effective daily throughput = distinct URLs covered in the last 7 days ÷ 7`;
`projected cycle days = eligible URLs ÷ effective daily throughput`. The 7-day measurement
window reflects recent scan velocity and is independent of each scanner's own target cycle
length. Relationships measures successful source-page coverage using
`relationship_scan_state.last_successful_at`; other scanners use their configured scan
timestamp. See src/services/cycle_pace_tracker.py's module docstring for why. 'No data' means
the scanner has no rows in its metadata.db within the window (never run against this database,
or the database doesn't cover this scanner)._
