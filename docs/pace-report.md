---
title: Scanner Cycle Pace Report
layout: page
---

_Generated: 2026-10-10 12:08 UTC_

Whether each scanner is on pace to complete its target cycle (30 days for most
covered in the last 7 days projected forward against the full eligible corpus.
For Relationships, coverage means a successful source-page scan; failed attempts
do not count toward relationship coverage. See
[WORKFLOW_ORCHESTRATION_AUDIT.md](https://github.com/mgifford/eu-plus-government-scans/blob/main/WORKFLOW_ORCHESTRATION_AUDIT.md)
Section 11 for the methodology.

| Scanner | Target cycle | Eligible URLs | Corpus covered | Covered (window) | Daily throughput | Projected cycle | Status |
|---|---|---|---|---|---|---|---|
| accessibility | 30d | 87,696 | 100.0% (87,690) | 18,614 (last 7d) | 2,659.1/day | 33.0d | 🟡 Marginal |
| social_media | 30d | 87,696 | 100.0% (87,690) | 17,970 (last 7d) | 2,567.1/day | 34.2d | 🟡 Marginal |
| technology | 30d | 87,696 | 100.0% (87,690) | 0 (last 7d) | 0.0/day | —d | 🟢 Caught up |
| third_party_js | 30d | 87,696 | 100.0% (87,690) | 19,794 (last 7d) | 2,827.7/day | 31.0d | 🟡 Marginal |
| overlays | 30d | 87,696 | 1.7% (1,523) | 0 (last 7d) | 0.0/day | —d | ⚪ No data |
| relationships | 60d | 87,696 | 93.9% (82,389) | 20,200 (last 7d) | 2,885.7/day | 30.4d | 🟢 Ahead |
| lighthouse | 60d | 87,696 | 74.9% (65,684) | 19,693 (last 7d) | 2,813.3/day | 31.2d | 🟢 Ahead |

_Projection method: `effective daily throughput = distinct URLs covered in the last 7 days ÷ 7`;
`projected cycle days = eligible URLs ÷ effective daily throughput`. The 7-day measurement
window reflects recent scan velocity and is independent of each scanner's own target cycle
length. Relationships measures successful source-page coverage using
`relationship_scan_state.last_successful_at`; other scanners use their configured scan
timestamp. See src/services/cycle_pace_tracker.py's module docstring for why. 'No data' means
the scanner has no rows in its metadata.db within the window (never run against this database,
or the database doesn't cover this scanner)._
