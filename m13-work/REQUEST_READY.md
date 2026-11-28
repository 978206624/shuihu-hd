# M13 Region 8 supervisor handoff

## Exploration (done)

The 26-part chain ends at 01-15 e0 (9,1), facing up at story 25.

## Browser replay (done)

The official replay completed 625 actions and 21,354 frames with zero errors.

## Art (done)

The scope includes eleven new maps and the accepted 00-2d plate from M12.

## GPT generation (done)

The owner accepted all eleven plates. Source and installed hashes and fit rectangles are in [provenance](integration/provenance.json).

## Supervisor setup

Run on the supervisor host with the workspace served on port 8765. Wait for other QA, recording, and heavy CPU work to finish before launching a stage.

```bash
cd /workspace/shawu
export NODE_PATH=/home/hatch/workspace/tools/playwright/node_modules
export PLAYWRIGHT_BROWSERS_PATH=/home/hatch/.cache/ms-playwright
export TZ=Asia/Shanghai
export RUN_ID="m13-region8-$(date -u +%Y%m%dT%H%M%S%NZ)"
export M13_RESULTS="/workspace/shawu/m13-work/results/$RUN_ID"
export R="$M13_RESULTS"
mkdir -p "$R"
printf '%s\n' "$R"
ps -eo pid,ppid,pgid,pcpu,comm
node -e "require('./m13-work/scripts/outer-common.cjs').verifyFreeze()"
```

The runner takes exclusive locks in order at `m7-work/stage-a/exclusive.lock`, `m8-work/outer-exclusive.lock`, `m9-work/outer-exclusive.lock`, `m10-work/outer-exclusive.lock`, `m11-work/outer-exclusive.lock`, `m12-work/outer-exclusive.lock`, and `m13-work/outer-exclusive.lock`. It opens the earlier locks read-only and verifies the frozen local and served M12 and M13 files. It checks ports 38811 and 8765 before, during, and after each stage. If either listener drops, the runner stops the worker group and exits 69. Stop the sequence and report the stage and time from `$R/port-stop.txt`.

Launch in the order below and let each stage finish before checking the results. To follow a stage, select its name and tail its attempt log.

```bash
stage=qa
A="$(cat "$R/$stage.latest-attempt")"
tail -f "$A/stage.log"
```

## 1. Formal QA

M13 and live M12 replay the official route from the M12 handover. All 37 historical routes require exact HD and coverage parity. The new route measures same-plate coverage and checks state, native framebuffer, actor and text hashes on every frame.

```bash
nohup env SUPERVISOR_CONFIRMED_EXCLUSIVE=1 bash m13-work/scripts/run-region8-outer.sh qa "$RUN_ID" </dev/null >>"$R/qa.nohup.log" 2>&1 &
printf '%s\n' "$!" > "$R/qa.launch.pid"
```

```bash
test "$(cat "$R/qa.exit-code.txt")" = 0 &&
test -f "$R/qa.done" &&
test ! -e "$R/port-stop.txt" &&
jq -e '.pass and (.routes|length)==38 and .actions==5697 and .frames==308584 and
  .statePassed==.frames and .nativePassed==.frames and .actorTextPassed==.frames and
  .baselineKnownDefects==[] and .earlierFrames==.earlierVisualPassed and
  all(.routes[1:][]; .pass and .frames==.earlierVisualPassed) and
  (.contacts|length)==12 and (.region8Coverage|length)==12 and
  all(.region8Coverage[]; .covered>0 and .eligible==(.covered+.gap) and .gap==(.otherHD+.nativeGap)) and
  .coverageWeighted.covered==([.region8Coverage[].covered]|add) and
  .coverageWeighted.eligible==([.region8Coverage[].eligible]|add)' "$R/qa/report.json" &&
jq -e --slurpfile plan m13-work/integration/outer-plan.json '.pass and .actions==625 and .frames==21354 and
  .evidencePassed==31 and .sourceSHA256==$plan[0].official.sourceSHA256 and
  .endpoint==$plan[0].official.endpoint' "$R/qa/official-region8/report.json"
jq '{region8Coverage,coverageWeighted,region8Excluded,addedPlateTransitionFrames,
  baselineKnownDefectFrames,earlierKnownDefectFrames,baselineKnownDefects}' "$R/qa/report.json"
```

## 2. Performance

The v3 protocol covers 30 inherited routes and eleven new routes. Each of the 492 samples measures 1,792 frames in a fresh context. Legacy adds 60 idle warmup frames. Cold starts on input frame one.

```bash
nohup env SUPERVISOR_CONFIRMED_EXCLUSIVE=1 bash m13-work/scripts/run-region8-outer.sh perf "$RUN_ID" </dev/null >>"$R/perf.nohup.log" 2>&1 &
printf '%s\n' "$!" > "$R/perf.launch.pid"
```

### Optional perf watch-resume

Use this after the perf launch if the watchdog should carry the same run through contact publication and preview. Wait until the perf attempt pointer exists and names the launched PID. Keep manual runners idle while the watchdog owns the sequence.

```bash
W=m13-work/outer-runs/m13-region8-watch-resume
WATCH_PID="$(cat "$R/perf.launch.pid")"
WATCH_ATTEMPT="$(cat "$R/perf.latest-attempt")"
if test "$WATCH_PID" = "$(cat "$WATCH_ATTEMPT/runner.pid")"; then
  nohup env WATCH_PID="$WATCH_PID" WATCH_ATTEMPT="$WATCH_ATTEMPT" \
    bash "$W.sh" </dev/null >>"$W.nohup.log" 2>&1 &
  printf '%s\n' "$!" > "$W.pid"
fi
```

The watchdog observes the registered PID and attempt path. It resumes only the known 120-second Playwright timeout, up to 14 times, and stops on listener loss or other errors. Its status and log are at `$W.status.json` and `$W.log`. On completion, run the acceptance checks for each stage below and skip the manual contact and preview launches.

```bash
jq -e --arg run "$RUN_ID" '.runId == $run and .phase == "complete" and
  .resumesUsed <= 14 and .inventory.complete == 492 and .inventory.remaining == 0 and
  .perfDone and .contactDone and .previewDone and (.portStop | not)' "$W.status.json"
```

### Performance acceptance

```bash
test "$(cat "$R/perf.exit-code.txt")" = 0 &&
test -f "$R/perf.done" &&
test ! -e "$R/port-stop.txt" &&
jq -e '(.samples | length) == 492 and .method.version == 3 and .method.TARGET == 1792 and
  .method.WARMUP == 60 and .method.REPEATS == 3 and .method.audit == false and
  .method.recording == false and .method.freshPageAndContextPerSample and
  all(.samples[]; .frames == 1792 and .errors == [])' "$R/perf/report.json" &&
jq -e '.samples == 492 and .nativeMismatches == [] and (.comparisons | length) == 82' "$R/perf/comparison.json"
jq '{samples,nativeMismatches,crossAttemptPairs,m12GameplayMeanRegressionCandidates}' "$R/perf/comparison.json"
node m13-work/scripts/region8-perf.cjs --inventory
```

The same read-only inventory command reports validated samples and work remaining after an interruption.

## 3. Contact sheet

The stage checks all 24 QA capture hashes and their 640×576 dimensions, then writes the verified sheet and its hash under the run directory. Publish it to `shots/m13_region8_contact.png`.

```bash
nohup env SUPERVISOR_CONFIRMED_EXCLUSIVE=1 bash m13-work/scripts/run-region8-outer.sh contact "$RUN_ID" </dev/null >>"$R/contact.nohup.log" 2>&1 &
printf '%s\n' "$!" > "$R/contact.launch.pid"
```

```bash
sheet=shots/m13_region8_contact.png
sheet_hash="$(sha256sum "$R/contact-verified.png")"
test "$(cat "$R/contact.exit-code.txt")" = 0 &&
test -f "$R/contact.done" &&
test ! -e "$R/port-stop.txt" &&
test -s "$R/contact-verified.png" &&
jq -e --arg sha "${sheet_hash%% *}" '.verified and .pairs == 12 and
  (.maps | length) == 12 and .width == 1332 and .height == 7518 and .sha256 == $sha' "$R/contact-report.json" &&
{ test -e "$sheet" || ln -T -- "$R/contact-verified.png" "$sheet"; } &&
cmp "$R/contact-verified.png" "$sheet"
```

## 4. Preview

Seven real-time excerpts cover the cave passages, the story-25 trigger, village, palace approach, inner hall arrival and settled endpoint.

```bash
nohup env SUPERVISOR_CONFIRMED_EXCLUSIVE=1 bash m13-work/scripts/run-region8-outer.sh preview "$RUN_ID" </dev/null >>"$R/preview.nohup.log" 2>&1 &
printf '%s\n' "$!" > "$R/preview.launch.pid"
```

```bash
preview=m13-work/region8_preview.webm
preview_hash="$(sha256sum "$preview")"
test "$(cat "$R/preview.exit-code.txt")" = 0 &&
test -f "$R/preview.done" &&
test ! -e "$R/port-stop.txt" &&
test -s "$preview" &&
test "$(stat -c '%s' "$preview")" -lt 25000000 &&
jq -e --arg sha "${preview_hash%% *}" '.videoSHA256 == $sha and .audio == false and
  .speedMultiplier == 1 and .bytes > 0 and .bytes < 25000000 and (.segments | length) == 7 and
  all(.segments[]; ((.end-.markerEnd)|fabs) <= 0.041) and
  (.segments[-1].endEvidence | .frame == 21354 and .map == "01-15" and .story == 25)' "$R/preview/encode-report.json" &&
jq -e '.streams | length == 1 and .[0].codec_type == "video" and .[0].codec_name == "vp9" and
  .[0].width == 640 and .[0].height == 576' "$R/preview/preview-probe.json"
```

## Interrupted stages

Reuse the same run ID after an ordinary interruption with the same freeze. After a fix round, generate a fresh run ID. QA resumes at validated route reports, perf at validated samples, and preview at its hash-verified capture or encode. The stage runner preserves interrupted captures and route directories. If a published file differs, keep both the published file and the run artifact for review.

After reporting a listener stop, the supervisor can resume once both listeners are back and exclusivity is confirmed.

```bash
stage=perf
nohup env SUPERVISOR_CONFIRMED_EXCLUSIVE=1 M13_RESUME_AFTER_PORT_STOP=1 \
  bash m13-work/scripts/run-region8-outer.sh "$stage" "$RUN_ID" </dev/null >>"$R/$stage.nohup.log" 2>&1 &
printf '%s\n' "$!" > "$R/$stage.launch.pid"
```
