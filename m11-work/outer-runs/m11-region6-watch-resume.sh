#!/usr/bin/env bash
# Supervisor host only. Watch an existing perf attempt, then run contact and preview.
set -euo pipefail
cd /workspace/shawu

export TZ=Asia/Shanghai
export NODE_PATH=/home/box/opt/test-tools/node_modules
export PLAYWRIGHT_BROWSERS_PATH=/home/box/opt/playwright-browsers
export PYTHONDONTWRITEBYTECODE=1

if [[ ! ${RUN_ID:-} =~ ^[A-Za-z0-9][A-Za-z0-9._-]*$ ||
      ! ${WATCH_PID:-} =~ ^[1-9][0-9]*$ || -z ${WATCH_ATTEMPT:-} ]]; then
  echo 'Set RUN_ID, WATCH_PID and WATCH_ATTEMPT for the already-launched perf runner.' >&2
  exit 64
fi
R="/workspace/shawu/m11-work/results/$RUN_ID"
[[ ${M11_RESULTS:-$R} == "$R" ]] || exit 64
export M11_RESULTS="$R"
if [[ $(realpath -e "$R") != "$R" ]]; then exit 64; fi

MAX_RESUMES=14
resumes=${RESUMES_USED:-0}
if [[ ! $resumes =~ ^([0-9]|1[0-4])$ ]]; then exit 64; fi
DIR=m11-work/outer-runs
PREFIX=$DIR/m11-region6-watch-resume
LOG=$PREFIX.log
STATUS=$PREFIX.status.json
BLOCK=$PREFIX.blocker.txt
exec 4>>"$PREFIX.lock"
flock -n 4 || { echo 'M11 watchdog lock is held' >&2; exit 75; }
if [[ -s $STATUS ]]; then
  prior=$(jq -r --arg run "$RUN_ID" 'select(.runId == $run) | .resumesUsed' "$STATUS")
  if [[ $prior =~ ^([0-9]|1[0-4])$ ]] && (( prior > resumes )); then resumes=$prior; fi
fi

phase=watch-current-perf
note='watching initial perf attempt'
runner_pid=$WATCH_PID
attempt=$WATCH_ATTEMPT
attempt_rc=

log() { printf '%s %s\n' "$(date --iso-8601=seconds)" "$*" | tee -a "$LOG" >&2; }

runner_alive() {
  local state
  state=$(ps -o stat= -p "$1") || return 1
  [[ -n $state && $state != Z* ]]
}

write_status() {
  local running=0
  if runner_alive "$runner_pid" && [[ ! -s $attempt/exit-code.txt ]]; then running=1; fi
  python3 - "$STATUS" "$RUN_ID" "$phase" "$note" "$resumes" "$MAX_RESUMES" \
    "$runner_pid" "$attempt" "$running" <<'PY'
import json
import sys
from datetime import datetime
from pathlib import Path

status, run_id, phase, note, resumes, cap, runner, attempt, alive = sys.argv[1:]
r = Path("/workspace/shawu/m11-work/results") / run_id
progress = r / "perf/resume-progress.json"
inventory = dict(expected=324, complete=0, remaining=324)
if progress.is_file():
    inventory = json.loads(progress.read_text())
payload = dict(updated=datetime.now().astimezone().isoformat(timespec="seconds"), runId=run_id,
               phase=phase, note=note, resumesUsed=int(resumes), maxResumes=int(cap),
               runnerPid=int(runner), runnerAttempt=attempt, runnerAlive=bool(int(alive)),
               inventory=inventory, qaDone=(r / "qa.done").is_file(),
               perfDone=(r / "perf.done").is_file(), contactDone=(r / "contact.done").is_file(),
               previewDone=(r / "preview.done").is_file(), portStop=(r / "port-stop.txt").is_file())
target = Path(status)
pending = target.with_suffix(".partial")
pending.write_text(json.dumps(payload, indent=2) + "\n")
pending.replace(target)
PY
}

block() {
  local rc=$1
  shift
  phase=blocked
  note="$*"
  write_status || true
  printf '%s\n%s\n' "$(date --iso-8601=seconds)" "$note" > "$BLOCK"
  log "$note"
  exit "$rc"
}

ports_up() {
  python3 - <<'PY'
from socket import create_connection
for port in (38811, 8765):
    try:
        with create_connection(("127.0.0.1", port), timeout=2):
            pass
    except OSError as error:
        raise SystemExit(f"listener {port} unavailable ({error})")
PY
}

check_port_stop() {
  if [[ -s $R/port-stop.txt ]]; then
    block 69 "Listener stop recorded. $(<"$R/port-stop.txt")"
  fi
}

matches_attempt() {
  local stage=$1 candidate=$2 pid=$3
  [[ ${candidate%/*} == "$R/attempts" && ${candidate##*/} == "$stage-"*-"$pid" &&
     -d $candidate && ! -L $candidate && -s $candidate/runner.pid &&
     $(<"$candidate/runner.pid") == "$pid" ]]
}

wait_attempt() {
  local stage=$1 grace_started=-1
  matches_attempt "$stage" "$attempt" "$runner_pid" || block 1 "Invalid $stage attempt for PID $runner_pid ($attempt)"
  # Read only this attempt's exit evidence. A brief grace period covers delayed publication.
  while [[ ! -s $attempt/exit-code.txt ]] || runner_alive "$runner_pid"; do
    if ! runner_alive "$runner_pid"; then
      if (( grace_started < 0 )); then grace_started=$SECONDS; fi
      if (( SECONDS - grace_started >= 90 )); then
        block 1 "$stage PID $runner_pid did not publish an exit code in $attempt"
      fi
    fi
    write_status || true
    sleep 5
  done
  read -r attempt_rc < "$attempt/exit-code.txt" || block 1 "Unreadable exit code in $attempt"
  [[ $attempt_rc =~ ^[0-9]+$ ]] || block 1 "Invalid exit code in $attempt ($attempt_rc)"
  log "$stage PID $runner_pid exited $attempt_rc ($attempt)"
  check_port_stop
  if [[ $attempt_rc == 69 ]]; then block 69 "$stage stopped on listener loss ($attempt)"; fi
}

is_timeout_flake() {
  [[ $attempt_rc == 1 && ! -e $attempt/port-stop.txt && -f $attempt/stage.log ]] || return 1
  if rg -q 'Frozen bytes differ|Freeze changed|Invalid perf sample|Formal invariant failed|Forbidden stairs row|Served bytes differ|REQUIRED_PORT_UNAVAILABLE' "$attempt/stage.log"; then
    return 1
  fi
  rg -q 'page\.waitForFunction: Timeout 120000ms exceeded' "$attempt/stage.log" &&
    rg -q "name: 'TimeoutError'" "$attempt/stage.log"
}

launch_stage() {
  local stage=$1 candidate rc
  check_port_stop
  ports_up || block 69 "Listeners 38811/8765 unavailable before $stage. Stop and report."
  # Close the watchdog lock FD in the child. The runner owns its own stage locks.
  nohup env SUPERVISOR_CONFIRMED_EXCLUSIVE=1 \
    bash m11-work/scripts/run-region6-outer.sh "$stage" "$RUN_ID" \
    4>&- </dev/null >>"$R/$stage.nohup.log" 2>&1 &
  runner_pid=$!
  attempt=
  printf '%s\n' "$runner_pid" > "$R/$stage.launch.pid"
  for _ in {1..120}; do
    candidate=
    if [[ -s $R/$stage.latest-attempt ]]; then candidate=$(<"$R/$stage.latest-attempt"); fi
    if matches_attempt "$stage" "$candidate" "$runner_pid"; then
      attempt=$candidate
      log "launched $stage PID $runner_pid ($attempt)"
      return 0
    fi
    if ! runner_alive "$runner_pid"; then
      # Recheck the pointer after observing exit, in case a short stage published it meanwhile.
      if [[ -s $R/$stage.latest-attempt ]]; then candidate=$(<"$R/$stage.latest-attempt"); fi
      if matches_attempt "$stage" "$candidate" "$runner_pid"; then
        attempt=$candidate
        return 0
      fi
      rc=0
      wait "$runner_pid" || rc=$?
      block 1 "$stage PID $runner_pid exited $rc before registering an attempt. See $R/$stage.nohup.log"
    fi
    sleep .5
  done
  block 1 "$stage PID $runner_pid did not register a matching attempt. See $R/$stage.nohup.log"
}

log "watch-resume start RUN_ID=$RUN_ID PID=$runner_pid attempt=$attempt cap=$MAX_RESUMES"
check_port_stop
wait_attempt perf
while [[ $attempt_rc != 0 || ! -f $R/perf.done ]]; do
  is_timeout_flake || block 1 "Perf failed with exit $attempt_rc. See $attempt/stage.log"
  (( resumes < MAX_RESUMES )) || block 1 "Perf waitForFunction timed out after $MAX_RESUMES resumes."
  resumes=$((resumes + 1))
  phase=resume-perf
  note="resume $resumes/$MAX_RESUMES after the 120s perf timeout"
  write_status
  launch_stage perf
  wait_attempt perf
done
[[ -f $R/qa.done && -f $R/perf.done ]] || block 1 'QA or perf completion marker missing.'
jq -e '.samples == 324 and .nativeMismatches == []' "$R/perf/comparison.json" >/dev/null ||
  block 1 'Perf comparison failed acceptance.'

phase=contact
note='verifying and publishing contact sheet'
write_status
if [[ ! -f $R/contact.done ]]; then
  launch_stage contact
  wait_attempt contact
  [[ $attempt_rc == 0 && -f $R/contact.done ]] || block 1 "Contact failed with exit $attempt_rc."
fi
check_port_stop
[[ -s $R/contact-verified.png ]] || block 1 'Verified contact sheet missing.'
digest=$(sha256sum "$R/contact-verified.png")
jq -e --arg sha "${digest%% *}" '.verified and .pairs == 11 and .sha256 == $sha' \
  "$R/contact-report.json" >/dev/null || block 1 'Contact sheet failed acceptance.'
sheet=shots/m11_region6_contact.png
if [[ ! -e $sheet ]]; then
  ln -T -- "$R/contact-verified.png" "$sheet" || block 1 'Contact sheet publication failed.'
fi
cmp "$R/contact-verified.png" "$sheet" || block 1 'Published contact sheet differs from verified PNG.'
log "contact ready $sheet"

phase=preview
note='verifying and publishing preview'
write_status
if [[ ! -f $R/preview.done ]]; then
  launch_stage preview
  wait_attempt preview
  [[ $attempt_rc == 0 && -f $R/preview.done ]] || block 1 "Preview failed with exit $attempt_rc."
fi
check_port_stop
preview=m11-work/region6_preview.webm
[[ -s $preview ]] || block 1 'Published preview missing.'
digest=$(sha256sum "$preview")
jq -e --arg sha "${digest%% *}" '.videoSHA256 == $sha and .audio == false and
  .codec == "vp9" and .width == 640 and .height == 576 and .speedMultiplier == 1 and
  .bytes > 0 and .bytes < 25000000 and (.segments | length) == 7' \
  "$R/preview/encode-report.json" >/dev/null || block 1 'Published preview failed acceptance.'
phase=complete
note='perf, contact and preview complete'
write_status
log "$note (resumes used $resumes)"
