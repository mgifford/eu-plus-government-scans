---
title: Scanner Cycle Pace Report
layout: page
---

_Generated: 2026-10-08 14:23 UTC_

Whether each scanner is on pace to complete its target cycle (30 days for most
covered in the last 7 days projected forward against the full eligible corpus.
For Relationships, coverage means a successful source-page scan; failed attempts
do not count toward relationship coverage. See
[WORKFLOW_ORCHESTRATION_AUDIT.md](https://github.com/mgifford/eu-plus-government-scans/blob/main/WORKFLOW_ORCHESTRATION_AUDIT.md)
Section 11 for the methodology.

| Scanner | Target cycle | Eligible URLs | Corpus covered | Covered (window) | Daily throughput | Projected cycle | Status |
|---|---|---|---|---|---|---|---|
| accessibility | 30d | 87,696 | 100.0% (87,690) | 18,837 (last 7d) | 2,691.0/day | 32.6d | 🟡 Marginal |
| social_media | 30d | 87,696 | 100.0% (87,690) | 24,049 (last 7d) | 3,435.6/day | 25.5d | 🟢 On pace |
| technology | 30d | 87,696 | 100.0% (87,690) | 2,972 (last 7d) | 424.6/day | 206.6d | 🟢 Caught up |
| third_party_js | 30d | 87,696 | 100.0% (87,690) | 20,794 (last 7d) | 2,970.6/day | 29.5d | 🟢 On pace |
| overlays | 30d | 87,696 | 1.7% (1,523) | 0 (last 7d) | 0.0/day | —d | ⚪ No data |
| relationships | 60d | 87,696 | 93.9% (82,331) | 19,515 (last 7d) | 2,787.9/day | 31.5d | 🟢 Ahead |
| lighthouse | 60d | 87,696 | 71.8% (62,997) | 20,444 (last 7d) | 2,920.6/day | 30.0d | 🟢 Ahead |

_Projection method: `effective daily throughput = distinct URLs covered in the last 7 days ÷ 7`;
`projected cycle days = eligible URLs ÷ effective daily throughput`. The 7-day measurement
window reflects recent scan velocity and is independent of each scanner's own target cycle
length. Relationships measures successful source-page coverage using
`relationship_scan_state.last_successful_at`; other scanners use their configured scan
timestamp. See src/services/cycle_pace_tracker.py's module docstring for why. 'No data' means
the scanner has no rows in its metadata.db within the window (never run against this database,
or the database doesn't cover this scanner)._
