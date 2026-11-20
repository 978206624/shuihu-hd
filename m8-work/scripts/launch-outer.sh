#!/bin/bash
set -euo pipefail
cd /workspace/shawu
[[ "${SUPERVISOR_CONFIRMED_EXCLUSIVE:-0}" == 1 ]] || { echo 'After Codex exits, inspect processes and explicitly set SUPERVISOR_CONFIRMED_EXCLUSIVE=1'; exit 1; }
export M8_RESULTS="${M8_RESULTS:-/workspace/shawu/m8-work/results/outer-$(date -u +%Y%m%dT%H%M%SZ)}"
mkdir -p m8-work/results
[[ ! -e "$M8_RESULTS" && ! -e "$M8_RESULTS.launch.log" ]] || { echo 'Use a NEW result path; resume with run-outer.sh to skip completed stages'; exit 1; }
nohup env M8_RESULTS="$M8_RESULTS" SUPERVISOR_CONFIRMED_EXCLUSIVE=1 bash m8-work/scripts/run-outer.sh all > "$M8_RESULTS.launch.log" 2>&1 < /dev/null &
outer_pid=$!
printf '%s\n' "$outer_pid" > "$M8_RESULTS.launch.pid"
printf '%s\n' "$M8_RESULTS" > m8-work/OUTER_RESULTS_PATH.txt
export M8_OUTER_PID="$outer_pid"
python3 - <<'PY'
import os,json
from pathlib import Path
p=Path(os.environ['M8_RESULTS'])
p.with_suffix('.launch.json').write_text(json.dumps({'results':str(p),'log':str(p)+'.launch.log','pidFile':str(p)+'.launch.pid','pid':int(os.environ['M8_OUTER_PID']),'command':'bash m8-work/scripts/run-outer.sh all','exclusiveConfirmed':True},indent=2)+'\n')
print('LAUNCHED',os.environ['M8_OUTER_PID'],p)
PY
