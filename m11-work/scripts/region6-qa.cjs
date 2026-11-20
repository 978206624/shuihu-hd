// Audit-only instrumentation is injected into fresh pages; runtime files stay unchanged.
const {fs,path,PROJECT,roots,output,write,read,sha,plan,proxy,verifyFreeze,page,officialEvidence}=require('./outer-common.cjs');
const assert=require('node:assert/strict');
const {randomUUID}=require('node:crypto');
const {exclusion,addCoverage}=require('./coverage-attribution.cjs');
const zlib=require('node:zlib');
const blackRGBA = Buffer.alloc(160*144*4);
for (let i=3; i<blackRGBA.length; i+=4) blackRGBA[i]=255;
const blackNative = sha(blackRGBA);
const blackHD = sha(Buffer.concat(Array(16).fill(blackRGBA)));
const flatUIScene = 'native-flat-ui-transition';

function compareFrame(candidate, baseline) {
  const u = candidate, v = baseline;
  const state = u.state===v.state;
  const native = ['native','ticks','map','story','mode','bank'].every(k=>u[k]===v[k]);
  const actor = u.actorHD===u.actorNative && u.actorNative===v.actorNative && v.actorHD===v.actorNative;
  const text = u.textHD===u.textNative && u.textNative===v.textNative;
  const baselineText = v.textHD===v.textNative;
  const isFlatUI = u.scene===flatUIScene;
  // The exception is limited to the reproduced blackout. Verify the entire
  // candidate output and both exact coverage totals before accepting it.
  const baselineKnownDefect = state && native && actor && text && !baselineText &&
    isFlatUI && v.scene==='verified-flat-transition' && u.native===blackNative && u.hd===blackHD &&
    u.coverage.eligible===23040 && u.coverage.covered===0 && u.coverage.gap===23040 &&
    v.coverage.eligible===23040 && v.coverage.covered===23040 && v.coverage.gap===0;
  const actorText = actor && text && (baselineKnownDefect || (baselineText && !isFlatUI));
  return {state,native,actorText,baselineKnownDefect};
}

function validateDefectCounts(report) {
  const {baselineKnownDefects:list,baselineKnownDefectFrames:total,
    earlierKnownDefectFrames:earlier,earlierVisualPassed:exact,earlierFrames:frames} = report;
  assert(Array.isArray(list) && list.length===total && total<=report.frames &&
    list.filter(row=>row.earlierRegion).length===earlier && exact+earlier===frames,
    'Invalid known M10 defect accounting: '+report.name);
}

async function instrument(p){await p.evaluate(async()=>{
 const {Renderer}=await import('./renderer.js'),draw=Renderer.prototype.draw;
 Renderer.prototype.draw=function(...a){
  window.__qaRenderer=this;window.__qaSources={};
  return draw.apply(this,a);
 };
 shuihu.setHD(true);shuihu.setAudit(true);
 const region=__qaRenderer.region,paint=region.paintSources;
 region.paintSources=function(ctx,candidates,variants,sources){
  for(const code of sources){
   if(code<0)continue;
   const id=candidates[code%64].map.id;
   __qaSources[id]=(__qaSources[id]||0)+1;
  }
  return paint.call(this,ctx,candidates,variants,sources);
 };
 window.__qaHash=async a=>Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',new Uint8Array(a)))).map(x=>x.toString(16).padStart(2,'0')).join('');
 const read=address=>shuihu.read(address);
 window.__qaObservation=()=>{
  const m=shuihu.meta();
  const camera=[read(0xff96),read(0xff97)];
  const player=Array.from({length:8},(_,i)=>read(0xcd00+i));
  const word=address=>read(address)|read(address+1)<<8;
  const signedWord=address=>(word(address)<<16)>>16;
  const hex=address=>read(address).toString(16).padStart(2,'0');
  const cell=[2*camera[0]+(signedWord(0xffae)+player[1]-8)/16,
              2*camera[1]+(signedWord(0xffb0)+player[0]-16)/16];
  const bank=read(0xd08f),mode=read(0xd0fa),dialogue=read(0xffbc),script=read(0xffd6),banner=read(0xffc1);
  return {frame:m.frames-1,ticks:m.ticks,scroll:m.scroll,romSHA256:m.romSHA256,
   map:[0xff9a,0xff9b].map(address=>read(address).toString(16).padStart(2,'0')).join('-'),
   story:read(0xffba),bank,mode,dialogue,camera,player,cell,script,banner,
   entry:read(0xff9c),facing:player[3],
   settled:[3,4,5].includes(bank)&&!mode&&!dialogue&&!script&&!banner&&cell.every(Number.isInteger),
   DAA:[0xdaa0,0xdaa1,0xdaa2,0xdaa3].map(hex), D2AC:[0xd2ac,0xd2ad].map(hex),
   D284:[0xd284,0xd285].map(hex),party:[0xd200,0xd216,0xd22c].map(hex),
   hp:[0xd202,0xd218,0xd22e].map(word),
   daa:[read(0xdaa1),read(0xdaa2)],d284:[read(0xd284),read(0xd285)]};
 };
 window.__qaFrame=async ()=>{
  const r=__qaRenderer,o=r.observation,n=r.nativeData.data,d=r.ctx.getImageData(0,0,640,576).data;
  if(!o)throw Error('Native observer unavailable for actor/text evidence');
  const expected=[[],[]],actual=[[],[]];
  for(let y=0;y<144;y++)for(let x=0;x<160;x++){
   const i=y*160+x,k=((((y+o.scy)&255)>>3)*32)+(((x+o.scx)&255)>>3),a=o.actorMask[i],t=o.mask[i]&&!a&&![161,162,163,164].includes(o.tiles[k]);
   if(!a&&!t)continue;const group=a?0:1;
   // Include location and all 16 output texels, not just pixel counts.
   expected[group].push(i&255,i>>8);actual[group].push(i&255,i>>8);
   for(let yy=0;yy<4;yy++)for(let xx=0;xx<4;xx++){const q=((y*4+yy)*640+x*4+xx)*4;for(let c=0;c<4;c++){expected[group].push(n[i*4+c]);actual[group].push(d[q+c]);}}
  }
  const m=shuihu.meta(),v=m.renderer.coverage;
  return {state:await __qaHash(shuihu.state()),native:await __qaHash(shuihu.pixels()),
   actorNative:await __qaHash(expected[0]),actorHD:await __qaHash(actual[0]),textNative:await __qaHash(expected[1]),textHD:await __qaHash(actual[1]),
   hd:await __qaHash(d),...__qaObservation(),scene:m.renderer.scene,sourcePixels:__qaSources,
   coverage:{eligible:v.eligibleBackgroundPixels,covered:v.gptBackgroundPixels,gap:v.uncoveredBackgroundPixels},
   mapResult:m.renderer.mapResult?{mapId:m.renderer.mapResult.mapId,uncoveredTiles:m.renderer.mapResult.uncoveredTiles}:null};
 };
});}
async function saveViews(p,out,id){
 const images=await p.evaluate(()=>{
  const r=__qaRenderer,native=document.createElement('canvas');native.width=640;native.height=576;
  const ctx=native.getContext('2d');ctx.imageSmoothingEnabled=false;ctx.drawImage(r.raw,0,0,640,576);
  return {native:native.toDataURL('image/png'),hd:r.c.toDataURL('image/png')};
 });
 for(const [mode,data] of Object.entries(images))fs.writeFileSync(out+'/'+id+'-'+mode+'.png',Buffer.from(data.split(',')[1],'base64'));
}

async function capture(p) {
  const {state,pixels,...obs} = await p.evaluate(() => ({
    state:shuihu.state(), pixels:shuihu.pixels(), ...__qaObservation()
  }));
  return {...obs,stateSHA256:sha(Buffer.from(state)),nativeFramebufferSHA256:sha(Buffer.from(pixels))};
}

const compareObservation = (got, expected, where) => {
  for (const key of ['frame','ticks','map','story','mode','bank','dialogue','player','camera','scroll',
    'romSHA256','entry','facing','cell','script','banner','settled','DAA','D2AC','D284','party','hp']) {
    if (Object.hasOwn(expected,key)) assert.deepEqual(got[key],expected[key],where+' '+key);
  }
};

const inStairGateRow = row => row.map==='00-2a' && row.cell[1]>=4 && row.cell[1]<5;

function checkpoints(spec, result) {
  const inside = new Map(), after = new Map();
  for (const record of result.records) {
    if (!record.frame) continue;
    const isTransition = spec.indexBase===1 && record.name.startsWith('frame-');
    (isTransition ? inside : after).set(record.frame,record);
  }
  return {inside,after};
}

function compareEvidence(capture, record, where) {
  compareObservation(capture,record,where);
  for (const key of ['stateSHA256','nativeFramebufferSHA256']) {
    assert.equal(capture[key], record[key], where + ' ' + key);
  }
}

async function playAction(p, action) {
  return p.evaluate(async ([key, hold, wait]) => {
    const rows = [];
    if (key) shuihu.input(key, true);
    for (let i=0; i<hold; i++) {
      shuihu.step(1);
      rows.push(await __qaFrame());
    }
    if (key) shuihu.input(key, false);
    for (let i=0; i<wait; i++) {
      shuihu.step(1);
      rows.push(await __qaFrame());
    }
    return {rows, contract:shuihu.presentationContract()};
  }, action);
}

async function runRoute(browser, out, route, evidence, contactActions, newMaps) {
  const name = route.name;
  const official = evidence?.result;
  const marks = official ? checkpoints(route,official) : null;
  const region6 = contactActions.size > 0;
  const dir = path.join(out, name);
  const complete = path.join(dir, 'report.json');
  if (fs.existsSync(complete)) {
    const saved = read(complete);
    assert(saved.pass && saved.name === name && saved.actions === route.actions.length &&
      saved.frames === route.actions.reduce((n,a) => n+a[1]+a[2],0) &&
      ['statePassed','nativePassed','actorTextPassed'].every(key=>saved[key]===saved.frames),
      'Invalid route checkpoint: ' + name);
    validateDefectCounts(saved);
    if (route.endpoint) assert.deepEqual(saved.endpoint,route.endpoint);
    if (official) assert.equal(saved.evidencePassed,marks.after.size+marks.inside.size);
    assert.equal(Object.keys(saved.contacts).length,contactActions.size);
    for (const [action,id] of contactActions) {
      assert.equal(saved.contacts[id]?.action,action);
      for (const mode of ['native','hd']) {
        assert.equal(saved.contacts[id][mode+'PNG'],sha(fs.readFileSync(path.join(dir,id+'-'+mode+'.png'))));
      }
    }
    return saved;
  }
  if (fs.existsSync(dir)) fs.renameSync(dir, dir+'.interrupted-'+randomUUID());
  fs.mkdirSync(dir);
  const r = {name, actions:0, frames:0, earlierFrames:0, statePassed:0, nativePassed:0,
    actorTextPassed:0, earlierVisualPassed:0, earlierKnownDefectFrames:0,
    baselineKnownDefectFrames:0, baselineKnownDefects:[],
    region6Coverage:{}, region6Excluded:{}, addedPlateTransitionFrames:0,
    row4Frames:0, evidencePassed:0, contacts:{}, pass:false};
  const sessions = [];
  try {
    await proxy();
    for (const root of [roots.candidate, roots.m10]) sessions.push(await page(browser, root));
    for (const {p} of sessions) await instrument(p);
    const input = fs.readFileSync(path.resolve(PROJECT, route.source));
    r.sourceSHA256 = sha(input);
    for (const {p} of sessions) await p.evaluate(s => shuihu.loadState(s), Array.from(input));
    const starts = await Promise.all(sessions.map(({p}) => capture(p)));
    compareEvidence(starts[0], starts[1], name+' initial M10 parity');
    if (official) {
      assert.equal(r.sourceSHA256, official.sourceSHA256);
      compareEvidence(starts[0], official.initial, name+' official start');
    }
    let final;
    for (const [ai, action] of route.actions.entries()) {
      const [candidate, baseline] = await Promise.all(sessions.map(({p}) => playAction(p, action)));
      const {rows} = candidate;
      assert.equal(rows.length, action[1]+action[2]);
      assert.equal(rows.length, baseline.rows.length);
      for (const [fi, u] of rows.entries()) {
        const v = baseline.rows[fi], at = name+'/'+ai+'/'+fi;
        const {state,native,actorText,baselineKnownDefect} = compareFrame(u,v);
        if (!state || !native || !actorText) {
          write(path.join(dir,'mismatch.json'), {at, candidate:u, baseline:v});
          throw Error('Formal invariant failed: '+at);
        }
        const expected = evidence?.frames[r.frames];
        if (expected) {
          assert.equal(expected.index, ai+route.indexBase, at);
          compareObservation(u,expected,at+' official');
          const checkpoint = marks.inside.get(u.frame);
          if (checkpoint) {
            compareEvidence({...u,stateSHA256:u.state,nativeFramebufferSHA256:u.native},checkpoint,at+' transition');
            r.evidencePassed++;
          }
        }
        r.frames++;
        r.statePassed++;
        r.nativePassed++;
        r.actorTextPassed++;
        assert.equal(u.coverage.eligible, u.coverage.covered+u.coverage.gap, at);
        assert(u.coverage.gap >= 0, at);
        if (inStairGateRow(u)) {
          assert(region6,at+' reached the forbidden stairs row');
          r.row4Frames++;
        }
        const showingAddedPlate = Object.keys(u.sourcePixels).some(id => newMaps.has(id));
        const earlierRegion = !region6 || (!newMaps.has(u.map) && !showingAddedPlate);
        if (baselineKnownDefect) {
          r.baselineKnownDefectFrames++;
          r.baselineKnownDefects.push({at,frame:u.frame,map:u.map,story:u.story,bank:u.bank,mode:u.mode,
            earlierRegion, textNative:u.textNative, candidateTextHD:u.textHD, baselineTextHD:v.textHD,
            candidateHD:u.hd, baselineHD:v.hd, candidateCoverage:u.coverage, baselineCoverage:v.coverage});
        }
        if (earlierRegion) {
          r.earlierFrames++;
          if (baselineKnownDefect) {
            r.earlierKnownDefectFrames++;
          } else if (u.hd!==v.hd || JSON.stringify(u.coverage)!==JSON.stringify(v.coverage)) {
            write(path.join(dir,'mismatch.json'), {at, candidate:u, baseline:v});
            throw Error('Earlier-region HD/coverage regression: '+at);
          } else {
            r.earlierVisualPassed++;
          }
        } else if (!newMaps.has(u.map)) {
          r.addedPlateTransitionFrames++;
        }
        if (region6) {
          const excluded = exclusion(u);
          if (excluded) {
            const counts = r.region6Excluded[u.map] ??= {};
            counts[excluded] = (counts[excluded] || 0)+1;
          } else {
            addCoverage(r.region6Coverage,u);
          }
        }
      }
      fs.writeFileSync(path.join(dir,String(ai).padStart(4,'0')+'.json.gz'),
        zlib.gzipSync(JSON.stringify({input:action,candidate,baseline})), {flag:'wx'});
      assert(!candidate.contract.actorErrors && !candidate.contract.textErrors, name+' candidate presentation contract');
      assert(!baseline.contract.actorErrors, name+' baseline actor presentation contract');
      const lastBaseline = baseline.rows.at(-1);
      if (lastBaseline) {
        // Every mismatch here already passed the frame-specific blackout check.
        assert.equal(Boolean(baseline.contract.textErrors), lastBaseline.textHD!==lastBaseline.textNative,
          name+' baseline text presentation contract');
      } else {
        assert(!baseline.contract.textErrors, name+' baseline text presentation contract without frames');
      }
      final = rows.at(-1);
      const checkpoint = marks?.after.get(r.frames);
      if (checkpoint) {
        const endpoint = await capture(sessions[0].p);
        compareEvidence(endpoint,checkpoint,name+' official action '+ai);
        r.evidencePassed++;
        if (route.endpoint && ai === route.actions.length-1) {
          r.endpoint = Object.fromEntries(Object.keys(route.endpoint).map(key=>[key,endpoint[key]]));
          assert.deepEqual(r.endpoint,route.endpoint);
        }
      }
      if (contactActions.has(ai)) {
        const id = contactActions.get(ai);
        assert(final.map===id && final.settled &&
          final.mapResult?.mapId===id && final.sourcePixels[id]>0,
          'Contact frame lacks a certified same-map plate: '+id);
        await saveViews(sessions[0].p,dir,id);
        r.contacts[id] = {action:ai, frame:r.frames, samePlate:final.sourcePixels[id], eligible:final.coverage.eligible,
          nativePNG:sha(fs.readFileSync(path.join(dir,id+'-native.png'))),
          hdPNG:sha(fs.readFileSync(path.join(dir,id+'-hd.png')))};
      }
      if (ai === route.saveAt) {
        assert.equal(final.map,route.target);
        // Preserve the historical audit sequence where the M8 route used the redraw.
        if (route.regressionVisualExact) for (const {p} of sessions) {
          await p.evaluate(() => {shuihu.setHD(false);shuihu.setHD(true);});
        }
      }
      r.actions++;
      if (ai%10===0) {
        await proxy();
        console.log('qa',name,r.actions,r.frames);
        write(path.join(dir,'progress.json'),r);
      }
    }
    assert(sessions.every(x => !x.errors.length), JSON.stringify(sessions.map(x => x.errors)));
    r.endpoint ??= {map:final.map,story:final.story};
    if (route.endStory !== undefined) assert.equal(final.story,route.endStory);
    if (official) {
      assert.equal(r.frames,evidence.frames.length);
      assert.equal(r.evidencePassed,marks.after.size+marks.inside.size);
      assert.equal(final.map,official.end.map);
      assert.equal(final.story,official.end.story);
    }
    if (region6) {
      assert.deepEqual(r.endpoint,route.endpoint);
      assert.equal(r.row4Frames,route.row4Frames);
      assert.equal(Object.keys(r.contacts).length,contactActions.size);
      for (const id of Object.keys(route.contacts)) {
        assert(r.region6Coverage[id]?.covered>0, 'Missing plate coverage '+id);
      }
      for (const [id,c] of Object.entries(r.region6Coverage)) {
        assert(c.eligible===c.covered+c.gap,id);
        assert.equal(c.gap,Object.values(c.reasons).reduce((a,b)=>a+b,0),id);
        c.ratio = c.eligible ? c.covered/c.eligible : null;
      }
    }
    await proxy();
    validateDefectCounts(r);
    r.pass = true;
    write(complete,r);
    return r;
  } catch (e) {
    write(path.join(dir,'failure.json'),{...r,error:e.stack});
    throw e;
  } finally {
    for (const {context} of sessions) await context.close();
  }
}

async function main() {
  const out=path.join(output(),'qa');
  fs.mkdirSync(out,{recursive:true});
  await proxy(); verifyFreeze();
  const config=plan(), spec=config.official;
  const {chromium}=require('playwright');
  const browser=await chromium.launch({args:['--no-sandbox']});
  try {
    const newMaps=new Set(config.newMaps);
    const reports=[];
    for (const official of [spec,config.region5Regression,config.region4Regression]) {
      const route={...official,actions:read(path.join(PROJECT,official.actions))};
      const contacts=new Map(Object.entries(official.contacts??{}).map(([id,i])=>[i,id]));
      reports.push(await runRoute(browser,out,route,officialEvidence(official),contacts,newMaps));
    }
    for (const route of read(path.join(PROJECT,config.oldQA))) {
      reports.push(await runRoute(browser,out,route,null,new Map(),newMaps));
    }
    const totals=Object.fromEntries(['frames','actions','earlierFrames','statePassed','nativePassed',
      'actorTextPassed','earlierVisualPassed','earlierKnownDefectFrames','baselineKnownDefectFrames',
      'addedPlateTransitionFrames','evidencePassed']
      .map(k=>[k,reports.reduce((sum,r)=>sum+r[k],0)]));
    assert.equal(totals.actions,config.qaTotals.actions);
    assert.equal(totals.frames,config.qaTotals.frames);
    assert.equal(reports.length,config.qaTotals.routes);
    const baselineKnownDefects=reports.flatMap(r=>r.baselineKnownDefects);
    validateDefectCounts({...totals, baselineKnownDefects, name:'all routes'});
    assert(reports.slice(1).every(r=>r.frames===r.earlierFrames),'Regression route lost visual checks');
    await proxy(); verifyFreeze();
    const {region6Coverage,region6Excluded,contacts}=reports[0];
    const coverageWeighted={frames:0,eligible:0,covered:0,gap:0,nativeGap:0,otherHD:0,reasons:{}};
    for (const map of Object.values(region6Coverage)) {
      for (const key of ['frames','eligible','covered','gap','nativeGap','otherHD']) coverageWeighted[key]+=map[key];
      for (const [reason,pixels] of Object.entries(map.reasons))
        coverageWeighted.reasons[reason]=(coverageWeighted.reasons[reason]||0)+pixels;
    }
    assert(coverageWeighted.eligible>0);
    coverageWeighted.ratio=coverageWeighted.covered/coverageWeighted.eligible;
    write(path.join(out,'report.json'),{pass:true,...totals,baselineKnownDefects,region6Coverage,coverageWeighted,region6Excluded,contacts,routes:reports,
      coverageMethod:'Same-plate native pixels divided by eligible background pixels on official-route world frames. Nonzero world mode and battle banks 2b–2d excluded.'});
    console.log('Formal QA passed',JSON.stringify(totals));
  } finally {await browser.close();}
}

if(require.main===module)main().catch(e=>{console.error(e);process.exitCode=1;});
module.exports={compareFrame,validateDefectCounts};
