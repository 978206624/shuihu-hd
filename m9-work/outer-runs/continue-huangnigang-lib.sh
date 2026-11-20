# shellcheck disable=SC1091
source m9-work/outer-runs/m9_play.supervisor.sh

stamp() { date --iso-8601=seconds; }
save_base_tag() { printf '%s\n' "$1" > m9-work/outer-runs/last-base-tag.txt; }

# All chatty play output must stay off the captured stdout of callers.
# write the resulting tag only via save_base_tag + this return helper.
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
  save_base_tag "$base"
}

walk_leg() {
  local tag=$1 base=$2 steps=$3 exp_map=$4 exp_cell=$5 exp_story=$6
  local prev_len
  prev_len=$(python3 -c 'import json,sys; print(len(json.load(open(sys.argv[1]))))' "m9-work/play/$base/actions.json")
  play_new "$tag" "$base" $steps
  local obs="m9-work/outer-runs/$tag-show.json"
  show_to "$tag" "$obs"
  if obs_py expect "$obs" "$exp_map" "$exp_cell" "$exp_story"; then
    save_base_tag "$tag"
    return 0
  fi
  # banner on the expected map: settle
  if [[ $(obs_py get "$obs" map) == "$exp_map" ]] && { obs_py banner "$obs" || [[ $(obs_py get "$obs" bank) == 13 ]]; }; then
    play_new "${tag}-settle" "$tag" wait
    show_to "${tag}-settle" "$obs"
    obs_py expect "$obs" "$exp_map" "$exp_cell" "$exp_story" || blocker "settled $exp_map after $tag but not at expected cell $exp_cell story $exp_story (see $obs)"
    save_base_tag "${tag}-settle"
    return 0
  fi
  # mid-leg encounter or leftover battle
  local left
  left=$(remaining_steps "$tag" "$steps" "$prev_len")
  progress "walk $tag did not reach $exp_map $exp_cell; leftover steps: '${left}'"
  local recovered
  recover_to_field "$tag" "$tag"
  recovered=$(cat m9-work/outer-runs/last-base-tag.txt)
  show_to "$recovered" "$obs"
  if obs_py expect "$obs" "$exp_map" "$exp_cell" "$exp_story"; then
    save_base_tag "$recovered"
    return 0
  fi
  if [[ -z "$left" ]]; then
    blocker "walk $tag ended on field $(obs_py get "$obs" map) $(obs_py get "$obs" cell) without leftover steps, expected $exp_map $exp_cell"
  fi
  # play leftover from recovered field
  play_new "${tag}-cont" "$recovered" $left
  show_to "${tag}-cont" "$obs"
  if obs_py expect "$obs" "$exp_map" "$exp_cell" "$exp_story"; then
    save_base_tag "${tag}-cont"
    return 0
  fi
  if [[ $(obs_py get "$obs" map) == "$exp_map" ]] && { obs_py banner "$obs" || [[ $(obs_py get "$obs" bank) == 13 ]]; }; then
    play_new "${tag}-cont-settle" "${tag}-cont" wait
    show_to "${tag}-cont-settle" "$obs"
    obs_py expect "$obs" "$exp_map" "$exp_cell" "$exp_story" || blocker "settled ${tag}-cont but not at $exp_map $exp_cell (see $obs)"
    save_base_tag "${tag}-cont-settle"
    return 0
  fi
  # one more recover+leftover pass
  local rec2 left2
  recover_to_field "${tag}-cont" "${tag}-cont"
  rec2=$(cat m9-work/outer-runs/last-base-tag.txt)
  left2=$(remaining_steps "${tag}-cont" "$left" "$(python3 -c 'import json,sys; print(len(json.load(open(sys.argv[1]))))' "m9-work/play/$recovered/actions.json")")
  if [[ -n "$left2" ]]; then
    play_new "${tag}-cont2" "$rec2" $left2
    show_to "${tag}-cont2" "$obs"
    if obs_py expect "$obs" "$exp_map" "$exp_cell" "$exp_story"; then
      save_base_tag "${tag}-cont2"
      return 0
    fi
  else
    show_to "$rec2" "$obs"
    if obs_py expect "$obs" "$exp_map" "$exp_cell" "$exp_story"; then
      save_base_tag "$rec2"
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
  save_base_tag "$base"
}

