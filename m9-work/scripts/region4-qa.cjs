// Audit-only instrumentation is injected into fresh pages; runtime files stay unchanged.
const {fs,path,PROJECT,roots,output,write,read,sha,plan,proxy,verifyFreeze,page}=require('./outer-common.cjs');
const assert=require('node:assert/strict');
const {randomUUID}=require('node:crypto');
const {exclusion,addRegion3Coverage}=require('../../m8-work/scripts/coverage-attribution.cjs');
const {chromium}=require('playwright'),zlib=require('zlib');
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
 window.__qaFrame=async collect=>{
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
   hd:collect?await __qaHash(d):null,ticks:m.ticks,map:[shuihu.read(0xff9a),shuihu.read(0xff9b)].map(v=>v.toString(16).padStart(2,'0')).join('-'),story:shuihu.read(0xffba),
   mode:shuihu.read(0xd0fa),bank:shuihu.read(0xd08f),scene:m.renderer.scene,sourcePixels:__qaSources,
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
  const native = await p.evaluate(() => ({state:shuihu.state(), pixels:shuihu.pixels(), ticks:shuihu.meta().ticks}));
  return {state:Buffer.from(native.state), stateSHA256:sha(Buffer.from(native.state)),
    nativeFramebufferSHA256:sha(Buffer.from(native.pixels)), ticks:native.ticks};
}

function compareEvidence(capture, record, where) {
  for (const key of ['stateSHA256','nativeFramebufferSHA256','ticks']) {
    assert.equal(capture[key], record[key], where + ' ' + key);
  }
}

async function playAction(p, action) {
  return p.evaluate(async ([key, hold, wait]) => {
    const rows = [];
    if (key) shuihu.input(key, true);
    for (let i=0; i<hold; i++) {
      shuihu.step(1);
      rows.push(await __qaFrame(true));
    }
    if (key) shuihu.input(key, false);
    for (let i=0; i<wait; i++) {
      shuihu.step(1);
      rows.push(await __qaFrame(true));
    }
    return {rows, contract:shuihu.presentationContract()};
  }, action);
}

async function runRoute(browser, out, route, official, nativeFrames, contactActions, newMaps) {
  const name = route.name;
  const dir = path.join(out, name);
  const complete = path.join(dir, 'report.json');
  if (fs.existsSync(complete)) {
    const saved = read(complete);
    assert(saved.pass && saved.name === name && saved.actions === route.actions.length &&
      saved.frames === route.actions.reduce((n,a) => n+a[1]+a[2],0), 'Invalid route checkpoint: ' + name);
    return saved;
  }
  if (fs.existsSync(dir)) fs.renameSync(dir, dir+'.interrupted-'+randomUUID());
  fs.mkdirSync(dir);
  const r = {name, actions:0, frames:0, earlierFrames:0, statePassed:0, nativePassed:0,
    actorTextPassed:0, earlierVisualPassed:0, region4Coverage:{}, region4Excluded:{}, contacts:{}, pass:false};
  const sessions = [];
  try {
    await proxy();
    for (const root of [roots.candidate, roots.m8]) sessions.push(await page(browser, root));
    for (const {p} of sessions) await instrument(p);
    const input = fs.readFileSync(path.resolve(PROJECT, route.source));
    r.sourceSHA256 = sha(input);
    for (const {p} of sessions) await p.evaluate(s => shuihu.loadState(s), Array.from(input));
    const starts = await Promise.all(sessions.map(({p}) => capture(p)));
    compareEvidence(starts[0], starts[1], name+' initial M8 parity');
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
        const state = u.state===v.state;
        const native = ['native','ticks','map','story','mode','bank'].every(k => u[k]===v[k]);
        const actors = ['actor','text'].every(k =>
          u[k+'HD']===u[k+'Native'] && u[k+'Native']===v[k+'Native'] && v[k+'HD']===v[k+'Native']);
        if (!state || !native || !actors) {
          write(path.join(dir,'mismatch.json'), {at, candidate:u, baseline:v});
          throw Error('Formal invariant failed: '+at);
        }
        const expected = official ? nativeFrames[r.frames] : null;
        if (expected) {
          assert.equal(expected.index, ai, at);
          for (const k of ['ticks','map','story','mode','bank']) assert.equal(u[k], expected[k], at+' official '+k);
        }
        r.frames++;
        r.statePassed++;
        r.nativePassed++;
        r.actorTextPassed++;
        assert.equal(u.coverage.eligible, u.coverage.covered+u.coverage.gap, at);
        assert(u.coverage.gap >= 0, at);
        if (!newMaps.has(u.map)) {
          r.earlierFrames++;
          if (u.hd!==v.hd || JSON.stringify(u.coverage)!==JSON.stringify(v.coverage)) {
            write(path.join(dir,'mismatch.json'), {at, candidate:u, baseline:v});
            throw Error('Earlier-region HD/coverage regression: '+at);
          }
          r.earlierVisualPassed++;
        }
        if (official && newMaps.has(u.map)) {
          const excluded = exclusion(u);
          if (excluded) {
            const counts = r.region4Excluded[u.map] ??= {};
            counts[excluded] = (counts[excluded] || 0)+1;
          } else {
            addRegion3Coverage(r.region4Coverage,u);
          }
        }
      }
      fs.writeFileSync(path.join(dir,String(ai).padStart(4,'0')+'.json.gz'),
        zlib.gzipSync(JSON.stringify({input:action,candidate,baseline})), {flag:'wx'});
      for (const {contract} of [candidate,baseline]) assert(!contract.actorErrors && !contract.textErrors);
      final = rows.at(-1);
      if (official) {
        const endpoint = await capture(sessions[0].p);
        compareEvidence(endpoint, official.records[ai], name+' official action '+ai);
        assert.equal(r.frames, official.records[ai].frame);
        if (ai === route.actions.length-1) {
          const offset = 147568 + 0x1000;
          r.wram = {DAA1:endpoint.state[offset+0xaa1], DAA2:endpoint.state[offset+0xaa2]};
          assert.deepEqual(r.wram,{DAA1:0x72,DAA2:1});
        }
      }
      if (contactActions.has(ai)) {
        const id = contactActions.get(ai);
        assert(final.map===id && final.mapResult?.mapId===id && final.sourcePixels[id]>0,
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
        console.log('qa',name,r.actions,r.frames);
        write(path.join(dir,'progress.json'),r);
      }
    }
    assert(sessions.every(x => !x.errors.length), JSON.stringify(sessions.map(x => x.errors)));
    r.endpoint = {map:final.map,story:final.story};
    if (route.endStory !== undefined) assert.equal(final.story,route.endStory);
    if (official) {
      assert.deepEqual(r.endpoint,{map:'00-2c',story:14});
      assert.equal(r.frames,nativeFrames.length);
      assert.equal(Object.keys(r.contacts).length,newMaps.size);
      for (const id of newMaps) {
        const c = r.region4Coverage[id];
        assert(c?.eligible>0 && c.covered>0 && c.eligible===c.covered+c.gap, 'Missing plate coverage '+id);
        assert.equal(c.gap,Object.values(c.reasons).reduce((a,b)=>a+b,0),id);
        c.ratio = c.covered/c.eligible;
      }
    }
    await proxy();
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
  const official=read(path.join(PROJECT,spec.result));
  const nativeFrames=fs.readFileSync(path.join(PROJECT,spec.frames),'utf8').trimEnd().split('\n')
    .map(line=>JSON.parse(line)).filter(row=>row.type==='frame');
  const route={...spec,actions:read(path.join(PROJECT,spec.actions))};
  const earlier=read(path.join(PROJECT,config.oldQA));
  const contacts=new Map(Object.entries(spec.contacts).map(([id,i])=>[i,id]));
  const newMaps=new Set(Object.keys(spec.contacts));
  const browser=await chromium.launch({args:['--no-sandbox']});
  try {
    const reports=[await runRoute(browser,out,route,official,nativeFrames,contacts,newMaps)];
    for (const r of earlier) reports.push(await runRoute(browser,out,r,null,[],new Map(),newMaps));
    const totals=Object.fromEntries(['frames','actions','earlierFrames','statePassed','nativePassed','actorTextPassed','earlierVisualPassed']
      .map(k=>[k,reports.reduce((sum,r)=>sum+r[k],0)]));
    assert.equal(totals.actions,1358); assert.equal(totals.frames,98707);
    assert.equal(totals.earlierVisualPassed,totals.earlierFrames);
    assert(reports.slice(1).every(r=>r.frames===r.earlierFrames),'Historical routes entered a region-4 map');
    await proxy(); verifyFreeze();
    const {region4Coverage,region4Excluded,contacts:proof}=reports[0];
    write(path.join(out,'report.json'),{pass:true,...totals,region4Coverage,region4Excluded,contacts:proof,routes:reports,
      coverageMethod:'Same-plate native pixel count / unchanged eligible background pixel count on official-route world frames. Nonzero world mode and battle banks 2b–2d reported separately.'});
    console.log('Formal QA passed',JSON.stringify(totals));
  } finally {await browser.close();}
}

main().catch(e=>{console.error(e);process.exitCode=1;});
