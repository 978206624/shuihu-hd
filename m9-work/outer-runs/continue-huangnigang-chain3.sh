#!/usr/bin/env bash
# Resume official-start play from the successful 00-24 arrival (town-cont).
# Does not capture mixed stdout as the next base tag.
set -euo pipefail
cd /workspace/shawu
export TZ=America/New_York
export NODE_PATH=/home/box/opt/test-tools/node_modules
export PLAYWRIGHT_BROWSERS_PATH=/home/box/opt/playwright-browsers
export PYTHONUNBUFFERED=1

LOCK=m9-work/outer-runs/continue-huangnigang-chain3.lock
LOG=m9-work/outer-runs/continue-huangnigang-chain3.log
BLOCK=m9-work/outer-runs/HUANGNIGANG_BLOCKER.md
exec > >(stdbuf -oL tee -a "$LOG") 2>&1
exec 9>"$LOCK"
if ! flock -n 9; then
  echo "$(date --iso-8601=seconds) chain3 already running; exiting"
  exit 0
fi

# shellcheck disable=SC1091
source m9-work/outer-runs/continue-huangnigang-lib.sh

load_base() { cat m9-work/outer-runs/last-base-tag.txt; }

progress "huangnigang chain3 started (pid $$). Resuming from m9-huangnigang-s01-town-cont (00-24 4,14 story 12). Do not relaunch living or completed tags."
require_ports
tag_ok m9-huangnigang-s01-town-cont || blocker "expected successful 00-24 tag m9-huangnigang-s01-town-cont"

BASE=m9-huangnigang-s01-town-cont
save_base_tag "$BASE"
OBS=m9-work/outer-runs/chain3-current-obs.json
show_to "$BASE" "$OBS"
progress "resume 00-24: cell=$(obs_py get "$OBS" cell) entry=$(obs_py get "$OBS" entry) story=$(obs_py get "$OBS" story) bank=$(obs_py get "$OBS" bank)"
status_update "Chain3 is resuming official-start play from 00-24 (4,14), tag $BASE. Next: inn door to 00-2b, front talk (story 13), rear 00-2c talk (story 14). Do not relaunch town-cont. 38811/8765 must stay up."

# Inn door
walk_leg m9-huangnigang-s01-inn "$BASE" "uuuuuuuurruu wait" 00-2b 3,8 12
BASE=$(load_base)
show_to "$BASE" "$OBS"
progress "arrived 00-2b inn front: cell=$(obs_py get "$OBS" cell) story=$(obs_py get "$OBS" story) tag=$BASE"

play_new m9-huangnigang-s01-front-talk "$BASE" ruuuuu page
BASE=m9-huangnigang-s01-front-talk
show_to "$BASE" "$OBS"
if (( $(obs_py get "$OBS" story) < 13 )); then
  page_until_story "$BASE" m9-huangnigang-s01-front 13 12
  BASE=$(load_base)
  show_to "$BASE" "$OBS"
fi
if ! obs_py field "$OBS"; then
  recover_to_field "$BASE" m9-huangnigang-s01-front-end
  BASE=$(load_base)
  show_to "$BASE" "$OBS"
fi
(( $(obs_py get "$OBS" story) >= 13 )) || blocker "front talk ended without story 13 (obs $OBS)"
obs_py daa1_bit6 "$OBS" || progress "WARNING: story advanced but DAA1 bit 6 is not set ($(obs_py get "$OBS" DAA1))"
progress "front talk done: story=$(obs_py get "$OBS" story) DAA1=$(obs_py get "$OBS" DAA1) cell=$(obs_py get "$OBS" cell) tag=$BASE"
status_update "Front inn talk reached story $(obs_py get "$OBS" story) on 00-2b (tag $BASE). Continuing to the rear room for story 14. Official-start chain3 still running. GPT/integration not started."

walk_leg m9-huangnigang-s01-rear "$BASE" "rurrruu wait" 00-2c 6,8 13
BASE=$(load_base)
show_to "$BASE" "$OBS"
progress "arrived 00-2c rear: cell=$(obs_py get "$OBS" cell) story=$(obs_py get "$OBS" story) tag=$BASE"

play_new m9-huangnigang-s01-rear-talk "$BASE" ulluuu page
BASE=m9-huangnigang-s01-rear-talk
show_to "$BASE" "$OBS"
if (( $(obs_py get "$OBS" story) < 14 )); then
  page_until_story "$BASE" m9-huangnigang-s01-rear 14 12
  BASE=$(load_base)
  show_to "$BASE" "$OBS"
fi
if ! obs_py field "$OBS"; then
  recover_to_field "$BASE" m9-huangnigang-s01-rear-end
  BASE=$(load_base)
  show_to "$BASE" "$OBS"
fi
(( $(obs_py get "$OBS" story) >= 14 )) || blocker "rear talk ended without story 14 (obs $OBS)"
if ! obs_py rear_flags "$OBS"; then
  progress "WARNING: story 14 reached but DAA1/DAA2 flags were not the expected 72/1 (DAA1=$(obs_py get "$OBS" DAA1) DAA2=$(obs_py get "$OBS" DAA2))"
fi
progress "rear talk done: story=$(obs_py get "$OBS" story) DAA1=$(obs_py get "$OBS" DAA1) DAA2=$(obs_py get "$OBS" DAA2) map=$(obs_py get "$OBS" map) cell=$(obs_py get "$OBS" cell) tag=$BASE"

printf '%s\n' "$BASE" > m9-work/outer-runs/huangnigang-final-tag.txt
python3 - "$BASE" "$OBS" <<'PY'
import json, pathlib, sys, subprocess
tag, obs_path = sys.argv[1], sys.argv[2]
obs = json.load(open(obs_path))
out = {
  'completedAt': subprocess.check_output(['bash','-lc','TZ=America/New_York date --iso-8601=seconds'], text=True).strip(),
  'finalTag': tag,
  'observation': obs,
  'officialStart': 'm9-work/checkpoints/story12-meeting-end.bin',
  'notes': 'Natural official-start play through 黄泥岗客栈 front (story 13) and rear (story 14) talks. Ready for region4-scope.json and GPT plates.',
}
path = pathlib.Path('m9-work/outer-runs/huangnigang-play-complete.json')
path.write_text(json.dumps(out, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print('wrote', path)
PY

progress "Huangnigang official-start inn play complete (final tag $BASE). Next: region4-scope, GPT plates, integration, QA/perf, preview."
status_update "Official-start 黄泥岗 inn play is complete (final tag $BASE, story $(obs_py get "$OBS" story)). Next is region4-scope.json and GPT full-map plates. 38811 and 8765 must stay up. Deliverables not yet produced."
echo "$(stamp) CHAIN3_OK final=$BASE"
exit 0
