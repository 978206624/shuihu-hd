#!/usr/bin/env bash
set -euo pipefail
export TZ=America/New_York
cd /workspace/shawu
echo "$(date --iso-8601=seconds) official evidence waiter started (pid $$)"
# Let any leftover front-q05 (or later leftover) finish; do not kill mid-play.
while pgrep -af 'browser-play.cjs m9-huangnigang-s01-front-|run-play.sh browser m9-huangnigang-s01-front-' | grep -v pgrep | grep -q .; do
  sleep 5
done
# Confirm chain4 is dead so it cannot start another page.
if pgrep -af 'continue-huangnigang-chain4.sh' | grep -v pgrep | grep -q .; then
  pkill -f '/workspace/shawu/m9-work/outer-runs/continue-huangnigang-chain4.sh' || true
  sleep 1
fi
if pgrep -af 'browser-play.cjs m9-|run-play.sh browser m9-' | grep -v pgrep | grep -q .; then
  echo "$(date --iso-8601=seconds) another m9 browser play is still running; not launching evidence"
  pgrep -af 'browser-play.cjs m9-|run-play.sh browser m9-' | grep -v pgrep || true
  exit 1
fi
tag=m9-huangnigang-official-evidence
chain=m9-work/outer-runs/${tag}-chain.json
if [[ -e m9-work/play/$tag || -e m9-work/outer-runs/$tag ]]; then
  echo "$(date --iso-8601=seconds) refusing to overwrite $tag"
  exit 1
fi
cp -n m9-work/outer-runs/huangnigang-inn-actions.json "$chain"
echo "$(date --iso-8601=seconds) launching one official-start browser replay $tag ($(python3 -c 'import json;print(len(json.load(open("m9-work/outer-runs/huangnigang-inn-actions.json"))))') actions)"
printf '\n- %s Launching one official browser evidence replay %s of the native-found 262-action inn chain. Do not relaunch.\n' "$(date --iso-8601=seconds)" "$tag" >> m9-work/progress.md
setsid --wait bash m9-work/outer-runs/run-play.sh browser "$tag" "$chain"
# show end
source m9-work/outer-runs/m9_play.supervisor.sh
m9_show "$tag" | tee m9-work/outer-runs/${tag}-obs.json
echo "$(date --iso-8601=seconds) official evidence replay exit $?"
