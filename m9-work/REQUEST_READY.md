# M9 Region 4 supervisor handoff

Offline integration is complete. The candidate is `http://127.0.0.1:8765/m9-work/runtime/`. It contains 34 registered maps and the five byte-identical accepted plates. The ROM, binjgb, rendering code, and prior plates, including Region 3 `00-06` v2, match the accepted M8 runtime byte for byte. The only edit to a copied file is the shared map registry. Browser QA, timing, and the two final media artifacts are pending supervisor execution. [Integration provenance](integration/provenance.json) · [Frozen inputs](integration/outer-freeze.json) · [Supervisor plate review](art/SUPERVISOR_VISUAL_REVIEW.md)

## Set up an exclusive run

On the supervisor host, wait for other QA, gameplay browsers, recordings, GPT jobs, and other heavy CPU work to finish. Keep the host exclusive through each stage, especially perf. Confirm the process inventory before setting the exclusive flag. All commands run from `/workspace/shawu`.

```bash
cd /workspace/shawu
RUN_ID="m9-region4-$(date -u +%Y%m%dT%H%M%S%NZ)"
R="/workspace/shawu/m9-work/results/$RUN_ID"
mkdir -p "$R"
printf '%s\n' "$R"
ps -eo pid,ppid,pgid,pcpu,comm
```

The runner takes nonblocking exclusive locks in this order and holds them through the whole stage. It opens the first two existing files read-only.

1. `m7-work/stage-a/exclusive.lock`
2. `m8-work/outer-exclusive.lock`
3. `m9-work/outer-exclusive.lock`

The runner checks TCP listeners on `127.0.0.1:38811` and `127.0.0.1:8765` before and after each stage and polls them during execution. It verifies the local freeze and HTTP bytes for all 104 candidate runtime files before starting work. A listener failure terminates the active stage and exits 69. If either port drops, stop the whole sequence and report the timestamp, stage, and result directory from `$R/port-stop.txt`. The integration sandbox returned EPERM on both socket probes, so the first live check occurs on the supervisor host.

The four launch blocks below only start their named stage. Review its result before launching the next stage. The shell writes `$R/<stage>.launch.pid`. The runner records its own PID in `$R/<stage>.runner.pid` and the current attempt directory in `$R/<stage>.latest-attempt`. That attempt contains `runner.pid`, `worker.pid`, `stage.log`, before and after process inventories, and `exit-code.txt`. Each `<stage>.nohup.log` collects launcher and checkpoint messages across attempts. To stop a running stage, send SIGTERM to the runner PID. It terminates the worker process group.

```bash
# Set stage to qa, perf, contact, or preview to inspect a launched job.
stage=qa
A="$(cat "$R/$stage.latest-attempt")"
tail -f "$A/stage.log"
```

## 1. Formal QA

```bash
nohup env SUPERVISOR_CONFIRMED_EXCLUSIVE=1 bash m9-work/scripts/run-region4-outer.sh qa "$RUN_ID" </dev/null >>"$R/qa.nohup.log" 2>&1 &
printf '%s\n' "$!" > "$R/qa.launch.pid"
```

The candidate replays the official story-12 save with all 262 inputs and checks each native observation and action checkpoint against the saved browser evidence. The start file SHA-256 is `2a3551ad5082236ce2b3223323d6fff983a984a3839ff2e6fa2359c1321edea2`. The final checkpoint is `00-2c`, story 14, with `DAA1=0x72` and `DAA2=0x01`. The same run compares native framebuffer, serialized state, actors, and text per frame with live M8 and verifies exact HD RGBA and coverage on earlier-region frames. It also reruns all 33 historical routes. Expect **1,358 actions and 98,707 native frames** in total. [Official action list](outer-runs/huangnigang-inn-actions.json) · [Official replay result](play/m9-huangnigang-official-evidence/result.json)

Each new-map coverage row uses same-plate native pixel count divided by the unchanged native-background eligible count. Other HD sources and native gaps remain in the denominator and are itemized. Nonzero world mode and battle banks `2b`–`2d` are counted separately. Preserve the frame dumps, five contact pairs, and the report with the counts and gap reasons.

```bash
test "$(cat "$R/qa.exit-code.txt")" = 0
test -f "$R/qa.done"
test ! -e "$R/port-stop.txt"
jq -e '.pass and .actions == 1358 and .frames == 98707 and
  .statePassed == .frames and .nativePassed == .frames and .actorTextPassed == .frames and
  .earlierVisualPassed == .earlierFrames and
  (.region4Coverage | keys == ["00-1f","00-21","00-24","00-2b","00-2c"])' "$R/qa/report.json"
jq '{endpoint,wram}' "$R/qa/official-huangnigang-inn/report.json"
jq '.region4Coverage' "$R/qa/report.json"
```

For an ordinary interruption, repeat the QA launch with the same run ID. Each successful route is a resume point. The unfinished route restarts from its frozen save, and its previous directory is preserved as `*.interrupted-*`. Retain the mismatch report and stop for supervisor review if an invariant fails.

## 2. Performance

After QA passes, check the host is still exclusive. The full perf pass takes roughly 2 hours 20 minutes plus page startup. It uses the adopted v3 protocol of **1,792 native frames per sample, three repeats**, legacy with 60 idle native warmup frames, and cold from the first input frame. Each sample starts in a fresh browser context. Audit and recording are off throughout the measurements. Fresh adopted v3 and live M8 controls run alongside M9 on 12 historical routes. Live M8 and M9 also run the five official-evidence approaches. The controls are timed serially with M9. The full inventory is **276 samples**.

```bash
nohup env SUPERVISOR_CONFIRMED_EXCLUSIVE=1 bash m9-work/scripts/run-region4-outer.sh perf "$RUN_ID" </dev/null >>"$R/perf.nohup.log" 2>&1 &
printf '%s\n' "$!" > "$R/perf.launch.pid"
```

```bash
test "$(cat "$R/perf.exit-code.txt")" = 0
test -f "$R/perf.done"
test ! -e "$R/port-stop.txt"
jq -e '(.samples | length) == 276 and .method.audit == false and .method.recording == false' "$R/perf/report.json"
jq '{samples,nativeMismatches,cold0017DisclosedLimitExceeded,
     m8MeanFlagCount: (.m8GameplayMeanRegressionCandidates | length)}' "$R/perf/comparison.json"
```

`perf.done` marks measurement completion. Review all three repeats, switch windows, the new-map samples, and the paired fresh controls in `perf/comparison.json`. The timing flags surface candidates for review. Use the paired controls and repeat spread to decide whether M9 introduced a regression.

The disclosed cold `00-17` residual remains the comparison boundary. In the earlier rejected fix, the means of the three per-sample frame and switch maxima were both **24.100 ms**, above the **19.0 ms** gate against saved v3 at **16.000 ms**. That fix recovered mean `debt.max` to **16.738 ms**. The original live M8 runtime was retained. Its same-round cold control measured **20.567 ms** for both frame and switch maxima and **16.732 ms** for `debt.max`. Keep those controls distinct when reviewing M9. If QA or perf establishes a new M9 regression, preserve the result directory and return for at most one bounded fix round. Otherwise disclose the residual and keep the isolated M9 runtime. [Frozen M8 cold decision](../m8-work/results/outer-cold-0017-20261118T092326742885874Z/decision.json)

For an ordinary interruption, repeat the perf launch with the same run ID. Each validated sample JSON is an atomic resume point. The runner measures missing samples, then rebuilds the report and comparison. A finished report can be reused if only summarization was interrupted. For a read-only inventory after the runner stops, use this command.

```bash
M9_RESULTS="$R" node m9-work/scripts/region4-perf.cjs --inventory
```

## 3. Contact sheet

Use the completed formal QA captures. The stage verifies all ten PNG hashes and composes the five matching 640×576 native and in-runtime HD screen pairs at their original capture size. Inspect the `00-24` inn plaque and both inn rooms in the final sheet. [Capture checkpoints](integration/outer-plan.json)

```bash
nohup env SUPERVISOR_CONFIRMED_EXCLUSIVE=1 bash m9-work/scripts/run-region4-outer.sh contact "$RUN_ID" </dev/null >>"$R/contact.nohup.log" 2>&1 &
printf '%s\n' "$!" > "$R/contact.launch.pid"
```

```bash
test "$(cat "$R/contact.exit-code.txt")" = 0
test -f "$R/contact.done"
test ! -e "$R/port-stop.txt"
cmp "$R/contact-verified.png" /workspace/shawu/shots/m9_region4_contact.png
```

Repeat the same launch after an ordinary interruption. The stage rebuilds from the verified pairs, then publishes the sheet to `/workspace/shawu/shots/m9_region4_contact.png`. An existing sheet with different bytes requires supervisor review.

## 4. Preview

The recorder starts from the official save in the M9 runtime and follows the frozen action list continuously. It uses native real-time playback for seven excerpts covering the approach to 黄泥岗, the woods, the inn exterior and entry, and the two inn talks. It compares the native framebuffer and serialized state at the excerpt boundaries with the official evidence. The encoder cuts the intervals between excerpts and preserves timing within each excerpt. The marked raw recording and cut timestamps stay in the run directory.

```bash
nohup env SUPERVISOR_CONFIRMED_EXCLUSIVE=1 bash m9-work/scripts/run-region4-outer.sh preview "$RUN_ID" </dev/null >>"$R/preview.nohup.log" 2>&1 &
printf '%s\n' "$!" > "$R/preview.launch.pid"
```

```bash
test "$(cat "$R/preview.exit-code.txt")" = 0
test -f "$R/preview.done"
test ! -e "$R/port-stop.txt"
test "$(stat -c '%s' m9-work/region4_preview.webm)" -lt 25000000
jq -e '.audio == false and .speedMultiplier == 1 and (.segments | length) == 7' "$R/preview/encode-report.json"
jq -e '.streams | length == 1 and .[0].codec_type == "video" and .[0].width == 640 and .[0].height == 576' "$R/preview/preview-probe.json"
```

Repeat the same launch after an ordinary interruption. A hash-verified raw capture resumes at encoding. A verified encode resumes at publication when necessary. An incomplete capture is preserved in `preview.interrupted-*` before recording again from the official save. The verified output goes to `/workspace/shawu/m9-work/region4_preview.webm`. An existing preview with different bytes requires supervisor review.

## Resuming after a listener stop or a fix

Report a listener drop before resuming any stage. Once the supervisor has restored both listeners, checked host exclusivity, and approved resuming the frozen run, set `stage` to the interrupted stage and use the command below. The runner archives the original port-stop record and uses the same route, sample, or recording resume point.

```bash
stage=perf
nohup env SUPERVISOR_CONFIRMED_EXCLUSIVE=1 M9_RESUME_AFTER_PORT_STOP=1 bash m9-work/scripts/run-region4-outer.sh "$stage" "$RUN_ID" </dev/null >>"$R/$stage.nohup.log" 2>&1 &
printf '%s\n' "$!" > "$R/$stage.launch.pid"
```

For an approved bounded fix, start a fresh run ID and freeze once the changes are ready. Retain prior timing and QA results under their original run ID. If earlier media has already been published, retain it with that run before publishing reviewed replacements.
