// Isolated natural-input survey. Candidate chains require a one-load browser replay.
const fs = require('node:fs');
const path = require('node:path');
const { pipeline } = require('node:stream/promises');
const { createGzip } = require('node:zlib');
const { core, png, readActions, sha } = require('./native-play.cjs');

const work = path.resolve(__dirname, '..');
const officialHash = '2a3551ad5082236ce2b3223323d6fff983a984a3839ff2e6fa2359c1321edea2';
const villageHash = '239a02b3b9b8efce8db3ac35b2111b11d96233b5d661ced0ab5abd6df399bc3e';
const doorwayMaps = ['00-08', '00-01', '00-02', '00-03', '00-04', '00-06', '00-09'];
const directions = ['up', 'down', 'left', 'right'];
const settle = [null, 120, 0];
const hold = 6;
const release = 32;
const pageLimit = 24;
const frameCount = actions => actions.reduce((sum, [, down, up]) => sum + down + up, 0);
const writeJSON = (file, data) => fs.writeFileSync(file, JSON.stringify(data, null, 2) + '\n');
const readJSON = file => JSON.parse(fs.readFileSync(file, 'utf8'));
const logJSON = (fd, data) => fs.writeSync(fd, JSON.stringify(data) + '\n');
const same = (a, b) => JSON.stringify(a) === JSON.stringify(b);
const byteDelta = (a, b) => ((a - b + 128) & 255) - 128;
const battle = meta => [0x2b, 0x2c, 0x2d].includes(meta.bank);
const walking = meta => meta.mode === 0 && meta.dialogue === 0 && !battle(meta);
const gate = (meta, knownMaps) => meta.story !== 12 || !knownMaps.has(meta.map);
const observedFields = ['ticks', 'map', 'story', 'dialogue', 'mode', 'bank', 'player', 'camera', 'scroll'];

function villageRoute() {
  const village = path.join(work, 'play/story12-village-exit');
  const prefix = readActions(path.join(village, 'actions.json'));
  const record = readJSON(path.join(village, 'result.json'));
  if (!same(prefix, record.records.map(entry => entry.action)) ||
      record.status !== 'COMPLETE' || record.sourceSHA256 !== officialHash ||
      record.end.stateSHA256 !== villageHash || record.end.frame !== frameCount(prefix) ||
      record.end.map !== '00-00' || record.end.story !== 12) {
    throw Error('Village checkpoint does not match its official replay prefix');
  }
  return { prefix, end: record.end };
}

function sourceRoute(source) {
  const hash = sha(source);
  if (sha(fs.readFileSync(path.join(work, 'checkpoints/story12-meeting-end.bin'))) !== officialHash) {
    throw Error('Official story12 save hash differs');
  }
  if (hash === officialHash) return { map: '00-05', knownMaps: new Set(['00-05', '00-00']), prefix: [] };
  const village = villageRoute();
  if (hash === villageHash) {
    const knownMaps = Object.keys(readJSON(path.join(work, 'search/village-doors-cont/result.json')).found);
    return { map: '00-00', knownMaps: new Set(['00-00', ...knownMaps]), prefix: village.prefix };
  }

  const dir = path.join(work, 'search/village-doors');
  const result = readJSON(path.join(dir, 'result.json'));
  const map = doorwayMaps.find(id => result.found[id]?.searchStateSHA256 === hash);
  if (!map) throw Error('Use the preserved story12 meeting, village, or supported village doorway save');
  const found = result.found[map];
  const provenance = readJSON(path.join(dir, 'provenance.json'));
  const suffix = readActions(path.join(dir, map + '-actions.json'));
  if (!result.isolatedSearch || result.origin !== '00-00' ||
      provenance.status !== 'COMPLETE' || provenance.mode !== 'doors' ||
      !provenance.naturalControlsOnly || provenance.sourceSHA256 !== villageHash ||
      sha(fs.readFileSync(path.join(dir, 'start.bin'))) !== villageHash ||
      found.id !== map || found.story !== 12 || found.mode !== 0 ||
      suffix.length < 2 || !same(suffix[0], settle) || !same(suffix, found.actions) ||
      suffix.slice(1).some(([key, down, up]) => !directions.includes(key) || down !== 16 || up !== 8)) {
    throw Error('Doorway evidence does not match the preserved village search');
  }
  const branch = fs.readFileSync(path.join(dir, 'branches.jsonl'), 'utf8').trimEnd().split('\n')
    .map(line => JSON.parse(line))
    .find(entry => entry.node === found.branchNode && entry.stateSHA256 === hash && entry.map === map &&
      entry.story === found.story && entry.mode === found.mode && same(entry.xy, found.xy) &&
      same(entry.actions, [suffix.at(-1)]));
  if (!branch) throw Error('Doorway checkpoint is missing from the village search branch log');
  return {
    map, knownMaps: new Set([map, '00-00']), prefix: [...village.prefix, ...suffix],
    doorway: { branch, screenshot: path.join(dir, map + '.png'), village },
  };
}

function compareFields(actual, expected, fields, label) {
  for (const field of fields) {
    if (!same(actual?.[field], expected[field])) throw Error(label + ' differs in ' + field);
  }
}

function verifyReplay(candidateFile, tag) {
  if (!/^[a-zA-Z0-9_-]+$/.test(tag || '')) throw Error('Pass the browser replay tag');
  const candidate = readJSON(candidateFile);
  const candidateDir = path.dirname(candidateFile);
  const source = fs.readFileSync(path.join(candidateDir, '..', 'start.bin'));
  const { prefix, doorway } = sourceRoute(source);
  const suffix = readActions(path.join(candidateDir, 'suffix-actions.json'));
  const dir = path.join(work, 'play', tag);
  const result = readJSON(path.join(dir, 'result.json'));
  const expectedActions = readActions(path.join(candidateDir, 'chain-actions.json'));
  const actualActions = readActions(path.join(dir, 'actions.json'));
  if (candidate.prefixActions !== prefix.length || !same(expectedActions, [...prefix, ...suffix]) ||
      result.status !== 'COMPLETE' || result.sourceSHA256 !== officialHash ||
      !same(expectedActions, actualActions) || !same(actualActions, result.records.map(record => record.action)) ||
      result.end.frame !== frameCount(actualActions)) {
    throw Error('Official replay did not execute the full candidate input chain');
  }
  if (doorway) {
    const village = result.records[doorway.village.prefix.length - 1];
    compareFields(village, doorway.village.end, ['frame', ...observedFields, 'nativeFramebufferSHA256'],
      'Browser village checkpoint');
    const arrival = result.records[prefix.length - 1];
    compareFields(arrival, { ...doorway.branch, frame: frameCount(prefix) },
      ['frame', ...observedFields], 'Browser doorway checkpoint');
    const arrivalName = 'action-' + String(prefix.length - 1).padStart(4, '0');
    if (!fs.readFileSync(path.join(dir, arrivalName + '.png')).equals(fs.readFileSync(doorway.screenshot))) {
      throw Error('Browser doorway screenshot differs from the preserved village search');
    }
  } else if (prefix.length > 0 && result.records[prefix.length - 1]?.stateSHA256 !== villageHash) {
    throw Error('Browser prefix did not reproduce the preserved village checkpoint');
  }
  compareFields(result.end, candidate.end, [...observedFields, 'nativeFramebufferSHA256'], 'Replay endpoint');
  const save = path.join(dir, result.end.name + '.bin');
  if (sha(fs.readFileSync(save)) !== result.end.stateSHA256) throw Error('Browser endpoint save hash differs');
  return path.relative(path.dirname(work), save);
}

async function survey(src, tag, nodeLimit, seconds) {
  if (!/^[a-zA-Z0-9_-]+$/.test(tag || '') ||
      !Number.isInteger(nodeLimit) || nodeLimit < 1 || nodeLimit > 4000 ||
      !Number.isInteger(seconds) || seconds < 1 || seconds > 300) {
    throw Error('Usage: interact-survey.cjs SOURCE TAG [1..4000 nodes] [1..300 seconds]');
  }
  const sourcePath = fs.realpathSync(src);
  if (!sourcePath.startsWith(work + path.sep)) throw Error('Use a preserved M9 save');
  const source = fs.readFileSync(sourcePath);
  const { map, knownMaps, prefix, doorway } = sourceRoute(source);
  const c = await core();
  const out = path.join(work, 'search', tag);
  fs.mkdirSync(out);
  fs.writeFileSync(path.join(out, 'start.bin'), source);
  writeJSON(path.join(out, 'prefix-actions.json'), prefix);
  const framePath = path.join(out, 'frames.jsonl');
  const frames = fs.openSync(framePath, 'wx');
  const branches = fs.openSync(path.join(out, 'branches.jsonl'), 'wx');
  c.setLog(frames);
  const root = { path: [], state: source, hash: sha(source) };
  const provenance = {
    isolatedSearch: true, accepted: false, source: sourcePath, sourceSHA256: root.hash,
    officialSHA256: officialHash, expectedMap: map, prefixFrames: frameCount(prefix),
    ...(doorway && { villagePrefixActions: doorway.village.prefix.length,
      doorwayEvidence: path.relative(work, path.dirname(doorway.screenshot)) }),
    scriptSHA256: sha(fs.readFileSync(__filename)), coreAdapterSHA256: sha(fs.readFileSync(require.resolve('./native-play.cjs'))),
    nodeLimit, seconds, pageLimit, started: new Date().toISOString(), status: 'RUNNING',
  };
  writeJSON(path.join(out, 'provenance.json'), provenance);

  const deadline = Date.now() + seconds * 1000;
  const queue = [];
  const seen = new Set();
  const stands = new Set();
  const presses = { A: 0, B: 0 };
  const candidates = [];
  const uiSamples = new Set();
  let expanded = 0;
  let confirmedMarker = false;
  let visualSamples = 0;

  function load(node, label) {
    c.setBranch(label);
    c.state(node.state);
    const before = c.meta();
    c.event({ type: 'branch-load', branch: label, stateSHA256: node.hash, path: node.path, ...before });
    return before;
  }

  function act(action, before) {
    const signals = new Set();
    let firstSignal;
    c.action(action, current => {
      const signalsNow = [];
      if (current.story !== before.story) signalsNow.push('story');
      if (current.map !== before.map && (action[0] === 'A' || action[0] === 'B' ||
          !knownMaps.has(current.map))) signalsNow.push('map');
      if (current.dialogue !== before.dialogue) signalsNow.push('dialogue');
      if (!signalsNow.length) return;
      signalsNow.forEach(signal => signals.add(signal));
      firstSignal ??= { meta: current, pixels: c.fb() };
    });
    return { before, action, signals: [...signals], firstSignal, end: c.meta() };
  }

  function record(node, probe, kind, xy) {
    const { before, action, signals, firstSignal, end } = probe;
    const suffix = [...node.path, action];
    const name = 'candidate-' + String(candidates.length + 1).padStart(3, '0');
    const dir = path.join(out, name);
    fs.mkdirSync(dir);
    c.snap(path.join(dir, 'response.png'));
    if (firstSignal) {
      fs.writeFileSync(path.join(dir, 'first-signal.png'), png(firstSignal.pixels, 160, 144));
    }
    const pages = [{ name: 'response', suffixActions: suffix.length, ...end }];
    let current = end;
    function checkpoint(action, name) {
      const checkpointProbe = act(action, current);
      suffix.push(action);
      current = checkpointProbe.end;
      c.snap(path.join(dir, name + '.png'));
      pages.push({ name, suffixActions: suffix.length, signals: checkpointProbe.signals,
        firstSignal: checkpointProbe.firstSignal?.meta ?? null, ...current });
    }
    if (signals.length || gate(current, knownMaps)) checkpoint(settle, 'settled');
    for (let page = 1; page <= pageLimit && Date.now() < deadline &&
         current.map === map && current.mode === 0 && current.dialogue > 0 &&
         !battle(current) && !gate(current, knownMaps); page++) {
      checkpoint(['A', hold, 120], 'page-' + String(page).padStart(2, '0'));
    }
    const marker = gate(current, knownMaps);
    if (marker && pages.at(-1).name !== 'settled') checkpoint(settle, 'end-settled');
    confirmedMarker = gate(current, knownMaps);
    const save = c.state();
    const result = {
      isolatedSearch: true, accepted: false, kind, name, xy, before, signals,
      firstSignal: firstSignal?.meta ?? null, action, prefixActions: prefix.length,
      pages, observedMarkerAtEnd: confirmedMarker,
      dialogueStillOpen: current.dialogue > 0,
      end: { ...current, stateSHA256: sha(save), nativeFramebufferSHA256: sha(c.fb()) },
    };
    fs.writeFileSync(path.join(dir, 'end.bin'), save);
    writeJSON(path.join(dir, 'candidate.json'), result);
    writeJSON(path.join(dir, 'suffix-actions.json'), suffix);
    writeJSON(path.join(dir, 'chain-actions.json'), [...prefix, ...suffix]);
    candidates.push({ name, kind, xy, signals, end: result.end, observedMarkerAtEnd: confirmedMarker });
    console.log(name, kind, xy, current.map, current.story, current.dialogue);
    return name;
  }

  function enqueue(parentPath, action, end, scroll) {
    const xy = [scroll[0] + end.player[1], scroll[1] + end.player[0]];
    const key = [end.map, ...xy, end.bank, end.player[3], ...end.player.slice(5)].join(',');
    if (seen.has(key)) return;
    seen.add(key);
    const save = c.state();
    queue.push({ id: queue.length, path: [...parentPath, action], state: save, hash: sha(save),
      xy, scroll, facing: end.player[3] });
  }

  try {
    const initial = load(root, 'root');
    if (initial.story !== 12 || initial.map !== map) throw Error('Unexpected preserved save metadata');
    const start = act(settle, initial);
    c.snap(path.join(out, 'start-settled.png'));
    if (start.signals.length || gate(start.end, knownMaps)) record(root, start, 'settle', null);
    if (!confirmedMarker && start.end.map === map && walking(start.end) && !start.signals.length) {
      enqueue([], settle, start.end, start.end.scroll.map((value, i) => value + start.end.camera[i] * 32));
    }

    while (!confirmedMarker && expanded < queue.length && expanded < nodeLimit && Date.now() < deadline) {
      const node = queue[expanded];
      queue[expanded++] = null;
      const standKey = [...node.xy, node.facing].join(',');
      const freshStand = !stands.has(standKey);
      if (freshStand) stands.add(standKey);
      const probes = freshStand ? [[null, hold + release, 0], ['A', hold, release], ['B', hold, release]] : [];
      const actions = [...probes, ...directions.map(direction => [direction, 16, 8])];
      let idleFrame;
      for (const action of actions) {
        if (confirmedMarker || Date.now() >= deadline) break;
        const key = action[0] ?? 'idle';
        const button = key === 'A' || key === 'B';
        const before = load(node, [node.id, key]);
        const probe = act(action, before);
        const { end, signals } = probe;
        const moved = directions.includes(key);
        const scroll = node.scroll.map((value, i) => value + byteDelta(end.scroll[i], before.scroll[i]));
        if (key === 'idle') idleFrame = sha(c.fb());
        if (button) presses[key]++;
        const framebuffer = button ? sha(c.fb()) : undefined;
        if (moved && !signals.length && end.map === map && end.story === 12 && walking(end)) {
          enqueue(node.path, action, end, scroll);
        }
        let candidate;
        if (signals.length || gate(end, knownMaps)) {
          candidate = record(node, probe, button ? 'interaction' : key, node.xy);
        } else if (end.map === map && (end.mode !== before.mode || end.bank !== before.bank)) {
          const signature = [key, end.mode, end.bank].join(',');
          if (!uiSamples.has(signature)) {
            uiSamples.add(signature);
            candidate = record(node, probe, 'mode-or-bank', node.xy);
          }
        } else if (button && framebuffer !== idleFrame && visualSamples < 24) {
          visualSamples++;
          candidate = record(node, probe, 'visual', node.xy);
        }

        logJSON(branches, { node: node.id, xy: node.xy, facing: before.player[3], action,
          signals, end, candidate, framebuffer, differsFromIdle: button && framebuffer !== idleFrame });
      }
    }
    const frontier = queue.length - expanded;
    const deadlineHit = Date.now() >= deadline;
    const result = {
      isolatedSearch: true, accepted: false, origin: map, expanded, frontier, nodes: seen.size,
      deadlineHit, nodeLimitHit: frontier > 0 && expanded >= nodeLimit,
      stoppedOnObservedMarker: confirmedMarker, standingPositionFacings: [...stands], presses, visualSamples, candidates,
    };
    writeJSON(path.join(out, 'result.json'), result);
    provenance.status = 'COMPLETE';
    console.log('OUTPUT', out, JSON.stringify({ expanded, frontier, deadlineHit, candidates: candidates.length }));
  } catch (error) {
    provenance.status = 'FAILED';
    provenance.error = error.message;
    throw error;
  } finally {
    fs.closeSync(branches);
    fs.closeSync(frames);
    await pipeline(fs.createReadStream(framePath), createGzip(), fs.createWriteStream(framePath + '.gz', { flags: 'wx' }));
    fs.unlinkSync(framePath);
    writeJSON(path.join(out, 'provenance.json'), { ...provenance, finished: new Date().toISOString() });
  }
}

async function main() {
  const [source, tag, limit = '3000', seconds = '240'] = process.argv.slice(2);
  if (source === '--verify') {
    console.log(verifyReplay(tag, process.argv[4]));
    return;
  }
  return survey(source, tag, Number(limit), Number(seconds));
}

if (require.main === module) main().catch(error => {
  console.error(error.message);
  process.exitCode = 1;
});
module.exports = { survey, verifyReplay };
