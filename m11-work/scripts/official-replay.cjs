// Consolidate directed runs and replay the full chain from the M10 endpoint.
const fs = require('node:fs');
const path = require('node:path');
const zlib = require('node:zlib');
const assert = require('node:assert/strict');
const { core, sha, readActions, fieldDetails, romSHA256 } = require('./native-play.cjs');

const work = path.resolve(__dirname, '..');
const chain = path.join(work, 'official-chain');
const checkpointDir = path.join(work, 'checkpoints');
const start = path.join(checkpointDir, 'story19-00-2a-official.bin');
const sourceSHA256 = 'c41b4188203bc45d2d0c5eeb24f8b307040be0644ce861ffbcc6281d4060c8f1';
const encode = value => JSON.stringify(value, null, 2) + '\n';

async function main() {
  const args = process.argv.slice(2);
  assert(args.length, 'Pass ordered action JSON files, optionally suffixed by :checkpoint-label');
  const plannedParts = [];
  const combined = [];
  for (const spec of args) {
    const [relative, milestone] = spec.split(':');
    const file = fs.realpathSync(path.resolve(work, relative));
    assert(file.startsWith(work + '/'), 'Read route parts from M11');
    if (milestone) assert(/^[\w-]+$/.test(milestone), 'Invalid checkpoint label');
    const input = readActions(file);
    plannedParts.push({
      path: relative, actionsSHA256: sha(fs.readFileSync(file)), startIndex: combined.length,
      actionCount: input.length, milestone: milestone || null,
    });
    combined.push(...input);
  }
  const out = path.join(chain, 'official-region6-replay');
  fs.mkdirSync(out);

  const initial = fs.readFileSync(start);
  assert.equal(sha(initial), sourceSHA256);
  const actionFile = path.join(chain, 'official-region6-actions.json');
  const actionBytes = encode(combined);
  fs.writeFileSync(actionFile, actionBytes);
  const actions = readActions(actionFile);
  const c = await core();
  c.state(initial);
  const observe = () => {
    const meta = c.meta();
    return { ...meta, frame: meta.frame - 1, ...fieldDetails(c.read, meta) };
  };
  const initialFields = observe();
  assert.deepEqual([initialFields.map, initialFields.story, initialFields.cell], ['00-2a', 19, [5, 8]]);

  const parts = [];
  const changes = [];
  const milestones = [];
  const frameLog = [];
  let previous = initialFields;
  let actionIndex = 0;

  function snapshot(directory, name, note) {
    const state = c.state();
    const meta = { sha256: sha(state), ...observe(), note };
    fs.writeFileSync(path.join(directory, name + '.bin'), state);
    fs.writeFileSync(path.join(directory, name + '.json'), encode(meta));
    return meta;
  }
  snapshot(out, 'start', 'Official M10 endpoint loaded in the accepted native core.');
  frameLog.push(JSON.stringify({ type: 'start', ...initialFields }));

  for (const part of plannedParts) {
    const { path: relative, startIndex, actionCount, milestone } = part;
    const input = actions.slice(startIndex, startIndex + actionCount);
    const startFields = observe();
    const startSHA256 = startIndex === 0 ? sourceSHA256 : sha(c.state());
    for (const action of input) {
      actionIndex++;
      c.action(action, () => {
        const obs = observe();
        frameLog.push(JSON.stringify({ type: 'frame', action: actionIndex, ...obs }));
        if (obs.map !== previous.map || obs.entry !== previous.entry || obs.story !== previous.story) {
          changes.push({ action: actionIndex, ...obs });
          const name = 'frame-' + String(obs.frame).padStart(6, '0');
          c.snap(path.join(out, name + '.png'));
        }
        previous = obs;
      });
    }
    const end = observe();
    const endSHA256 = sha(c.state());
    if (milestone) milestones.push(snapshot(checkpointDir, milestone, 'Verified in the continuous official native replay.'));
    parts.push({
      ...part,
      startFrame: startFields.frame, endFrame: end.frame, frames: end.frame - startFields.frame,
      startSHA256, endSHA256, end,
    });
    console.log(relative, end.frame, end.map, end.entry, end.story, end.cell.join(','), end.hp.join('/'));
  }

  const end = observe();
  assert.equal(end.map, '00-2e');
  assert.equal(end.entry, 3);
  assert.equal(end.story, 22);
  assert.deepEqual(end.cell, [25, 5]);
  assert.equal(end.facing, 2);
  assert.equal(end.settled, true);
  assert.equal(end.DAA[2], '3e');
  assert.deepEqual(end.D2AC, ['10', '01']);
  assert.deepEqual(end.D284, ['00', '00']);
  const totalFrames = actions.reduce((sum, [, held, released]) => sum + held + released, 0);
  assert.equal(actionIndex, actions.length);
  assert.equal(end.frame, totalFrames);
  const final = snapshot(checkpointDir, 'region6-end-native', 'Story 22. One cell east of the exact-story-22 trigger at (24,5).');
  fs.copyFileSync(path.join(checkpointDir, 'region6-end-native.bin'), path.join(out, 'end.bin'));
  c.snap(path.join(out, 'end.png'));

  const manifest = {
    source: 'checkpoints/story19-00-2a-official.bin', sourceSHA256, romSHA256,
    actionsSHA256: sha(actionBytes), totalActions: actions.length, totalFrames, parts, milestones,
  };
  fs.writeFileSync(path.join(chain, 'official-region6-parts.json'), encode(manifest));
  fs.writeFileSync(path.join(out, 'frames.jsonl.gz'), zlib.gzipSync(frameLog.join('\n') + '\n'));
  fs.writeFileSync(path.join(out, 'result.json'), encode({
    status: 'COMPLETE', sourceSHA256, romSHA256, actionsSHA256: manifest.actionsSHA256,
    totalActions: actions.length, totalFrames, initial: initialFields, end: final, changes,
  }));
}
main().catch(error => { console.error(error); process.exitCode = 1; });
