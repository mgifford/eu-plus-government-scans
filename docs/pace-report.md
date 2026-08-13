---
title: Scanner Cycle Pace Report
layout: page
---

_Generated: 2026-08-13 19:20 UTC_

Whether each scanner is on pace to complete its target cycle (30 days for most
scanners, 60 days for Lighthouse and Relationships), based on distinct URLs scanned
in the last 7 days projected forward against the full eligible corpus. See
[WORKFLOW_ORCHESTRATION_AUDIT.md](https://github.com/mgifford/eu-plus-government-scans/blob/main/WORKFLOW_ORCHESTRATION_AUDIT.md)
Section 11 for the methodology.

| Scanner | Target cycle | Eligible URLs | Scanned (window) | Daily throughput | Projected cycle | Status |
|---|---|---|---|---|---|---|
| accessibility | 30d | 87,696 | 14,767 (last 7d) | 2,109.6/day | 41.6d | 🔴 Behind |
| social_media | 30d | 87,696 | 8,811 (last 7d) | 1,258.7/day | 69.7d | 🔴 Behind |
| technology | 30d | 87,696 | 9,683 (last 7d) | 1,383.3/day | 63.4d | 🔴 Behind |
| third_party_js | 30d | 87,696 | 8,576 (last 7d) | 1,225.1/day | 71.6d | 🔴 Behind |
| overlays | 30d | 87,696 | 1,503 (last 7d) | 214.7/day | 408.4d | 🔴 Behind |
| lighthouse | 60d | 87,696 | 2,704 (last 7d) | 386.3/day | 227.0d | 🔴 Behind |

_Projection method: `effective daily throughput = distinct URLs scanned in the last 7 days ÷ 7`;
`projected cycle days = eligible URLs ÷ effective daily throughput`. The 7-day measurement
window reflects recent scan velocity and is independent of each scanner's own target cycle
length -- see src/services/cycle_pace_tracker.py's module docstring for why. 'No data' means
the scanner has no rows in its metadata.db within the window (never run against this database,
or the database doesn't cover this scanner)._
