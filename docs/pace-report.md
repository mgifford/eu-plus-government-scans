---
title: Scanner Cycle Pace Report
layout: page
---

_Generated: 2026-08-17 10:48 UTC_

Whether each scanner is on pace to complete its target cycle (30 days for most
scanners, 60 days for Lighthouse and Relationships), based on distinct URLs scanned
in the last 7 days projected forward against the full eligible corpus. See
[WORKFLOW_ORCHESTRATION_AUDIT.md](https://github.com/mgifford/eu-plus-government-scans/blob/main/WORKFLOW_ORCHESTRATION_AUDIT.md)
Section 11 for the methodology.

| Scanner | Target cycle | Eligible URLs | Scanned (window) | Daily throughput | Projected cycle | Status |
|---|---|---|---|---|---|---|
| accessibility | 30d | 87,696 | 42,457 (last 7d) | 6,065.3/day | 14.5d | 🟢 Ahead |
| social_media | 30d | 87,696 | 28,933 (last 7d) | 4,133.3/day | 21.2d | 🟢 Ahead |
| technology | 30d | 87,696 | 31,598 (last 7d) | 4,514.0/day | 19.4d | 🟢 Ahead |
| third_party_js | 30d | 87,696 | 16,277 (last 7d) | 2,325.3/day | 37.7d | 🟡 Marginal |
| overlays | 30d | 87,696 | 1,523 (last 7d) | 217.6/day | 403.1d | 🔴 Behind |
| lighthouse | 60d | 87,696 | 2,226 (last 7d) | 318.0/day | 275.8d | 🔴 Behind |

_Projection method: `effective daily throughput = distinct URLs scanned in the last 7 days ÷ 7`;
`projected cycle days = eligible URLs ÷ effective daily throughput`. The 7-day measurement
window reflects recent scan velocity and is independent of each scanner's own target cycle
length -- see src/services/cycle_pace_tracker.py's module docstring for why. 'No data' means
the scanner has no rows in its metadata.db within the window (never run against this database,
or the database doesn't cover this scanner)._
