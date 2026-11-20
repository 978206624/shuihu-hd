#!/usr/bin/env bash
# Supervisor host only. Run one stage under all three existing-workflow locks.
set -euo pipefail
cd /workspace/shawu

stage=${1:-}
tag=${2:-}
if [[ $# != 2 || ! $stage =~ ^(qa|perf|contact|preview)$ || ! $tag =~ ^[A-Za-z0-9][A-Za-z0-9._-]*$ ]]; then
  echo 'Usage: run-region4-outer.sh qa|perf|contact|preview RUN_ID' >&2
  exit 64
fi
[[ ${SUPERVISOR_CONFIRMED_EXCLUSIVE:-} == 1 ]] || {
  echo 'Confirm the supervisor host is exclusive before setting SUPERVISOR_CONFIRMED_EXCLUSIVE=1' >&2
  exit 64
}

export M9_RESULTS="/workspace/shawu/m9-work/results/$tag"
export NODE_PATH=/home/box/opt/test-tools/node_modules
export PLAYWRIGHT_BROWSERS_PATH=/home/box/opt/playwright-browsers
export PYTHONDONTWRITEBYTECODE=1

exec 9<m7-work/stage-a/exclusive.lock
flock -n 9 || { echo 'Stage A exclusive lock is held'; exit 75; }
exec 8<m8-work/outer-exclusive.lock
flock -n 8 || { echo 'M8 outer lock is held'; exit 75; }
exec 7>>m9-work/outer-exclusive.lock
flock -n 7 || { echo 'M9 outer lock is held'; exit 75; }

mkdir -p "$M9_RESULTS"
[[ $(realpath "$M9_RESULTS") == "$M9_RESULTS" ]] || exit 64
attempt="$M9_RESULTS/attempts/$stage-$(date -u +%Y%m%dT%H%M%S%NZ)-$$"
mkdir -p "$attempt/tmp"
export TMPDIR="$attempt/tmp"
export stage attempt
printf '%s\n' "$$" > "$attempt/runner.pid"
printf '%s\n' "$$" > "$M9_RESULTS/$stage.runner.pid"
printf '%s\n' "$attempt" > "$M9_RESULTS/$stage.latest-attempt"
printf 'Runner PID %s, attempt %s\n' "$$" "$attempt"

checkpoint() {
  printf '\n- %s M9 outer %s %s. %s\n' "$(date --iso-8601=seconds)" "$tag" "$stage" "$1" |
    tee -a m9-work/progress.md
}

worker=
watcher=
finish() {
  local rc=$?
  trap - EXIT
  trap '' INT TERM USR1
  if [[ -n $watcher ]]; then
    kill "$watcher" 2>/dev/null || true
    wait "$watcher" 2>/dev/null || true
  fi
  if [[ -n $worker ]] && kill -0 -- "-$worker" 2>/dev/null; then
    kill -TERM -- "-$worker" 2>/dev/null || true
    for _ in {1..20}; do
      if ! kill -0 -- "-$worker" 2>/dev/null; then break; fi
      sleep .25
    done
    kill -KILL -- "-$worker" 2>/dev/null || true
    wait "$worker" 2>/dev/null || true
  fi
  if [[ -s "$attempt/port-stop.txt" ]]; then
    rc=69
    cp "$attempt/port-stop.txt" "$M9_RESULTS/port-stop.txt"
    cat "$attempt/port-stop.txt"
  fi
  if [[ $rc == 0 ]]; then
    touch "$M9_RESULTS/$stage.done"
  fi
  printf '%s\n' "$rc" > "$attempt/exit-code.txt"
  printf '%s\n' "$rc" > "$M9_RESULTS/$stage.exit-code.txt"
  checkpoint "Exit $rc. Attempt $attempt"
  exit "$rc"
}
trap finish EXIT
trap 'exit 69' USR1
trap 'exit 130' INT
trap 'exit 143' TERM

if [[ -e "$M9_RESULTS/port-stop.txt" ]]; then
  cat "$M9_RESULTS/port-stop.txt"
  [[ ${M9_RESUME_AFTER_PORT_STOP:-} == 1 ]] || exit 69
  checkpoint 'Supervisor acknowledged prior listener stop and authorized this resume'
  mv "$M9_RESULTS/port-stop.txt" "$attempt/prior-port-stop.txt"
fi
freeze=$(sha256sum m9-work/integration/outer-freeze.json)
if [[ -e "$M9_RESULTS/run-freeze.sha256" ]]; then
  [[ $(< "$M9_RESULTS/run-freeze.sha256") == "$freeze" ]] || { echo 'Freeze changed. Use a fresh run ID.'; exit 65; }
else
  printf '%s\n' "$freeze" > "$M9_RESULTS/run-freeze.sha256"
fi

port_monitor=$(cat <<'PY'
from datetime import datetime, timezone
from pathlib import Path
import os
import signal
import socket
import sys
import time

stage, stop, runner, mode = sys.argv[1:]
while True:
    for port in (38811, 8765):
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=1):
                pass
        except OSError as error:
            message = f"{datetime.now(timezone.utc).isoformat()} {stage} listener {port} unavailable ({error}). Stop and report."
            Path(stop).write_text(message + "\n")
            if mode == "watch":
                os.kill(int(runner), signal.SIGUSR1)
            raise SystemExit(69)
    if mode == "once":
        break
    time.sleep(1)
PY
)

run_stage() {
  ps -eo pid,ppid,pgid,pcpu,comm > "$attempt/processes-before.txt"
  node -e "require('./m9-work/scripts/outer-common.cjs').verifyFreeze()"
  python3 - <<'PY'
from hashlib import sha256
from http.client import HTTPConnection
from pathlib import Path
import json

hashes = json.loads(Path("m9-work/integration/outer-freeze.json").read_text())
prefix = "m9-work/runtime/"
checks = [p for p in hashes if p.startswith(prefix)]
server = HTTPConnection("127.0.0.1", 8765, timeout=15)
try:
    for path in checks:
        url = "/" + (prefix if path == prefix + "index.html" else path)
        server.request("GET", url, headers={"Cache-Control": "no-cache"})
        response = server.getresponse()
        data = response.read()
        if response.status != 200 or sha256(data).hexdigest() != hashes[path]:
            raise SystemExit(f"Served bytes differ for {url} (HTTP {response.status})")
finally:
    server.close()
print(f"HTTP verified {len(checks)} candidate runtime files")
PY
  if [[ -f "$M9_RESULTS/$stage.done" ]]; then
    echo "Already complete: $M9_RESULTS/$stage.done"
    return
  fi
  if [[ "$stage" != qa && ! -f "$M9_RESULTS/qa.done" ]]; then
    echo 'Complete formal QA in this run first'
    return 65
  fi
  case "$stage" in
    qa) node m9-work/scripts/region4-qa.cjs ;;
    perf)
      node m9-work/scripts/region4-perf.cjs
      python3 m9-work/scripts/region4-perf-summary.py
      ;;
    contact) python3 m9-work/scripts/region4-contact.py ;;
    preview) node m9-work/scripts/region4-preview.cjs ;;
  esac
  node -e "require('./m9-work/scripts/outer-common.cjs').verifyFreeze()"
}
export -f run_stage

checkpoint 'Preflight'
python3 -c "$port_monitor" "$stage/preflight" "$attempt/port-stop.txt" "$$" once
python3 -c "$port_monitor" "$stage/running" "$attempt/port-stop.txt" "$$" watch &
watcher=$!
setsid bash -c 'set -euo pipefail; run_stage' > "$attempt/stage.log" 2>&1 &
worker=$!
printf '%s\n' "$worker" > "$attempt/worker.pid"
status=0
wait "$worker" || status=$?
ps -eo pid,ppid,pgid,pcpu,comm > "$attempt/processes-after.txt"
if rg -o -m1 'REQUIRED_PORT_UNAVAILABLE (38811|8765)' "$attempt/stage.log" > "$attempt/script-port-errors.txt"; then
  if [[ ! -s "$attempt/port-stop.txt" ]]; then
    printf '%s %s %s. Stop and report.\n' "$(date --iso-8601=seconds)" "$stage"       "$(< "$attempt/script-port-errors.txt")" > "$attempt/port-stop.txt"
  fi
  exit 69
fi
[[ $status == 0 ]] || exit "$status"
python3 -c "$port_monitor" "$stage/postflight" "$attempt/port-stop.txt" "$$" once
