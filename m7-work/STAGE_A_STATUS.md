# Stage A v2 status

REQUEST_READY

- State: V2_FROZEN / OFFLINE_PASS / PROBE_REQUEST_READY / ACCEPTANCE_PENDING.
- V1 NOT ACCEPTED: substantive switch-tail/debt regressions vs M5.2; historical 442/31396/coverage passes do not accept v2.
- Preserved v1 runtime/freeze/scripts/all results: m7-work/stage-a/versions/v1/; preserved-sha256.json covers 244 files; original result files unchanged.
- V2 isolated runtime: m7-work/stage-a/v2/runtime/. Original m7-work/runtime and original v1 scripts/freeze preserved.
- V2 runtime diff: only region-renderer.js (certified identity rectangles; exact recovered-row mapping reuse). ROM/core/timing/input/Observer/masks/coverage/measurement definitions unchanged.
- Freeze: m7-work/stage-a/v2/freeze-sha256.json; SHA256 ff573a9166aa07527e66d80319ae735be86072f537baf276d792f5c1fee64eed.
- Offline evidence: v2/offline/checks.json (364 frozen files + 244 v1 preserved files; 9 pixel cases/13271040 bytes; 80 palette sequences/3 rejection cases).
- Native structural oracle: v2/offline/native-structure.json, 2110 actual WASM frames with identical source/row palettes/metadata. Rendering omitted: not Chromium/perf acceptance.
- V1 raw analysis: v2/offline/v1-analysis.json.
- Chinese candidate report: m7-work/stage-a/v2/REPORT_STAGE_A_V2_zh.md.
- Exact outer commands: m7-work/SUPERVISOR_RUN_STAGE_A_V2.md. First run bash m7-work/stage-a/v2/scripts/run.sh probe using documented fresh STAGE_A_RESULTS and exclusive environment. 12 samples, ~6+ minutes.
- Optional diagnostic mode adds broad method attribution/CPU profile; NEVER acceptance perf. Full mode retains 442/31396/72 checks and all original measurement definitions, no post-hoc tolerance.
- V2 browser QA/perf not yet run; measurable improvement unproven. Full acceptance still requires 442/442, exact visuals/coverage, region regressions, complete exclusive 72-sample comparison with all failures disclosed.
- Sandbox socket EPERM known; no new socket/browser attempts. Supervisor confirms proxy 38811 and server 8765. Outer script checks proxy and records blocker/stops on failure; no auth/route changes.
- All code by current Codex. No nested Codex, M8, art, ZIP or video. Stage B only after explicit supervisor acceptance.

V2_probe_EXIT_2: /workspace/shawu/m7-work/stage-a/v2/results/probe-supervised; inspect reports; acceptance remains pending.

## Supervisor 2026-11-11 13:34 CST
- V2_PROBE_REJECTED / FULL_ACCEPTANCE_NOT_STARTED / V3_ITERATION_REQUESTED.
- Probe exit 2 at m7-work/stage-a/v2/results/probe-supervised/. Clean cold v2 r2 switchFrameMax 30.9ms vs M5.2 11.6/12.2ms. See SUPERVISOR_PROBE_ANALYSIS.md.
- Historical v1/v2 evidence must stay frozen. Next coding is isolated v3 by Codex.

## Current Stage A v3 — 2026-11-11

REQUEST_READY

- State: V3_FROZEN / OFFLINE_PASS / PROBE_PENDING / ACCEPTANCE_PENDING. V1 and V2 REJECTED; full v2 intentionally not started. M8/Stage B not started.
- Isolated v3: m7-work/stage-a/v3/runtime|scripts|offline|results. Runtime changes only region-renderer.js; ROM/core/Observer/timing/input/masks/coverage/native evidence code unchanged.
- Complete v2 preserved BEFORE edits: stage-a/versions/v2/, 132 SHA256 entries, ALL results/probe/raw/supervisor analysis included. Original v2 and original m7-work/runtime untouched. V1 244-file preservation and original history rechecked.
- V3 changes: reusable typed-array identity rectangles; exact 32-color numeric-hash cache with full collision verification; contiguous certified-run LUT texel traversal. No proof yet of Chromium tail improvement.
- Freeze: stage-a/v3/freeze-sha256.json, SHA256 49d5840720f3174f78556441b7c0f6aeef02b8ca62bc54374be2199937120cf7 (546 files).
- Offline pass: 16 RGBA cases / 23592960 bytes; 80 palette sequences / 3 evidence rejection cases / collision exact check; 14584 actual native frames with identical sources/palettes/metadata; 80 native-selected synthetic-art paint cases / 117964800 bytes. NOT Chromium/performance acceptance.
- Evidence/report: stage-a/v3/offline/checks.json, probe-analysis.json, native-structure.json, runtime.diff; stage-a/v3/REPORT_STAGE_A_V3_zh.md.
- New exact outer command doc: m7-work/SUPERVISOR_RUN_STAGE_A_V3.md. Run documented fresh-directory 12-sample probe FIRST; full 442/31396/72 only if probe warrants. perf/qa/visual byte-identical to v2, no measure/window/denominator/tolerance changes. All failures retained.
- Known sandbox socket EPERM: no retry/browser/network/install. Keep 8765 root service; outer scripts check 38811, record BLOCKER and stop on drop. No auth/route changes or nested Codex.

V3_probe_EXIT_2: /workspace/shawu/m7-work/stage-a/v3/results/probe-20261111T055247Z; inspect reports; acceptance remains pending.

V3_full_EXIT_2: /workspace/shawu/m7-work/stage-a/v3/results/full-20261111T060217Z; inspect reports; acceptance remains pending.

## Current Stage A v4 — 2026-11-11T07:58:11.141431+00:00

REQUEST_READY

- V4_FROZEN / OFFLINE_PASS / OUTER_PROBE_PENDING / ACCEPTANCE_PENDING. Final bounded Stage A iteration; v3 NOT ACCEPTED. M8 not started.
- Preserved complete v3 before edits: stage-a/versions/v3/, 270 SHA256 entries including all probe/full/72 raw/runtime/scripts/freeze/offline. Original v1/v2/v3 and m7-work/runtime unchanged.
- V4 only changes Region camera candidate preparation: immutable-snapshot cells reuse, stable top8 anchors, mathematically impossible-origin early rejection. V3 paint/recover/history/startup/coverage unchanged. No ROM/core/timing/input/Observer/masks/assets changes or core pre-running.
- Freeze: stage-a/v4/freeze-sha256.json; SHA256 d6553eb1c50fcefb655a38270d55557c72d4a13569602f5b43faeb1683f1b84d, 638 files.
- Offline pass: 65341 threshold cases, 1083 score cases, 128 anchor cases; 16 RGBA cases/23592960 bytes; 29168 native frames across forced/flat-gated Region schedules; 157 native-selected synthetic-art paint cases/231505920 bytes. NOT browser/performance acceptance.
- Path correction: actual flat gate skips Region; frame497 then does 21 locate/257 agreement and falls back. Old always-Region structural palette work does not describe that outer path. Remaining fallback/Canvas/runtime costs not fully attributed.
- New commands: m7-work/SUPERVISOR_RUN_STAGE_A_V4.md; report: stage-a/v4/REPORT_STAGE_A_V4_zh.md. First 18-sample SAME measure probe including existing legacy00-17; M5.2/v3/v4 x2. Then complete442/31396/72 with M5.2/pre-fix M7/v4. Full m7 is NOT v1.
- QA/visual/perf and frozen routes unchanged; all strict failures/noise remain. Comparison thresholds/exit2/acceptanceReady unchanged. Only supervisor may explicitly accept NEAR-PARITY after full evidence and disclosed small (~<=20ms) residuals with FPS/debt parity; no automatic v5 or M8.
- Known socket EPERM: no browser/network/install retries or credential/config reads. Keep existing38811/8765; outer proxy failure writes BLOCKER/stops. No concurrent profiler/code with QA; local CPU checks used exclusive.lock and finished. No ZIP/art/video.

## Supervisor Step 1 decision — 2026-11-11 02:58:47 EST
- 已复核v3完整证据full-20261111T060217Z；原PID680299早已自然完成，EXIT_2，不重跑。442/442 state SHA、native framebuffer SHA、人物文字全通过；31396/31396帧HD RGBA和逐帧coverage零差异；438411621/439578861=99.73446403%，分母/原因不变，无页面错误。
- 严格失败是性能配对回退，不是玩法/画面正确性失败。重点三次均值（ms，v3 vs同期M5.2）：legacy00-12 maxDebt27.058vs65.326；frame p95/max4.300/38.767vs9.867/61.567；switch max14.033vs13.333。legacy00-17 maxDebt35.293vs93.861；frame p95/max4.433/49.233vs8.933/105.700；switch p95/max6.133/21.467vs8.633/12.600，switch max范围17.9–24.5vs10.6–15.7。cold00-17 maxDebt33.054vs93.409；frame p95/max5.967/53.433vs13.100/67.967；switch p95/max5.933/16.933vs10.567/13.800，max差3.133ms（22.7%）。
- 官方被拒v1旧轮：legacy00-12 maxDebt163.504vsM5.2 40.243；cold00-17 switch max31.000vs13.067。不同轮机器噪声不可当严格配对。v3整体FPS与债务已恢复，最关键cold尾改善，但legacy00-17 switch max仍+8.867ms（70.4%），三次都高于基线，超过“约10%/几ms”近似持平标准，故V3_REJECTED_PERF_TAIL，不冒充near-parity接受。
- 一次有界v4已由同一Codex完成代码与离线检查，REQUEST_READY；freeze SHA256 d6553eb1c50fcefb655a38270d55557c72d4a13569602f5b43faeb1683f1b84d（638文件）。只优化camera候选准备，不改ROM/core/画面/coverage/测量；尚无外层浏览器验收，不能接受v4。命令SUPERVISOR_RUN_STAGE_A_V4.md（18样本probe→442/31396/72 full）；不再自动v5。
- 38811/8765正常；检查仍有Codex PID770379收尾，未启动重复任务。M8未启动、未产生第三片地图/图片/录像。按本次“step1决定后立即返回”要求，先交回监督结论，不继续长测或跳过Stage A门禁。

- 2026-11-11 03:00:05 EST：Codex v4已自然退出，末条报告codex-stage-a-v4-last.txt；当前无Codex/QA任务在跑。未启动probe/full；可按V4命令文档续接。

## Supervisor v4 browser acceptance resumed — 2026-11-11 03:00:36 EST
- 代理/HTTP正常，Codex已退出、没有既有QA。依照上级新裁决标准：全部正确性必过；所有switch max距M5.2约3ms以内可接受，否则不迭代，比较v3/v4总体并披露残差择优采用，再进M8。严格脚本阈值/证据不改。
- 启动18样本独占probe，目录：/workspace/shawu/m7-work/stage-a/v4/results/probe-20261111T080036Z。

V4_probe_EXIT_2: /workspace/shawu/m7-work/stage-a/v4/results/probe-20261111T080036Z; inspect reports; acceptance remains pending.

## V4 probe finished / full starts — 2026-11-11 03:14:40 EST
- 18样本自然完成，EXIT_2；结果stage-a/v4/results/probe-20261111T080036Z/probe/。同期cold00-17 switch max v4 17.6/15.9ms，v3 17.8/20.9，M5.2 16.4/11.8；legacy00-17 v4 18.7/15.3，v3 16.2/16.5，M5.2 17.7/12.7。仍有噪声/债务回退，全部原样保留。
- 无正确性异常证据；有改善且值得完整验收，依照新裁决政策跑442/31396/72，不追加代码迭代。新full目录：/workspace/shawu/m7-work/stage-a/v4/results/full-20261111T081440Z。

- 2026-11-11 03:33:38 EST：v4完整442/442三项正确性和31396帧HD/coverage零差异全部通过，原任务转入72独占性能样本。不据此提前宣称性能通过，不启动M8。

- 2026-11-11 03:50:46 EST：再次接续确认v4 full仍是原PID804949，perf子PID813640，已落盘22/72 raw（加progress共23json）；未重复启动、未并行任务。38811/8765正常；继续等同一任务完成。新交接终点为StageA决定落盘并nohup启动M8 Codex后立即返回，不等M8预览。

V4_full_EXIT_2: /workspace/shawu/m7-work/stage-a/v4/results/full-20261111T081440Z; inspect reports; acceptance remains pending.

## STAGE_A_FINAL: ADOPT_V3_WITH_DISCLOSED_SWITCH_RESIDUAL — 2026-11-11 04:24:17 EST
- v4原PID804949/813640已自然退出，72样本完成、EXIT_2；442/31396/coverage完全相同。
- 按已授权不再迭代策略，v4并非所有switch max均在M5.2约3ms：legacy00-12 43.000vs34.267（+8.733，含91.9ms样本）。内城典型切图有改善，但cold00-17/r1出现46.829fps/15779.698ms欠债（max单帧67ms），原因未证实，未剔除。
- 综合稳定性择优采用已完整验收的v3冻结runtime，明确接受为“带残差继续”，不是严格全绿；无v5。v3 legacy内城switch max21.467vs12.600（+8.867），cold内城16.933vs13.800（+3.133）；FPS约59.7，debt/p95显著改善。详见STAGE_A_FINAL_DECISION_zh.md。
- 最终采用目录m7-work/stage-a/v3/runtime/。授权M8在此隔离复制后自然继续介绍信→醉仙楼→东溪村，人物/ROM/core/时钟不改。

- 2026-11-11 04:24:32 EST：StageA裁决已落盘，M8 Codex已nohup启动，PID869057/session01a1c9ec-3f2e-78f3-aa1a-62349c57cf11；日志m8-work/codex-m8-region3.log。依最新要求此处返回，不等待M8完成。
