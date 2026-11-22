'use strict';
const {verifyFreeze, stats, fs, path, W, sha} = require('../scripts/common.cjs');
verifyFreeze();
const assert = require('node:assert/strict');
const {isDeepStrictEqual} = require('node:util');
const run = process.env.M8_RESULTS;
assert.equal(path.dirname(run), path.join(W, 'results'));
const read = file => JSON.parse(fs.readFileSync(file, 'utf8'));
const keys = ['frame.max', 'switchAggregate.frame.max', 'firstSwitch.frame.max',
  'debt.max', 'firstSwitch.debt.max', 'frame.p95', 'gameFPS',
  'startup.navigationToReadyMs', 'loadState.durationMs'];
const modes = ['legacy', 'cold'];
const variants = ['adopted', 'candidate'];
const id = s => [s.mode, s.id, s.which, 'r' + s.repeat].join('-');
const windows = s => s.switchWindows.map(({from, to, lo, hi}) => [from, to, lo, hi]);
const reportFile = path.join(run, 'perf/report.json');
function selected() {
  const {samples} = read(reportFile);
  assert.equal(samples.length, 144);
  const rows = samples.filter(s => s.id === '00-17');
  assert.equal(rows.length, 12);
  return rows;
}
const rows = selected();
const summary = {}, nativeMismatches = [];
for (const mode of modes) {
  const byVariant = {};
  for (const which of variants) {
    byVariant[which] = [1, 2, 3].map(repeat => {
      const matches = rows.filter(s => s.mode === mode && s.repeat === repeat && s.which === which);
      assert.equal(matches.length, 1);
      const [s] = matches;
      assert.equal(s.frames, 1792);
      assert.equal(s.records.length, 1792);
      assert.deepEqual(s.errors, []);
      assert.deepEqual(s, read(path.join(run, 'perf', id(s) + '.json')));
      return s;
    });
  }
  byVariant.candidate.forEach((s, i) => {
    const ref = byVariant.adopted[i];
    if (!s.records.every((r, j) => r.frame === j+1 && ref.records[j].frame === r.frame && r.map === ref.records[j].map)
        || s.stateSha256 !== ref.stateSha256 || s.framebufferSha256 !== ref.framebufferSha256
        || !isDeepStrictEqual(windows(s), windows(ref))) nativeMismatches.push(id(s));
  });
  summary[mode] = {};
  for (const [group, samples] of Object.entries({savedV3: byVariant.adopted, original: byVariant.candidate, candidate: byVariant.candidate})) {
    summary[mode][group] = Object.fromEntries(keys.map(key => {
      const values = samples.map(s => key.split('.').reduce((v, k) => v?.[k], s));
      assert(values.every(v => Number.isFinite(v) && v >= 0), mode + ' ' + group + ' ' + key);
      return [key, {...stats(values), values}];
    }));
  }
}
const q = read(path.join(run, 'qa/report.json'));
assert.equal(q.pass, true);
const qa = {routes:q.routes.length, actions:q.actions, frames:q.frames, state:q.statePassed, native:q.nativePassed, actorText:q.actorTextPassed};
const digest = sha(fs.readFileSync(path.join(W, 'freeze-sha256.json')));
assert.equal(digest, '772bdf6e2bc046b97f5a1e382b582435161af76014f703d2af68b6b3259baeb3');
const rebaseline = {
  method:'Fresh paired M8 00-17 measurements in legacy and cold modes, three repeats per variant. savedV3 uses adopted samples.',
  sourceRunId:path.basename(run), sourceSampleIds:rows.map(id), amendedFreezeSHA256:digest,
  amendedFreeze:'Owner amendment removed eight unavailable GPT art CLI logs. All 321 retained entries passed verifyFreeze().',
  originalEqualsCandidate:'The 00-17 fix was reverted. The fresh candidate measures the retained original m8-work/runtime/. Both groups use those same samples.',
  omittedSavedM8:'There is no historical M8 reference run in the fresh chain.',
  certification:'This file is NOT certified by check.cjs against historical evidence.'
};
const coldThresholdMs = 19;
const meetsRoundGate = !nativeMismatches.length && keys.slice(0,3).every(k => summary.cold.candidate[k].mean <= coldThresholdMs);
const dir = path.join(W,'results','outer-cold-0017-'+new Date().toISOString().replace(/[-:]/g,'').replace(/\.\d{3}/,''));
fs.mkdirSync(dir);
const file = path.join(dir,'decision.json');
fs.writeFileSync(file,JSON.stringify({meetsRoundGate,coldThresholdMs,qa,nativeMismatches,summary,rebaseline},null,2)+'\n',{flag:'wx'});
const saved = read(file);
const inputs = selected();
for (const mode of modes) for (const [group, which] of Object.entries({savedV3:'adopted', original:'candidate', candidate:'candidate'})) {
  const paired = inputs.filter(s => s.mode === mode && s.which === which).sort((a,b) => a.repeat-b.repeat);
  const actual = saved.summary[mode][group];
  assert.deepEqual(Object.keys(actual),keys);
  for (const key of keys) {
    const values = paired.map(s => key.split('.').reduce((v,k) => v[k],s));
    assert.deepEqual(actual[key], {...stats(values), values});
    assert(Object.values(actual[key]).flat().every(Number.isFinite));
  }
}
console.log(file);
