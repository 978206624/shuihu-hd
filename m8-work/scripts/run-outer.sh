#!/bin/bash
set -euo pipefail
cd /workspace/shawu
export NODE_PATH=/home/box/opt/test-tools/node_modules
export PLAYWRIGHT_BROWSERS_PATH=/home/box/opt/playwright-browsers
: "${M8_RESULTS:?Set an absolute m8-work/results directory}"
: "${SUPERVISOR_CONFIRMED_EXCLUSIVE:?Confirm Codex/art/QA/heavy jobs have ended}"
[[ "$SUPERVISOR_CONFIRMED_EXCLUSIVE" == 1 ]] || exit 1
mode=${1:-all}
[[ "$mode" == all || "$mode" == qa || "$mode" == perf || "$mode" == deliver || "$mode" == resume ]] || exit 1
python3 - <<'PY'
from pathlib import Path
import os
p=Path(os.environ['M8_RESULTS']);root=Path('/workspace/shawu/m8-work/results')
assert p.is_absolute() and root in p.resolve().parents,'Invalid results directory'
PY
mkdir -p "$M8_RESULTS"
exec 9>m7-work/stage-a/exclusive.lock
flock -n 9 || { echo 'Another QA/perf task holds exclusive lock'; exit 1; }
exec 8>m8-work/outer-exclusive.lock
flock -n 8 || { echo 'Another M8 outer task holds lock'; exit 1; }
if [[ "$mode" == resume ]]; then
  [[ -f "$M8_RESULTS/qa.done" && -s "$M8_RESULTS/qa/report.json" ]] || { echo 'Resume requires completed QA in the same result directory'; exit 1; }
  echo "Skip completed QA: $M8_RESULTS"
fi
printf '%s\n' "$$" > "$M8_RESULTS/runner.pid"
python3 - "$mode" <<'PY'
import os,json,datetime
import sys
from pathlib import Path
p=Path(os.environ['M8_RESULTS'])/'launches.jsonl'
with p.open('a') as f:f.write(json.dumps({'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'pid':os.getppid(),'results':os.environ['M8_RESULTS'],'mode':sys.argv[1],'exclusiveConfirmed':True})+'\n')
PY
trap 'rc=$?; printf "\nOuter %s EXIT_%s: %s; inspect measured reports; acceptance pending review.\n" "$mode" "$rc" "$M8_RESULTS" >> m8-work/progress.md; printf "%s\n" "$rc" > "$M8_RESULTS/exit-code.txt"' EXIT
gate_suffix=
if [[ "$mode" == resume ]]; then gate_suffix=-resume; fi
node -e "require('./m8-work/scripts/common.cjs').proxy().catch(e=>{console.error(e);process.exitCode=1;})" >> "$M8_RESULTS/ports$gate_suffix.log" 2>&1
python3 m8-work/scripts/offline-check.py --verify-only >> "$M8_RESULTS/offline$gate_suffix.log" 2>&1
ps -eo pid,ppid,pcpu,comm >> "$M8_RESULTS/processes-before$gate_suffix.txt"
run_once() {
  local name=$1 log
  if [[ -f "$M8_RESULTS/$name.done" ]]; then
    echo "Skip validated $name"
  else
    log="$M8_RESULTS/$name.log"
    if [[ "$name" == perf && -e "$log" ]]; then log="$M8_RESULTS/perf-resume.log"; fi
    node "m8-work/scripts/$name.cjs" >> "$log" 2>&1
    touch "$M8_RESULTS/$name.done"
    printf '\nOuter stage %s finished: %s\n' "$name" "$M8_RESULTS" >> m8-work/progress.md
  fi
}
if [[ "$mode" == all || "$mode" == qa ]]; then run_once qa; fi
if [[ "$mode" == all || "$mode" == perf || "$mode" == resume ]]; then
  [[ -f "$M8_RESULTS/qa.done" ]] || { echo 'QA must pass before perf'; exit 1; }
  ps -eo pid,ppid,pcpu,comm >> "$M8_RESULTS/processes-before-perf$gate_suffix.txt"
  run_once perf
  ps -eo pid,ppid,pcpu,comm > "$M8_RESULTS/processes-after-perf.txt"
fi
if [[ "$mode" == all || "$mode" == deliver || "$mode" == resume ]]; then
  [[ -f "$M8_RESULTS/qa.done" && -f "$M8_RESULTS/perf.done" ]] || exit 1
  if [[ "$mode" == resume && -d "$M8_RESULTS/recording" && ! -f "$M8_RESULTS/record.done" ]]; then
    echo 'Interrupted recording exists; retain it for supervisor review'
    exit 1
  fi
  run_once record
  if [[ ! -f "$M8_RESULTS/contact.done" ]]; then python3 m8-work/scripts/contact.py > "$M8_RESULTS/contact.log" 2>&1; touch "$M8_RESULTS/contact.done"; fi
  if [[ ! -f "$M8_RESULTS/video.done" ]]; then
    [[ ! -e m8-work/region3_preview.webm ]] || { echo 'Refusing to replace preview'; exit 1; }
    pending=$(mktemp --suffix=.webm "$M8_RESULTS/preview-XXXXXX")
    ffmpeg -hide_banner -loglevel warning -y -i "$M8_RESULTS/recording/region_raw.webm" -an -c:v libvpx-vp9 -b:v 1400k -maxrate 1800k -bufsize 2800k -crf 32 "$pending" > "$M8_RESULTS/encode.log" 2>&1
    ffprobe -v quiet -show_format -show_streams -of json "$pending" > "$M8_RESULTS/preview-probe.json"
    python3 - "$pending" <<'PY'
from pathlib import Path
import os,json,sys
p=Path(sys.argv[1]);assert 0<p.stat().st_size<25_000_000
probe=json.loads((Path(os.environ['M8_RESULTS'])/'preview-probe.json').read_text());assert not any(x['codec_type']=='audio' for x in probe['streams'])
assert float(probe['format']['duration'])>=52,'Do not compress time or lose excerpts'
PY
    mv -n "$pending" m8-work/region3_preview.webm
    [[ ! -e "$pending" ]] || { echo 'Preview destination appeared during encoding'; exit 1; }
    touch "$M8_RESULTS/video.done"
  fi
  if [[ ! -f "$M8_RESULTS/summary.done" ]]; then
    set +e
    python3 m8-work/scripts/summarize.py > "$M8_RESULTS/summary.log" 2>&1
    summary_rc=$?
    set -e
    [[ "$summary_rc" == 0 || "$summary_rc" == 2 ]] || exit "$summary_rc"
    touch "$M8_RESULTS/summary.done"
    printf '%s\n' "$summary_rc" > "$M8_RESULTS/acceptance-exit.txt"
  fi
  python3 m8-work/scripts/offline-check.py --verify-only > "$M8_RESULTS/offline-final.log" 2>&1
  exit "$(cat "$M8_RESULTS/acceptance-exit.txt")"
fi
