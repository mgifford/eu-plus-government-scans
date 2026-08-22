---
title: Scanner Cycle Pace Report
layout: page
---

_Generated: 2026-08-22 20:40 UTC_

Whether each scanner is on pace to complete its target cycle (30 days for most
scanners, 60 days for Lighthouse and Relationships), based on distinct URLs scanned
in the last 7 days projected forward against the full eligible corpus. See
[WORKFLOW_ORCHESTRATION_AUDIT.md](https://github.com/mgifford/eu-plus-government-scans/blob/main/WORKFLOW_ORCHESTRATION_AUDIT.md)
Section 11 for the methodology.

| Scanner | Target cycle | Eligible URLs | Scanned (window) | Daily throughput | Projected cycle | Status |
|---|---|---|---|---|---|---|
| accessibility | 30d | 87,696 | 46,151 (last 7d) | 6,593.0/day | 13.3d | 🟢 Ahead |
| social_media | 30d | 87,696 | 21,449 (last 7d) | 3,064.1/day | 28.6d | 🟢 On pace |
| technology | 30d | 87,696 | 27,128 (last 7d) | 3,875.4/day | 22.6d | 🟢 Ahead |
| third_party_js | 30d | 87,696 | 15,243 (last 7d) | 2,177.6/day | 40.3d | 🔴 Behind |
| overlays | 30d | 87,696 | 1,446 (last 7d) | 206.6/day | 424.5d | 🔴 Behind |
| lighthouse | 60d | 87,696 | 3,293 (last 7d) | 470.4/day | 186.4d | 🔴 Behind |

_Projection method: `effective daily throughput = distinct URLs scanned in the last 7 days ÷ 7`;
`projected cycle days = eligible URLs ÷ effective daily throughput`. The 7-day measurement
window reflects recent scan velocity and is independent of each scanner's own target cycle
length -- see src/services/cycle_pace_tracker.py's module docstring for why. 'No data' means
the scanner has no rows in its metadata.db within the window (never run against this database,
or the database doesn't cover this scanner)._
