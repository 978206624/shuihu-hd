# 00-06 v2 outer verification

The reviewed v2 plate is installed in the live `m8-work/runtime/`. The offline freeze check passed for all 329 entries. Outer browser verification is pending.

| Integration provenance | Value |
| --- | --- |
| Live plate | `m8-work/runtime/assets/region3/00-06_hd.png` |
| Source | `m8-work/art/00-06_gpt_v2.png` |
| Source and live SHA-256 | `91125e14a469c162db6454acd0d573b812d9908ae8c1c45a90a26fb39676316a` |
| CLI metadata | `m8-work/art/00-06_gpt_v2.png.meta.json` |
| Metadata SHA-256 | `419b10a401346ebdaea5b1f87335e734de6451b04ada4d0bdc810c5a6fa6cc4d` |
| Requested image | `gpt-image-2`, medium, 960 × 800 |
| Actual PNG | 1374 × 1145 |
| Prompt and review crop | `m8-work/art/00-06_prompt_v2.txt`, `m8-work/art/00-06_glyphs_before_after.png` |
| Preserved v1 provenance | `m8-work/art/00-06_gpt.png`, SHA-256 `3a5a9c9d132690fd38c5ac2836ffa7272ea839737b5148adacfddf52393ce11d` in `integration/provenance.json` under `previousVersion` |

## Run on the outer host

Keep the existing 8765 server and wait for conflicting QA or perf work to finish. The block acquires both exclusive locks, checks the local and served plate bytes, and runs the complete official temple doorway replay using the frozen start and inputs. It applies the route selection and expected totals in memory. The official per-frame state, native framebuffer, actor/text, and coverage assertions still run. The accepted report is consulted for summary and endpoint parity.

```bash
cd /workspace/shawu && setsid --wait bash <<'OUTER'
set -euo pipefail
export NODE_PATH=/home/box/opt/test-tools/node_modules
export PLAYWRIGHT_BROWSERS_PATH=/home/box/opt/playwright-browsers
export M8_RESULTS="/workspace/shawu/m8-work/results/outer-00-06-v2-$(date -u +%Y%m%dT%H%M%S%NZ)"
pgid=$(ps -o pgid= -p "$$")
[[ ${pgid//[[:space:]]/} == "$$" ]]
for port in 38811 8765; do
  listener=$(ss -Hltn "sport = :$port")
  [[ -n "$listener" ]] || { echo "Listener $port unavailable. Stop and report." >&2; exit 1; }
done
exec 9>>m7-work/stage-a/exclusive.lock
flock -n 9 || { echo 'Stage A exclusive lock is held.' >&2; exit 1; }
exec 8>>m8-work/outer-exclusive.lock
flock -n 8 || { echo 'M8 exclusive lock is held.' >&2; exit 1; }
mkdir -- "$M8_RESULTS"
printf '%s\n' "$$" > "$M8_RESULTS/runner.pid"
watcher=
checkpoint() {
  printf '%s 00-06 v2 outer %s %s\n' "$(date -u +%FT%TZ)" "$1" "$M8_RESULTS" |
    tee -a m8-work/progress.md
}
finish() {
  local rc=$?
  trap - EXIT TERM INT
  if [[ -n "$watcher" ]]; then
    kill "$watcher" 2>/dev/null || true
    wait "$watcher" 2>/dev/null || true
  fi
  printf '%s\n' "$rc" > "$M8_RESULTS/exit-code.txt"
  checkpoint "EXIT_$rc"
  exit "$rc"
}
trap finish EXIT
trap 'exit 143' TERM
trap 'exit 130' INT
checkpoint 'preflight started'
node m8-work/cold-0017/check.cjs watch "$$" > "$M8_RESULTS/ports.log" 2>&1 &
watcher=$!

sha=91125e14a469c162db6454acd0d573b812d9908ae8c1c45a90a26fb39676316a
asset=m8-work/runtime/assets/region3/00-06_hd.png
printf '%s  %s\n' "$sha" "$asset" | sha256sum --check
cmp -- m8-work/art/00-06_gpt_v2.png "$asset"
curl -fsS --max-time 10 "http://127.0.0.1:8765/$asset" |
  cmp -- - "$asset"
python3 m8-work/scripts/offline-check.py --verify-only | tee "$M8_RESULTS/offline.log"

checkpoint 'formal-door-00-06 started'
node <<'REPLAY' 2>&1 | tee "$M8_RESULTS/qa.log"
const assert = require('node:assert/strict');
const Module = require('node:module');
const { fs, path, W, roots } = require('./m8-work/scripts/common.cjs');
assert.equal(roots.candidate, W + '/runtime');
const read = name => JSON.parse(fs.readFileSync(W + '/inputs/' + name));
const selected = read('qa-routes.json').filter(route => route.name === 'formal-door-00-06');
assert.equal(selected.length, 1);
const [route] = selected;
assert.equal(route.target, '00-06');
assert.equal(route.independentDoorSurvey, true);
assert.equal(route.regressionVisualExact, false);
assert.equal(route.saveAt, 34);
assert.equal(route.actions.length, 35);
assert.equal(route.actions.reduce((frames, [, hold, wait]) => frames + hold + wait, 0), 1092);

const file = path.join(W, 'scripts', 'qa.cjs');
let code = fs.readFileSync(file, 'utf8');
function replaceOnce(original, replacement) {
  assert.equal(code.split(original).length, 2, 'Official QA source changed: ' + original);
  code = code.replace(original, replacement);
}
replaceOnce(
  "for(const b of JSON.parse(fs.readFileSync(W+'/inputs/qa-routes.json'))){",
  "for(const b of JSON.parse(fs.readFileSync(W+'/inputs/qa-routes.json')).filter(route=>route.name==='formal-door-00-06')){"
);
replaceOnce(
  'report.actions===expected.formalQAActions&&report.frames===expected.formalQAFrames&&report.regressionActions===442&&report.regressionFrames===31396',
  'report.actions===35&&report.frames===1092&&report.regressionActions===0&&report.regressionFrames===0'
);
replaceOnce('report.regressionVisualPassed===31396', 'report.regressionVisualPassed===0');
const scopedQA = new Module(file, module);
scopedQA.filename = file;
scopedQA.paths = module.paths;
scopedQA._compile(code, file);
REPLAY

node <<'CHECK' | tee "$M8_RESULTS/qa-check.json"
const assert = require('node:assert/strict');
const { fs, W, output, sha } = require('./m8-work/scripts/common.cjs');
const acceptedBytes = fs.readFileSync(W + '/results/outer-20261118T062207Z/qa/report.json');
assert.equal(sha(acceptedBytes), '42575581d9f543208324ba932f5c891cbd95ac5d44644f76a2e0bca487654fca');
const accepted = JSON.parse(acceptedBytes);
const dir = output() + '/qa';
const qa = JSON.parse(fs.readFileSync(dir + '/report.json'));
assert(accepted.pass && qa.pass && !qa.error && qa.errors.length === 0);
assert.equal(qa.actions, 35);
for (const field of ['frames', 'statePassed', 'nativePassed', 'actorTextPassed']) {
  assert.equal(qa[field], 1092, field);
}
const historical = accepted.routes.filter(route => route.name === 'formal-door-00-06');
assert.equal(historical.length, 1);
assert.deepEqual(qa.routes, historical, 'Temple start or action endpoints differ');
assert.equal(qa.routes[0].endpoint.map, '00-06');
const map = '00-06';
assert.deepEqual(qa.sourceMapFrames[map], accepted.sourceMapFrames[map], 'Temple frame/source counts differ');
const selections = report => Object.fromEntries(
  Object.entries(report.sourceMapFrames)
    .filter(([, sources]) => sources[map] > 0)
    .map(([nativeMap, sources]) => [nativeMap, sources[map]])
);
assert.deepEqual(selections(qa), selections(accepted), 'Focused route did not reproduce all accepted temple plate selections');
assert.deepEqual(qa.region3Coverage[map], accepted.region3Coverage[map], 'Temple coverage differs');
assert.deepEqual(qa.region3Excluded[map], accepted.region3Excluded[map], 'Temple exclusions differ');
const coverage = qa.region3Coverage[map];
assert(coverage.covered > 0, 'The authored temple plate was never credited');
for (const mode of ['native', 'hd']) assert(fs.statSync(dir + '/' + map + '-' + mode + '.png').size > 0);
console.log(JSON.stringify({
  pass: true, route: qa.routes[0].name, actions: qa.actions, frames: qa.frames,
  state: qa.statePassed, native: qa.nativePassed, actorText: qa.actorTextPassed, coverage,
}, null, 2));
CHECK

test ! -e "$M8_RESULTS/port-stop.txt"
touch "$M8_RESULTS/qa.done"
checkpoint 'focused temple verification passed'
OUTER
```

Require exit code 0, `qa.done`, and `qa-check.json` with `pass: true` and 1,092 checks in each invariant. The doorway evidence is `qa/00-06-native.png` and `qa/00-06-hd.png` in the new result directory. A coverage or selection mismatch leaves focused verification open. If 38811 drops, the watchdog stops the process group. Report the time, stage, and result path from `port-stop.txt` and the progress checkpoint. Leave auth, routes, and credentials alone.
