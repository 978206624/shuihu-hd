// Fast native talk/page from a preserved M10 save. Natural joypad only.
// Dialogue paging: A when dialogue!=0; wait only when dialogue==0 and scriptRunning!=0.
// Stall detection uses framebuffer SHA, not flag equality.
const fs = require('node:fs');
const path = require('node:path');
const { core, sha } = require('../scripts/native-play.cjs');

const ROOT = path.resolve(__dirname, '../..');
const WORK = path.join(ROOT, 'm10-work');
const keys = { u: 'up', d: 'down', l: 'left', r: 'right' };

const [srcArg, tag, letters = ''] = process.argv.slice(2);
if (!srcArg || !tag || !/^[a-zA-Z0-9_-]+$/.test(tag)) {
  throw new Error('Usage: native-talk.cjs source.bin unique-tag [ulrd walk letters]');
}
const src = path.resolve(srcArg);
if (!fs.realpathSync(src).startsWith(WORK + '/')) throw new Error('Use a preserved M10 source save');
const out = path.join(WORK, 'native', tag);
if (fs.existsSync(out)) throw new Error('Refusing to overwrite ' + out);
fs.mkdirSync(out, { recursive: true });

function flags(c) {
  const save = c.state();
  if (save.length !== 199608) throw new Error('Unexpected state format');
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
    arrivalBanner: save[hr(0xffc1)],
    scriptRunning: save[hr(0xffd6)],
    DAA1: selectedWram(0xdaa1).toString(16),
    DAA2: selectedWram(0xdaa2).toString(16),
    stateSHA256: sha(save),
    nativeFramebufferSHA256: sha(c.fb()),
  };
}

const writeJSON = (file, data) => fs.writeFileSync(file, JSON.stringify(data, null, 2) + '\n');

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
      scriptRunning: obs.scriptRunning, DAA1: obs.DAA1, DAA2: obs.DAA2,
      cell: obs.cell, facing: obs.facing,
    }));
    return obs;
  };
  const apply = (action, name) => {
    c.action(action);
    executed.push(action);
    writeJSON(path.join(out, 'actions.json'), executed);
    return snap(name);
  };
  const page = (name) => apply(['A', 6, 120], name);
  const wait = (name) => apply([null, 120, 0], name);

  let obs = snap('start');
  if (letters) {
    for (const ch of letters) {
      if (!keys[ch]) throw new Error('Invalid walk letter ' + ch);
      c.action([keys[ch], 16, 8]);
      executed.push([keys[ch], 16, 8]);
    }
    writeJSON(path.join(out, 'actions.json'), executed);
    obs = snap('after-walk');
  }

  let i = 0, stall = 0, prev = obs.nativeFramebufferSHA256;
  obs = page('talk-00');
  while (i < 48) {
    const name = 'talk-' + String(i + 1).padStart(2, '0');
    if (obs.dialogue !== 0) obs = page(name);
    else if (obs.scriptRunning) obs = wait(name);
    else break;
    const key = obs.nativeFramebufferSHA256;
    stall = key === prev ? stall + 1 : 0;
    prev = key;
    if (stall >= 8) {
      console.log('STALL after', name);
      break;
    }
    i++;
  }
  i = 0;
  while (!(obs.bank === 5 && obs.mode === 0 && obs.dialogue === 0 && !obs.scriptRunning) && i < 8) {
    obs = wait('settle-' + String(i).padStart(2, '0'));
    i++;
  }
  writeJSON(path.join(out, 'result.json'), { source: src, sourceSHA256: sha(source), letters, actions: executed, end: obs, records });
  console.log('END', JSON.stringify({ map: obs.map, story: obs.story, DAA1: obs.DAA1, DAA2: obs.DAA2, cell: obs.cell, facing: obs.facing, dialogue: obs.dialogue }));
  console.log('OUTPUT', out);
})().catch(e => { console.error(e); process.exitCode = 1; });
