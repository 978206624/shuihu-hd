// Replay the official M11 start in the accepted M10 browser runtime.
const fs = require('node:fs');
const path = require('node:path');
const { chromium } = require('playwright');
const { png, sha, readActions, romSHA256 } = require('./native-play.cjs');

const work = path.resolve(__dirname, '..');
const start = path.join(work, 'checkpoints/story19-00-2a-official.bin');
const startHash = 'c41b4188203bc45d2d0c5eeb24f8b307040be0644ce861ffbcc6281d4060c8f1';
const url = 'http://127.0.0.1:8765/m10-work/runtime/';
const origin = new URL(url).origin;
const [tag, actionFile] = process.argv.slice(2);

function writeJSON(file, data) {
  const temporary = `${file}.tmp`;
  fs.writeFileSync(temporary, JSON.stringify(data, null, 2) + '\n');
  fs.renameSync(temporary, file);
}

async function main() {
  if (!/^[a-zA-Z0-9_-]+$/.test(tag || '') || !actionFile) {
    throw Error('Usage: node m11-work/scripts/browser-play.cjs unique-tag path/to/actions.json');
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
    if (result.sourceSHA256 !== startHash) throw Error('Official story19 checkpoint file hash differs');

    const manifest = JSON.parse(fs.readFileSync(path.join(work, 'official-chain/official-region6-parts.json'), 'utf8'));
    const expected = JSON.parse(fs.readFileSync(path.join(work, 'checkpoints/region6-end-native.json'), 'utf8'));
    if (sha(fs.readFileSync(actionFile)) !== manifest.actionsSHA256) throw Error('Official action file hash differs');
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
      window.m11Observe = () => {
        const { frames, ticks, romSHA256, scroll } = g.meta();
        const read = address => g.read(address);
        const bytes = (address, size) => Array.from({ length: size }, (_, i) =>
          read(address + i).toString(16).padStart(2, '0'));
        const word = address => read(address) | (read(address + 1) << 8);
        const signed = address => word(address) << 16 >> 16;
        const cell = [
          2 * read(0xff96) + (signed(0xffae) + read(0xcd01) - 8) / 16,
          2 * read(0xff97) + (signed(0xffb0) + read(0xcd00) - 16) / 16,
        ];
        const bank = read(0xd08f), mode = read(0xd0fa), dialogue = read(0xffbc);
        const script = read(0xffd6), banner = read(0xffc1);
        return {
          frame: frames - 1, ticks, romSHA256, scroll,
          map: [0xff9a, 0xff9b].map(address => read(address).toString(16).padStart(2, '0')).join('-'),
          story: read(0xffba), dialogue, mode, bank, script, banner,
          entry: read(0xff9c), cell, facing: read(0xcd03),
          settled: [3, 4, 5].includes(bank) && !mode && !dialogue && !script && !banner && cell.every(Number.isInteger),
          DAA: bytes(0xdaa0, 4), D2AC: bytes(0xd2ac, 2), D284: bytes(0xd284, 2),
          party: [0xd200, 0xd216, 0xd22c].map(address => bytes(address, 1)[0]),
          hp: [0xd202, 0xd218, 0xd22e].map(word),
          player: Array.from({ length: 8 }, (_, i) => read(0xcd00 + i)),
          camera: [read(0xff96), read(0xff97)],
        };
      };
      window.m11Capture = (meta = window.m11Observe()) => ({
        state: g.state(), pixels: g.pixels(), meta,
      });
      return window.m11Observe();
    }, Array.from(source));
    if (initial.romSHA256 !== romSHA256 || initial.story !== 19 || initial.map !== '00-2a') {
      throw Error(`Unexpected official start (ROM ${initial.romSHA256}, map ${initial.map}, story ${initial.story})`);
    }
    log({ type: 'start', ...initial });
    result.initial = saveSnapshot(await page.evaluate(() => window.m11Capture()), {
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
            return window.m11Observe();
          }, { key, on });
          log({ type: 'input', index, key, on, ...observation });
        }

        for (let remaining = count; remaining > 0;) {
          const batch = Math.min(remaining, 60);
          const observed = await page.evaluate(({ batch, map, entry, story }) => {
            const frames = [];
            for (let i = 0; i < batch; i++) {
              window.shuihu.step(1);
              const meta = window.m11Observe();
              const reasons = [];
              if (meta.map !== map) reasons.push('map-change');
              if (meta.entry !== entry) reasons.push('entry-change');
              if (meta.story !== story) reasons.push('story-change');
              // Capture before the next step so mid-batch transitions retain their own pixels and state.
              const snapshot = reasons.length ? window.m11Capture(meta) : null;
              frames.push({ meta, snapshot, reasons });
              map = meta.map;
              entry = meta.entry;
              story = meta.story;
            }
            return frames;
          }, { batch, map: previous.map, entry: previous.entry, story: previous.story });

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
        saveSnapshot(await page.evaluate(() => window.m11Capture()), {
          index, action, name, reasons: ['every-50th-action'],
        });
      }
    }

    result.end = saveSnapshot(await page.evaluate(() => window.m11Capture()), {
      index: actions.length, name: 'end', reasons: ['end'],
    });
    result.totalActions = executed.length;
    result.totalFrames = result.end.frame;
    if (result.totalActions !== manifest.totalActions || result.totalFrames !== manifest.totalFrames) {
      throw Error('Official route action or frame count differs');
    }
    for (const key of ['map', 'entry', 'story', 'cell', 'facing', 'bank', 'mode', 'dialogue',
      'script', 'banner', 'settled', 'DAA', 'D2AC', 'D284', 'party', 'hp']) {
      if (JSON.stringify(result.end[key]) !== JSON.stringify(expected[key])) {
        throw Error(`Endpoint ${key}: expected ${JSON.stringify(expected[key])}, got ${JSON.stringify(result.end[key])}`);
      }
    }
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
