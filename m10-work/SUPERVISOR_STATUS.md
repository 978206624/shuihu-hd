# M10 SUPERVISOR_STATUS
Updated: 2026-11-19T15:47:30+08:00 Asia/Shanghai

## Closed — region 5 accepted for delivery
- Official chain 1669/55206. Endpoint 00-2a e0 (5,8) story 19, DAA 52/06, D284=04 01, party 02/17/24, HP 5/24/4. Fruit 63. Do not walk 00-2a row 4.
- Isolated m10 runtime (38 maps). Formal QA PASSED 35/35, 3027 actions, 153913/153913 hashes. Weighted coverage 690,340,846/836,125,181 = 82.56429320%.
- Perf PASSED 252/252, native mismatches 0, 8/14 timeout-flake resumes, same RUN_ID m10-region5-20261119T021341364667010Z. Bounded fix unused. 337 mean flags are paired vs same-machine M9; single-repeat spikes exist on both sides.
- Contact PASSED: shots/m10_region5_contact.png (5,913,988 bytes, SHA-256 4aa74454a738d64fe13df506680090a045b2cdd18efc749195422abdedbb6477).
- Preview PASSED (encode-only rerun of hash-verified raw capture): m10-work/region5_preview.webm 4,861,916 bytes, 49.6 s, 640×576 VP9, audio=false, speed=1, 6 segments, SHA-256 cc10d9ca6b7fe61c850af14cb95a4be8d1b1637b8b78c8b44f3d8576a281fd3d.
- Report: m10-work/REPORT_region5_zh.md.

## Preview encode note
First encode (PID 789468) recorded all 6 excerpts then failed the M10 abs-duration check (white-bar tails ~0.23–0.26 s, last clip longer). Capture retained. Codex aligned encode() with accepted M9 trim logic and updated only the region5-preview.cjs freeze hash. Supervisor updated this run’s run-freeze.sha256 (backup run-freeze.sha256.pre-preview-encode-fix) and reran encode only. Runtime inventory unchanged (591/591).

## Next
Do not start later chapters until asked. Do not walk 00-2a row 4. Do not modify m8-work/runtime/ or m9-work/runtime/.
