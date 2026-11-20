#!/usr/bin/env bash
set -euo pipefail
cd /workspace/shawu

if [[ $# -lt 2 || ! $2 =~ ^[a-zA-Z0-9_-]+$ ]]; then
  echo 'Usage: setsid --wait bash run-play.sh browser|native TAG [ARGS...]' >&2
  exit 64
fi
engine=$1
tag=$2
shift 2
case "$engine" in
  browser) command=(node m9-work/scripts/browser-play.cjs "$tag" "$@") ;;
  native)
    if [[ $# -lt 2 ]]; then
      echo 'Native play requires MODE SOURCE [ARGS...]' >&2
      exit 64
    fi
    mode=$1
    source_save=$2
    shift 2
    if [[ $mode == interact ]]; then
      command=(node m9-work/scripts/interact-survey.cjs "$source_save" "$tag" "$@")
    else
      command=(node m9-work/scripts/native-play.cjs "$mode" "$source_save" "$tag" "$@")
    fi
    ;;
  *) echo 'Use browser or native' >&2; exit 64 ;;
esac

group=$(ps -o pgid= -p "$$")
if [[ ${group//[[:space:]]/} != "$$" ]]; then
  echo 'Launch through setsid --wait so a port drop stops only this play run.' >&2
  exit 64
fi

run="m9-work/outer-runs/$tag"
mkdir -- "$run"
mkdir -- "$run/tmp"
export TZ=America/New_York
export NODE_PATH=/home/box/opt/test-tools/node_modules
export PLAYWRIGHT_BROWSERS_PATH=/home/box/opt/playwright-browsers
export TMPDIR="/workspace/shawu/$run/tmp"

checkpoint() {
  printf '\n- %s M9 outer %s %s (%s)\n' "$(date --iso-8601=seconds)" "$engine" "$tag" "$1" |
    tee -a m9-work/progress.md
}

watcher=
finish() {
  local status=$?
  trap - EXIT TERM INT
  if [[ -n $watcher ]]; then
    kill "$watcher" 2>/dev/null || true
    wait "$watcher" 2>/dev/null || true
  fi
  printf '%s\n' "$status" > "$run/exit-code.txt"
  checkpoint "exit $status"
  exit "$status"
}
trap finish EXIT
trap 'exit 143' TERM
trap 'exit 130' INT

missing_port() {
  local port listener
  for port in 38811 8765; do
    if ! listener=$(ss -Hltn "sport = :$port") || [[ -z $listener ]]; then
      printf '%s\n' "$port"
      return 0
    fi
  done
  return 1
}

record_stop() {
  local message="listener $1 unavailable at $2. Stop and report."
  printf '%s %s\n' "$(date --iso-8601=seconds)" "$message" > "$run/port-stop.txt"
  checkpoint "$message"
}

checkpoint 'listener preflight'
if port=$(missing_port); then
  record_stop "$port" preflight
  exit 69
fi

leader=$$
(
  while sleep 1; do
    if port=$(missing_port); then
      record_stop "$port" play
      kill -TERM -- "-$leader"
      exit 69
    fi
  done
) &
watcher=$!

checkpoint 'play started'
"${command[@]}" > "$run/play.log" 2>&1 &
play_pid=$!
wait "$play_pid"
if port=$(missing_port); then
  record_stop "$port" completion
  exit 69
fi
checkpoint 'play evidence written'
