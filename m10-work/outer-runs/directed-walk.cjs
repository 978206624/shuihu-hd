// Supervisor host directed walk for REQUEST_READY. Uses the M7/M9 flee recipe.
const fs = require('node:fs');
const path = require('node:path');
const { core, sha } = require('../scripts/native-play.cjs');
const ROOT = path.resolve(__dirname, '../..');
const WORK = path.join(ROOT, 'm10-work');
const keys = { u: 'up', d: 'down', l: 'left', r: 'right' };
const [srcArg, tag, letters = ''] = process.argv.slice(2);
if (!srcArg || !tag || !/^[a-zA-Z0-9_-]+$/.test(tag)) {
  throw new Error('Usage: directed-walk.cjs source.bin unique-tag [ulrd letters]');
}
const src = fs.realpathSync(path.resolve(srcArg));
if (!src.startsWith(WORK + '/')) throw new Error('Use a preserved M10 source save');
const out = path.join(WORK, 'native', tag);
if (fs.existsSync(out)) throw new Error('Refusing to overwrite ' + out);
fs.mkdirSync(out, { recursive: true });

const FLEE = [[null, 360, 0], ['B', 6, 160], ['right', 6, 12], ['down', 6, 12], ['A', 6, 240], ['B', 6, 100]];

function flags(c) {
  const save = c.state();
  const hr = a => 199440 + a - 0xff80;
  const wram = a => save[147568 + a - 0xc000];
  const selectedWram = a => save[147568 + 0x1000 + a - 0xd000];
  const meta = c.meta();
  const x = 2 * save[hr(0xff96)] + (save.readInt16LE(hr(0xffae)) + wram(0xcd01) - 8) / 16;
  const y = 2 * save[hr(0xff97)] + (save.readInt16LE(hr(0xffb0)) + wram(0xcd00) - 16) / 16;
  const field = meta.bank === 5 && meta.mode === 0 && meta.dialogue === 0;
  return {
    ...meta,
    entry: save[hr(0xff9c)],
    cell: field ? [x, y] : null,
    facing: field ? wram(0xcd03) : null,
    scriptRunning: save[hr(0xffd6)],
    DAA1: selectedWram(0xdaa1).toString(16),
    DAA2: selectedWram(0xdaa2).toString(16),
    DAA3: selectedWram(0xdaa3).toString(16),
    nativeFramebufferSHA256: sha(c.fb()),
    stateSHA256: sha(save),
  };
}

const battle = obs => [43, 44, 45].includes(obs.bank);

(async () => {
  const source = fs.readFileSync(src);
  const c = await core();
  c.state(source);
  const executed = [];
  const records = [];
  const snap = (name) => {
    const obs = flags(c);
    c.snap(path.join(out, name + '.png'));
    fs.writeFileSync(path.join(out, name + '.bin'), c.state());
    records.push({ name, input: executed[executed.length - 1] || null, ...obs });
    console.log(name, JSON.stringify({
      map: obs.map, story: obs.story, dialogue: obs.dialogue, bank: obs.bank, mode: obs.mode,
      scriptRunning: obs.scriptRunning, DAA1: obs.DAA1, DAA2: obs.DAA2, DAA3: obs.DAA3,
      cell: obs.cell, facing: obs.facing, entry: obs.entry,
    }));
    return obs;
  };
  const apply = (action) => { c.action(action); executed.push(action); };
  const fleeIfNeeded = (label) => {
    let obs = flags(c);
    let n = 0;
    while (battle(obs) && n < 8) {
      for (const a of FLEE) apply(a);
      obs = snap(label + '-flee-' + String(n).padStart(2, '0'));
      n++;
    }
    if (battle(obs)) throw new Error('Bounded flee exhausted at ' + label);
    return obs;
  };
  let obs = snap('start');
  obs = fleeIfNeeded('start');
  // brief settle if mid-transition
  if (!(obs.bank === 5 && obs.mode === 0 && obs.dialogue === 0 && !obs.scriptRunning)) {
    apply([null, 120, 0]);
    obs = snap('settle');
  }
  let map = obs.map;
  let step = 0;
  for (const ch of letters) {
    if (!keys[ch]) throw new Error('Invalid walk letter ' + ch);
    obs = fleeIfNeeded('pre-' + step);
    apply([keys[ch], 16, 8]);
    obs = flags(c);
    if (battle(obs) || obs.dialogue || obs.scriptRunning || obs.map !== map) {
      obs = snap('step-' + String(step).padStart(3, '0') + '-' + ch);
      if (battle(obs)) obs = fleeIfNeeded('step-' + step);
      let page = 0, stall = 0, prev = obs.nativeFramebufferSHA256;
      while ((obs.dialogue || obs.scriptRunning) && page < 48) {
        if (obs.dialogue) apply(['A', 6, 120]);
        else apply([null, 120, 0]);
        obs = snap('page-' + String(step).padStart(3, '0') + '-' + String(page).padStart(2, '0'));
        stall = obs.nativeFramebufferSHA256 === prev ? stall + 1 : 0;
        prev = obs.nativeFramebufferSHA256;
        if (stall >= 8) break;
        page++;
        if (battle(obs)) obs = fleeIfNeeded('page-' + step);
      }
      if (obs.map !== map) {
        // settle arrival
        // Arrival cells are unreliable on the first map-change frame; always settle.
        apply([null, 126, 0]);
        obs = snap('arrive-' + obs.map + '-settled');
        for (let i = 0; i < 6 && !(obs.bank === 5 && obs.mode === 0 && obs.dialogue === 0 && !obs.scriptRunning && obs.cell); i++) {
          apply([null, 120, 0]);
          obs = snap('arrive-' + obs.map + '-' + i);
        }
        console.log('MAPCHANGE', map, '->', obs.map, 'cell', obs.cell, 'entry', obs.entry, 'after letter', step, ch);
        map = obs.map;
      }
    }
    step++;
  }
  obs = fleeIfNeeded('end');
  obs = snap('end');
  fs.writeFileSync(path.join(out, 'actions.json'), JSON.stringify(executed, null, 2) + '\n');
  fs.writeFileSync(path.join(out, 'result.json'), JSON.stringify({
    source: src, sourceSHA256: sha(source), letters, actions: executed, end: obs, records,
  }, null, 2) + '\n');
  console.log('END', JSON.stringify({
    map: obs.map, story: obs.story, DAA1: obs.DAA1, DAA2: obs.DAA2, DAA3: obs.DAA3,
    cell: obs.cell, facing: obs.facing, entry: obs.entry, dialogue: obs.dialogue, bank: obs.bank,
    stateSHA256: obs.stateSHA256,
  }));
  console.log('OUTPUT', out);
})().catch(e => { console.error(e && e.stack || e); process.exitCode = 1; });
