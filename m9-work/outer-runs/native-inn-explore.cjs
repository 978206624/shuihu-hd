// Fast native (binjgb) exploration of the 黄泥岗客栈 talks.
// Official-start prefix only; natural joypad; no RAM/PC writes.
// One later official browser replay will be the evidence chain.
const fs = require('node:fs');
const path = require('node:path');
const { core, sha, readActions, romSHA256 } = require('../scripts/native-play.cjs');

const ROOT = path.resolve(__dirname, '../..');
const WORK = path.join(ROOT, 'm9-work');
const official = path.join(WORK, 'checkpoints/story12-meeting-end.bin');
const officialHash = '2a3551ad5082236ce2b3223323d6fff983a984a3839ff2e6fa2359c1321edea2';
const tag = 'm9-native-huangnigang-inn';
const out = path.join(WORK, 'native', tag);
const prefixTag = 'm9-huangnigang-s01-front-q03';
const keys = { u: 'up', d: 'down', l: 'left', r: 'right' };

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

function writeJSON(file, data) {
  fs.writeFileSync(file, JSON.stringify(data, null, 2) + '\n');
}

function stamp(msg) {
  const line = `- ${new Date().toISOString()} ${msg}`;
  fs.appendFileSync(path.join(WORK, 'progress.md'), '\n' + line + '\n');
  console.log(line);
}

(async () => {
  const source = fs.readFileSync(official);
  if (sha(source) !== officialHash) throw new Error('Official story12 save hash differs');
  const prefix = readActions(path.join(WORK, 'play', prefixTag, 'actions.json'));
  const c = await core();
  c.state(source);
  const start = flags(c);
  stamp(`native inn explore started (pid ${process.pid}); replaying official prefix ${prefix.length} actions from ${prefixTag}`);
  const executed = [];
  const records = [];
  const snap = (name) => {
    const obs = flags(c);
    const file = path.join(out, name);
    c.snap(file + '.png');
    fs.writeFileSync(file + '.bin', c.state());
    records.push({ name, input: executed[executed.length - 1] || null, ...obs });
    console.log(name, JSON.stringify({
      map: obs.map, story: obs.story, dialogue: obs.dialogue, bank: obs.bank,
      scriptRunning: obs.scriptRunning, DAA1: obs.DAA1, DAA2: obs.DAA2,
      cell: obs.cell, facing: obs.facing,
    }));
    return obs;
  };

  for (let i = 0; i < prefix.length; i++) {
    c.action(prefix[i]);
    executed.push(prefix[i]);
    if (i === prefix.length - 1 || (i + 1) % 50 === 0) {
      const obs = flags(c);
      console.log('prefix', i + 1, '/', prefix.length, obs.map, 'story', obs.story, 'dialogue', obs.dialogue, 'bank', obs.bank);
    }
  }
  let obs = snap('after-prefix');
  writeJSON(path.join(out, 'actions.json'), executed);

  const apply = (action, name) => {
    c.action(action);
    executed.push(action);
    writeJSON(path.join(out, 'actions.json'), executed);
    return snap(name);
  };
  const page = (name) => apply(['A', 6, 120], name);
  const wait = (name) => apply([null, 120, 0], name);
  const walk = (letters, name) => {
    for (const ch of letters) c.action([keys[ch], 16, 8]), executed.push([keys[ch], 16, 8]);
    writeJSON(path.join(out, 'actions.json'), executed);
    return snap(name);
  };

  let i = 0;
  let stall = 0;
  const sameKey = o => [o.map, o.story, o.dialogue, o.bank, o.scriptRunning, o.DAA1, o.DAA2, JSON.stringify(o.cell)].join('|');
  let prevKey = sameKey(obs);
  while (obs.story < 13 && i < 32) {
    const name = 'front-' + String(i).padStart(2, '0');
    if (obs.dialogue !== 0) obs = page(name);
    else if (obs.scriptRunning) obs = wait(name);
    else obs = page(name);
    const key = sameKey(obs);
    stall = key === prevKey ? stall + 1 : 0;
    prevKey = key;
    if (stall >= 6) throw new Error('Front talk stalled without story 13 after ' + name);
    i++;
  }
  if (obs.story < 13) throw new Error('Front talk ended without story 13');
  i = 0;
  while (!(obs.bank === 5 && obs.mode === 0 && obs.dialogue === 0 && !obs.scriptRunning) && i < 8) {
    obs = wait('front-settle-' + String(i).padStart(2, '0'));
    i++;
  }
  stamp(`front talk reached story ${obs.story} DAA1=${obs.DAA1} map=${obs.map} cell=${JSON.stringify(obs.cell)}`);
  writeJSON(path.join(out, 'front-end.json'), obs);

  if (obs.map !== '00-2c') {
    obs = walk('rurrruu', 'rear-walk');
    obs = wait('rear-arrive-wait');
  }
  if (obs.map !== '00-2c') {
    writeJSON(path.join(out, 'blocker.json'), { reason: 'rear walk did not reach 00-2c', obs });
    throw new Error('Rear walk did not reach 00-2c: ' + JSON.stringify(obs));
  }
  stamp(`arrived 00-2c cell=${JSON.stringify(obs.cell)} story=${obs.story}`);
  obs = walk('ulluuu', 'rear-approach');
  obs = page('rear-talk-open');

  i = 0;
  stall = 0;
  prevKey = sameKey(obs);
  while (obs.story < 14 && i < 32) {
    const name = 'rear-' + String(i).padStart(2, '0');
    if (obs.dialogue !== 0) obs = page(name);
    else if (obs.scriptRunning) obs = wait(name);
    else obs = page(name);
    const key = sameKey(obs);
    stall = key === prevKey ? stall + 1 : 0;
    prevKey = key;
    if (stall >= 6) throw new Error('Rear talk stalled without story 14 after ' + name);
    i++;
  }
  i = 0;
  while (!(obs.bank === 5 && obs.mode === 0 && obs.dialogue === 0) && i < 8) {
    obs = wait('rear-settle-' + String(i).padStart(2, '0'));
    i++;
  }
  if (obs.story < 14) throw new Error('Rear talk ended without story 14');
  stamp(`rear talk reached story ${obs.story} DAA1=${obs.DAA1} DAA2=${obs.DAA2} map=${obs.map} cell=${JSON.stringify(obs.cell)}`);

  writeJSON(path.join(out, 'result.json'), {
    status: 'COMPLETE',
    officialStart: 'm9-work/checkpoints/story12-meeting-end.bin',
    officialSHA256: officialHash,
    romSHA256,
    prefixTag,
    prefixLength: prefix.length,
    actionCount: executed.length,
    end: obs,
    records,
  });
  writeJSON(path.join(WORK, 'outer-runs/huangnigang-inn-actions.json'), executed);
  writeJSON(path.join(WORK, 'outer-runs/huangnigang-play-complete.json'), {
    completedAt: new Date().toISOString(),
    engine: 'native-binjgb',
    tag,
    officialStart: 'm9-work/checkpoints/story12-meeting-end.bin',
    observation: obs,
    actions: 'm9-work/outer-runs/huangnigang-inn-actions.json',
    notes: 'Native official-start exploration through 黄泥岗客栈 front (story 13) and rear (story 14). One official browser replay of this action list is still required for evidence.',
  });
  fs.writeFileSync(path.join(WORK, 'outer-runs/huangnigang-final-tag.txt'), tag + '\n');
  stamp(`native inn explore complete; ${executed.length} official-start actions written for one browser evidence replay`);
  console.log('NATIVE_INN_OK', out);
})().catch(err => {
  console.error(err);
  fs.writeFileSync(path.join(out, 'error.txt'), String(err && err.stack || err) + '\n');
  process.exitCode = 1;
});
