# Codex supervisor handoff — M7 switch latency, then M8 region 3

Owner explicitly requires all coding/development through Codex CLI, using existing Cockpit proxy 127.0.0.1:38811. Supervisor may scope, monitor, review, and run prepared QA/art/perf scripts; not hand-write renderer or development scripts. No alternate coding agent/provider if gateway unavailable. Do not inspect or print credentials.

## Read first
- m7-work/REPORT_region2_zh.md and m7-work/progress.md
- m5-work/progress.md, m3-work notes for invocation and environment
- m7-work/verify-final.sh, existing QA/perf/recording harnesses and art provenance
- Preserve M5.2 and M6 baselines and existing evidence; append progress often.

## Stage A: M7 first-switch tail latency
Problem: first outer-city/inner-city transitions stall although average fps is normal. Current measured render maxima approximately 94.6/74.4ms and temporary emulation debt 164/218ms. M5.2 vs M7 route render p95: outer city 8.7 vs 10.6ms; inner city 9.4 vs 9.9ms. Investigate independently, do not assume one root cause.
Possible nonbinding hypothesis: decode/prewarm plate and LUT strips off switch-critical path, avoid sync readbacks at map switch. Preserve startup/loading semantics truthfully, do not disguise latency in unreported phases. No clock changes, gameplay/frame skipping, expanded masks, or denominator changes.
Acceptance:
1. Rerun all 442 state SHA256, original framebuffer SHA256, and actor/text preservation checks. Must remain 442/442.
2. Coverage unchanged from weighted 99.7345% for the 13 maps under identical QA route/denominator. Preserve exact visuals; any visual change requires inspection.
3. Exclusive headless Chromium performance, audit off/no recording, same frozen starts, native-frame inputs, warmup and machine. Compare M5.2, pre-fix M7 and candidate including first/cold transitions, switch p95/max, frame p95/max, temporary debt, and overall fps. Show repeats/variance; do not claim no regression if any required target fails.
4. ROM/core unchanged; regions 1 and 2 regressions pass. Save before/after data and human-readable Chinese report.
5. Only if visuals changed, produce m7-work/region2_preview_v2.webm (<25MB, real-time). No needless repeat video, no ZIP.

## Stage B: M8 region 3 after Stage A accepted
Create isolated copy m8-work/runtime from fixed M7 runtime. Naturally continue play/region2-story9-end.bin: return for introduction letter, deliver at 醉仙楼, continue to 东溪村 and connected maps until next major story gate. Map names/scope need original dialogue and natural doorway/story evidence; do not invent count or gate. No RAM/PC/map/story edits or teleporting to claim natural progress. Preserve input provenance and saves; isolated search attempts must not be presented as continuous play.
Full-map plates only, same approved V4 visual style. All new art exclusively user GPT gateway configured in /workspace/shawu/.image_api.env, gpt-image-2, quality <= medium; read env programmatically, never print any key. Reuse established authorized art harness. Bounded requests, hard deadlines, retry/backoff, save each attempt and final provenance. No alternate image provider, no smoothing/upscale fallback. No characters, text, monsters, portraits in plates; no character redraws. Full map alignment: original geometry, doors, roads and object identity/count retained.
Regression: immutable ROM/core; identical starting states/inputs comparing full state and native framebuffer SHA256, actor/text preservation; check original regions 1 and 2. Exact backgrounds measured with strict native evidence, retain uncovered nearest-neighbor pixels rather than guess. Report actual coverage denominators, route and exclusions. Performance same exclusive protocol as fixed M7 and M5.2 including cold switch tails; no hidden speed/frame changes.
Deliver shots/m8_region3_contact.png and m8-work/region3_preview.webm <25MB real-time (segment/load boundaries and no audio disclosed). No ZIP. Chinese final report: before/after fix numbers, verified map list, coverage, invariants, performance, exact story point reached, how much coding was done by Codex, all artifact/evidence paths and remaining limitations.

## Execution and interruption protocol
Launch codex exec using documented Cockpit routing, detached/nohup, logs within work directory. Freeze runtime hashes before exclusive QA, stop competing CPU jobs for performance measurements. Supervisor runs requested QA/GPT jobs if Codex sandbox cannot access network/browser; Codex prepares scripts and REQUEST_READY/STATUS notes. Append m7-work/progress.md and m8-work/progress.md at each milestone. Do not change proxy credentials or route around unavailable gateway; report and stop.
