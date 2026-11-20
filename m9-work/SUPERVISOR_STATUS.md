# SUPERVISOR_STATUS
Updated: 2026-11-18T15:20:14-05:00 America/New_York

Region 4 is closed for this workstream. Both deliverables exist and were reviewed. Isolated M9 runtime kept. Do not modify m8-work/runtime/. Do not start later chapters unless asked.

## Deliverables
- `shots/m9_region4_contact.png` (SHA-256 402ee0f8488c8348dcf75f276f27b5cd9638fb7a93e7f10fd1665d16b4de4144)
- `m9-work/region4_preview.webm` (5,687,067 bytes, 71.2s, 7 excerpts, 640×576, no audio, SHA-256 05d263c4ba6ef47b3ed5aeeb90ac0bff29aaec93016717a7e35273263b90686f)
- Report: `m9-work/REPORT_region4_zh.md`

## QA (accepted)
1,358 actions, 98,707 frames. Invariants 98707/98707 (state/native/actor-text), earlier visual 87957/87957. 34/34 routes. Official end 00-2c story 14, DAA1=0x72, DAA2=0x01. Coverage: 00-1f 80.47%, 00-21 53.12%, 00-24 87.98%, 00-2b 97.19%, 00-2c 97.22%; weighted 137568443/166264826 = 82.74%.

## Perf (accepted; residual disclosed)
276/276 samples, native mismatches 0, residual exceedances 0. cold/00-17 candidate frame/switch max mean 21.600 ms (under disclosed 24.100, still above old 19.0 vs v3 16.000). frame.p95 4.333 ms. debt.max 16.738 ms. gameFPS 59.720.
