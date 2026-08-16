---
title: Scanner Cycle Pace Report
layout: page
---

_Generated: 2026-08-16 01:57 UTC_

Whether each scanner is on pace to complete its target cycle (30 days for most
scanners, 60 days for Lighthouse and Relationships), based on distinct URLs scanned
in the last 7 days projected forward against the full eligible corpus. See
[WORKFLOW_ORCHESTRATION_AUDIT.md](https://github.com/mgifford/eu-plus-government-scans/blob/main/WORKFLOW_ORCHESTRATION_AUDIT.md)
Section 11 for the methodology.

| Scanner | Target cycle | Eligible URLs | Scanned (window) | Daily throughput | Projected cycle | Status |
|---|---|---|---|---|---|---|
| accessibility | 30d | 87,696 | 31,981 (last 7d) | 4,568.7/day | 19.2d | 🟢 Ahead |
| social_media | 30d | 87,696 | 23,913 (last 7d) | 3,416.1/day | 25.7d | 🟢 On pace |
| technology | 30d | 87,696 | 22,859 (last 7d) | 3,265.6/day | 26.9d | 🟢 On pace |
| third_party_js | 30d | 87,696 | 15,133 (last 7d) | 2,161.9/day | 40.6d | 🔴 Behind |
| overlays | 30d | 87,696 | 1,523 (last 7d) | 217.6/day | 403.1d | 🔴 Behind |
| lighthouse | 60d | 87,696 | 2,432 (last 7d) | 347.4/day | 252.4d | 🔴 Behind |

_Projection method: `effective daily throughput = distinct URLs scanned in the last 7 days ÷ 7`;
`projected cycle days = eligible URLs ÷ effective daily throughput`. The 7-day measurement
window reflects recent scan velocity and is independent of each scanner's own target cycle
length -- see src/services/cycle_pace_tracker.py's module docstring for why. 'No data' means
the scanner has no rows in its metadata.db within the window (never run against this database,
or the database doesn't cover this scanner)._
