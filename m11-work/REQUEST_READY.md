# M11 Region 6 supervisor handoff

Formal QA needs a fresh `RUN_ID` for the revised freeze. The run
`m11-region6-20261120T140423261638555Z` is preserved as failed evidence.
The native replay reproduced the transition defect and the offline checks passed.
[Diagnosis and fix](integration/qa-fix-diagnosis.md)

The isolated runtime is ready at `http://127.0.0.1:8765/m11-work/runtime/`. It contains 44 registered maps. Five Region 6 PNGs were copied byte for byte, including the full cave plate. For `00-25`, the decoded black pad has faint RGB values up to 7. The detected painted box is `[0,0,858,1402]`. A centered `[9,1,849,1401]` crop fits the native 3:5 rectangle at 840×1400 without resampling. Both SHA-256 values and both crop boxes are in the manifest. All 11 map IDs on the official route have registered plates. Pixels without certified HD coverage stay native and are measured by QA. [Integration manifest](integration/provenance.json) · [Run plan](integration/outer-plan.json) · [Frozen inputs](integration/outer-freeze.json)

## Exploration (done)

The accepted Region 6 route restores the party on the detour, crosses the row-4 item gate, clears the scripted maze fight and the fan fight, and reaches the story-22 cutoff in Stone Cave. The browser evidence contains 717 actions, 63,131 frames and 42 saved records. The next cell west of the endpoint triggers story 23. [Accepted replay](play/region6-official/result.json) · [ROM gate analysis](rom-gate-analysis.md#region-cutoff)

## Supervisor setup

Run on the supervisor host with the workspace served on port 8765. Wait for other QA, recording, and heavy CPU work to finish before launching a stage.

```bash
cd /workspace/shawu
export NODE_PATH=/home/box/opt/test-tools/node_modules
export PLAYWRIGHT_BROWSERS_PATH=/home/box/opt/playwright-browsers
export TZ=Asia/Shanghai
export RUN_ID="m11-region6-$(date -u +%Y%m%dT%H%M%S%NZ)"
export M11_RESULTS="/workspace/shawu/m11-work/results/$RUN_ID"
export R="$M11_RESULTS"
mkdir -p "$R"
printf '%s\n' "$R"
ps -eo pid,ppid,pgid,pcpu,comm
node -e "require('./m11-work/scripts/outer-common.cjs').verifyFreeze()"
```

The runner takes exclusive locks in order at `m7-work/stage-a/exclusive.lock`, `m8-work/outer-exclusive.lock`, `m9-work/outer-exclusive.lock`, `m10-work/outer-exclusive.lock`, and `m11-work/outer-exclusive.lock`. It opens the earlier locks read-only and verifies the frozen local and served M10 and M11 files. It checks ports 38811 and 8765 before, during, and after each stage. If either listener drops, the runner stops the worker group and exits 69. Stop the sequence and report the stage and time from `$R/port-stop.txt`.

Launch in the order below and let each stage finish before checking the results. To follow a stage, select its name and tail its attempt log.

```bash
stage=qa
A="$(cat "$R/$stage.latest-attempt")"
tail -f "$A/stage.log"
```

## 1. Formal QA

The Region 6 replay starts from `story19-00-2a-official.bin` with SHA-256 `c41b4188203bc45d2d0c5eeb24f8b307040be0644ce861ffbcc6281d4060c8f1`. M11 and live M10 run with HD on and page-only instrumentation. The suite checks native state, framebuffer, actor and text hashes for every frame. M11 actor and text samples must always match the native raster. The 35 inherited routes require exact HD and coverage parity outside verified instances of the documented M10 blackout defect. Region 6 also checks earlier-map frames, except when a certified added plate is already rendered during a map transition. In the blackout exception, QA verifies the entire M11 output is native black and checks both exact coverage totals. The report lists each instance in `baselineKnownDefects` and counts them in `baselineKnownDefectFrames` and `earlierKnownDefectFrames`. The report gives per-map and weighted same-plate coverage with gap attribution. Positive coverage in the 11 maps and the corresponding native and HD captures are required.

```bash
nohup env SUPERVISOR_CONFIRMED_EXCLUSIVE=1 bash m11-work/scripts/run-region6-outer.sh qa "$RUN_ID" </dev/null >>"$R/qa.nohup.log" 2>&1 &
printf '%s\n' "$!" > "$R/qa.launch.pid"
```

```bash
test "$(cat "$R/qa.exit-code.txt")" = 0 &&
test -f "$R/qa.done" &&
test ! -e "$R/port-stop.txt" &&
jq -e 'def defects_accounted:
    (.baselineKnownDefects | length) == .baselineKnownDefectFrames and
    ([.baselineKnownDefects[] | select(.earlierRegion)] | length) == .earlierKnownDefectFrames and
    (.earlierVisualPassed + .earlierKnownDefectFrames) == .earlierFrames;
  .pass and (.routes | length) == 36 and .actions == 3744 and .frames == 217044 and
  .statePassed == .frames and .nativePassed == .frames and .actorTextPassed == .frames and defects_accounted and
  .baselineKnownDefects == [.routes[].baselineKnownDefects[]] and
  any(.baselineKnownDefects[]; .at == "official-region6/705/83" and .frame == 61811 and .earlierRegion) and
  all(.baselineKnownDefects[]; .candidateTextHD == .textNative and .baselineTextHD != .textNative and
    .candidateCoverage == {eligible:23040,covered:0,gap:23040} and
    .baselineCoverage == {eligible:23040,covered:23040,gap:0}) and
  all(.routes[]; .pass and defects_accounted) and
  all(.routes[1:][]; .earlierFrames == .frames) and
  (.contacts | length) == 11 and (.region6Coverage | length) == 11 and
  all(.region6Coverage[]; .covered > 0 and .eligible == (.covered + .gap) and
    .gap == (.nativeGap + .otherHD) and .gap == (([.reasons[]] | add) // 0)) and
  .coverageWeighted.eligible == ([.region6Coverage[].eligible] | add) and
  .coverageWeighted.covered == ([.region6Coverage[].covered] | add) and
  (.coverageWeighted | .eligible == (.covered + .gap) and .ratio == (.covered / .eligible))' "$R/qa/report.json" &&
jq -e '.pass and .actions == 717 and .frames == 63131 and .evidencePassed == 41 and .row4Frames > 0 and
  .sourceSHA256 == "c41b4188203bc45d2d0c5eeb24f8b307040be0644ce861ffbcc6281d4060c8f1" and
  .endpoint == {frame:63131,map:"00-2e",entry:3,cell:[25,5],facing:2,story:22,bank:5,
                mode:0,dialogue:0,script:0,banner:0,settled:true,DAA:["e6","52","3e","30"],
                D2AC:["10","01"],D284:["00","00"],party:["02","17","24"],hp:[0,13,34]}' \
  "$R/qa/official-region6/report.json"
jq '{region6Coverage,coverageWeighted,region6Excluded,addedPlateTransitionFrames,
  baselineKnownDefectFrames,earlierKnownDefectFrames,baselineKnownDefects}' "$R/qa/report.json"
```

## 2. Performance

The v3 protocol pairs fresh M10 and M11 contexts on 21 inherited routes and six Region 6 routes. It measures 1,792 native frames per sample, with three repeats each for legacy (60 idle warmup frames) and cold (measurement starts with the first input frame). Audit and recording are off. The 324 samples take about 2 hours 42 minutes at native speed, plus warmup and startup. The comparison includes timing distributions, switch windows, paired native hashes, cross-attempt pairs and saved M10 metrics for the inherited routes.

```bash
nohup env SUPERVISOR_CONFIRMED_EXCLUSIVE=1 bash m11-work/scripts/run-region6-outer.sh perf "$RUN_ID" </dev/null >>"$R/perf.nohup.log" 2>&1 &
printf '%s\n' "$!" > "$R/perf.launch.pid"
```

### Optional perf watch-resume

Use this after the perf launch if the watchdog should carry the same run through contact publication and preview. Wait until the perf attempt pointer exists and names the launched PID. Keep manual runners idle while the watchdog owns the sequence.

```bash
W=m11-work/outer-runs/m11-region6-watch-resume
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
  .resumesUsed <= 14 and .inventory.complete == 324 and .inventory.remaining == 0 and
  .perfDone and .contactDone and .previewDone and (.portStop | not)' "$W.status.json"
```

### Performance acceptance

```bash
test "$(cat "$R/perf.exit-code.txt")" = 0 &&
test -f "$R/perf.done" &&
test ! -e "$R/port-stop.txt" &&
jq -e '(.samples | length) == 324 and .method.version == 3 and .method.TARGET == 1792 and
  .method.WARMUP == 60 and .method.REPEATS == 3 and .method.audit == false and
  .method.recording == false and .method.freshPageAndContextPerSample and
  all(.samples[]; .frames == 1792 and .errors == [])' "$R/perf/report.json" &&
jq -e '.samples == 324 and .nativeMismatches == [] and (.comparisons | length) == 54' "$R/perf/comparison.json"
jq '{samples,nativeMismatches,crossAttemptPairs,m10GameplayMeanRegressionCandidates}' "$R/perf/comparison.json"
node m11-work/scripts/region6-perf.cjs --inventory
```

The same read-only inventory command reports validated samples and work remaining after an interruption.

## 3. Contact sheet

The stage checks all 22 QA capture hashes and their 640×576 dimensions, then writes the verified sheet and its hash under the run directory. Publish it to `shots/m11_region6_contact.png`.

```bash
nohup env SUPERVISOR_CONFIRMED_EXCLUSIVE=1 bash m11-work/scripts/run-region6-outer.sh contact "$RUN_ID" </dev/null >>"$R/contact.nohup.log" 2>&1 &
printf '%s\n' "$!" > "$R/contact.launch.pid"
```

```bash
sheet=shots/m11_region6_contact.png
sheet_hash="$(sha256sum "$R/contact-verified.png")"
test "$(cat "$R/contact.exit-code.txt")" = 0 &&
test -f "$R/contact.done" &&
test ! -e "$R/port-stop.txt" &&
test -s "$R/contact-verified.png" &&
jq -e --arg sha "${sheet_hash%% *}" '.verified and .pairs == 11 and
  (.maps | length) == 11 and .width == 1332 and .height == 6898 and .sha256 == $sha' "$R/contact-report.json" &&
{ test -e "$sheet" || ln -T -- "$R/contact-verified.png" "$sheet"; } &&
cmp "$R/contact-verified.png" "$sheet"
```

## 4. Preview

Seven real-time excerpts show the row-4 gate, Cloud Tower Gate entrance, both maze maps, the passage, the fan encounter lead-in in Twin Statue Hall, the return, and the Stone Cave arrival and settled endpoint. The published excerpts contain world-map views. The recorder checks action boundaries against the official evidence, trims each marker interval to measured playback duration with the accepted M9/M10 logic, and publishes a silent 640×576 VP9 WebM under 25,000,000 bytes.

```bash
nohup env SUPERVISOR_CONFIRMED_EXCLUSIVE=1 bash m11-work/scripts/run-region6-outer.sh preview "$RUN_ID" </dev/null >>"$R/preview.nohup.log" 2>&1 &
printf '%s\n' "$!" > "$R/preview.launch.pid"
```

```bash
preview=m11-work/region6_preview.webm
preview_hash="$(sha256sum "$preview")"
test "$(cat "$R/preview.exit-code.txt")" = 0 &&
test -f "$R/preview.done" &&
test ! -e "$R/port-stop.txt" &&
test -s "$preview" &&
test "$(stat -c '%s' "$preview")" -lt 25000000 &&
jq -e --arg sha "${preview_hash%% *}" '.videoSHA256 == $sha and .audio == false and
  .speedMultiplier == 1 and .bytes > 0 and .bytes < 25000000 and (.segments | length) == 7 and
  (.segments[-1].endEvidence | .frame == 63131 and .map == "00-2e" and .story == 22)' "$R/preview/encode-report.json" &&
jq -e '.streams | length == 1 and .[0].codec_type == "video" and .[0].codec_name == "vp9" and
  .[0].width == 640 and .[0].height == 576' "$R/preview/preview-probe.json"
```

## Interrupted stages

Reuse the same run ID after an ordinary interruption with the same freeze. After a fix round, generate a fresh run ID. QA resumes at validated route reports, perf at validated samples, and preview at its hash-verified capture or encode. The stage runner preserves interrupted captures and route directories. If a published file differs, keep both the published file and the run artifact for review.

After reporting a listener stop, the supervisor can resume once both listeners are back and exclusivity is confirmed.

```bash
stage=perf
nohup env SUPERVISOR_CONFIRMED_EXCLUSIVE=1 M11_RESUME_AFTER_PORT_STOP=1 \
  bash m11-work/scripts/run-region6-outer.sh "$stage" "$RUN_ID" </dev/null >>"$R/$stage.nohup.log" 2>&1 &
printf '%s\n' "$!" > "$R/$stage.launch.pid"
```
