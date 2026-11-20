// Supervisor host directed walk for REQUEST_READY. Uses the M7/M9 flee recipe.
const fs = require('node:fs');
const path = require('node:path');
const { core, sha, fieldDetails } = require('../scripts/native-play.cjs');
const ROOT = path.resolve(__dirname, '../..');
const WORK = path.join(ROOT, 'm11-work');
const keys = { u: 'up', d: 'down', l: 'left', r: 'right' };
const [srcArg, tag, letters = ''] = process.argv.slice(2);
if (!srcArg || !tag || !/^[a-zA-Z0-9_-]+$/.test(tag)) {
  throw new Error('Usage: directed-walk.cjs source.bin unique-tag [ulrd letters]');
}
const src = fs.realpathSync(path.resolve(srcArg));
if (!src.startsWith(WORK + '/')) throw new Error('Use a preserved M11 source save');
const out = path.join(WORK, 'native', tag);
if (fs.existsSync(out)) throw new Error('Refusing to overwrite ' + out);
fs.mkdirSync(out, { recursive: true });

const FLEE = [[null, 360, 0], ['B', 6, 160], ['right', 6, 12], ['down', 6, 12], ['A', 6, 240], ['B', 6, 100]];

function flags(c) {
  const meta = c.meta();
  const details = fieldDetails(c.read, meta);
  return { ...meta, ...details, scriptRunning: details.script,
    DAA1: details.DAA[1], DAA2: details.DAA[2], DAA3: details.DAA[3],
    nativeFramebufferSHA256: sha(c.fb()), stateSHA256: sha(c.state()) };

}

const battle = obs => [43, 44, 45, 46].includes(obs.bank);
const scriptedBattle = obs => battle(obs) && obs.scriptRunning;

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
    if (scriptedBattle(obs)) return obs;
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
  if (!obs.settled) {
    apply([null, 120, 0]);
    obs = snap('settle');
  }
  let step = 0;
  for (const ch of letters) {
    if (!keys[ch]) throw new Error('Invalid walk letter ' + ch);
    if (!obs.settled) break;
    const before = obs;
    const label = 'step-' + String(step).padStart(3, '0') + '-' + ch;
    for (let attempt = 0; attempt < 3; attempt++) {
      apply([keys[ch], 16, 8]);
      obs = flags(c);
      const changedMap = () => obs.map !== before.map || obs.entry !== before.entry;
      if (obs.settled && !changedMap()) break;
      snap(label + '-attempt-' + attempt);
      if (changedMap() && !obs.dialogue) {
        apply([null, 126, 0]);
        obs = snap(label + '-arrival-' + attempt);
      }
      let interrupted = false;
      for (let page = 0; page < 48 && !obs.settled; page++) {
        if (scriptedBattle(obs)) break;
        if (battle(obs)) {
          interrupted = true;
          obs = fleeIfNeeded(label + '-' + attempt + '-' + page);
        } else {
          apply(obs.dialogue ? ['A', 6, 120] : [null, 120, 0]);
          obs = snap(label + '-page-' + attempt + '-' + page);
        }
      }
      if (!obs.settled || !interrupted || changedMap() ||
          obs.cell.join() !== before.cell.join()) break;
    }
    if (!obs.settled) break;
    if (obs.map !== before.map || obs.entry !== before.entry) {
      console.log('MAPCHANGE', before.map, '->', obs.map, 'cell', obs.cell, 'entry', obs.entry, 'after letter', step, ch);
    }
    step++;
  }
  obs = fleeIfNeeded('end');
  obs = snap('end');
  fs.writeFileSync(path.join(out, 'actions.json'), JSON.stringify(executed, null, 2) + '\n');
  fs.writeFileSync(path.join(out, 'result.json'), JSON.stringify({
    source: src, sourceSHA256: sha(source), letters, completedLetters: step, actions: executed, end: obs, records,
  }, null, 2) + '\n');
  console.log('END', JSON.stringify({
    map: obs.map, story: obs.story, DAA1: obs.DAA1, DAA2: obs.DAA2, DAA3: obs.DAA3,
    cell: obs.cell, facing: obs.facing, entry: obs.entry, dialogue: obs.dialogue, bank: obs.bank,
    stateSHA256: obs.stateSHA256,
  }));
  console.log('OUTPUT', out);
})().catch(e => { console.error(e && e.stack || e); process.exitCode = 1; });
