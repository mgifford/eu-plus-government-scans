---
title: Scanner Cycle Pace Report
layout: page
---

_Generated: 2026-08-26 07:53 UTC_

Whether each scanner is on pace to complete its target cycle (30 days for most
scanners, 60 days for Lighthouse and Relationships), based on distinct URLs scanned
in the last 7 days projected forward against the full eligible corpus. See
[WORKFLOW_ORCHESTRATION_AUDIT.md](https://github.com/mgifford/eu-plus-government-scans/blob/main/WORKFLOW_ORCHESTRATION_AUDIT.md)
Section 11 for the methodology.

| Scanner | Target cycle | Eligible URLs | Scanned (window) | Daily throughput | Projected cycle | Status |
|---|---|---|---|---|---|---|
| accessibility | 30d | 87,696 | 44,014 (last 7d) | 6,287.7/day | 13.9d | 🟢 Ahead |
| social_media | 30d | 87,696 | 22,132 (last 7d) | 3,161.7/day | 27.7d | 🟢 On pace |
| technology | 30d | 87,696 | 25,002 (last 7d) | 3,571.7/day | 24.6d | 🟢 On pace |
| third_party_js | 30d | 87,696 | 15,820 (last 7d) | 2,260.0/day | 38.8d | 🟡 Marginal |
| overlays | 30d | 87,696 | 0 (last 7d) | 0.0/day | —d | ⚪ No data |
| lighthouse | 60d | 87,696 | 5,266 (last 7d) | 752.3/day | 116.6d | 🔴 Behind |

_Projection method: `effective daily throughput = distinct URLs scanned in the last 7 days ÷ 7`;
`projected cycle days = eligible URLs ÷ effective daily throughput`. The 7-day measurement
window reflects recent scan velocity and is independent of each scanner's own target cycle
length -- see src/services/cycle_pace_tracker.py's module docstring for why. 'No data' means
the scanner has no rows in its metadata.db within the window (never run against this database,
or the database doesn't cover this scanner)._
