#!/usr/bin/env bash
# Supervisor host only. Run one stage under the M7–M10 workflow locks.
set -euo pipefail
cd /workspace/shawu

stage=${1:-}
tag=${2:-}
if [[ $# != 2 || ! $stage =~ ^(qa|perf|contact|preview)$ || ! $tag =~ ^[A-Za-z0-9][A-Za-z0-9._-]*$ ]]; then
  echo 'Usage: run-region5-outer.sh qa|perf|contact|preview RUN_ID' >&2
  exit 64
fi
[[ ${SUPERVISOR_CONFIRMED_EXCLUSIVE:-} == 1 ]] || {
  echo 'Confirm the supervisor host is exclusive before setting SUPERVISOR_CONFIRMED_EXCLUSIVE=1' >&2
  exit 64
}

expected="/workspace/shawu/m10-work/results/$tag"
[[ ${M10_RESULTS:-$expected} == "$expected" ]] || {
  echo 'M10_RESULTS disagrees with RUN_ID' >&2
  exit 64
}
export M10_RESULTS="$expected"
export TZ=Asia/Shanghai
export NODE_PATH=/home/box/opt/test-tools/node_modules
export PLAYWRIGHT_BROWSERS_PATH=/home/box/opt/playwright-browsers
export PYTHONDONTWRITEBYTECODE=1

exec 9<m7-work/stage-a/exclusive.lock
flock -n 9 || { echo 'Stage A exclusive lock is held'; exit 75; }
exec 8<m8-work/outer-exclusive.lock
flock -n 8 || { echo 'M8 outer lock is held'; exit 75; }
exec 7<m9-work/outer-exclusive.lock
flock -n 7 || { echo 'M9 outer lock is held'; exit 75; }
exec 6>>m10-work/outer-exclusive.lock
flock -n 6 || { echo 'M10 outer lock is held'; exit 75; }

mkdir -p "$M10_RESULTS"
[[ $(realpath "$M10_RESULTS") == "$M10_RESULTS" ]] || exit 64
attempt="$M10_RESULTS/attempts/$stage-$(date -u +%Y%m%dT%H%M%S%NZ)-$$"
mkdir -p "$attempt/tmp"
export TMPDIR="$attempt/tmp"
export stage attempt
printf '%s\n' "$$" > "$attempt/runner.pid"
printf '%s\n' "$$" > "$M10_RESULTS/$stage.runner.pid"
printf '%s\n' "$attempt" > "$M10_RESULTS/$stage.latest-attempt"
printf 'Runner PID %s, attempt %s\n' "$$" "$attempt"

checkpoint() {
  printf '\n- %s M10 outer %s %s. %s\n' "$(date --iso-8601=seconds)" "$tag" "$stage" "$1" |
    tee -a m10-work/progress.md
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
    cp "$attempt/port-stop.txt" "$M10_RESULTS/port-stop.txt"
    cat "$attempt/port-stop.txt"
  fi
  if [[ $rc == 0 ]]; then
    touch "$M10_RESULTS/$stage.done"
  fi
  printf '%s\n' "$rc" > "$attempt/exit-code.txt"
  printf '%s\n' "$rc" > "$M10_RESULTS/$stage.exit-code.txt"
  checkpoint "Exit $rc. Attempt $attempt"
  exit "$rc"
}
trap finish EXIT
trap 'exit 69' USR1
trap 'exit 130' INT
trap 'exit 143' TERM

if [[ -e "$M10_RESULTS/port-stop.txt" ]]; then
  cat "$M10_RESULTS/port-stop.txt"
  [[ ${M10_RESUME_AFTER_PORT_STOP:-} == 1 ]] || exit 69
  checkpoint 'Supervisor acknowledged prior listener stop and authorized this resume'
  mv "$M10_RESULTS/port-stop.txt" "$attempt/prior-port-stop.txt"
fi
freeze=$(sha256sum m10-work/integration/outer-freeze.json)
if [[ -e "$M10_RESULTS/run-freeze.sha256" ]]; then
  [[ $(< "$M10_RESULTS/run-freeze.sha256") == "$freeze" ]] || { echo 'Freeze changed. Use a fresh run ID.'; exit 65; }
else
  printf '%s\n' "$freeze" > "$M10_RESULTS/run-freeze.sha256"
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
  node -e "require('./m10-work/scripts/outer-common.cjs').verifyFreeze()"
  python3 - <<'PY'
from hashlib import sha256
from http.client import HTTPConnection
from pathlib import Path
import json

hashes = json.loads(Path("m10-work/integration/outer-freeze.json").read_text())
prefixes = ("m10-work/runtime/", "m9-work/runtime/")
checks = [p for p in hashes if p.startswith(prefixes)]
server = HTTPConnection("127.0.0.1", 8765, timeout=15)
try:
    for path in checks:
        url = "/" + path.removesuffix("index.html")
        server.request("GET", url, headers={"Cache-Control": "no-cache"})
        response = server.getresponse()
        data = response.read()
        if response.status != 200 or sha256(data).hexdigest() != hashes[path]:
            raise SystemExit(f"Served bytes differ for {url} (HTTP {response.status})")
finally:
    server.close()
print(f"HTTP verified {len(checks)} M9 and M10 runtime files")
PY
  if [[ -f "$M10_RESULTS/$stage.done" ]]; then
    echo "Already complete: $M10_RESULTS/$stage.done"
    return
  fi
  if [[ "$stage" != qa && ! -f "$M10_RESULTS/qa.done" ]]; then
    echo 'Complete formal QA in this run first'
    return 65
  fi
  case "$stage" in
    qa) node m10-work/scripts/region5-qa.cjs ;;
    perf)
      node m10-work/scripts/region5-perf.cjs
      python3 m10-work/scripts/region5-perf-summary.py
      ;;
    contact) python3 m10-work/scripts/region5-contact.py ;;
    preview) node m10-work/scripts/region5-preview.cjs ;;
  esac
  node -e "require('./m10-work/scripts/outer-common.cjs').verifyFreeze()"
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
