---
title: Scanner Cycle Pace Report
layout: page
---

_Generated: 2026-08-12 20:02 UTC_

Whether each scanner is on pace to complete its target cycle (30 days for most
scanners, 60 days for Lighthouse and Relationships), based on distinct URLs scanned
in the last 7 days projected forward against the full eligible corpus. See
[WORKFLOW_ORCHESTRATION_AUDIT.md](https://github.com/mgifford/eu-plus-government-scans/blob/main/WORKFLOW_ORCHESTRATION_AUDIT.md)
Section 11 for the methodology.

| Scanner | Target cycle | Eligible URLs | Scanned (window) | Daily throughput | Projected cycle | Status |
|---|---|---|---|---|---|---|
| accessibility | 30d | 87,696 | 10,034 (last 7d) | 1,433.4/day | 61.2d | 🔴 Behind |
| social_media | 30d | 87,696 | 5,593 (last 7d) | 799.0/day | 109.8d | 🔴 Behind |
| technology | 30d | 87,696 | 6,766 (last 7d) | 966.6/day | 90.7d | 🔴 Behind |
| third_party_js | 30d | 87,696 | 3,213 (last 7d) | 459.0/day | 191.1d | 🔴 Behind |
| overlays | 30d | 87,696 | 1,503 (last 7d) | 214.7/day | 408.4d | 🔴 Behind |
| lighthouse | 60d | 87,696 | 2,704 (last 7d) | 386.3/day | 227.0d | 🔴 Behind |

_Projection method: `effective daily throughput = distinct URLs scanned in the last 7 days ÷ 7`;
`projected cycle days = eligible URLs ÷ effective daily throughput`. The 7-day measurement
window reflects recent scan velocity and is independent of each scanner's own target cycle
length -- see src/services/cycle_pace_tracker.py's module docstring for why. 'No data' means
the scanner has no rows in its metadata.db within the window (never run against this database,
or the database doesn't cover this scanner)._
