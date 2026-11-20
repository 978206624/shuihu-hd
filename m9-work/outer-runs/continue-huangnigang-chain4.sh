#!/usr/bin/env bash
# After chain3's wait-only front paging (scriptRunning stayed 1, dialogue
# did not advance), resume from the last completed front tag and PAGE with A
# until story 13, then rear room story 14. Do not overwrite completed tags.
set -euo pipefail
cd /workspace/shawu
export TZ=America/New_York
export NODE_PATH=/home/box/opt/test-tools/node_modules
export PLAYWRIGHT_BROWSERS_PATH=/home/box/opt/playwright-browsers
export PYTHONUNBUFFERED=1

LOCK=m9-work/outer-runs/continue-huangnigang-chain4.lock
LOG=m9-work/outer-runs/continue-huangnigang-chain4.log
BLOCK=m9-work/outer-runs/HUANGNIGANG_BLOCKER.md
exec > >(stdbuf -oL tee -a "$LOG") 2>&1
exec 9>"$LOCK"
if ! flock -n 9; then
  echo "$(date --iso-8601=seconds) chain4 already running; exiting"
  exit 0
fi

# shellcheck disable=SC1091
source m9-work/outer-runs/continue-huangnigang-lib.sh
load_base() { cat m9-work/outer-runs/last-base-tag.txt; }

# Prefer wait only for animation with no dialogue box; otherwise page.
page_until_story() {
  local base=$1 prefix=$2 want=$3 max=${4:-16}
  local obs="m9-work/outer-runs/$prefix-talk-obs.json"
  show_to "$base" "$obs"
  local i=0 tag dlg script
  while (( $(obs_py get "$obs" story) < want )); do
    if (( i >= max )); then
      blocker "after $max pages from $prefix, story is still $(obs_py get "$obs" story), want $want"
    fi
    tag="${prefix}-q$(printf '%02d' "$i")"
    dlg=$(obs_py get "$obs" dialogue)
    script=$(obs_py get "$obs" scriptRunning)
    if [[ "$dlg" == 0 && "$script" != 0 && "$script" != '' ]]; then
      play_new "$tag" "$base" wait
    else
      play_new "$tag" "$base" page
    fi
    base=$tag
    show_to "$base" "$obs"
    i=$((i + 1))
  done
  i=0
  while ! obs_py field "$obs" || { [[ $(obs_py get "$obs" scriptRunning) != 0 && $(obs_py get "$obs" scriptRunning) != '' ]]; }; do
    if (( i >= 6 )); then
      break
    fi
    tag="${prefix}-settle-$(printf '%02d' "$i")"
    play_new "$tag" "$base" wait
    base=$tag
    show_to "$base" "$obs"
    i=$((i + 1))
  done
  save_base_tag "$base"
}

progress "huangnigang chain4 started (pid $$). Waiting for the live front-p01 wait to finish, then paging the 吴用 scene with A. Do not relaunch living tags."

# Wait for any in-flight front-p01 (or later wait) to finish; then stop chain3.
while pgrep -af 'browser-play.cjs m9-huangnigang-s01-front-p0|run-play.sh browser m9-huangnigang-s01-front-p0' | grep -v pgrep | grep -q .; do
  sleep 5
done
# If chain3 is still alive and not mid-play, stop it so it cannot start another wait.
if pgrep -af 'continue-huangnigang-chain3.sh' | grep -v pgrep | grep -q .; then
  progress "stopping chain3 after its in-flight front wait finished, before another wait-only page"
  pkill -f 'continue-huangnigang-chain3.sh' || true
  sleep 1
fi
# If chain3 managed to start another wait play, let THAT finish too.
while pgrep -af 'browser-play.cjs m9-huangnigang-s01-front-|run-play.sh browser m9-huangnigang-s01-front-' | grep -v pgrep | grep -q .; do
  sleep 5
done

require_ports

BASE=
for cand in m9-huangnigang-s01-front-p02 m9-huangnigang-s01-front-p01 m9-huangnigang-s01-front-p00 m9-huangnigang-s01-front-talk; do
  if tag_ok "$cand"; then
    BASE=$cand
    break
  fi
done
[[ -n "$BASE" ]] || blocker "chain4 found no successful front-talk tag"

OBS=m9-work/outer-runs/chain4-current-obs.json
show_to "$BASE" "$OBS"
progress "chain4 resume from $BASE: map=$(obs_py get "$OBS" map) story=$(obs_py get "$OBS" story) dialogue=$(obs_py get "$OBS" dialogue) bank=$(obs_py get "$OBS" bank) scriptRunning=$(obs_py get "$OBS" scriptRunning) image=$(obs_py get "$OBS" image)"
status_update "Chain4 is paging the 00-2b 吴用 scene with A from tag $BASE (chain3 was wait-only while scriptRunning stayed 1). Do not relaunch completed front tags. Next: story 13, rear 00-2c, story 14, then region4 scope and GPT plates."

if (( $(obs_py get "$OBS" story) < 13 )); then
  page_until_story "$BASE" m9-huangnigang-s01-front 13 16
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
progress "front talk done: story=$(obs_py get "$OBS" story) DAA1=$(obs_py get "$OBS" DAA1) cell=$(obs_py get "$OBS" cell) map=$(obs_py get "$OBS" map) tag=$BASE"
status_update "Front inn talk reached story $(obs_py get "$OBS" story) (tag $BASE). Continuing to 00-2c rear talk for story 14. Official-start chain4 still running. GPT/integration not started."

# Rear room from (4,3): rurrruu wait → 00-2c (6,8) at story 13
walk_leg m9-huangnigang-s01-rear "$BASE" "rurrruu wait" 00-2c 6,8 13
BASE=$(load_base)
show_to "$BASE" "$OBS"
progress "arrived 00-2c rear: cell=$(obs_py get "$OBS" cell) story=$(obs_py get "$OBS" story) tag=$BASE"

play_new m9-huangnigang-s01-rear-talk "$BASE" ulluuu page
BASE=m9-huangnigang-s01-rear-talk
show_to "$BASE" "$OBS"
if (( $(obs_py get "$OBS" story) < 14 )); then
  page_until_story "$BASE" m9-huangnigang-s01-rear 14 16
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
echo "$(stamp) CHAIN4_OK final=$BASE"
exit 0
