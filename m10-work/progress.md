# M10 / region 5 progress

- Supervisor only. All coding by fresh Codex sessions via Cockpit (38811). Helper scripts stay under m10-work/. Do not modify m8-work/runtime/ or m9-work/runtime/. If 38811 drops, stop and report.
- Official start: m10-work/checkpoints/story14-inn-end.bin (byte-identical to official region-4 evidence action-0261.bin). SHA-256 f389cebc3fc59a310571c66538d38808c32483c7632164f35d207f0738e8d6c0. 00-2c, story 14, DAA1=0x72, DAA2=0x01.
- 2026-11-18T19:32:28-05:00 Created m10-work tree. Native inspect of the official start succeeded (00-2c story 14). Starting door surveys and a Codex ROM-gate session for post-inn story 15+.

- M10 static ROM analysis verified the official checkpoint hash and identified the post-inn actor at `00-23 (12,6)`. Its script checks actor visibility through `DAA2.0` and writes stories 15 and 16 consecutively. Exit collision, cutscene transitions, and the next settled boundary are under review.

- 2026-11-18T19:36:39-05:00 Official-start door surveys finished for 00-2c/2b/24/21/1f/20/22/0a/0b/2d (story still 14). New maps: 00-0a, 00-0b, 00-2d (sign), 00-20, 00-22 (NPC). 00-21 first pass hit 1800-node cap with frontier 1; follow-up story14-doors-00-21-full launched. Codex ROM-gate still running.

- 2026-11-18T19:38:29-05:00 00-21-full complete (no 00-23). 00-2c 惠农 is flavor. 00-22 chest: 金翅鸟羽. 00-2d 山门 gatekeeper blocks passage to 桃花会 unless the party has 伏魔扇; story still 14. Searching for that item. Codex ROM-gate still running.

- Static ROM-gate analysis complete. `00-21` west `(0,5..6)` has an unconditional crossing to `00-23`. The actor enabled by `DAA2.0` settles at story 16 and gifts beast `17`. Capturing beast `24` in western `00-23`, returning through `酒`, and clearing the fruit game leads to story 19 and pocket-2 item `04`. Recommended endpoint is settled `00-2a e0 (5,8)`, with item intact before the row-4 gate. The later fan-related branch checks `DAA2.5`, which the story-21 reward sets. Directed native checks and the continuous browser replay are pending on the supervisor host. [ROM analysis](rom-gate-analysis.md) · [Outer request](REQUEST_READY.md)

- Static follow-up decoded the player movement lists after the story-16, story-18 and story-19 scenes. Predicted settled cells are `(13,7)`, `(8,3)` and `(6,5)` respectively. The analysis and host request use these cells for the subsequent walking legs. The archived surveys show battle interruptions on the west approach at `00-21 (3,5)` and on the eastern route at `00-0b (23,18)`.

- 2026-11-18T19:52:41-05:00 ROM-gate written (Codex finished). Official-start native walk reached 00-23. Story 15→16 verified: checkpoints/story16-00-23.bin SHA-256 691b3a54177863ba5593faae560562e412bcdf57119f09e1965f1875a348cecd, FFBA=16, DAA e6 72 00 38, beast 17 in D216. West-zone hunts in progress; 24 not confirmed captured yet. Command menu documented (攻击/神兽/道具/逃跑).

- 2026-11-18T19:58:20-05:00 Capture item confirmed in battle bag: 安魂符 x01. Group-07 zone is x<8,y<4 (docs had axes swapped). 36 SW-zone encounters were all group 6; hunting NW next.

- 2026-11-18T20:03:20-05:00 Captured Lv9 狼子 (id 24) with 安魂符 after weakening to 7 HP in the real group-07 box x<8,y<4. Checkpoint story16-captured-24.bin SHA-256 7d3744daf667b2c9119079c2e5f0bbaa692f6ebc0ef910353346c8c0d4af6706. Party 02/17/24. Heading back to 酒 for story 17.

- 2026-11-18T20:06:40-05:00 Capture checkpoint frozen. Return walk reached 00-23 (9,7). Flee can fail; a subsequent fight hit GAME OVER (discard that tree). Retry flee from story16-row7-flee2/s-12-w.bin or from s-07-r.bin, then 酒.

- 2026-11-18T20:08:45-05:00 Story 17 verified at 酒: checkpoints/story17-inn.bin SHA-256 becce6a4413a47653e572244d7678cfd8945425dcdfcbb21dfca546dfc2aa807, 00-2c e1 (6,3), FFBA=17, DAA e6 72 00 38, party 02/17/24. Next: fruit game ≥35.

- 2026-11-18T20:11:50-05:00 Story 17 frozen. Fruit game reached: start saved as checkpoints/story17-fruit-start.bin. Best score 32/35 in native/story17-fruit-play2 (time expired). Need one more successful run (>=35) then story 18 / 19 / 00-2a.

- 2026-11-18T20:23:10-05:00 Fruit 51, story 18/19 frozen (52/02 then 52/06, D284=04 01). Arrived 00-0b e2 (26,1). Last clean field 00-0b (27,13)=native/story19-00-0b-north2/s-12-d.bin. Do not use 00-1c leftovers. Next: official flee, then north to 00-2a (5,8).

- 2026-11-18T20:25:00-05:00 Native endpoint frozen: checkpoints/story19-00-2a.bin SHA-256 e43f73af9425aa7268caedca3c8779ce5f2ea447d892b0f43a0bf27e02501515. Settled 00-2a e0 (5,8), story 19, DAA 52/06, D284=04 01, party 02/17/24. Next: one official-start browser replay, then scope/plates/runtime/QA/deliverables.

- Region 5 scope and art inputs verified against the accepted replay through frame 55206, ending at `00-2a e0 (5,8)` before the row-4 item trigger. All eight maps have native and 4× nearest-neighbor PNGs. Geometry and native size match the accepted M9 plates for `00-21`, `00-24`, `00-2b` and `00-2c`. The four new plates are `PREPARED_NOT_GENERATED`. [Scope](region5-scope.json) · [Batch manifest](art/batch-manifest.json)

- Region 5 integration and offline checks complete. The isolated M10 runtime has 38 registrations and four byte-identical accepted PNGs. The copied ROM, binjgb core, launchers, and prior plate bytes match M9. Offline replay confirmed the story-19 endpoint and avoided row 4. The M9 official replay, 33 historical routes, and both perf warmup modes passed native checks. Contact and preview passed synthetic fixture checks. The supervisor runner acquires all four workflow locks, and its freeze is verified. Host listener checks, live browser runs, and media publication are pending. [Supervisor commands](REQUEST_READY.md) · [Integration manifest](integration/provenance.json)

- 2026-11-19T10:13:41+08:00 M10 outer m10-region5-20261119T021341364667010Z qa. Preflight

- 2026-11-19T11:11:40+08:00 M10 outer m10-region5-20261119T021341364667010Z qa. Exit 1. Attempt /workspace/shawu/m10-work/results/m10-region5-20261119T021341364667010Z/attempts/qa-20261119T021341378886832Z-603874

- 2026-11-19T11:16:51+08:00 M10 outer m10-region5-20261119T021341364667010Z qa. Preflight

- 2026-11-19T11:54:39+08:00 M10 outer m10-region5-20261119T021341364667010Z qa. Exit 0. Attempt /workspace/shawu/m10-work/results/m10-region5-20261119T021341364667010Z/attempts/qa-20261119T031651399063416Z-634830

- 2026-11-19T11:56:06+08:00 M10 outer m10-region5-20261119T021341364667010Z perf. Preflight

- 2026-11-19T12:10:50+08:00 M10 outer m10-region5-20261119T021341364667010Z perf. Exit 1. Attempt /workspace/shawu/m10-work/results/m10-region5-20261119T021341364667010Z/attempts/perf-20261119T035606179712561Z-658708

- 2026-11-19T12:16:59+08:00 M10 outer m10-region5-20261119T021341364667010Z perf. Preflight

- 2026-11-19T12:32:40+08:00 M10 outer m10-region5-20261119T021341364667010Z perf. Exit 1. Attempt /workspace/shawu/m10-work/results/m10-region5-20261119T021341364667010Z/attempts/perf-20261119T041659443899020Z-670895

- 2026-11-19T12:36:11+08:00 M10 outer m10-region5-20261119T021341364667010Z perf. Preflight

- 2026-11-19T13:29:37+08:00 M10 outer m10-region5-20261119T021341364667010Z perf. Exit 1. Attempt /workspace/shawu/m10-work/results/m10-region5-20261119T021341364667010Z/attempts/perf-20261119T043611589292372Z-682129

- 2026-11-19T13:29:50+08:00 M10 outer m10-region5-20261119T021341364667010Z perf. Preflight

- 2026-11-19T13:49:07+08:00 M10 outer m10-region5-20261119T021341364667010Z perf. Exit 1. Attempt /workspace/shawu/m10-work/results/m10-region5-20261119T021341364667010Z/attempts/perf-20261119T052950272889284Z-713763

- 2026-11-19T13:49:19+08:00 M10 outer m10-region5-20261119T021341364667010Z perf. Preflight

- 2026-11-19T14:09:27+08:00 M10 outer m10-region5-20261119T021341364667010Z perf. Exit 1. Attempt /workspace/shawu/m10-work/results/m10-region5-20261119T021341364667010Z/attempts/perf-20261119T054919241505351Z-725197

- 2026-11-19T14:09:40+08:00 M10 outer m10-region5-20261119T021341364667010Z perf. Preflight

- 2026-11-19T14:26:27+08:00 M10 outer m10-region5-20261119T021341364667010Z perf. Exit 1. Attempt /workspace/shawu/m10-work/results/m10-region5-20261119T021341364667010Z/attempts/perf-20261119T060940571102968Z-739339

- 2026-11-19T14:26:40+08:00 M10 outer m10-region5-20261119T021341364667010Z perf. Preflight

- 2026-11-19T14:42:35+08:00 M10 outer m10-region5-20261119T021341364667010Z perf. Exit 1. Attempt /workspace/shawu/m10-work/results/m10-region5-20261119T021341364667010Z/attempts/perf-20261119T062640013945398Z-749698

- 2026-11-19T14:42:48+08:00 M10 outer m10-region5-20261119T021341364667010Z perf. Preflight

- 2026-11-19T14:58:08+08:00 M10 outer m10-region5-20261119T021341364667010Z perf. Exit 1. Attempt /workspace/shawu/m10-work/results/m10-region5-20261119T021341364667010Z/attempts/perf-20261119T064248815483826Z-759991

- 2026-11-19T14:58:21+08:00 M10 outer m10-region5-20261119T021341364667010Z perf. Preflight

- 2026-11-19T15:05:52+08:00 M10 outer m10-region5-20261119T021341364667010Z perf. Exit 1. Attempt /workspace/shawu/m10-work/results/m10-region5-20261119T021341364667010Z/attempts/perf-20261119T065821510014079Z-770120

- 2026-11-19T15:06:05+08:00 M10 outer m10-region5-20261119T021341364667010Z perf. Preflight

- 2026-11-19T15:15:08+08:00 M10 outer m10-region5-20261119T021341364667010Z perf. Exit 1. Attempt /workspace/shawu/m10-work/results/m10-region5-20261119T021341364667010Z/attempts/perf-20261119T070605428014805Z-775233

- 2026-11-19T15:15:21+08:00 M10 outer m10-region5-20261119T021341364667010Z perf. Preflight

- 2026-11-19T15:26:53+08:00 M10 outer m10-region5-20261119T021341364667010Z perf. Exit 0. Attempt /workspace/shawu/m10-work/results/m10-region5-20261119T021341364667010Z/attempts/perf-20261119T071521835356561Z-780691

- 2026-11-19T15:26:59+08:00 M10 outer m10-region5-20261119T021341364667010Z contact. Preflight

- 2026-11-19T15:27:00+08:00 M10 outer m10-region5-20261119T021341364667010Z contact. Exit 0. Attempt /workspace/shawu/m10-work/results/m10-region5-20261119T021341364667010Z/attempts/contact-20261119T072658994022128Z-789071

- 2026-11-19T15:27:12+08:00 M10 outer m10-region5-20261119T021341364667010Z preview. Preflight

- 2026-11-19T15:31:41+08:00 M10 outer m10-region5-20261119T021341364667010Z preview. Exit 1. Attempt /workspace/shawu/m10-work/results/m10-region5-20261119T021341364667010Z/attempts/preview-20261119T072712676867394Z-789468

- 2026-11-19T15:41:16+08:00 M10 outer m10-region5-20261119T021341364667010Z preview. Exit 65. Attempt /workspace/shawu/m10-work/results/m10-region5-20261119T021341364667010Z/attempts/preview-20261119T074116556485259Z-798542

- 2026-11-19T15:42:15+08:00 M10 outer m10-region5-20261119T021341364667010Z preview. Preflight

- 2026-11-19T15:42:54+08:00 M10 outer m10-region5-20261119T021341364667010Z preview. Exit 0. Attempt /workspace/shawu/m10-work/results/m10-region5-20261119T021341364667010Z/attempts/preview-20261119T074215436764291Z-799146
