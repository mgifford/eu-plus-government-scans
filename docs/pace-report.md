---
title: Scanner Cycle Pace Report
layout: page
---

_Generated: 2026-08-24 09:42 UTC_

Whether each scanner is on pace to complete its target cycle (30 days for most
scanners, 60 days for Lighthouse and Relationships), based on distinct URLs scanned
in the last 7 days projected forward against the full eligible corpus. See
[WORKFLOW_ORCHESTRATION_AUDIT.md](https://github.com/mgifford/eu-plus-government-scans/blob/main/WORKFLOW_ORCHESTRATION_AUDIT.md)
Section 11 for the methodology.

| Scanner | Target cycle | Eligible URLs | Scanned (window) | Daily throughput | Projected cycle | Status |
|---|---|---|---|---|---|---|
| accessibility | 30d | 87,696 | 43,918 (last 7d) | 6,274.0/day | 14.0d | 🟢 Ahead |
| social_media | 30d | 87,696 | 21,100 (last 7d) | 3,014.3/day | 29.1d | 🟢 On pace |
| technology | 30d | 87,696 | 24,746 (last 7d) | 3,535.1/day | 24.8d | 🟢 On pace |
| third_party_js | 30d | 87,696 | 15,677 (last 7d) | 2,239.6/day | 39.2d | 🔴 Behind |
| overlays | 30d | 87,696 | 0 (last 7d) | 0.0/day | —d | ⚪ No data |
| lighthouse | 60d | 87,696 | 4,684 (last 7d) | 669.1/day | 131.1d | 🔴 Behind |

_Projection method: `effective daily throughput = distinct URLs scanned in the last 7 days ÷ 7`;
`projected cycle days = eligible URLs ÷ effective daily throughput`. The 7-day measurement
window reflects recent scan velocity and is independent of each scanner's own target cycle
length -- see src/services/cycle_pace_tracker.py's module docstring for why. 'No data' means
the scanner has no rows in its metadata.db within the window (never run against this database,
or the database doesn't cover this scanner)._
