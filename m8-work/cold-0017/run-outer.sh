#!/bin/bash
set -euo pipefail
cd /workspace/shawu
export NODE_PATH=/home/box/opt/test-tools/node_modules
export PLAYWRIGHT_BROWSERS_PATH=/home/box/opt/playwright-browsers
[[ ${SUPERVISOR_CONFIRMED_EXCLUSIVE:-} == 1 ]]
[[ ${M8_RESULTS:-} =~ ^/workspace/shawu/m8-work/results/outer-cold-0017-[0-9]{8}T[0-9]{15}Z$ ]]
pgid=$(ps -o pgid= -p "$$")
[[ ${pgid//[[:space:]]/} == "$$" ]] || { echo 'Launch from a dedicated setsid process group'; exit 1; }
for port in 38811 8765; do
  listener=$(ss -Hltn "sport = :$port")
  [[ -n "$listener" ]] || { echo "Required listener missing on $port"; exit 1; }
done

exec 9>>m7-work/stage-a/exclusive.lock
flock -n 9 || { echo 'Stage A QA/perf lock is held'; exit 1; }
exec 8>>m8-work/outer-exclusive.lock
flock -n 8 || { echo 'M8 outer lock is held'; exit 1; }
mkdir -- "$M8_RESULTS"
printf '%s\n' "$$" > "$M8_RESULTS/runner.pid"
stage=preflight
watcher=
checkpoint() {
  printf '%s cold/00-17 outer %s %s\n' "$(date -u +%FT%TZ)" "$1" "$M8_RESULTS" |
    tee -a m8-work/progress.md
}
finish() {
  local rc=$?
  trap - EXIT TERM INT
  if [[ -n "$watcher" ]]; then
    kill "$watcher" 2>/dev/null || true
    wait "$watcher" 2>/dev/null || true
  fi
  printf '%d\n' "$rc" > "$M8_RESULTS/exit-code.txt"
  checkpoint "EXIT_$rc at $stage"
  exit "$rc"
}
trap finish EXIT
trap 'exit 143' TERM
trap 'exit 130' INT
checkpoint 'preflight started'
node m8-work/cold-0017/check.cjs watch "$$" > "$M8_RESULTS/ports.log" 2>&1 &
watcher=$!
python3 m8-work/scripts/offline-check.py --verify-only > "$M8_RESULTS/offline.log" 2>&1
node m8-work/cold-0017/check.cjs verify >> "$M8_RESULTS/offline.log" 2>&1

stage=qa
checkpoint 'formal QA started'
node m8-work/cold-0017/check.cjs qa > "$M8_RESULTS/qa.log" 2>&1
node m8-work/cold-0017/check.cjs verify >> "$M8_RESULTS/qa.log" 2>&1
node m8-work/cold-0017/check.cjs qa-check > "$M8_RESULTS/qa-check.json"
touch "$M8_RESULTS/qa.done"
checkpoint 'formal QA and coverage passed'

stage=perf
checkpoint '00-17 cold and legacy perf started'
node m8-work/cold-0017/check.cjs perf > "$M8_RESULTS/perf.log" 2>&1
touch "$M8_RESULTS/perf.done"
checkpoint '18 focused perf samples saved'

stage=decision
node m8-work/cold-0017/check.cjs decide > "$M8_RESULTS/decision.log" 2>&1
checkpoint 'automated round gate met'
