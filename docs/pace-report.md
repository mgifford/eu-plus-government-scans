---
title: Scanner Cycle Pace Report
layout: page
---

_Generated: 2026-08-26 01:59 UTC_

Whether each scanner is on pace to complete its target cycle (30 days for most
scanners, 60 days for Lighthouse and Relationships), based on distinct URLs scanned
in the last 7 days projected forward against the full eligible corpus. See
[WORKFLOW_ORCHESTRATION_AUDIT.md](https://github.com/mgifford/eu-plus-government-scans/blob/main/WORKFLOW_ORCHESTRATION_AUDIT.md)
Section 11 for the methodology.

| Scanner | Target cycle | Eligible URLs | Scanned (window) | Daily throughput | Projected cycle | Status |
|---|---|---|---|---|---|---|
| accessibility | 30d | 87,696 | 43,378 (last 7d) | 6,196.9/day | 14.2d | 🟢 Ahead |
| social_media | 30d | 87,696 | 21,292 (last 7d) | 3,041.7/day | 28.8d | 🟢 On pace |
| technology | 30d | 87,696 | 23,981 (last 7d) | 3,425.9/day | 25.6d | 🟢 On pace |
| third_party_js | 30d | 87,696 | 15,494 (last 7d) | 2,213.4/day | 39.6d | 🔴 Behind |
| overlays | 30d | 87,696 | 0 (last 7d) | 0.0/day | —d | ⚪ No data |
| lighthouse | 60d | 87,696 | 5,175 (last 7d) | 739.3/day | 118.6d | 🔴 Behind |

_Projection method: `effective daily throughput = distinct URLs scanned in the last 7 days ÷ 7`;
`projected cycle days = eligible URLs ÷ effective daily throughput`. The 7-day measurement
window reflects recent scan velocity and is independent of each scanner's own target cycle
length -- see src/services/cycle_pace_tracker.py's module docstring for why. 'No data' means
the scanner has no rows in its metadata.db within the window (never run against this database,
or the database doesn't cover this scanner)._
