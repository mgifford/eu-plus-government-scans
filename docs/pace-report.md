---
title: Scanner Cycle Pace Report
layout: page
---

_Generated: 2026-08-22 14:02 UTC_

Whether each scanner is on pace to complete its target cycle (30 days for most
scanners, 60 days for Lighthouse and Relationships), based on distinct URLs scanned
in the last 7 days projected forward against the full eligible corpus. See
[WORKFLOW_ORCHESTRATION_AUDIT.md](https://github.com/mgifford/eu-plus-government-scans/blob/main/WORKFLOW_ORCHESTRATION_AUDIT.md)
Section 11 for the methodology.

| Scanner | Target cycle | Eligible URLs | Scanned (window) | Daily throughput | Projected cycle | Status |
|---|---|---|---|---|---|---|
| accessibility | 30d | 87,696 | 48,473 (last 7d) | 6,924.7/day | 12.7d | 🟢 Ahead |
| social_media | 30d | 87,696 | 25,119 (last 7d) | 3,588.4/day | 24.4d | 🟢 On pace |
| technology | 30d | 87,696 | 31,061 (last 7d) | 4,437.3/day | 19.8d | 🟢 Ahead |
| third_party_js | 30d | 87,696 | 15,856 (last 7d) | 2,265.1/day | 38.7d | 🟡 Marginal |
| overlays | 30d | 87,696 | 1,446 (last 7d) | 206.6/day | 424.5d | 🔴 Behind |
| lighthouse | 60d | 87,696 | 3,123 (last 7d) | 446.1/day | 196.6d | 🔴 Behind |

_Projection method: `effective daily throughput = distinct URLs scanned in the last 7 days ÷ 7`;
`projected cycle days = eligible URLs ÷ effective daily throughput`. The 7-day measurement
window reflects recent scan velocity and is independent of each scanner's own target cycle
length -- see src/services/cycle_pace_tracker.py's module docstring for why. 'No data' means
the scanner has no rows in its metadata.db within the window (never run against this database,
or the database doesn't cover this scanner)._
