#!/usr/bin/env bash
# Build an official-start joypad replay and pass it to the supervisor launcher.

m9_play() (
  set -euo pipefail
  cd /workspace/shawu
  if [[ $# -lt 2 || ! $1 =~ ^[a-zA-Z0-9_-]+$ ]]; then
    echo 'Usage: m9_play UNIQUE_TAG BASE [STEPS...]' >&2
    return 64
  fi
  local tag=$1 base=$2 chain
  shift 2
  chain="m9-work/outer-runs/$tag-chain.json"
  test ! -e "m9-work/outer-runs/$tag"
  test ! -e "m9-work/play/$tag"

  node - "$chain" "$base" "$@" <<'NODE'
const fs = require('node:fs');
const { readActions } = require('./m9-work/scripts/native-play.cjs');
const [output, base, ...steps] = process.argv.slice(2);
const key = { u: 'up', d: 'down', l: 'left', r: 'right' };
let actions;
if (base === '@yard') {
  actions = readActions('m9-work/search/story12-interact-00-08-s02/prefix-actions.json');
  actions.push([null, 120, 0]);
} else {
  const source = /^([A-Za-z0-9_-]+)(?::([1-9][0-9]*))?$/.exec(base);
  if (!source) throw Error('Expected a prior replay tag, optionally followed by :action-count');
  actions = readActions(`m9-work/play/${source[1]}/actions.json`);
  if (source[2]) {
    if (+source[2] > actions.length) throw Error('Action count exceeds the recorded replay');
    actions = actions.slice(0, +source[2]);
  }
}
for (const step of steps) {
  if (/^[udlr]+$/.test(step)) {
    for (const direction of step) actions.push([key[direction], 16, 8]);
  } else if (step === 'wait') {
    actions.push([null, 120, 0]);
  } else if (step === 'battle-wait') {
    actions.push([null, 360, 0]);
  } else if (step === 'flee') {
    actions.push(...readActions('m8-work/play/field-flee-03/actions.json'));
  } else if (step === 'page') {
    actions.push(['A', 6, 120]);
  } else if (/^tap-(up|down|left|right|A|B)$/.test(step)) {
    actions.push([step.slice(4), 6, 120]);
  } else {
    throw Error(`Unrecognized input: ${step}`);
  }
}
fs.writeFileSync(output, JSON.stringify(actions, null, 2) + '\n', { flag: 'wx' });
NODE

  setsid --wait bash m9-work/outer-runs/run-play.sh browser "$tag" "$chain"
  m9_show "$tag"
)

m9_show() (
  cd /workspace/shawu || return
  node - "$1" "${2:-}" <<'NODE'
const fs = require('node:fs');
const [tag, index] = process.argv.slice(2);
const dir = `m9-work/play/${tag}`;
const result = JSON.parse(fs.readFileSync(`${dir}/result.json`, 'utf8'));
const observation = index === '' ? result.end : result.records[Number(index)];
if (!observation) throw Error('No recorded checkpoint for this action');
const file = `${dir}/${observation.name}`;
const save = fs.readFileSync(`${file}.bin`);
if (save.length !== 199608) throw Error('Unexpected state format');
const hr = address => 199440 + address - 0xff80;
const wram = address => save[147568 + address - 0xc000];
const selectedWram = address => save[147568 + 0x1000 + address - 0xd000];
const x = 2 * save[hr(0xff96)] +
  (save.readInt16LE(hr(0xffae)) + wram(0xcd01) - 8) / 16;
const y = 2 * save[hr(0xff97)] +
  (save.readInt16LE(hr(0xffb0)) + wram(0xcd00) - 16) / 16;
const { map, story, dialogue, mode, bank } = observation;
const field = bank === 5 && mode === 0 && dialogue === 0;
console.log(JSON.stringify({
  map, entry: save[hr(0xff9c)], story, dialogue, mode, bank,
  cell: field ? [x, y] : null,
  facing: field ? wram(0xcd03) : null,
  arrivalBanner: save[hr(0xffc1)],
  scriptRunning: save[hr(0xffd6)],
  DAA1: selectedWram(0xdaa1).toString(16),
  DAA2: selectedWram(0xdaa2).toString(16),
  nextActionIndex: (observation.index ?? -1) + 1,
  image: `${file}.png`,
}, null, 2));
NODE
)

# If sourced, define functions only. If executed, run m9_play "$@".
if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
  m9_play "$@"
fi
