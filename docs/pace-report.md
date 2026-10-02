---
title: Scanner Cycle Pace Report
layout: page
---

_Generated: 2026-10-02 06:18 UTC_

Whether each scanner is on pace to complete its target cycle (30 days for most
covered in the last 7 days projected forward against the full eligible corpus.
For Relationships, coverage means a successful source-page scan; failed attempts
do not count toward relationship coverage. See
[WORKFLOW_ORCHESTRATION_AUDIT.md](https://github.com/mgifford/eu-plus-government-scans/blob/main/WORKFLOW_ORCHESTRATION_AUDIT.md)
Section 11 for the methodology.

| Scanner | Target cycle | Eligible URLs | Corpus covered | Covered (window) | Daily throughput | Projected cycle | Status |
|---|---|---|---|---|---|---|---|
| accessibility | 30d | 87,696 | 100.0% (87,690) | 19,402 (last 7d) | 2,771.7/day | 31.6d | 🟡 Marginal |
| social_media | 30d | 87,696 | 100.0% (87,690) | 19,504 (last 7d) | 2,786.3/day | 31.5d | 🟡 Marginal |
| technology | 30d | 87,696 | 100.0% (87,690) | 24,767 (last 7d) | 3,538.1/day | 24.8d | 🟢 On pace |
| third_party_js | 30d | 87,696 | 100.0% (87,690) | 21,167 (last 7d) | 3,023.9/day | 29.0d | 🟢 On pace |
| overlays | 30d | 87,696 | 1.7% (1,523) | 0 (last 7d) | 0.0/day | —d | ⚪ No data |
| relationships | 60d | 87,696 | 93.8% (82,240) | 17,700 (last 7d) | 2,528.6/day | 34.7d | 🟢 Ahead |
| lighthouse | 60d | 87,696 | 63.3% (55,483) | 22,426 (last 7d) | 3,203.7/day | 27.4d | 🟢 Ahead |

_Projection method: `effective daily throughput = distinct URLs covered in the last 7 days ÷ 7`;
`projected cycle days = eligible URLs ÷ effective daily throughput`. The 7-day measurement
window reflects recent scan velocity and is independent of each scanner's own target cycle
length. Relationships measures successful source-page coverage using
`relationship_scan_state.last_successful_at`; other scanners use their configured scan
timestamp. See src/services/cycle_pace_tracker.py's module docstring for why. 'No data' means
the scanner has no rows in its metadata.db within the window (never run against this database,
or the database doesn't cover this scanner)._
