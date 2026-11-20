# M10 Region 5 supervisor handoff

The isolated runtime is ready at `http://127.0.0.1:8765/m10-work/runtime/`. The registry contains 38 maps. Four accepted Region 5 PNGs are installed byte for byte, and the four reused plates retain the accepted M9 bytes. The runtime includes `start.bat` and the frozen ROM and binjgb core. Live QA, timings, captures, and playback are pending. [Integration manifest](integration/provenance.json) · [Run plan](integration/outer-plan.json) · [Frozen byte inventory](integration/outer-freeze.json)

## Set up the run

Run on the supervisor host. Port 8765 already serves `/workspace/shawu`. Check the process inventory and wait for other browser sessions, recordings, and heavy CPU work to finish before setting the exclusive flag.

```bash
cd /workspace/shawu
export NODE_PATH=/home/box/opt/test-tools/node_modules
export PLAYWRIGHT_BROWSERS_PATH=/home/box/opt/playwright-browsers
export TZ=Asia/Shanghai
export RUN_ID="m10-region5-$(date -u +%Y%m%dT%H%M%S%NZ)"
export M10_RESULTS="/workspace/shawu/m10-work/results/$RUN_ID"
R="$M10_RESULTS"
mkdir -p "$R"
printf '%s\n' "$R"
ps -eo pid,ppid,pgid,pcpu,comm
```

Each stage takes nonblocking exclusive locks in this order. The runner opens the three earlier lock files read-only.

1. `m7-work/stage-a/exclusive.lock`
2. `m8-work/outer-exclusive.lock`
3. `m9-work/outer-exclusive.lock`
4. `m10-work/outer-exclusive.lock`

The runner verifies local and served M9 and M10 runtime bytes. It checks TCP listeners on ports 38811 and 8765 before and after each stage and polls them during execution. If either listener drops, stop the sequence and report the stage and timestamp from `$R/port-stop.txt`. The runner terminates the active worker process group and exits 69. Listener status is pending the first supervisor check.

Run the launch blocks in order. Wait for each stage and run its checks before the next launch. To follow the current stage, set `stage` to its name and run the commands below. To stop the worker, send SIGTERM to the PID in `$R/$stage.runner.pid`.

```bash
stage=qa
A="$(cat "$R/$stage.latest-attempt")"
tail -f "$A/stage.log"
```

## 1. Formal QA

QA replays the official start with HD enabled and instrumentation injected in the browser page. It checks all 1,669 actions and 55,206 frames against the accepted evidence, and compares per-frame serialized native state, framebuffer, actors, and text with live M9. The suite also replays the M9 official chain and all 33 historical QA routes. Those earlier routes require exact HD and coverage parity. Official Region 5 frames that display a certified new plate while a previous map ID is still active are counted as added-plate transitions. The run saves eight native and HD capture pairs and reports same-plate coverage for the four new and four reused maps.

The start file SHA-256 is `f389cebc3fc59a310571c66538d38808c32483c7632164f35d207f0738e8d6c0`. The endpoint is `00-2a e0 (5,8)` facing up, story 19, `DAA 52/06`, `D284=04 01`, bank 4, mode 0, dialogue 0. The runner checks every `00-2a` frame for the forbidden row 4. [Accepted browser replay](play/m10-region5-official-evidence/result.json)

```bash
nohup env SUPERVISOR_CONFIRMED_EXCLUSIVE=1 bash m10-work/scripts/run-region5-outer.sh qa "$RUN_ID" </dev/null >>"$R/qa.nohup.log" 2>&1 &
printf '%s\n' "$!" > "$R/qa.launch.pid"
```

```bash
test "$(cat "$R/qa.exit-code.txt")" = 0
test -f "$R/qa.done"
test ! -e "$R/port-stop.txt"
jq -e '.pass and (.routes | length) == 35 and .actions == 3027 and .frames == 153913 and
  .statePassed == .frames and .nativePassed == .frames and .actorTextPassed == .frames and
  .earlierVisualPassed == .earlierFrames and (.contacts | length) == 8 and
  (.region5Coverage | length) == 8' "$R/qa/report.json"
jq -e '.pass and .actions == 1669 and .frames == 55206 and
  .endpoint == {frame:55206,map:"00-2a",entry:0,cell:[5,8],story:19,daa:[82,6],d284:[4,1],
                bank:4,mode:0,dialogue:0,facing:1,script:0}' "$R/qa/official-region5/report.json"
jq '{region5Coverage,region5Excluded,addedPlateTransitionFrames}' "$R/qa/report.json"
```

## 2. Performance

Use the adopted v3 protocol of 1,792 measured native frames per sample, three repeats, legacy with 60 idle warmup frames and cold from the first input frame. Fresh M9 and M10 contexts pair across all 17 inherited routes and four Region 5 routes for 252 samples. Audit and recording are off. At native speed, the timed samples alone take about 2 hours 6 minutes. The comparison includes every repeat, native hashes, timing flags, switch windows, and saved M9 metrics where available. Review repeat spread and same-attempt controls before attributing timing changes.

```bash
nohup env SUPERVISOR_CONFIRMED_EXCLUSIVE=1 bash m10-work/scripts/run-region5-outer.sh perf "$RUN_ID" </dev/null >>"$R/perf.nohup.log" 2>&1 &
printf '%s\n' "$!" > "$R/perf.launch.pid"
```

```bash
test "$(cat "$R/perf.exit-code.txt")" = 0
test -f "$R/perf.done"
test ! -e "$R/port-stop.txt"
jq -e '(.samples | length) == 252 and .method.TARGET == 1792 and .method.WARMUP == 60 and
  .method.REPEATS == 3 and .method.audit == false and .method.recording == false' "$R/perf/report.json"
jq -e '.samples == 252 and (.nativeMismatches | length) == 0' "$R/perf/comparison.json"
jq '{samples,nativeMismatches,crossAttemptPairs,m9GameplayMeanRegressionCandidates}' "$R/perf/comparison.json"
```

After the runner stops, this read-only inventory lists completed and missing samples.

```bash
node m10-work/scripts/region5-perf.cjs --inventory
```

## 3. Contact sheet

The stage verifies the 16 formal QA PNG hashes and composes eight native and HD pairs at the original 640×576 capture size. The supervisor publishes the verified sheet to `shots/m10_region5_contact.png`.

```bash
nohup env SUPERVISOR_CONFIRMED_EXCLUSIVE=1 bash m10-work/scripts/run-region5-outer.sh contact "$RUN_ID" </dev/null >>"$R/contact.nohup.log" 2>&1 &
printf '%s\n' "$!" > "$R/contact.launch.pid"
```

```bash
test "$(cat "$R/contact.exit-code.txt")" = 0 &&
test -f "$R/contact.done" &&
test ! -e "$R/port-stop.txt" &&
test -s "$R/contact-verified.png" &&
{ test -e shots/m10_region5_contact.png ||
  ln -T -- "$R/contact-verified.png" shots/m10_region5_contact.png; } &&
cmp "$R/contact-verified.png" shots/m10_region5_contact.png
```

## 4. Preview

The recorder follows the official action list continuously through the accepted endpoint. It records six excerpts at native real-time cadence, covering the west forest arrival and story scene, the story-19 inn scene, the exit path, the mountain road, and the stairs arrival. It checks the replay boundaries against accepted frame evidence and available state and framebuffer hashes. The final clip holds the settled endpoint briefly. Raw capture and cut timestamps stay with the run. The encoded preview is silent and must be smaller than 25,000,000 bytes.

```bash
nohup env SUPERVISOR_CONFIRMED_EXCLUSIVE=1 bash m10-work/scripts/run-region5-outer.sh preview "$RUN_ID" </dev/null >>"$R/preview.nohup.log" 2>&1 &
printf '%s\n' "$!" > "$R/preview.launch.pid"
```

```bash
test "$(cat "$R/preview.exit-code.txt")" = 0
test -f "$R/preview.done"
test ! -e "$R/port-stop.txt"
test "$(stat -c '%s' m10-work/region5_preview.webm)" -lt 25000000
jq -e '.audio == false and .speedMultiplier == 1 and (.segments | length) == 6' "$R/preview/encode-report.json"
jq -e '.streams | length == 1 and .[0].codec_type == "video" and .[0].width == 640 and .[0].height == 576' "$R/preview/preview-probe.json"
```

## Interruptions and the bounded fix round

Reuse the same run ID after an ordinary interruption. QA resumes at completed routes, perf at validated sample files, and preview at a hash-verified raw capture or encode. Interrupted captures and routes are preserved in sibling directories. If an existing published artifact differs, retain it and review the run copy.

After a listener stop, first report the failure. Once the supervisor restores the listeners, rechecks exclusivity, and authorizes resume, select the interrupted stage and run the following.

```bash
stage=perf
nohup env SUPERVISOR_CONFIRMED_EXCLUSIVE=1 M10_RESUME_AFTER_PORT_STOP=1 bash m10-work/scripts/run-region5-outer.sh "$stage" "$RUN_ID" </dev/null >>"$R/$stage.nohup.log" 2>&1 &
printf '%s\n' "$!" > "$R/$stage.launch.pid"
```

Preserve the first run's results. An established M10 regression may use one bounded fix round at most. Regenerate the freeze with `PYTHONDONTWRITEBYTECODE=1 python3 m10-work/scripts/prepare-outer.py` and use a fresh run ID after that fix. No fix round has been used.
