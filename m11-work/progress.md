- 2026-11-20T20:04:00.981559+08:00 Fresh execution; read M10 handoff and native tools; adapted M11 tools, all writes restricted to m11-work. Both starting SHA-256 values verified.
- 2026-11-20T20:04:30+08:00 SUPERVISOR: run1 (session 01a1f8d7…, gpt-6.1-sol effort none after account switch) stopped by supervisor for model/effort parity with M10. Its files (scripts/native-play.cjs, outer-runs/native-talk.cjs, directed-walk.cjs, native/first-gate, native/enter-maze) are unreviewed drafts: review/reuse or supersede them. Run2 = fresh session gpt-6.2-sol effort high.

- 2026-11-20T20:04:57+08:00 Verified both supplied checkpoint hashes and reviewed the existing M11 draft tools against M10.

- 2026-11-20T20:06:20+08:00 Both starts agree on map, cell, story, flags, pocket, and party. Bank samples differ (native 5, official 4). Both naturally entered 00-26 through the item gate and 00-25 staging.
- 2026-11-20T20:16:58+08:00 Reached 00-26 e11 via the e10 corridor; the exact-story-19 trigger starts a three-beast battle. Probing natural party recovery and combat.

- 2026-11-20T20:21:25+08:00 Recovered party to 24/31/34 HP at 00-06 and returned to the story-19 battle with 22/31/34 HP.

- 2026-11-20T20:34:09+08:00 Rechecked both checkpoint hashes and decoded the return script to 00-27 e9 (7,7), including its two screen-coordinate offsets.

- 2026-11-20T20:43:09+08:00 Won the 00-26 scripted battle with joypad input, verified story 20 at (11,7), and reached the fan battle in 00-29.

- 2026-11-20T20:45:41+08:00 Won the fan battle, verified pocket 1 at D2AC, and reached story 22 at 00-2e e3 (25,5), one cell before the next trigger.

- 2026-11-20T20:48:19+08:00 Verified the consolidated official native replay (717 actions, 63131 frames), all nine checkpoint hashes and fields, and the 120-frame idle check at 00-2e e3 (25,5). Browser replay syntax checked and handed off in REQUEST_READY.md.

- 2026-11-20T21:05:07+08:00 Verified official hashes, 11 map IDs, five matching accepted plates, and one loaded layout per maze map across all official entries.
- 2026-11-20T21:12:36+08:00 Ran prepare-art.py twice and verified 11 native/4× pairs, three byte-identical style refs, five reuse hashes, seven planned requests, and the pixel-exact cave reference seam.

- 2026-11-20T21:54:13+08:00 Integrated six Region 6 plates into the verified M10 copy and checked all five reused plates.
- 2026-11-20T21:54:13+08:00 Froze 36 QA routes, 27 perf routes, 11 contact pairs and seven preview excerpts. Offline checks passed. Supervisor stages pending.
- 2026-11-20T21:55:33+08:00 Rechecked runtime and crop bytes, freeze hashes, handoff commands, and watchdog attempt matching with a socket-free fixture.

- 2026-11-20T22:04:25+08:00 M11 outer m11-region6-20261120T140423261638555Z qa. Preflight

- 2026-11-20T23:20:27+08:00 M11 outer m11-region6-20261120T140423261638555Z qa. Exit 1. Attempt /workspace/shawu/m11-work/results/m11-region6-20261120T140423261638555Z/attempts/qa-20261120T140425027899813Z-890642

- 2026-11-20T23:44:51+08:00 Reproduced QA frame 61811 natively. The flat HD transition plate overwrites black framebuffer samples selected by the staged BG dialogue.

- 2026-11-20T23:47:02+08:00 Applied the M11 flat-blackout fix, checked the target and adjacent frames natively, and verified the revised freeze and jq acceptance. Formal QA needs a fresh run ID.

- 2026-11-20T23:55:50+08:00 M11 outer m11-region6-20261120T155549527334400Z qa. Preflight

- 2026-11-21T01:39:57+08:00 M11 outer m11-region6-20261120T155549527334400Z qa. Exit 0. Attempt /workspace/shawu/m11-work/results/m11-region6-20261120T155549527334400Z/attempts/qa-20261120T155550257952370Z-930056

- 2026-11-21T01:48:04+08:00 M11 outer m11-region6-20261120T155549527334400Z perf. Preflight

- 2026-11-21T01:48:04+08:00 M11 outer m11-region6-20261120T155549527334400Z perf. Exit 69. Attempt /workspace/shawu/m11-work/results/m11-region6-20261120T155549527334400Z/attempts/perf-20261120T174804922455559Z-5577

- 2026-11-21T01:51:34+08:00 M11 outer m11-region6-20261120T155549527334400Z perf. Supervisor acknowledged prior listener stop and authorized this resume

- 2026-11-21T01:51:34+08:00 M11 outer m11-region6-20261120T155549527334400Z perf. Preflight

- 2026-11-21T02:01:14+08:00 M11 outer m11-region6-20261120T155549527334400Z perf. Exit 143. Attempt /workspace/shawu/m11-work/results/m11-region6-20261120T155549527334400Z/attempts/perf-20261120T175134166861711Z-11061

- 2026-11-22T08:36:06+08:00 M11 outer prepare (direct supervisor run). M10_PERF re-pointed to the new M10 comparison; prepare exit 0; freeze 674/674.

- 2026-11-22T11:30:51+08:00 M11 outer m11-region6-20261122T033051767758133Z qa. Preflight

- 2026-11-22T12:49:46+08:00 M11 outer m11-region6-20261122T033051767758133Z qa. Preflight

- 2026-11-22T12:49:46+08:00 M11 outer m11-region6-20261122T033051767758133Z qa. Exit 69. Attempt /workspace/shawu/m11-work/results/m11-region6-20261122T033051767758133Z/attempts/qa-20261122T044946728062154Z-2222

- 2026-11-22T12:53:16+08:00 M11 outer m11-region6-20261122T033051767758133Z qa. Supervisor acknowledged prior listener stop and authorized this resume

- 2026-11-22T12:53:50+08:00 M11 outer m11-region6-20261122T033051767758133Z qa. Preflight

- 2026-11-22 05:01 UTC QA replay has 0/36 completed routes, 41/3744 actions and 3490/217044 frames. Run m11-region6-20261122T033051767758133Z.

- 2026-11-22 05:16 UTC QA replay has 0/36 completed routes, 231/3744 actions and 17348/217044 frames. Run m11-region6-20261122T033051767758133Z.

- 2026-11-22 05:31 UTC QA replay has 0/36 completed routes, 421/3744 actions and 32584/217044 frames. Run m11-region6-20261122T033051767758133Z.

- 2026-11-22 05:46 UTC QA replay has 0/36 completed routes, 521/3744 actions and 42116/217044 frames. Run m11-region6-20261122T033051767758133Z.

- 2026-11-22 06:01 UTC QA replay has 0/36 completed routes, 621/3744 actions and 52746/217044 frames. Run m11-region6-20261122T033051767758133Z.

- 2026-11-22 06:16 UTC QA replay has 1/36 completed routes, 758/3744 actions and 64421/217044 frames. Run m11-region6-20261122T033051767758133Z.

- 2026-11-22T14:18:34+08:00 M11 outer m11-region6-20261122T033051767758133Z qa. Preflight

- 2026-11-22T14:18:36+08:00 M11 outer m11-region6-20261122T033051767758133Z qa. Exit 1. Attempt /workspace/shawu/m11-work/results/m11-region6-20261122T033051767758133Z/attempts/qa-20261122T061834119109290Z-2088

- 2026-11-22T14:19:07+08:00 M11 outer m11-region6-20261122T033051767758133Z qa. Preflight

- 2026-11-22T16:17:06+08:00 M11 outer m11-region6-20261122T033051767758133Z qa. Preflight

- 2026-11-22T17:02:45+08:00 M11 outer m11-region6-20261122T033051767758133Z qa. Exit 0. Attempt /workspace/shawu/m11-work/results/m11-region6-20261122T033051767758133Z/attempts/qa-20261122T081705995277315Z-2132

- 2026-11-22T17:02:45+08:00 M11 outer m11-region6-20261122T033051767758133Z perf. Preflight

- 2026-11-22T17:56:48+08:00 M11 outer m11-region6-20261122T033051767758133Z perf. Preflight

- m11-region6-20261122T033051767758133Z 2026-11-22T10:03:21+00:00 perf 84/324, 240 remaining.

- m11-region6-20261122T033051767758133Z 2026-11-22T10:11:21+00:00 perf 96/324, 228 remaining.

- m11-region6-20261122T033051767758133Z 2026-11-22T10:19:21+00:00 perf 108/324, 216 remaining.

- m11-region6-20261122T033051767758133Z 2026-11-22T10:27:21+00:00 perf 120/324, 204 remaining.

- m11-region6-20261122T033051767758133Z 2026-11-22T10:35:51+00:00 perf 132/324, 192 remaining.

- m11-region6-20261122T033051767758133Z 2026-11-22T10:43:52+00:00 perf 144/324, 180 remaining.

- m11-region6-20261122T033051767758133Z 2026-11-22T10:52:22+00:00 perf 156/324, 168 remaining.

- m11-region6-20261122T033051767758133Z 2026-11-22T11:00:22+00:00 perf 168/324, 156 remaining.

- m11-region6-20261122T033051767758133Z 2026-11-22T11:08:52+00:00 perf 180/324, 144 remaining.

- m11-region6-20261122T033051767758133Z 2026-11-22T11:16:52+00:00 perf 192/324, 132 remaining.

- m11-region6-20261122T033051767758133Z 2026-11-22T11:24:52+00:00 perf 204/324, 120 remaining.

- m11-region6-20261122T033051767758133Z 2026-11-22T11:32:53+00:00 perf 216/324, 108 remaining.

- m11-region6-20261122T033051767758133Z 2026-11-22T11:41:23+00:00 perf 228/324, 96 remaining.

- m11-region6-20261122T033051767758133Z 2026-11-22T11:49:53+00:00 perf 240/324, 84 remaining.

- 2026-11-22 19:56 CST — Resume 6 verified QA 36/36, freeze 674/674 and perf inventory 248/324 in m11-region6-20261122T033051767758133Z.

- 2026-11-22T19:57:23+08:00 M11 outer m11-region6-20261122T033051767758133Z perf. Preflight

- 2026-11-22T19:58:10+08:00 M11 outer m11-region6-20261122T033051767758133Z perf. Preflight

- 2026-11-22T20:19:16+08:00 — Resume 6 perf checkpoint 278/324; same run, QA complete.

- 2026-11-22T20:50:04+08:00 M11 outer m11-region6-20261122T033051767758133Z perf. Exit 0. Attempt /workspace/shawu/m11-work/results/m11-region6-20261122T033051767758133Z/attempts/perf-20261122T115810966689773Z-2443

- 2026-11-22T20:50:05+08:00 M11 outer m11-region6-20261122T033051767758133Z contact. Preflight

- 2026-11-22T20:50:09+08:00 M11 outer m11-region6-20261122T033051767758133Z contact. Exit 0. Attempt /workspace/shawu/m11-work/results/m11-region6-20261122T033051767758133Z/attempts/contact-20261122T125005414800600Z-28839

- 2026-11-22T20:50:11+08:00 M11 outer m11-region6-20261122T033051767758133Z preview. Preflight

- 2026-11-22T21:01:13+08:00 M11 outer m11-region6-20261122T033051767758133Z preview. Exit 1. Attempt /workspace/shawu/m11-work/results/m11-region6-20261122T033051767758133Z/attempts/preview-20261122T125011076759782Z-29181

- 2026-11-22 21:02 CST — Resume 6 finished perf (324/324, 54 comparisons, 0 native mismatches) and published the 11-pair contact sheet. Preview exited 1 at the Row-4 marker assertion. Verified raw SHA-256; first detected marker lasted 0.280 s for 7.9431 s of playback. Capture and marker log retained; final publication and Chinese report pending.

- 2026-11-22T21:06:35+08:00 M11 outer m11-region6-20261122T033051767758133Z preview. Preflight

- 2026-11-22T21:20:03+08:00 M11 outer m11-region6-20261122T033051767758133Z preview. Exit 0. Attempt /workspace/shawu/m11-work/results/m11-region6-20261122T033051767758133Z/attempts/preview-20261122T130635734645272Z-34746
- 2026-11-22T21:24:22+08:00 M11 resume 7 verified preview publication and completed m11-work/REPORT_region6_zh.md. Seven segments, 8146186 bytes, frame 63131, 00-2e, story 22.
