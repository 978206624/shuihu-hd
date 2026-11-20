#!/usr/bin/env bash
# Second official-start chain: after chain1 stops on the post-failed-flee
# command menu, flee one input at a time from 攻击, then walk to the inn.
set -euo pipefail
cd /workspace/shawu
export TZ=America/New_York
export NODE_PATH=/home/box/opt/test-tools/node_modules
export PLAYWRIGHT_BROWSERS_PATH=/home/box/opt/playwright-browsers
export PYTHONUNBUFFERED=1

LOCK=m9-work/outer-runs/continue-huangnigang-chain2.lock
LOG=m9-work/outer-runs/continue-huangnigang-chain2.log
BLOCK=m9-work/outer-runs/HUANGNIGANG_BLOCKER.md
# line-buffer the log
exec > >(stdbuf -oL tee -a "$LOG") 2>&1
exec 9>"$LOCK"
if ! flock -n 9; then
  echo "$(date --iso-8601=seconds) chain2 already running; exiting"
  exit 0
fi

# shellcheck disable=SC1091
source m9-work/outer-runs/continue-huangnigang-lib.sh

progress "huangnigang chain2 started (pid $$). Waiting for chain1 and recover-02 to finish; will not relaunch living tags."

# Wait for chain1 (PID from pidfile) to exit, and for no recover-02 play to be running.
chain1_pid=
if [[ -f m9-work/outer-runs/continue-huangnigang-chain.pid ]]; then
  chain1_pid=$(cat m9-work/outer-runs/continue-huangnigang-chain.pid)
fi
while :; do
  live=0
  if [[ -n "$chain1_pid" ]] && kill -0 "$chain1_pid" 2>/dev/null; then
    live=1
  fi
  if pgrep -af 'continue-huangnigang-chain.sh' | grep -v pgrep | grep -v chain2 | grep -q .; then
    live=1
  fi
  if pgrep -af 'browser-play.cjs m9-huangnigang-s01-town-field-recover-02|run-play.sh browser m9-huangnigang-s01-town-field-recover-02' | grep -v pgrep | grep -q .; then
    live=1
  fi
  [[ $live -eq 0 ]] && break
  sleep 10
done

require_ports

# Prefer the last successful recover tag.
BASE=
for cand in m9-huangnigang-s01-town-field-recover-02 m9-huangnigang-s01-town-field-recover-01 m9-huangnigang-s01-town-field-recover-00; do
  if tag_ok "$cand"; then
    BASE=$cand
    break
  fi
done
[[ -n "$BASE" ]] || blocker "chain2 found no successful recover tag to resume from"

OBS=m9-work/outer-runs/chain2-current-obs.json
show_to "$BASE" "$OBS"
progress "chain2 resume from $BASE: map=$(obs_py get "$OBS" map) bank=$(obs_py get "$OBS" bank) story=$(obs_py get "$OBS" story) cell=$(obs_py get "$OBS" cell) image=$(obs_py get "$OBS" image)"
status_update "Chain2 is resuming official-start play from $BASE after a failed 逃跑 (enemy message, menu returned to 攻击). Next: tap-right, tap-down, tap-A, battle-wait, then the 00-24/inn talks if the field is recovered. Do not relaunch living tags."

# If somehow already on the field, skip flee retries.
if ! obs_py field "$OBS"; then
  [[ $(obs_py get "$OBS" bank) == 43 ]] || blocker "chain2 expected battle menu bank 43 or a field, got bank=$(obs_py get "$OBS" bank)"
  attempts=0
  while ! obs_py field "$OBS"; do
    attempts=$((attempts + 1))
    if (( attempts > 3 )); then
      blocker "逃跑 failed to return to the field after 3 confirmed menu attempts from 攻击 (last tag $BASE, obs $OBS)"
    fi
    prefix="m9-huangnigang-s01-town-flee${attempts}"
    play_new "${prefix}-right" "$BASE" tap-right
    play_new "${prefix}-down" "${prefix}-right" tap-down
    play_new "${prefix}-a" "${prefix}-down" tap-A
    play_new "${prefix}-wait" "${prefix}-a" battle-wait
    BASE="${prefix}-wait"
    show_to "$BASE" "$OBS"
    progress "flee attempt $attempts endpoint: bank=$(obs_py get "$OBS" bank) map=$(obs_py get "$OBS" map) cell=$(obs_py get "$OBS" cell) image=$(obs_py get "$OBS" image)"
    if obs_py field "$OBS"; then
      break
    fi
    # settle leftover animation or result text, then require the 攻击 menu again
    if [[ $(obs_py get "$OBS" bank) != 43 ]]; then
      BASE=$(recover_to_field "$BASE" "${prefix}-rec")
      show_to "$BASE" "$OBS"
    fi
    if obs_py field "$OBS"; then
      break
    fi
    if [[ $(obs_py get "$OBS" bank) != 43 ]]; then
      blocker "after flee attempt $attempts, not on field and not on bank 43 (obs $OBS)"
    fi
  done
fi

show_to "$BASE" "$OBS"
progress "field or post-flee state: map=$(obs_py get "$OBS" map) cell=$(obs_py get "$OBS" cell) facing=$(obs_py get "$OBS" facing) story=$(obs_py get "$OBS" story) tag=$BASE"

if [[ $(obs_py get "$OBS" map) == 00-24 ]]; then
  progress "already on 00-24; skipping ruuu walk"
else
  [[ $(obs_py get "$OBS" map) == 00-21 ]] || blocker "expected 00-21 field after flee, got $(obs_py get "$OBS" map) $(obs_py get "$OBS" cell)"
  cell=$(obs_py get "$OBS" cell)
  if [[ "$cell" != "15,3" ]]; then
    progress "WARNING: expected cell 15,3 after flee, observed $cell. Attempting planned ruuu anyway."
  fi
  BASE=$(walk_leg m9-huangnigang-s01-town-cont "$BASE" "ruuu wait" 00-24 4,14 12)
fi
show_to "$BASE" "$OBS"
progress "arrived 00-24: cell=$(obs_py get "$OBS" cell) entry=$(obs_py get "$OBS" entry) story=$(obs_py get "$OBS" story) tag=$BASE"

BASE=$(walk_leg m9-huangnigang-s01-inn "$BASE" "uuuuuuuurruu wait" 00-2b 3,8 12)
show_to "$BASE" "$OBS"
progress "arrived 00-2b inn front: cell=$(obs_py get "$OBS" cell) story=$(obs_py get "$OBS" story) tag=$BASE"

play_new m9-huangnigang-s01-front-talk "$BASE" ruuuuu page
BASE=m9-huangnigang-s01-front-talk
show_to "$BASE" "$OBS"
if (( $(obs_py get "$OBS" story) < 13 )); then
  BASE=$(page_until_story "$BASE" m9-huangnigang-s01-front 13 12)
  show_to "$BASE" "$OBS"
fi
if ! obs_py field "$OBS"; then
  BASE=$(recover_to_field "$BASE" m9-huangnigang-s01-front-end)
  show_to "$BASE" "$OBS"
fi
(( $(obs_py get "$OBS" story) >= 13 )) || blocker "front talk ended without story 13 (obs $OBS)"
obs_py daa1_bit6 "$OBS" || progress "WARNING: story advanced but DAA1 bit 6 is not set ($(obs_py get "$OBS" DAA1))"
progress "front talk done: story=$(obs_py get "$OBS" story) DAA1=$(obs_py get "$OBS" DAA1) cell=$(obs_py get "$OBS" cell) tag=$BASE"
status_update "Front inn talk reached story $(obs_py get "$OBS" story) on 00-2b (tag $BASE). Continuing to the rear room for story 14. Official-start chain2 still running. GPT/integration not started."

BASE=$(walk_leg m9-huangnigang-s01-rear "$BASE" "rurrruu wait" 00-2c 6,8 13)
show_to "$BASE" "$OBS"
progress "arrived 00-2c rear: cell=$(obs_py get "$OBS" cell) story=$(obs_py get "$OBS" story) tag=$BASE"

play_new m9-huangnigang-s01-rear-talk "$BASE" ulluuu page
BASE=m9-huangnigang-s01-rear-talk
show_to "$BASE" "$OBS"
if (( $(obs_py get "$OBS" story) < 14 )); then
  BASE=$(page_until_story "$BASE" m9-huangnigang-s01-rear 14 12)
  show_to "$BASE" "$OBS"
fi
if ! obs_py field "$OBS"; then
  BASE=$(recover_to_field "$BASE" m9-huangnigang-s01-rear-end)
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
echo "$(stamp) CHAIN2_OK final=$BASE"
exit 0
