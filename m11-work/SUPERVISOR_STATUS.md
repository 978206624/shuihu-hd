# M11 SUPERVISOR_STATUS (region 6)
Updated: 2026-11-21T02:02+08:00 Asia/Shanghai

## Stage: PAUSED by user (GitHub upload requested); perf stopped mid-run
## USER PAUSED — 2026-11-21T02:00+08:00 Asia/Shanghai
- User asked to stop and push the project to their GitHub.
- Stopped watchdog PID 11718 and perf runner PID 11061 (and children). QA results remain on disk (qa.done). Perf was incomplete (~13/324 when last checked).
- Do not resume region 6 work unless the user asks again.

## Stage: 10 — perf running with watch-resume (then contact + preview by watchdog)
- Parent: 38811 back (cockpit-tools PID 8143). Old watchdog 5705 was dead. Perf resumed same RUN_ID with M11_RESUME_AFTER_PORT_STOP=1: runner PID 11061. Watchdog PID 11718 (m11-work/outer-runs/m11-region6-watch-resume.{status.json,log}). 324 samples (~3h). Do not relaunch while these live.
- Next: when watchdog phase=complete → jq checks → publish contact (ln to shots/m11_region6_contact.png) → Codex report (prompt CODEX_M11_REPORT_PROMPT.txt).

## Stage 9 (history) — QA PASSED; perf BLOCKED by box reset (38811 down, needs GUI account switch)
- QA rerun m11-region6-20261120T155549527334400Z PASSED (qa.done, exit 0, REQUEST_READY jq checks true): 36 routes, 3744 actions, 217044 frames; state/native/actorText 217044/217044; earlier visual 183754/183759 + 5 baselineKnownDefectFrames (M10 transition-plate defect, documented); addedPlateTransitionFrames 41; evidencePassed 354; contacts 11.
- Coverage weighted 583603685/894844585 = 65.2184% (main residual: legacy map renderer uncertified native background 259,922,906). Per map: 00-2a 87.18, 00-0b 47.92, 00-09 73.22, 00-00 87.03, 00-06 94.32, 00-25 81.95, 00-26 60.48, 00-27 70.95, 00-28 77.79, 00-29 46.23, 00-2e 79.57 (%).
- ~01:41 BOX RESET (uptime 7 min at 01:48). Perf launched 01:48 (PID 5577) exited 69 at preflight: 38811 refused → zero samples taken. Watchdog (PID 5705) phase=blocked.
- Recovery done: reinstall.sh OK (cockpit-tools 1.3.81), http.server 8765 restarted (HTTP 200), cockpit-tools started DISPLAY=:6 PID 8143 (do NOT start another). 38811 still not listening → needs GUI switch to 「Cockpit 网关」 (▶ then 切换).
- After 38811 is up: relaunch perf with same RUN_ID using M11_RESUME_AFTER_PORT_STOP=1 (REQUEST_READY "Interrupted stages"), then the watch-resume wrapper (it continues contact + preview), then Codex report.

## Stage 8 (history) — formal QA rerun (fresh RUN_ID after fix round)
- Fix round DONE 23:47 (integration/qa-fix-diagnosis.md): flat HD transition plate (intertitle_hd.png) covered a native full-black frame whose BG already held dialogue tiles; M11 renderer now preserves full native blackout. Known M10 baseline defect frames counted separately; candidate invariants unchanged. Fix round is now USED (no more fix rounds).
- QA rerun RUN_ID m11-region6-20261120T155549527334400Z (logs/RUN_ID.txt; failed run in logs/RUN_ID.failed1.txt), runner PID 930056, launched 23:56.

## Stage 7b (history) — QA failed once → fix
- 23:4x QA run m11-region6-20261120T140423261638555Z exited 1 at official-region6/705/83 (00-2a story 21 bank 10, dialogue in story-22 exit staging). 61810 frames passed all invariants before that. Mismatch: textHD != textNative on BOTH M11 and live M10 baseline (identical hashes both sides) → inherited M10 HD text path defect in a scene M10 never reached; not an M11 divergence. Old run kept as failed evidence.
- QA-fix Codex: PID 922657, session 01a1f9a0-36af-7391-baa4-196cb050b64a, prompt CODEX_M11_QA_FIX_PROMPT.txt, log logs/codex-m11-qafix.log. This uses the ONE bounded fix round. After fix: fresh RUN_ID, rerun QA.

## Stage 7 (history) — formal QA running
- Integrate run DONE 21:55: runtime m11-work/runtime/ (44 maps), 00-25 cropped [9,1,849,1401] → 840×1400 no resampling, other 5 byte-for-byte; plan 36 QA routes (3744 actions/217044 frames), 324 perf samples, 11 contact pairs, 7 preview excerpts. Runbook m11-work/REQUEST_READY.md.
- RUN_ID m11-region6-20261120T140423261638555Z (also in logs/RUN_ID.txt). R=m11-work/results/$RUN_ID. QA launched 22:04, runner PID 890642 ($R/qa.launch.pid). Resume = same RUN_ID same command.
- 23:18 checkpoint: QA still running (same PID 890642), official-region6 route at ~55k/63131 frames (~550-900 frames/min; 217044 total → expect several more hours). Do not relaunch.
- Next: QA checks → perf + watch-resume wrapper (wrapper also does contact+preview) → publish contact → REPORT_region6_zh.md (via Codex).

## Stage 6 (history) — integration
- 21:36 parent: plate sheet sent to user; proceed with integration → QA → coverage → perf (auto-resume) → contact → preview → REPORT_region6_zh.md. If the user asks for a redraw, parent will notify.
- Integrate run: PID 884084, session 01a1f92d-15d5-7e83-aee2-4cc99157eb96, prompt CODEX_M11_INTEGRATE_PROMPT.txt, log logs/codex-m11-integrate.log, last logs/codex-m11-integrate-last.txt. 00-25 must be cropped to x<858 (no stretch).

## Stage 5 (history) — plate sheet
- All 6 new plates SAVED (gpt-image-2 medium; 00-29 and 00-2e needed 1 retry after 504). Gateway ignores requested size (returns ~1.57MP at its own ratio), same as M9/M10:
  00-25 1122x1402 (painted area x[0,858) + pure-black pad on the right; aspect 0.612 vs native 0.600 -> integration must crop x<858, do NOT stretch the pad), 00-26 1254x1254, 00-27 1254x1254, 00-28 1254x1254, 00-29 1374x1145, 00-2e 1254x1254 (single full plate succeeded; strip fallback NOT used).
- Supervisor review vs native 4x: layout faithful; maze hedges in 00-27/00-28 slightly simplified (coverage QA will quantify); 00-25 ground painted as pale paving vs native white.
- Plate sheet: shots/m11_region6_gpt_plates.jpg (1760x1260, SHA-256 9ebe8729e2b84b524ac299c816f893ac7fbf6c5fea1cdd42b3e3e19eb59e908b; 00-25 shown cropped to painted area, display only).
- Next on resume: Codex integrate into isolated m11-work/runtime/ (from m10 runtime copy; do not modify m8/m9/m10 runtimes) incl. reused plates 00-2a,00-0b (M10), 00-09,00-00,00-06 (M8); then QA, coverage, perf w/ auto-resume wrapper in outer-runs/, contact sheet, preview webm, REPORT_region6_zh.md.

## Stage 4 (history) — GPT plates generating
- Scope run DONE (~21:30): region6-scope.json, art/batch-manifest.json. Reused: 00-2a(M10), 00-0b(M10), 00-09(M8), 00-00(M8), 00-06(M8 v2). New: 00-25 云中塔门 768x1280 town_style; 00-26 回廊迷宫 1536x1536; 00-27 云台迷宫 1536x1536; 00-28 云台回廊 1024x1024; 00-29 双像殿 960x800; 00-2e 石洞 (room_style).
- Supervisor decision: 00-2e try ONE full plate 1920x1920 first (art/00-2e_prompt.txt, derived from Codex strip prompt) to avoid seams; Codex north/south strip prompts kept as fallback only if the gateway rejects the size.
- Jobs: outer-runs/gpt-plates/run-plate.sh (skips existing outputs => safe to rerun). PIDs/logs in outer-runs/gpt-plates/<id>.pid/.log. Started ~21:37.
- Next: review plates, build shots/m11_region6_gpt_plates.jpg, return to parent (stop point).

## Stage 3 (history) — scope + art prep
- Scope run: PID 868901, session 01a1f90b-c70b-7063-8edd-9ea832847445, prompt CODEX_M11_SCOPE_ART_PROMPT.txt, log logs/codex-m11-scope-art.log.
- Browser replay region6-official PASSED: status COMPLETE, errors [], 717 actions / 63131 frames, source SHA c41b4188…, end 00-2e e3 (25,5) facing 2, story 22, bank 5 mode 0 dialogue 0 settled, DAA e6 52 3e 30, D2AC 10 01, D284 00 00, party 02/17/24, hp 0/13/34. Evidence m11-work/play/region6-official/.

## Stage 2 (history) — official browser replay
- 20:48 Codex explore run2 DONE (exited). Native official chain 717 actions / 63131 frames from story19-00-2a-official.bin. New maps: 00-25, 00-26, 00-27, 00-28, 00-29, 00-2e. Endpoint 00-2e e3 (25,5) facing left, story 22, 伏魔扇 obtained; next step left (24,5) writes story 23. region6-end-native.bin f8e87d6a…
- Browser replay tag region6-official, log logs/browser-play-official.log.

## Stage 1 (history) — exploration
- 20:01 parent: Cockpit switched to 「Cockpit 网关」, 38811 listening (cockpit-tools PID 841436; do NOT start a second one). Root path 404 is normal.
- Account switch rewrote ~/.codex/config.toml to gpt-6.1-sol/effort none. Run1 (PID 845780, session 01a1f8d7…) stopped. Run2 launched with `-m gpt-6.2-sol -c model_reasoning_effort="high"` (M10 parity): PID 846703, session 01a1f8d8-0a22-78f0-94b2-562ab1627660, prompt CODEX_M11_EXPLORE_PROMPT.txt, log logs/codex-m11-explore.log, last msg logs/codex-m11-explore-last.txt.
- Official start for region 6: checkpoints/story19-00-2a-official.bin (c41b4188…). Native start: checkpoints/story19-00-2a.bin (e43f73af…).
- Launch form: (nohup codex -a never exec --skip-git-repo-check -m gpt-6.2-sol -c model_reasoning_effort='"high"' -s workspace-write -C /workspace/shawu -o <last> - < <prompt> > <log> 2>&1 &)

## Stage 0 (history)
- web server 8765: OK (python3 http.server PID 8081, HTTP 200).
- Cockpit Tools 1.3.81 installed (no reinstall needed), but process was not running. Supervisor started it:
  `DISPLAY=:6 WEBKIT_DISABLE_DMABUF_RENDERER=1 nohup cockpit-tools` -> PID 841436, log m11-work/logs/cockpit-tools.log.
- Cockpit gateway sidecar 127.0.0.1:38811: NOT listening (curl 000). Sidecar only starts after the GUI account switch to "Cockpit 网关" (▶ then 切换). Supervisor has no desktop tool -> waiting for parent/user.
- GPT image gateway (~/.config/gpt-image/api.env): reachable (unauthenticated probe 401 = up).
- No Codex session started yet. No m11 work beyond logs/ and this file.

## Start point
m10-work/checkpoints/story19-00-2a.bin (SHA e43f73af…), 00-2a e0 (5,8), story 19. Do not walk 00-2a row 4.

## Next (after 38811 is up)
1. Fresh Codex session: native PyBoy exploration from the checkpoint, then one consolidated official browser replay.
2. Region 6 scope json. 3. GPT plates + shots/m11_region6_gpt_plates.jpg -> return to parent.

- 2026-11-20T20:48:19+08:00 Region 6 native replay complete (717 actions, 63131 frames) at 00-2e e3 (25,5), story 22. Browser replay pending via REQUEST_READY.md.

- 2026-11-20T21:12:36+08:00 Region 6 art prep verified in region6-scope.json and art/batch-manifest.json: 11 maps, five accepted reuses, six new plates planned across seven requests.

- 2026-11-20T21:54:13+08:00 M11 runtime integration and offline freeze checks passed. Supervisor QA, perf, contact and preview commands are in REQUEST_READY.md.
