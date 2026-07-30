---
title: Scanner Cycle Pace Report
layout: page
---

_Generated: 2026-07-30 12:51 UTC_

Whether each scanner is on pace to complete its target cycle (30 days for most
scanners, 60 days for Lighthouse and Relationships), based on distinct URLs scanned
in the last 7 days projected forward against the full eligible corpus. See
[WORKFLOW_ORCHESTRATION_AUDIT.md](https://github.com/mgifford/eu-plus-government-scans/blob/main/WORKFLOW_ORCHESTRATION_AUDIT.md)
Section 11 for the methodology.

| Scanner | Target cycle | Eligible URLs | Scanned (window) | Daily throughput | Projected cycle | Status |
|---|---|---|---|---|---|---|
| accessibility | 30d | 87,696 | 30,913 (last 7d) | 4,416.1/day | 19.9d | 🟢 Ahead |
| social_media | 30d | 87,696 | 83,636 (last 7d) | 11,948.0/day | 7.3d | 🟢 Ahead |
| technology | 30d | 87,696 | 15,008 (last 7d) | 2,144.0/day | 40.9d | 🔴 Behind |
| third_party_js | 30d | 87,696 | 16,806 (last 7d) | 2,400.9/day | 36.5d | 🟡 Marginal |
| overlays | 30d | 87,696 | 0 (last 7d) | 0.0/day | —d | ⚪ No data |
| lighthouse | 60d | 87,696 | 5,003 (last 7d) | 714.7/day | 122.7d | 🔴 Behind |

_Projection method: `effective daily throughput = distinct URLs scanned in the last 7 days ÷ 7`;
`projected cycle days = eligible URLs ÷ effective daily throughput`. The 7-day measurement
window reflects recent scan velocity and is independent of each scanner's own target cycle
length -- see src/services/cycle_pace_tracker.py's module docstring for why. 'No data' means
the scanner has no rows in its metadata.db within the window (never run against this database,
or the database doesn't cover this scanner)._
