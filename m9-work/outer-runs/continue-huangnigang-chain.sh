#!/usr/bin/env bash
# Session-independent official-start continuation of the 黄泥岗 inn route.
# Waits for the live town-menu-a tap-A if it is still running, then recovers
# to the field and plays the remaining inn legs. Restart-safe: completed
# unique tags are reused, never overwritten. No RAM pokes. Helpers stay here.
set -euo pipefail
cd /workspace/shawu
export TZ=America/New_York
export NODE_PATH=/home/box/opt/test-tools/node_modules
export PLAYWRIGHT_BROWSERS_PATH=/home/box/opt/playwright-browsers

LOCK=m9-work/outer-runs/continue-huangnigang-chain.lock
LOG=m9-work/outer-runs/continue-huangnigang-chain.log
BLOCK=m9-work/outer-runs/HUANGNIGANG_BLOCKER.md
exec >>"$LOG" 2>&1
exec 9>"$LOCK"
if ! flock -n 9; then
  echo "$(date --iso-8601=seconds) chain already running; exiting"
  exit 0
fi

# shellcheck disable=SC1091
source m9-work/outer-runs/m9_play.supervisor.sh

stamp() { date --iso-8601=seconds; }
progress() {
  local msg="$*"
  printf '\n- %s %s\n' "$(stamp)" "$msg" | tee -a m9-work/progress.md
}

status_update() {
  python3 - "$1" <<'PY'
import pathlib, sys, subprocess
note = sys.argv[1]
est = subprocess.check_output(['bash','-lc','TZ=America/New_York date --iso-8601=seconds'], text=True).strip()
path = pathlib.Path('m9-work/SUPERVISOR_STATUS.md')
body = path.read_text(encoding='utf-8') if path.exists() else '# SUPERVISOR_STATUS\n'
# prepend a fresh header block while keeping previous text below a cut
header = (
    '# SUPERVISOR_STATUS\n'
    f'Updated: {est} America/New_York\n\n'
    f'{note}\n\n'
    '---\n'
)
path.write_text(header, encoding='utf-8')
PY
}

blocker() {
  local msg="$*"
  progress "BLOCKER: $msg"
  printf '%s %s\n' "$(stamp)" "$msg" | tee "$BLOCK" >/dev/null
  status_update "BLOCKER during official-start 黄泥岗 play: $msg Stop and report. Ports must be checked. Do not poke RAM. Do not relaunch a living play tag."
  exit 2
}

ports_ok() {
  local port listener
  for port in 38811 8765; do
    if ! listener=$(ss -Hltn "sport = :$port") || [[ -z $listener ]]; then
      return 1
    fi
  done
  return 0
}

require_ports() {
  ports_ok || blocker "listener unavailable (38811 or 8765 down) at $(stamp)"
}

tag_ok() {
  local tag=$1
  [[ -f "m9-work/outer-runs/$tag/exit-code.txt" ]] \
    && [[ $(cat "m9-work/outer-runs/$tag/exit-code.txt") == 0 ]] \
    && [[ -f "m9-work/play/$tag/result.json" ]]
}

show_to() {
  local tag=$1 dest=$2
  m9_show "$tag" >"$dest"
}

play_new() {
  local tag=$1
  shift
  if tag_ok "$tag"; then
    echo "$(stamp) reuse completed tag $tag"
    m9_show "$tag"
    return 0
  fi
  if [[ -e "m9-work/outer-runs/$tag" || -e "m9-work/play/$tag" ]]; then
    blocker "tag $tag exists but is not a successful complete replay"
  fi
  require_ports
  progress "chain launching official-start replay $tag $*"
  m9_play "$tag" "$@"
  tag_ok "$tag" || blocker "replay $tag did not finish with exit 0"
}

obs_py() {
  python3 - "$@" <<'PY'
import json, sys
cmd, path, *rest = sys.argv[1:]
obs = json.load(open(path))
bank = obs.get('bank')
banner = obs.get('arrivalBanner') or 0
field = bank == 5 and obs.get('mode') == 0 and obs.get('cell') is not None and banner == 0
if cmd == 'field':
    sys.exit(0 if field else 1)
if cmd == 'banner':
    sys.exit(0 if (obs.get('map') and (banner or bank == 13)) else 1)
if cmd == 'get':
    key = rest[0]
    val = obs.get(key)
    if isinstance(val, list):
        print(','.join(str(x) for x in val))
    elif val is None:
        print('')
    else:
        print(val)
    sys.exit(0)
if cmd == 'expect':
    # expect map cellx,celly story
    exp_map, exp_cell, exp_story = rest
    cell = ','.join(str(int(x) if float(x).is_integer() else x) for x in obs.get('cell') or [])
    # cells may be ints
    if obs.get('cell'):
        cell = '{},{}'.format(int(obs['cell'][0]), int(obs['cell'][1]))
    ok = field and obs.get('map') == exp_map and cell == exp_cell and int(obs.get('story') or -1) == int(exp_story)
    sys.exit(0 if ok else 1)
if cmd == 'daa1_bit6':
    sys.exit(0 if (int(str(obs.get('DAA1')), 16) & 0x40) else 1)
if cmd == 'rear_flags':
    daa1 = int(str(obs.get('DAA1')), 16)
    daa2 = int(str(obs.get('DAA2') or '0'), 16)
    sys.exit(0 if ((daa1 & 0x80) == 0 and (daa2 & 0x01) and int(obs.get('story') or -1) >= 14) else 1)
print('unknown', cmd, file=sys.stderr)
sys.exit(64)
PY
}

remaining_steps() {
  python3 - "$1" "$2" "$3" <<'PY'
import json, sys
tag, planned, prev_len = sys.argv[1], sys.argv[2], int(sys.argv[3])
result = json.load(open(f'm9-work/play/{tag}/result.json'))
records = result['records'][prev_len:]
key = {'r': 'right', 'u': 'up', 'd': 'down', 'l': 'left'}
actions = []
for tok in planned.split():
    if tok in ('wait', 'battle-wait', 'page') or tok.startswith('tap-'):
        actions.append(tok)
    else:
        for ch in tok:
            if ch not in key:
                raise SystemExit(f'bad step {tok}')
            actions.append(key[ch])
if not records:
    print(planned)
    raise SystemExit(0)
first_battle = None
for i, rec in enumerate(records):
    if rec.get('bank') != 5:
        first_battle = i
        break
if first_battle is None:
    # all field; nothing to replay unless caller expected a map change
    print('')
    raise SystemExit(0)
# the triggering move is consumed; leftover planned inputs after it must be replayed
left = actions[first_battle + 1:]
out = []
dirs = []
def flush():
    global dirs
    if dirs:
        compact = ''.join({'right':'r','up':'u','down':'d','left':'l'}[d] for d in dirs)
        out.append(compact)
        dirs = []
for a in left:
    if a in ('right', 'up', 'down', 'left'):
        dirs.append(a)
    else:
        flush()
        out.append(a)
flush()
print(' '.join(out))
PY
}

recover_to_field() {
  local base=$1 prefix=$2
  local i=0 obs="m9-work/outer-runs/$prefix-recover-obs.json"
  show_to "$base" "$obs"
  while ! obs_py field "$obs"; do
    if (( i >= 8 )); then
      blocker "could not return to a settled field from $base after $i recoveries (see $obs)"
    fi
    require_ports
    local step tag
    tag="${prefix}-recover-$(printf '%02d' "$i")"
    # Prefer settling animation first, then close result text, then intro pages.
    local bank banner
    bank=$(obs_py get "$obs" bank)
    banner=$(obs_py get "$obs" arrivalBanner)
    if [[ "$banner" != 0 && -n "$banner" ]] || [[ "$bank" == 13 ]]; then
      step=wait
    elif [[ "$bank" == 45 ]]; then
      step=page
    elif [[ "$bank" == 36 ]]; then
      step=tap-B
    elif [[ "$bank" == 43 ]]; then
      if (( i == 0 )); then
        step=battle-wait
      elif (( i == 1 )); then
        step=tap-B
      elif (( i == 2 )); then
        step=wait
      else
        # still on a battle menu after wait/B: do not mash; stop for review
        blocker "still in battle bank 43 from $base after wait/B recoveries; inspect ${base} and $tag images before more inputs"
      fi
    else
      step=battle-wait
    fi
    progress "recover $tag from $base with $step (bank=$bank banner=$banner)"
    play_new "$tag" "$base" "$step"
    base=$tag
    show_to "$base" "$obs"
    i=$((i + 1))
  done
  echo "$base"
}

walk_leg() {
  local tag=$1 base=$2 steps=$3 exp_map=$4 exp_cell=$5 exp_story=$6
  local prev_len
  prev_len=$(python3 -c 'import json,sys; print(len(json.load(open(sys.argv[1]))))' "m9-work/play/$base/actions.json")
  play_new "$tag" "$base" $steps
  local obs="m9-work/outer-runs/$tag-show.json"
  show_to "$tag" "$obs"
  if obs_py expect "$obs" "$exp_map" "$exp_cell" "$exp_story"; then
    echo "$tag"
    return 0
  fi
  # banner on the expected map: settle
  if [[ $(obs_py get "$obs" map) == "$exp_map" ]] && { obs_py banner "$obs" || [[ $(obs_py get "$obs" bank) == 13 ]]; }; then
    play_new "${tag}-settle" "$tag" wait
    show_to "${tag}-settle" "$obs"
    obs_py expect "$obs" "$exp_map" "$exp_cell" "$exp_story" || blocker "settled $exp_map after $tag but not at expected cell $exp_cell story $exp_story (see $obs)"
    echo "${tag}-settle"
    return 0
  fi
  # mid-leg encounter or leftover battle
  local left
  left=$(remaining_steps "$tag" "$steps" "$prev_len")
  progress "walk $tag did not reach $exp_map $exp_cell; leftover steps: '${left}'"
  local recovered
  recovered=$(recover_to_field "$tag" "$tag")
  show_to "$recovered" "$obs"
  if obs_py expect "$obs" "$exp_map" "$exp_cell" "$exp_story"; then
    echo "$recovered"
    return 0
  fi
  if [[ -z "$left" ]]; then
    blocker "walk $tag ended on field $(obs_py get "$obs" map) $(obs_py get "$obs" cell) without leftover steps, expected $exp_map $exp_cell"
  fi
  # play leftover from recovered field
  play_new "${tag}-cont" "$recovered" $left
  show_to "${tag}-cont" "$obs"
  if obs_py expect "$obs" "$exp_map" "$exp_cell" "$exp_story"; then
    echo "${tag}-cont"
    return 0
  fi
  if [[ $(obs_py get "$obs" map) == "$exp_map" ]] && { obs_py banner "$obs" || [[ $(obs_py get "$obs" bank) == 13 ]]; }; then
    play_new "${tag}-cont-settle" "${tag}-cont" wait
    show_to "${tag}-cont-settle" "$obs"
    obs_py expect "$obs" "$exp_map" "$exp_cell" "$exp_story" || blocker "settled ${tag}-cont but not at $exp_map $exp_cell (see $obs)"
    echo "${tag}-cont-settle"
    return 0
  fi
  # one more recover+leftover pass
  local rec2 left2
  rec2=$(recover_to_field "${tag}-cont" "${tag}-cont")
  left2=$(remaining_steps "${tag}-cont" "$left" "$(python3 -c 'import json,sys; print(len(json.load(open(sys.argv[1]))))' "m9-work/play/$recovered/actions.json")")
  if [[ -n "$left2" ]]; then
    play_new "${tag}-cont2" "$rec2" $left2
    show_to "${tag}-cont2" "$obs"
    if obs_py expect "$obs" "$exp_map" "$exp_cell" "$exp_story"; then
      echo "${tag}-cont2"
      return 0
    fi
  else
    show_to "$rec2" "$obs"
    if obs_py expect "$obs" "$exp_map" "$exp_cell" "$exp_story"; then
      echo "$rec2"
      return 0
    fi
  fi
  blocker "could not complete walk to $exp_map $exp_cell from $tag (last obs $obs)"
}

page_until_story() {
  local base=$1 prefix=$2 want=$3 max=${4:-12}
  local obs="m9-work/outer-runs/$prefix-talk-obs.json"
  show_to "$base" "$obs"
  local i=0 tag
  while (( $(obs_py get "$obs" story) < want )); do
    if (( i >= max )); then
      blocker "after $max pages from $prefix, story is still $(obs_py get "$obs" story), want $want"
    fi
    tag="${prefix}-p$(printf '%02d' "$i")"
    if [[ $(obs_py get "$obs" scriptRunning) != 0 && $(obs_py get "$obs" scriptRunning) != '' ]]; then
      play_new "$tag" "$base" wait
    else
      play_new "$tag" "$base" page
    fi
    base=$tag
    show_to "$base" "$obs"
    i=$((i + 1))
  done
  # settle if a script is still running or we are not on a field bank
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
  echo "$base"
}

progress "huangnigang continuation chain started (pid $$). Waiting for live town-menu-a if needed."
status_update "Official-start 黄泥岗 chain is running under m9-work/outer-runs/continue-huangnigang-chain.sh (pid $$). It will wait for m9-huangnigang-s01-town-menu-a, recover to the 00-21 field, walk to 00-24 / 00-2b, and finish the two inn talks (story 13 then 14). Do not relaunch living tags. 38811 and 8765 must stay up. GPT/integration not started."

# Wait for the already-running tap-A, but never relaunch it.
if pgrep -af 'm9_play.supervisor.sh m9-huangnigang-s01-town-menu-a|browser-play.cjs m9-huangnigang-s01-town-menu-a' | grep -v pgrep >/dev/null; then
  progress "waiting for live m9-huangnigang-s01-town-menu-a to finish"
  while pgrep -af 'm9_play.supervisor.sh m9-huangnigang-s01-town-menu-a|run-play.sh browser m9-huangnigang-s01-town-menu-a|browser-play.cjs m9-huangnigang-s01-town-menu-a' | grep -v pgrep >/dev/null; do
    sleep 10
  done
fi
# give the launcher a moment to write exit-code
for _ in 1 2 3 4 5 6; do
  tag_ok m9-huangnigang-s01-town-menu-a && break
  sleep 5
done
tag_ok m9-huangnigang-s01-town-menu-a || blocker "m9-huangnigang-s01-town-menu-a is not a successful complete replay"

require_ports
BASE=m9-huangnigang-s01-town-menu-a
OBS=m9-work/outer-runs/chain-current-obs.json
show_to "$BASE" "$OBS"
progress "town-menu-a endpoint: map=$(obs_py get "$OBS" map) bank=$(obs_py get "$OBS" bank) story=$(obs_py get "$OBS" story) cell=$(obs_py get "$OBS" cell) image=$(obs_py get "$OBS" image)"

BASE=$(recover_to_field "$BASE" m9-huangnigang-s01-town-field)
show_to "$BASE" "$OBS"
progress "field after flee recover: map=$(obs_py get "$OBS" map) cell=$(obs_py get "$OBS" cell) facing=$(obs_py get "$OBS" facing) story=$(obs_py get "$OBS" story)"
# Expected (15,3) facing 1 on 00-21. If we got it, walk ruuu. If we already reached 00-24, skip.
if [[ $(obs_py get "$OBS" map) == 00-24 ]]; then
  progress "already on 00-24 after recover; skipping ruuu walk"
else
  [[ $(obs_py get "$OBS" map) == 00-21 ]] || blocker "expected 00-21 field after flee, got $(obs_py get "$OBS" map) $(obs_py get "$OBS" cell)"
  cell=$(obs_py get "$OBS" cell)
  if [[ "$cell" != "15,3" ]]; then
    progress "WARNING: expected cell 15,3 after flee, observed $cell. Will still attempt planned ruuu if leftover recovery can reach 00-24; otherwise this is a blocker after the walk."
  fi
  BASE=$(walk_leg m9-huangnigang-s01-town-cont "$BASE" "ruuu wait" 00-24 4,14 12)
fi
show_to "$BASE" "$OBS"
progress "arrived 00-24: cell=$(obs_py get "$OBS" cell) entry=$(obs_py get "$OBS" entry) story=$(obs_py get "$OBS" story) tag=$BASE"

BASE=$(walk_leg m9-huangnigang-s01-inn "$BASE" "uuuuuuuurruu wait" 00-2b 3,8 12)
show_to "$BASE" "$OBS"
progress "arrived 00-2b inn front: cell=$(obs_py get "$OBS" cell) story=$(obs_py get "$OBS" story) tag=$BASE"

# Front NPC: from (3,8), ruuuuu page
play_new m9-huangnigang-s01-front-talk "$BASE" ruuuuu page
BASE=m9-huangnigang-s01-front-talk
show_to "$BASE" "$OBS"
if (( $(obs_py get "$OBS" story) < 13 )); then
  BASE=$(page_until_story "$BASE" m9-huangnigang-s01-front 13 12)
  show_to "$BASE" "$OBS"
fi
# settle after the scene
if ! obs_py field "$OBS"; then
  BASE=$(recover_to_field "$BASE" m9-huangnigang-s01-front-end)
  show_to "$BASE" "$OBS"
fi
(( $(obs_py get "$OBS" story) >= 13 )) || blocker "front talk ended without story 13 (obs $OBS)"
obs_py daa1_bit6 "$OBS" || progress "WARNING: story advanced but DAA1 bit 6 is not set ($(obs_py get "$OBS" DAA1))"
progress "front talk done: story=$(obs_py get "$OBS" story) DAA1=$(obs_py get "$OBS" DAA1) cell=$(obs_py get "$OBS" cell) tag=$BASE"
status_update "Front inn talk reached story $(obs_py get "$OBS" story) on 00-2b (tag $BASE). Continuing to the rear room for story 14. Official-start chain still running. GPT/integration not started."

# Rear room from confirmed (4,3): rurrruu wait → 00-2c (6,8)
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
import json, pathlib, sys, shutil
from datetime import datetime
tag, obs_path = sys.argv[1], sys.argv[2]
obs = json.load(open(obs_path))
out = {
  'completedAt': __import__('subprocess').check_output(['bash','-lc','TZ=America/New_York date --iso-8601=seconds'], text=True).strip(),
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
echo "$(stamp) CHAIN_OK final=$BASE"
exit 0
