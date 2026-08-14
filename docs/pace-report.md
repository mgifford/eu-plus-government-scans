---
title: Scanner Cycle Pace Report
layout: page
---

_Generated: 2026-08-14 04:00 UTC_

Whether each scanner is on pace to complete its target cycle (30 days for most
scanners, 60 days for Lighthouse and Relationships), based on distinct URLs scanned
in the last 7 days projected forward against the full eligible corpus. See
[WORKFLOW_ORCHESTRATION_AUDIT.md](https://github.com/mgifford/eu-plus-government-scans/blob/main/WORKFLOW_ORCHESTRATION_AUDIT.md)
Section 11 for the methodology.

| Scanner | Target cycle | Eligible URLs | Scanned (window) | Daily throughput | Projected cycle | Status |
|---|---|---|---|---|---|---|
| accessibility | 30d | 87,696 | 16,738 (last 7d) | 2,391.1/day | 36.7d | 🟡 Marginal |
| social_media | 30d | 87,696 | 12,835 (last 7d) | 1,833.6/day | 47.8d | 🔴 Behind |
| technology | 30d | 87,696 | 14,602 (last 7d) | 2,086.0/day | 42.0d | 🔴 Behind |
| third_party_js | 30d | 87,696 | 9,942 (last 7d) | 1,420.3/day | 61.7d | 🔴 Behind |
| overlays | 30d | 87,696 | 1,503 (last 7d) | 214.7/day | 408.4d | 🔴 Behind |
| lighthouse | 60d | 87,696 | 2,692 (last 7d) | 384.6/day | 228.0d | 🔴 Behind |

_Projection method: `effective daily throughput = distinct URLs scanned in the last 7 days ÷ 7`;
`projected cycle days = eligible URLs ÷ effective daily throughput`. The 7-day measurement
window reflects recent scan velocity and is independent of each scanner's own target cycle
length -- see src/services/cycle_pace_tracker.py's module docstring for why. 'No data' means
the scanner has no rows in its metadata.db within the window (never run against this database,
or the database doesn't cover this scanner)._
