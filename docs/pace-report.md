---
title: Scanner Cycle Pace Report
layout: page
---

_Generated: 2026-08-27 10:49 UTC_

Whether each scanner is on pace to complete its target cycle (30 days for most
scanners, 60 days for Lighthouse and Relationships), based on distinct URLs scanned
in the last 7 days projected forward against the full eligible corpus. See
[WORKFLOW_ORCHESTRATION_AUDIT.md](https://github.com/mgifford/eu-plus-government-scans/blob/main/WORKFLOW_ORCHESTRATION_AUDIT.md)
Section 11 for the methodology.

| Scanner | Target cycle | Eligible URLs | Scanned (window) | Daily throughput | Projected cycle | Status |
|---|---|---|---|---|---|---|
| accessibility | 30d | 87,696 | 40,020 (last 7d) | 5,717.1/day | 15.3d | 🟢 Ahead |
| social_media | 30d | 87,696 | 22,326 (last 7d) | 3,189.4/day | 27.5d | 🟢 On pace |
| technology | 30d | 87,696 | 23,988 (last 7d) | 3,426.9/day | 25.6d | 🟢 On pace |
| third_party_js | 30d | 87,696 | 15,431 (last 7d) | 2,204.4/day | 39.8d | 🔴 Behind |
| overlays | 30d | 87,696 | 0 (last 7d) | 0.0/day | —d | ⚪ No data |
| lighthouse | 60d | 87,696 | 5,470 (last 7d) | 781.4/day | 112.2d | 🔴 Behind |

_Projection method: `effective daily throughput = distinct URLs scanned in the last 7 days ÷ 7`;
`projected cycle days = eligible URLs ÷ effective daily throughput`. The 7-day measurement
window reflects recent scan velocity and is independent of each scanner's own target cycle
length -- see src/services/cycle_pace_tracker.py's module docstring for why. 'No data' means
the scanner has no rows in its metadata.db within the window (never run against this database,
or the database doesn't cover this scanner)._
