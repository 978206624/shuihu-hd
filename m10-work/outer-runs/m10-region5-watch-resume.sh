#!/usr/bin/env bash
# Session-independent watchdog for M10 Region 5 outer stages.
# Lives under m10-work/outer-runs/ (not a frozen tree). Does not modify
# m8/m9/m10 runtimes, m10-work/scripts/, or integration freeze files.
#
# Waits for an already-running perf attempt (do not relaunch it). If that
# attempt, or a later same-RUN_ID resume, exits nonzero because of the known
# 120s Playwright waitForFunction timeout flake, auto-resumes perf (max 14
# additional launches). Then runs contact and preview. Stops on port loss,
# lock/freeze failures, or any non-timeout error.
set -euo pipefail
cd /workspace/shawu

export TZ=Asia/Shanghai
export NODE_PATH=/home/box/opt/test-tools/node_modules
export PLAYWRIGHT_BROWSERS_PATH=/home/box/opt/playwright-browsers
export PYTHONDONTWRITEBYTECODE=1

RUN_ID=${RUN_ID:-m10-region5-20261119T021341364667010Z}
export M10_RESULTS="/workspace/shawu/m10-work/results/$RUN_ID"
R=$M10_RESULTS
MAX_RESUMES=${MAX_RESUMES:-14}
WATCH_PID=${WATCH_PID:-682129}
WATCH_ATTEMPT=${WATCH_ATTEMPT:-$R/attempts/perf-20261119T043611589292372Z-682129}

DIR=m10-work/outer-runs
LOG=$DIR/m10-region5-watch-resume.log
STATUS=$DIR/m10-region5-watch-resume.status.json
BLOCK=$DIR/m10-region5-watch-resume.blocker.txt
mkdir -p "$DIR" "$R"

resumes=${RESUMES_USED:-0}
phase=watch-current-perf
note='starting'

ts() { date --iso-8601=seconds; }

# Logs go to the log file and stderr only. Stdout is reserved for
# launch_stage to print the attempt path (so $(launch_stage) is a dir).
log() {
  printf '%s %s\n' "$(ts)" "$*" | tee -a "$LOG" >&2
}

write_status() {
  local running=0
  if [[ -n ${runner_pid:-} ]] && kill -0 "$runner_pid" 2>/dev/null; then running=1; fi
  python3 - "$STATUS" "$RUN_ID" "$phase" "$note" "$resumes" "$MAX_RESUMES" "${runner_pid:-}" "$running" <<'PY'
import json, sys
from datetime import datetime, timezone
from pathlib import Path

status_path, run_id, phase, note, resumes, max_resumes, runner_pid, running = sys.argv[1:]
r = Path("/workspace/shawu/m10-work/results") / run_id
inv = {"expected": 252, "complete": None, "remaining": None}
try:
    import os, subprocess
    env = os.environ.copy()
    env["NODE_PATH"] = "/home/box/opt/test-tools/node_modules"
    env["TZ"] = "Asia/Shanghai"
    out = subprocess.check_output(
        ["node", "m10-work/scripts/region5-perf.cjs", "--inventory"],
        cwd="/workspace/shawu", env=env, text=True, stderr=subprocess.STDOUT, timeout=60)
    for line in out.splitlines():
        if "perf inventory" in line:
            inv = json.loads(line.split("perf inventory", 1)[1].strip())
            break
except Exception as e:
    inv["error"] = str(e)

def exists(p):
    return (r / p).is_file()

payload = {
    "updated": datetime.now().astimezone().isoformat(timespec="seconds"),
    "runId": run_id,
    "phase": phase,
    "note": note,
    "resumesUsed": int(resumes),
    "maxResumes": int(max_resumes),
    "runnerPid": int(runner_pid) if runner_pid.isdigit() else None,
    "runnerAlive": bool(int(running)),
    "inventory": inv,
    "qaDone": exists("qa.done"),
    "perfDone": exists("perf.done"),
    "contactDone": exists("contact.done"),
    "previewDone": exists("preview.done"),
    "portStop": exists("port-stop.txt"),
}
Path(status_path).write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
PY
}

ports_up() {
  python3 - <<'PY'
import socket, sys
for port in (38811, 8765):
    try:
        with socket.create_connection(("127.0.0.1", port), timeout=2):
            pass
    except OSError as e:
        print(f"listener {port} unavailable ({e})")
        sys.exit(1)
PY
}

wait_pid() {
  local pid=$1
  [[ -n $pid ]] || return 0
  while kill -0 "$pid" 2>/dev/null; do
    write_status || true
    sleep 10
  done
}

wait_attempt_exit() {
  local attempt=$1 pid=${2:-}
  if [[ -n $attempt && -f $attempt/runner.pid ]]; then
    pid=$(tr -d " \n" < "$attempt/runner.pid")
  fi
  if [[ -n $pid ]]; then
    wait_pid "$pid"
  fi
  local i
  for i in $(seq 1 90); do
    if [[ -f $attempt/exit-code.txt ]]; then
      cat "$attempt/exit-code.txt"
      return 0
    fi
    sleep 1
  done
  echo "timeout waiting for $attempt/exit-code.txt" >&2
  return 1
}

is_timeout_flake() {
  local attempt=$1 rc=$2
  [[ $rc == 1 ]] || return 1
  [[ ! -e $R/port-stop.txt && ! -e $attempt/port-stop.txt ]] || return 1
  [[ -f $attempt/stage.log ]] || return 1
  if rg -q 'Frozen bytes differ|Freeze changed|Invalid perf sample|Formal invariant failed|Forbidden stairs row|Served bytes differ|REQUIRED_PORT_UNAVAILABLE' "$attempt/stage.log"; then
    return 1
  fi
  rg -q 'page\.waitForFunction: Timeout 120000ms exceeded' "$attempt/stage.log" \
    && rg -q "name: 'TimeoutError'" "$attempt/stage.log"
}

launch_stage() {
  local stage=$1
  log "launch $stage (resume count $resumes/$MAX_RESUMES)"
  # Give the previous flock holders a moment to close FDs.
  sleep 2
  ports_up
  nohup env SUPERVISOR_CONFIRMED_EXCLUSIVE=1 \
    bash m10-work/scripts/run-region5-outer.sh "$stage" "$RUN_ID" \
    </dev/null >>"$R/$stage.nohup.log" 2>&1 &
  local pid=$!
  printf '%s\n' "$pid" > "$R/$stage.launch.pid"
  runner_pid=$pid
  # latest-attempt is written by the runner shortly after start
  local i attempt=
  for i in $(seq 1 60); do
    if [[ -f $R/$stage.latest-attempt ]]; then
      attempt=$(cat "$R/$stage.latest-attempt")
      if [[ -d $attempt && -f $attempt/runner.pid ]] && [[ $(cat "$attempt/runner.pid") == "$pid" ]]; then
        break
      fi
    fi
    sleep 0.5
  done
  if [[ -z ${attempt:-} || ! -d $attempt ]]; then
    attempt=$(cat "$R/$stage.latest-attempt" 2>/dev/null || true)
  fi
  log "launched $stage pid=$pid attempt=${attempt:-unknown}"
  WATCH_ATTEMPT=${attempt:-}
  runner_pid=$pid
}

block() {
  phase=blocked
  note="$*"
  write_status || true
  printf '%s\n%s\n' "$(ts)" "$*" | tee "$BLOCK" | tee -a "$LOG"
  exit 1
}

finish_ok() {
  phase=complete
  note="$*"
  write_status
  log "COMPLETE $*"
}

# --- perf: wait for the live attempt, then resume on the known flake ---
phase=watch-current-perf
runner_pid=$WATCH_PID
note="watching existing perf PID $WATCH_PID; will not relaunch it"
log "watch-resume start RUN_ID=$RUN_ID watch_pid=$WATCH_PID attempt=$WATCH_ATTEMPT max_resumes=$MAX_RESUMES"
write_status

if [[ -f $R/perf.done ]]; then
  log "perf already done; skip to contact/preview"
else
  if kill -0 "$WATCH_PID" 2>/dev/null || [[ ! -f $WATCH_ATTEMPT/exit-code.txt ]]; then
    log "waiting for current perf attempt to finish (PID $WATCH_PID)"
    rc=$(wait_attempt_exit "$WATCH_ATTEMPT" "$WATCH_PID") || block "Current perf attempt did not write an exit code"
  else
    rc=$(cat "$WATCH_ATTEMPT/exit-code.txt")
  fi
  log "current perf attempt exit=$rc"

  while true; do
    if [[ -f $R/perf.done && ${rc:-1} == 0 ]]; then
      log "perf passed"
      break
    fi
    if [[ -e $R/port-stop.txt ]]; then
      block "Port stop recorded; not auto-resuming. $(tr '\n' ' ' < "$R/port-stop.txt")"
    fi
    if ! is_timeout_flake "${WATCH_ATTEMPT}" "${rc:-}"; then
      # If a later attempt is the one that just finished, WATCH_ATTEMPT was updated.
      block "Perf exited $rc with a non-timeout error (or missing flake signature). Not auto-resuming. See ${WATCH_ATTEMPT}/stage.log"
    fi
    if (( resumes >= MAX_RESUMES )); then
      block "Perf timeout flake recurred after $resumes resumes (cap $MAX_RESUMES). Inventory left incomplete."
    fi
    if ! ports_up; then
      block "Listeners 38811/8765 not both up; not auto-resuming."
    fi
    resumes=$((resumes + 1))
    phase=resume-perf
    note="auto-resume $resumes/$MAX_RESUMES after 120s waitForFunction timeout"
    write_status
    launch_stage perf
    [[ -n ${WATCH_ATTEMPT:-} && -d $WATCH_ATTEMPT ]] || block "Resume $resumes launched but latest attempt dir is missing (${WATCH_ATTEMPT:-empty})"
    rc=$(wait_attempt_exit "$WATCH_ATTEMPT" "$runner_pid") || block "Resume $resumes did not write an exit code"
    log "resume $resumes exit=$rc attempt=$WATCH_ATTEMPT"
  done
fi

# --- contact then preview ---
if [[ ! -f $R/qa.done ]]; then
  block "QA is not done; refusing contact/preview"
fi
if [[ ! -f $R/perf.done ]]; then
  block "Perf is not done; refusing contact/preview"
fi

if [[ ! -f $R/contact.done ]]; then
  phase=contact
  note="launching contact"
  write_status
  launch_stage contact
  [[ -n ${WATCH_ATTEMPT:-} && -d $WATCH_ATTEMPT ]] || block "Contact launched but latest attempt dir is missing (${WATCH_ATTEMPT:-empty})"
  rc=$(wait_attempt_exit "$WATCH_ATTEMPT" "$runner_pid") || block "Contact did not write an exit code"
  log "contact exit=$rc"
  [[ $rc == 0 && -f $R/contact.done && ! -e $R/port-stop.txt ]] || block "Contact failed (exit $rc)"
  [[ -s $R/contact-verified.png ]] || block "contact-verified.png missing"
  if [[ ! -e shots/m10_region5_contact.png ]]; then
    ln -T -- "$R/contact-verified.png" shots/m10_region5_contact.png
  fi
  cmp "$R/contact-verified.png" shots/m10_region5_contact.png || block "Published contact sheet differs from verified PNG"
  log "contact published shots/m10_region5_contact.png"
else
  log "contact already done"
fi

if [[ ! -f $R/preview.done ]]; then
  phase=preview
  note="launching preview"
  write_status
  launch_stage preview
  [[ -n ${WATCH_ATTEMPT:-} && -d $WATCH_ATTEMPT ]] || block "Preview launched but latest attempt dir is missing (${WATCH_ATTEMPT:-empty})"
  rc=$(wait_attempt_exit "$WATCH_ATTEMPT" "$runner_pid") || block "Preview did not write an exit code"
  log "preview exit=$rc"
  [[ $rc == 0 && -f $R/preview.done && ! -e $R/port-stop.txt ]] || block "Preview failed (exit $rc)"
  [[ -f m10-work/region5_preview.webm ]] || block "region5_preview.webm missing"
  bytes=$(stat -c '%s' m10-work/region5_preview.webm)
  (( bytes < 25000000 )) || block "Preview is $bytes bytes (must be < 25000000)"
  log "preview ready m10-work/region5_preview.webm bytes=$bytes"
else
  log "preview already done"
fi

phase=complete
note="perf/contact/preview complete; supervisor can write REPORT_region5_zh.md"
write_status
log "watch-resume finished successfully (resumes used: $resumes)"
exit 0
