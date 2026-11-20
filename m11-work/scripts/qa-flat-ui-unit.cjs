const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const {core, readActions, sha} = require('./native-play.cjs');
const {compareFrame, validateDefectCounts} = require('./region6-qa.cjs');

const work = path.resolve(__dirname, '..');
const failedRun = 'm11-region6-20261120T140423261638555Z';
const width = 160, height = 144, scale = 4;

function nearest(pixels) {
  const native = new Uint32Array(pixels.buffer, pixels.byteOffset, width*height);
  const hd = new Uint32Array(width*height*scale*scale);
  for (let y=0; y<height*scale; y++) {
    for (let x=0; x<width*scale; x++) {
      hd[y*width*scale+x] = native[Math.floor(y/scale)*width+Math.floor(x/scale)];
    }
  }
  return Buffer.from(hd.buffer);
}

function textHash(observation, rgba, rendered) {
  const bytes = [];
  for (let y=0; y<height; y++) {
    for (let x=0; x<width; x++) {
      const i = y*width+x;
      const k = (((y+observation.scy)&255)>>3)*32+(((x+observation.scx)&255)>>3);
      if (!observation.mask[i] || observation.actorMask[i] ||
          [0xa1,0xa2,0xa3,0xa4].includes(observation.tiles[k])) continue;
      bytes.push(i&255,i>>8);
      for (let dy=0; dy<scale; dy++) {
        for (let dx=0; dx<scale; dx++) {
          const q = ((y*scale+dy)*width*scale+x*scale+dx)*4;
          bytes.push(...(rendered ? rendered.subarray(q,q+4) : rgba.subarray(i*4,i*4+4)));
        }
      }
    }
  }
  return sha(Buffer.from(bytes));
}

async function main() {
  const {Renderer} = await import('../runtime/renderer.js');
  const {Observer} = await import('../../m10-work/runtime/observer.js');
  const c = await core();
  const observer = new Observer(c.m,c.e);
  const mismatch = JSON.parse(fs.readFileSync(path.join(work,'results',failedRun,'qa/official-region6/mismatch.json')));
  const start = fs.readFileSync(path.join(work,'checkpoints/story19-00-2a-official.bin'));
  assert.equal(sha(start),'c41b4188203bc45d2d0c5eeb24f8b307040be0644ce861ffbcc6281d4060c8f1');
  c.state(start);
  const actions = readActions(path.join(work,'official-chain/official-region6-actions.json'));
  for (const action of actions.slice(0,705)) c.action(action);
  assert.deepEqual(actions[705],['A',6,120]);

  let fi = -1;
  let verified = 0;
  c.action(actions[705], () => {
    if (++fi < 82 || fi > 84) return;
    const p = c.fb();
    const o = observer.sample(p);
    const renderer = Object.create(Renderer.prototype);
    renderer.raw = nearest(p);
    // Exercise the real drawFlat decision and model the integer Canvas copy.
    const plate = Symbol('HD plate');
    renderer.plate = () => plate;
    let rendered;
    renderer.ctx = {drawImage(image,...args) {
      assert.deepEqual(args,image===plate ? [0,0] : [0,0,640,576]);
      rendered = image;
    }};
    const frame = c.meta().frame-1;
    const flat = renderer.drawFlat(p,o);

    if (fi===82) {
      assert.equal(frame,61810);
      assert.deepEqual(o.dialogueRects,[]);
      assert.equal(flat.scene,'verified-flat-transition');
      assert.equal(rendered,plate);
      return;
    }
    if (fi===84) {
      assert.equal(frame,61812);
      assert.deepEqual(o.dialogueRects,[{x:0,y:80,w:88,h:64}]);
      assert.equal(flat,null,'The first colored dialogue frame uses the ordinary renderer');
      return;
    }

    const baseline = mismatch.baseline;
    assert.equal(frame,baseline.frame);
    assert.equal(sha(c.state()),baseline.state);
    assert.equal(sha(p),baseline.native);
    assert.equal(textHash(o,p),baseline.textNative);
    assert.deepEqual([o.lcdc,o.wx,o.wy,o.scx,o.scy,o.window],[0xc7,-7,0,0,0,false]);
    assert.deepEqual(o.dialogueRects,[{x:0,y:80,w:88,h:64}]);
    assert.deepEqual(o.tiles.slice(320,331),[0xa1,...Array(9).fill(0xa2),0xa1]);
    assert.equal(o.mask.reduce((sum,bit)=>sum+bit,0),2688);
    assert.equal(rendered,renderer.raw);
    const candidate = {...mismatch.candidate,scene:flat.scene,hd:sha(rendered),textHD:textHash(o,p,rendered),
      coverage:{eligible:flat.eligiblePixels,covered:flat.backgroundPixels,gap:flat.unsupportedPixels}};
    assert.deepEqual(compareFrame(candidate,baseline),{state:true,native:true,actorText:true,baselineKnownDefect:true});
    assert.equal(compareFrame(mismatch.candidate,baseline).actorText,false);
    for (const key of ['state','native','ticks','map','story','mode','bank','actorHD','actorNative','textHD','textNative','hd','scene']) {
      assert.equal(compareFrame({...candidate,[key]:null},baseline).baselineKnownDefect,false,key);
    }
    assert.equal(compareFrame({...candidate,coverage:{...candidate.coverage,gap:0}},baseline).actorText,false);
    assert.equal(compareFrame(candidate,{...baseline,textHD:baseline.textNative}).actorText,false);
    assert.equal(compareFrame({...baseline,textHD:baseline.textNative},{...baseline,textHD:baseline.textNative}).actorText,true);
    assert.equal(compareFrame(candidate,{...baseline,scene:'unsupported'}).actorText,false);

    const report = {name:'fixture',frames:3,earlierFrames:3,earlierVisualPassed:2,earlierKnownDefectFrames:1,
      baselineKnownDefectFrames:1,baselineKnownDefects:[{at:mismatch.at,earlierRegion:true}]};
    validateDefectCounts(report);
    assert.throws(()=>validateDefectCounts({...report,earlierVisualPassed:3}));
    console.log(JSON.stringify({at:mismatch.at,frame,scene:flat.scene,textNative:candidate.textNative,
      textHD:candidate.textHD,coverage:candidate.coverage}));
    verified++;
  });
  assert.equal(verified,1);
}

main().catch(error=>{console.error(error);process.exitCode=1;});
