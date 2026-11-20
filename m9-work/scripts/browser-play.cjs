// Replay explicit joypad actions in the already-served, accepted M8 runtime.
const fs = require('node:fs');
const path = require('node:path');
const { chromium } = require('playwright');
const { png, sha, readActions, romSHA256 } = require('./native-play.cjs');

const work = path.resolve(__dirname, '..');
const start = path.join(work, 'checkpoints/story12-meeting-end.bin');
const startHash = '2a3551ad5082236ce2b3223323d6fff983a984a3839ff2e6fa2359c1321edea2';
const url = 'http://127.0.0.1:8765/m8-work/runtime/';
const [tag, actionFile] = process.argv.slice(2);

function writeJSON(file, data) {
  fs.writeFileSync(file, JSON.stringify(data, null, 2) + '\n');
}

async function main() {
  if (!/^[a-zA-Z0-9_-]+$/.test(tag || '')) {
    throw Error('Usage: browser-play.cjs unique-tag [m9-work/path/to/actions.json]');
  }
  const actions = actionFile ? readActions(actionFile) : [];
  const source = fs.readFileSync(start);
  if (sha(source) !== startHash) throw Error('Official story12 save hash differs');
  const out = path.join(work, 'play', tag);
  fs.mkdirSync(out);
  fs.writeFileSync(path.join(out, 'start.bin'), source);
  writeJSON(path.join(out, 'planned-actions.json'), actions);

  const frames = fs.openSync(path.join(out, 'frames.jsonl'), 'wx');
  const log = data => fs.writeSync(frames, JSON.stringify(data) + '\n');
  const records = [];
  const errors = [];
  let browser;
  let initial;
  try {
    browser = await chromium.launch({ timeout: 30000 });
    const context = await browser.newContext({ serviceWorkers: 'block' });
    await context.route('**/*', route => new URL(route.request().url()).origin === new URL(url).origin
      ? route.continue() : route.abort());
    const page = await context.newPage();
    page.on('pageerror', error => errors.push(error.message));
    await page.goto(url, { timeout: 30000 });
    await page.waitForFunction(() => window.shuihu?.ready, {}, { timeout: 60000 });
    initial = await page.evaluate(bytes => {
      const g = window.shuihu;
      if (g.meta().frames !== 1) throw Error('Unexpected startup native frame count');
      g.loadState(new Uint8Array(bytes));
      g.setHD(false);
      window.m9Observe = () => {
        const { frames, ticks, romSHA256, scroll } = g.meta();
        const read = address => g.read(address);
        return {
          frame: frames - 1, ticks, romSHA256, scroll,
          map: [0xff9a, 0xff9b].map(a => read(a).toString(16).padStart(2, '0')).join('-'),
          story: read(0xffba), dialogue: read(0xffbc), mode: read(0xd0fa), bank: read(0xd08f),
          player: Array.from({ length: 8 }, (_, i) => read(0xcd00 + i)),
          camera: [read(0xff96), read(0xff97)],
        };
      };
      return window.m9Observe();
    }, Array.from(source));
    if (initial.romSHA256 !== romSHA256 || initial.story !== 12) throw Error('Unexpected ROM or story12 entry');
    log({ type: 'start', ...initial });

    async function capture(name) {
      const { state, pixels, meta } = await page.evaluate(() => ({
        state: shuihu.state(), pixels: shuihu.pixels(), meta: window.m9Observe(),
      }));
      const save = Buffer.from(state);
      const rgba = Buffer.from(pixels);
      fs.writeFileSync(path.join(out, `${name}.png`), png(rgba, 160, 144));
      fs.writeFileSync(path.join(out, `${name}.bin`), save);
      return { ...meta, stateSHA256: sha(save), nativeFramebufferSHA256: sha(rgba) };
    }

    const startCapture = await capture('initial');
    for (const [index, action] of actions.entries()) {
      const [key, hold, wait] = action;
      for (const [on, count] of [[true, hold], [false, wait]]) {
        if (key) {
          const observation = await page.evaluate(({ key, on }) => {
            shuihu.input(key, on);
            return window.m9Observe();
          }, { key, on });
          log({ type: 'input', index, key, on, ...observation });
        }
        for (let remaining = count; remaining > 0;) {
          const batch = Math.min(remaining, 60);
          const observed = await page.evaluate(n => Array.from({ length: n }, () => {
            shuihu.step(1);
            return window.m9Observe();
          }), batch);
          for (const frame of observed) log({ type: 'frame', index, ...frame });
          remaining -= batch;
        }
      }
      const name = `action-${String(index).padStart(4, '0')}`;
      const record = { index, action, name, ...await capture(name) };
      records.push(record);
      log({ type: 'checkpoint', ...record });
      writeJSON(path.join(out, 'actions.json'), actions.slice(0, index + 1));
      console.log(name, record.frame, record.map, record.story, record.dialogue);
    }
    if (errors.length) throw Error('Runtime page error; inspect result.json');
    writeJSON(path.join(out, 'result.json'), {
      status: 'COMPLETE', acceptance: 'REVIEW_REQUIRED', sourceSHA256: startHash, url,
      initial: startCapture, end: records.at(-1) ?? startCapture, records, errors,
    });
    console.log('OUTPUT', out);
  } catch (error) {
    writeJSON(path.join(out, 'result.json'), {
      status: 'FAILED', initial, records, errors: [...errors, error.message],
    });
    throw error;
  } finally {
    fs.closeSync(frames);
    if (browser) await browser.close();
  }
}

main().catch(error => {
  console.error(error.message);
  process.exitCode = 1;
});
