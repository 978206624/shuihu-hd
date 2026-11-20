const assert = require('node:assert/strict');
const { randomUUID } = require('node:crypto');
const { isDeepStrictEqual } = require('node:util');
const os = require('node:os');
const common = require('../scripts/common.cjs');
const { fs, path, W, PROJECT, roots, output, proxy, sha, stats, verifyFreeze } = common;
const { measure, TARGET, WARMUP, REPEATS } = require('../scripts/perf.cjs');

const original = roots.candidate;
roots.original = original;
roots.candidate = W + '/runtime-fix-0017';
const reference = W + '/results/outer-20261118T062207Z';
const read = file => JSON.parse(fs.readFileSync(file));
const hash = file => sha(fs.readFileSync(file));
const changes = {
  'map-renderer.js': '5ee4519e0bb3df3e1f976a69ff7a1fa76b8e5c17e7091525b336b7f545f38a2d',
  'region-renderer.js': 'e3928aec91fd5a505acbab815f48c2a82781042fa416b7a658399d5cb00d5809',
};
const modes = ['legacy', 'cold'];
const variants = ['adopted', 'candidate', 'original'];

function publish(file, value) {
  fs.mkdirSync(path.dirname(file), { recursive: true });
  const temp = file + '.partial-' + randomUUID();
  fs.writeFileSync(temp, JSON.stringify(value, null, 2) + '\n', { flag: 'wx', flush: true });
  fs.linkSync(temp, file);
  fs.unlinkSync(temp);
}

function verifyCandidate() {
  const manifest = W + '/freeze-sha256.json';
  assert.equal(hash(manifest), '07aac456b160969f987e6d5d77b34209453bc6867281ee51c2d814318bd89c8e');
  const files = Object.entries(read(manifest)).filter(([file]) => file.startsWith('m8-work/runtime/'));
  const actual = fs.readdirSync(roots.candidate, { recursive: true, withFileTypes: true })
    .filter(entry => !entry.isDirectory());
  assert.equal(actual.length, files.length, 'Candidate file count differs');
  for (const [file, baseline] of files) {
    const relative = path.relative(original, path.join(PROJECT, file));
    const expected = changes[relative] ?? baseline;
    const candidate = path.join(roots.candidate, relative);
    assert(fs.lstatSync(candidate).isFile(), 'Candidate file is not regular: ' + relative);
    assert.equal(hash(candidate), expected, 'Candidate digest differs: ' + relative);
  }
  assert(actual.every(entry => entry.isFile()), 'Candidate contains nonregular files');
}

function qaCheck() {
  const source = reference + '/qa/report.json';
  assert.equal(hash(source), '42575581d9f543208324ba932f5c891cbd95ac5d44644f76a2e0bca487654fca');
  const baseline = read(source);
  const sidecar = reference + '/qa-coverage-attribution.json';
  assert.equal(hash(sidecar), 'b9f2835699dd4460aa7f93f245bf9980c7caa1ef7f509ae0e08c3b672c746f0e');
  const coverage = read(sidecar);
  assert.equal(coverage.qaReportSHA256, hash(source));
  const qa = read(output() + '/qa/report.json');
  assert(qa.pass && !qa.error && qa.errors.length === 0, 'Formal QA failed');
  assert.equal(qa.routes.length, 33);
  assert.equal(qa.actions, 1096);
  for (const field of ['frames', 'statePassed', 'nativePassed', 'actorTextPassed']) {
    assert.equal(qa[field], 84135, 'Formal QA differs: ' + field);
  }
  assert.equal(qa.regressionActions, 442);
  assert.equal(qa.regressionFrames, 31396);
  assert.equal(qa.regressionVisualPassed, 31396);
  for (const field of ['routes', 'region3Excluded', 'regressionCoverage', 'sourceMapFrames']) {
    assert(isDeepStrictEqual(qa[field], baseline[field]), 'Accepted QA differs: ' + field);
  }
  assert(isDeepStrictEqual(qa.region3Coverage, coverage.region3Coverage), 'Accepted Region 3 coverage or attribution differs');
  const totals = Object.values(qa.region3Coverage);
  const covered = totals.reduce((sum, row) => sum + row.covered, 0);
  const eligible = totals.reduce((sum, row) => sum + row.eligible, 0);
  assert.equal(covered, 420011267);
  assert.equal(eligible, 517119168);
  return { routes: qa.routes.length, actions: qa.actions, frames: qa.frames,
    state: qa.statePassed, native: qa.nativePassed, actorText: qa.actorTextPassed,
    oldVisual: qa.regressionVisualPassed, region3: { covered, eligible } };
}

async function perf() {
  qaCheck();
  assert(fs.existsSync(output() + '/qa.done'), 'Formal QA stage must be complete');
  const dir = output() + '/perf';
  fs.mkdirSync(dir);
  const route = read(W + '/inputs/perf-routes.json').find(route => route.id === '00-17');
  const { chromium } = require('playwright');
  const browser = await chromium.launch({ args: ['--no-sandbox'] });
  const samples = [];
  try {
    const machine = { platform: os.platform(), release: os.release(), cpu: os.cpus()[0]?.model,
      cpuCount: os.cpus().length, browser: await browser.version(), node: process.version };
    publish(dir + '/run.json', { machine, startedUtc: new Date().toISOString(),
      route: route.id, modes, variants, TARGET, WARMUP, REPEATS,
      sourceSHA256: hash(route.source), candidateChanges: changes });
    for (let repeat = 1; repeat <= REPEATS; repeat++) {
      // Same adopted/candidate order as the original runner. Add the original M8 as a control.
      const order = repeat === 2 ? ['candidate', 'adopted', 'original'] : variants;
      for (const mode of modes) for (const which of order) {
        await proxy();
        verifyFreeze();
        verifyCandidate();
        const sample = await measure(browser, which, route, mode, repeat);
        publish(dir + '/' + mode + '-00-17-' + which + '-r' + repeat + '.json', sample);
        samples.push(sample);
        console.log(mode, which, repeat, JSON.stringify({
          frameMax: sample.frame.max, switchMax: sample.switchAggregate?.frame.max,
          debtMax: sample.debt.max, fps: sample.gameFPS,
        }));
      }
    }
  } finally {
    await browser.close();
  }
  await proxy();
  verifyCandidate();
  publish(dir + '/report.json', { route: route.id, TARGET, WARMUP, REPEATS, samples });
}

function decide() {
  verifyCandidate();
  const dir = output() + '/perf';
  const qa = qaCheck();
  const { samples } = read(dir + '/report.json');
  const keys = ['frame.max', 'switchAggregate.frame.max', 'firstSwitch.frame.max',
    'debt.max', 'firstSwitch.debt.max', 'frame.p95', 'gameFPS', 'startup.navigationToReadyMs', 'loadState.durationMs'];
  const metric = (sample, key) => key.split('.').reduce((value, part) => value?.[part], sample);
  const summary = {};
  const nativeMismatches = [];
  assert.equal(samples.length, modes.length * variants.length * REPEATS);
  for (const mode of modes) {
    const rows = {};
    const saved = [];
    for (let repeat = 1; repeat <= REPEATS; repeat++) {
      const prior = read(reference + '/perf/' + mode + '-00-17-candidate-r' + repeat + '.json');
      saved.push(prior);
      for (const which of variants) {
        const id = mode + '-00-17-' + which + '-r' + repeat;
        const matches = samples.filter(sample => sample.mode === mode && sample.which === which && sample.repeat === repeat);
        assert.equal(matches.length, 1, 'Expected one sample: ' + id);
        const [row] = matches;
        assert(isDeepStrictEqual(row, read(dir + '/' + id + '.json')), 'Raw sample differs: ' + id);
        assert(row.id === '00-17' && row.frames === TARGET && row.records.length === TARGET && !row.errors.length,
          'Incomplete sample: ' + id);
        const sameMaps = row.records.every((record, i) => record.frame === i + 1 && record.map === prior.records[i].map);
        const windows = sample => sample.switchWindows.map(({ from, to, lo, hi }) => [from, to, lo, hi]);
        if (!sameMaps || row.stateSha256 !== prior.stateSha256 || row.framebufferSha256 !== prior.framebufferSha256 ||
            !isDeepStrictEqual(windows(row), windows(prior))) nativeMismatches.push(id);
        (rows[which] ??= []).push(row);
      }
    }
    rows.savedM8 = saved;
    rows.savedV3 = Array.from({ length: REPEATS }, (_, i) =>
      read(reference + '/perf/' + mode + '-00-17-adopted-r' + (i + 1) + '.json'));
    summary[mode] = Object.fromEntries(Object.entries(rows).map(([which, group]) =>
      [which, Object.fromEntries(keys.map(key => {
        const values = group.map(row => metric(row, key));
        assert(values.every(value => Number.isFinite(value) && value >= 0), 'Missing timing metric: ' + key);
        return [key, { ...stats(values), values }];
      }))]));
  }
  const maxKeys = keys.slice(0, 3);
  const coldThresholdMs = 19;
  const coldPass = maxKeys.every(key => summary.cold.candidate[key].mean <= coldThresholdMs + 1e-6);
  const decision = { meetsRoundGate: coldPass && !nativeMismatches.length,
    coldThresholdMs, qa, nativeMismatches, summary };
  publish(output() + '/decision.json', decision);
  for (const mode of modes) {
    console.log(mode, 'three-repeat means (ms except fps)');
    for (const which of Object.keys(summary[mode])) {
      const row = summary[mode][which];
      console.log(which, keys.slice(0, 7).map(key => key + '=' + row[key].mean.toFixed(3)).join(' '));
    }
  }
  console.log(decision.meetsRoundGate ? 'ROUND_GATE_MET' : 'ROUND_GATE_FAILED');
  if (!decision.meetsRoundGate) process.exitCode = 2;
}

async function watch() {
  const runner = Number(process.argv[3]);
  assert(Number.isInteger(runner) && runner > 1);
  for (;;) {
    try {
      await proxy();
    } catch (e) {
      fs.writeFileSync(output() + '/port-stop.txt', new Date().toISOString() + ' ' + e.message + '\n');
      console.error(e.message);
      process.kill(-runner, 'SIGTERM');
      return;
    }
    await new Promise(resolve => setTimeout(resolve, 1000));
  }
}

async function main() {
  switch (process.argv[2]) {
    case 'watch': return watch();
    case 'verify': return verifyCandidate();
    case 'qa':
      verifyCandidate();
      // The official QA takes its candidate path from this shared object.
      require('../scripts/qa.cjs');
      return;
    case 'qa-check': return console.log(JSON.stringify(qaCheck()));
    case 'perf': return perf();
    case 'decide': return decide();
    default: throw Error('Expected verify, qa, qa-check, perf, decide, or watch');
  }
}
main().catch(error => { console.error(error); process.exitCode = 1; });
