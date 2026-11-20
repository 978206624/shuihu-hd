// Replay the official M10 start in the accepted M8 browser runtime.
const fs = require('node:fs');
const path = require('node:path');
const { chromium } = require('playwright');
const { png, sha, readActions, romSHA256 } = require('./native-play.cjs');

const work = path.resolve(__dirname, '..');
const start = path.join(work, 'checkpoints/story14-inn-end.bin');
const startHash = 'f389cebc3fc59a310571c66538d38808c32483c7632164f35d207f0738e8d6c0';
const url = 'http://127.0.0.1:8765/m8-work/runtime/';
const origin = new URL(url).origin;
const [tag, actionFile] = process.argv.slice(2);

function writeJSON(file, data) {
  const temporary = `${file}.tmp`;
  fs.writeFileSync(temporary, JSON.stringify(data, null, 2) + '\n');
  fs.renameSync(temporary, file);
}

async function main() {
  if (!/^[a-zA-Z0-9_-]+$/.test(tag || '') || !actionFile) {
    throw Error('Usage: node m10-work/scripts/browser-play.cjs unique-tag path/to/actions.json');
  }

  const out = path.join(work, 'play', tag);
  fs.mkdirSync(out);
  const result = { status: 'FAILED', sourceSHA256: null, url, initial: null, end: null, records: [], errors: [] };
  const executed = [];
  let browser;
  let frames;
  const log = data => fs.writeSync(frames, JSON.stringify(data) + '\n');

  function saveSnapshot({ state, pixels, meta }, details) {
    const save = Buffer.from(state);
    const rgba = Buffer.from(pixels);
    const { name, index } = details;
    fs.writeFileSync(path.join(out, `${name}.png`), png(rgba, 160, 144));
    fs.writeFileSync(path.join(out, `${name}.bin`), save);
    const record = { ...details, ...meta, stateSHA256: sha(save), nativeFramebufferSHA256: sha(rgba) };
    result.records.push(record);
    log({ type: 'checkpoint', ...record });
    console.log(`${name} index=${index} frame=${meta.frame} map=${meta.map} story=${meta.story} dialogue=${meta.dialogue}`);
    return record;
  }

  try {
    const source = fs.readFileSync(start);
    result.sourceSHA256 = sha(source);
    if (result.sourceSHA256 !== startHash) throw Error('Official story14 checkpoint file hash differs');

    const actions = readActions(actionFile);
    const actionsPath = path.join(out, 'actions.json');
    writeJSON(path.join(out, 'planned-actions.json'), actions);
    writeJSON(actionsPath, executed);
    frames = fs.openSync(path.join(out, 'frames.jsonl'), 'wx');

    browser = await chromium.launch({ timeout: 30000 });
    const context = await browser.newContext({ serviceWorkers: 'block' });
    await context.route('**/*', route => new URL(route.request().url()).origin === origin
      ? route.continue() : route.abort());
    const page = await context.newPage();
    page.on('pageerror', error => result.errors.push(error.message));
    await page.goto(url, { timeout: 30000 });
    await page.waitForFunction(() => window.shuihu?.ready, {}, { timeout: 60000 });

    const initial = await page.evaluate(bytes => {
      const g = window.shuihu;
      if (g.meta().frames !== 1) throw Error('Unexpected startup native frame count');
      g.loadState(new Uint8Array(bytes));
      g.setHD(false);
      window.m10Observe = () => {
        const { frames, ticks, romSHA256, scroll } = g.meta();
        const read = address => g.read(address);
        return {
          frame: frames - 1, ticks, romSHA256, scroll,
          map: [0xff9a, 0xff9b].map(address => read(address).toString(16).padStart(2, '0')).join('-'),
          story: read(0xffba), dialogue: read(0xffbc), mode: read(0xd0fa), bank: read(0xd08f),
          player: Array.from({ length: 8 }, (_, i) => read(0xcd00 + i)),
          camera: [read(0xff96), read(0xff97)],
        };
      };
      window.m10Capture = (meta = window.m10Observe()) => ({
        state: g.state(), pixels: g.pixels(), meta,
      });
      return window.m10Observe();
    }, Array.from(source));
    if (initial.romSHA256 !== romSHA256 || initial.story !== 14 || initial.map !== '00-2c') {
      throw Error(`Unexpected official start (ROM ${initial.romSHA256}, map ${initial.map}, story ${initial.story})`);
    }
    log({ type: 'start', ...initial });
    result.initial = saveSnapshot(await page.evaluate(() => window.m10Capture()), {
      index: 0, name: 'initial', reasons: ['initial'],
    });

    let previous = initial;
    for (const [offset, action] of actions.entries()) {
      const index = offset + 1;
      const [key, hold, release] = action;
      for (const [on, count] of [[true, hold], [false, release]]) {
        if (key) {
          const observation = await page.evaluate(({ key, on }) => {
            window.shuihu.input(key, on);
            return window.m10Observe();
          }, { key, on });
          log({ type: 'input', index, key, on, ...observation });
        }

        for (let remaining = count; remaining > 0;) {
          const batch = Math.min(remaining, 60);
          const observed = await page.evaluate(({ batch, map, story }) => {
            const frames = [];
            for (let i = 0; i < batch; i++) {
              window.shuihu.step(1);
              const meta = window.m10Observe();
              const reasons = [];
              if (meta.map !== map) reasons.push('map-change');
              if (meta.story !== story) reasons.push('story-change');
              // Capture before the next step so mid-batch transitions retain their own pixels and state.
              const snapshot = reasons.length ? window.m10Capture(meta) : null;
              frames.push({ meta, snapshot, reasons });
              map = meta.map;
              story = meta.story;
            }
            return frames;
          }, { batch, map: previous.map, story: previous.story });

          for (const { meta, snapshot, reasons } of observed) {
            log({ type: 'frame', index, ...meta });
            if (snapshot) {
              const name = `frame-${String(meta.frame).padStart(6, '0')}`;
              saveSnapshot(snapshot, { index, action, name, reasons });
            }
            previous = meta;
          }
          remaining -= batch;
        }
      }

      executed.push(action);
      writeJSON(actionsPath, executed);
      if (index % 50 === 0) {
        const name = `action-${String(index).padStart(4, '0')}`;
        saveSnapshot(await page.evaluate(() => window.m10Capture()), {
          index, action, name, reasons: ['every-50th-action'],
        });
      }
    }

    result.end = saveSnapshot(await page.evaluate(() => window.m10Capture()), {
      index: actions.length, name: 'end', reasons: ['end'],
    });
    if (result.errors.length) throw Error('Runtime page error. Inspect result.json.');
    result.status = 'COMPLETE';
  } catch (error) {
    result.errors.push(error.message);
    throw error;
  } finally {
    writeJSON(path.join(out, 'result.json'), result);
    if (frames !== undefined) fs.closeSync(frames);
    if (browser) await browser.close();
  }
  console.log('OUTPUT', out);
}

main().catch(error => {
  console.error(error.message);
  process.exitCode = 1;
});
