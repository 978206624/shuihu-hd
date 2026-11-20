const fs = require('node:fs'), path = require('node:path'), crypto = require('node:crypto'), net = require('node:net');
const PROJECT = path.resolve(__dirname, '../..');
const W = path.join(PROJECT, 'm10-work');
const roots = {
  m9: path.join(PROJECT, 'm9-work/runtime'),
  candidate: path.join(W, 'runtime'),
};
const url = root => 'http://127.0.0.1:8765/' + path.relative(PROJECT, root) + '/';
const read = p => JSON.parse(fs.readFileSync(p, 'utf8'));
const sha = value => crypto.createHash('sha256').update(value).digest('hex');
const plan = () => read(path.join(W, 'integration/outer-plan.json'));

function officialEvidence(spec) {
  const result = read(path.join(PROJECT, spec.result));
  const frames = fs.readFileSync(path.join(PROJECT, spec.frames), 'utf8').trimEnd().split('\n')
    .map(line => JSON.parse(line)).filter(row => row.type === 'frame');
  return {result, frames};
}

function output() {
  const p = process.env.M10_RESULTS;
  if (!p || !path.isAbsolute(p) || path.dirname(path.resolve(p)) !== path.join(W, 'results')) {
    throw Error('Set M10_RESULTS to an absolute run directory directly under m10-work/results');
  }
  return path.resolve(p);
}

function write(p, value) {
  const temp = p + '.partial-' + crypto.randomUUID();
  try {
    fs.writeFileSync(temp, JSON.stringify(value, null, 2) + '\n', { flag: 'wx', flush: true });
    fs.renameSync(temp, p);
  } finally {
    fs.rmSync(temp, { force: true });
  }
}

function stats(values) {
  if (!values.length) return null;
  const s = values.slice().sort((a, b) => a - b);
  const mean = s.reduce((a, b) => a + b, 0) / s.length;
  return { samples: s.length, mean, p95: s[Math.ceil(s.length * .95) - 1], max: s.at(-1),
    min: s[0], stddev: Math.sqrt(s.reduce((n, v) => n + (v - mean) ** 2, 0) / s.length) };
}

async function proxy() {
  for (const port of [38811, 8765]) {
    await new Promise((resolve, reject) => {
      const socket = net.createConnection({ host: '127.0.0.1', port });
      socket.setTimeout(2000);
      socket.once('connect', () => { socket.destroy(); resolve(); });
      socket.once('error', error => reject(Error('REQUIRED_PORT_UNAVAILABLE ' + port, { cause: error })));
      socket.once('timeout', () => { socket.destroy(); reject(Error('REQUIRED_PORT_UNAVAILABLE ' + port)); });
    });
  }
}

function verifyFreeze() {
  const hashes = read(path.join(W, 'integration/outer-freeze.json'));
  for (const [p, h] of Object.entries(hashes)) {
    if (sha(fs.readFileSync(path.join(PROJECT, p))) !== h) throw Error('Frozen bytes differ: ' + p);
  }
}

async function page(browser, root, options = {}) {
  const context = await browser.newContext({ viewport: { width: 960, height: 900 }, serviceWorkers: 'block', ...options });
  try {
    const p = await context.newPage(), errors = [];
    await context.route('**/*', route => new URL(route.request().url()).origin === new URL(url(root)).origin
      ? route.continue() : route.abort());
    p.on('pageerror', error => errors.push(error.message));
    p.on('requestfailed', request => errors.push(request.url() + ' ' + request.failure()?.errorText));
    p.on('response', response => {
      if (response.status() >= 400) errors.push(response.status() + ' ' + response.url());
    });
    const started = Date.now();
    await p.goto(url(root));
    await p.waitForFunction(() => window.shuihu?.ready, {}, { timeout: 120000 });
    if (await p.evaluate(() => shuihu.meta().frames) !== 1) throw Error('Unexpected startup native frames');
    return { p, context, errors, startup: { navigationToReadyMs: Date.now() - started, ...await p.evaluate(() => shuihu.startup) } };
  } catch (error) {
    await context.close();
    throw error;
  }
}

module.exports = { fs, path, PROJECT, W, roots, url, read, sha, plan, officialEvidence, output, write, stats, proxy, verifyFreeze, page };
