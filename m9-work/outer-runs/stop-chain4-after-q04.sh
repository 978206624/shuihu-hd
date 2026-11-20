#!/usr/bin/env bash
set -euo pipefail
export TZ=America/New_York
Q=/workspace/shawu/m9-work/play/m9-huangnigang-s01-front-q04
echo "$(date --iso-8601=seconds) waiting for front-q04 to finish before stopping chain4"
for i in $(seq 1 300); do
  if [[ -f "$Q/result.json" ]] && ! pgrep -af 'browser-play.cjs m9-huangnigang-s01-front-q04|run-play.sh browser m9-huangnigang-s01-front-q04' | grep -v pgrep | grep -q .; then
    echo "$(date --iso-8601=seconds) front-q04 finished; stopping chain4"
    break
  fi
  sleep 2
done
# Do not kill an in-flight q04; only the chain script.
pkill -f '/workspace/shawu/m9-work/outer-runs/continue-huangnigang-chain4.sh' || true
sleep 1
# If chain4 already spawned q05, leave that play running and report.
echo '==== after stop ===='
pgrep -af 'continue-huangnigang-chain|browser-play.cjs m9-huangnigang|run-play.sh browser m9' | grep -v pgrep || echo 'no chain4/browser play'
date --iso-8601=seconds
