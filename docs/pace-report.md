---
title: Scanner Cycle Pace Report
layout: page
---

_Generated: 2026-07-31 12:55 UTC_

Whether each scanner is on pace to complete its target cycle (30 days for most
scanners, 60 days for Lighthouse and Relationships), based on distinct URLs scanned
in the last 7 days projected forward against the full eligible corpus. See
[WORKFLOW_ORCHESTRATION_AUDIT.md](https://github.com/mgifford/eu-plus-government-scans/blob/main/WORKFLOW_ORCHESTRATION_AUDIT.md)
Section 11 for the methodology.

| Scanner | Target cycle | Eligible URLs | Scanned (window) | Daily throughput | Projected cycle | Status |
|---|---|---|---|---|---|---|
| accessibility | 30d | 87,696 | 28,985 (last 7d) | 4,140.7/day | 21.2d | 🟢 Ahead |
| social_media | 30d | 87,696 | 82,472 (last 7d) | 11,781.7/day | 7.4d | 🟢 Ahead |
| technology | 30d | 87,696 | 14,831 (last 7d) | 2,118.7/day | 41.4d | 🔴 Behind |
| third_party_js | 30d | 87,696 | 16,921 (last 7d) | 2,417.3/day | 36.3d | 🟡 Marginal |
| overlays | 30d | 87,696 | 0 (last 7d) | 0.0/day | —d | ⚪ No data |
| lighthouse | 60d | 87,696 | 4,639 (last 7d) | 662.7/day | 132.3d | 🔴 Behind |

_Projection method: `effective daily throughput = distinct URLs scanned in the last 7 days ÷ 7`;
`projected cycle days = eligible URLs ÷ effective daily throughput`. The 7-day measurement
window reflects recent scan velocity and is independent of each scanner's own target cycle
length -- see src/services/cycle_pace_tracker.py's module docstring for why. 'No data' means
the scanner has no rows in its metadata.db within the window (never run against this database,
or the database doesn't cover this scanner)._
