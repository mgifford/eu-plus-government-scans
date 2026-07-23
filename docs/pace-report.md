---
title: Scanner Cycle Pace Report
layout: page
---

_Generated: 2026-07-23 23:21 UTC_

Whether each scanner is on pace to complete its target cycle (30 days for most
scanners, 60 days for Lighthouse and Relationships), based on distinct URLs scanned
in the last 7 days projected forward against the full eligible corpus. See
[WORKFLOW_ORCHESTRATION_AUDIT.md](https://github.com/mgifford/eu-plus-government-scans/blob/main/WORKFLOW_ORCHESTRATION_AUDIT.md)
Section 11 for the methodology.

| Scanner | Target cycle | Eligible URLs | Scanned (window) | Daily throughput | Projected cycle | Status |
|---|---|---|---|---|---|---|
| accessibility | 30d | 87,696 | 15,838 (last 7d) | 2,262.6/day | 38.8d | 🟡 Marginal |
| social_media | 30d | 87,696 | 62,730 (last 7d) | 8,961.4/day | 9.8d | 🟢 Ahead |
| technology | 30d | 87,696 | 4,918 (last 7d) | 702.6/day | 124.8d | 🔴 Behind |
| third_party_js | 30d | 87,696 | 14,448 (last 7d) | 2,064.0/day | 42.5d | 🔴 Behind |
| overlays | 30d | 87,696 | 0 (last 7d) | 0.0/day | —d | ⚪ No data |
| lighthouse | 60d | 87,696 | 4,239 (last 7d) | 605.6/day | 144.8d | 🔴 Behind |

_Projection method: `effective daily throughput = distinct URLs scanned in the last 7 days ÷ 7`;
`projected cycle days = eligible URLs ÷ effective daily throughput`. The 7-day measurement
window reflects recent scan velocity and is independent of each scanner's own target cycle
length -- see src/services/cycle_pace_tracker.py's module docstring for why. 'No data' means
the scanner has no rows in its metadata.db within the window (never run against this database,
or the database doesn't cover this scanner)._
