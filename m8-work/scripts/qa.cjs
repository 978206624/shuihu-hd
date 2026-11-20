// Audit-only instrumentation is injected into fresh pages; runtime files stay unchanged.
const {fs,W,roots,output,write,unique,proxy,verifyFreeze,page}=require('./common.cjs');
const {gapReason,exclusion,addRegion3Coverage}=require('./coverage-attribution.cjs');
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
(async()=>{await proxy();verifyFreeze();const out=output()+'/qa';unique(out+'/report.json');fs.mkdirSync(out,{recursive:true});const browser=await chromium.launch({args:['--no-sandbox']});
 const expected=JSON.parse(fs.readFileSync(W+'/inputs/route-disclosures.json'));
 const newMaps=new Set(expected.newMapIDs);
 const report={pass:false,actions:0,frames:0,regressionActions:0,regressionFrames:0,statePassed:0,nativePassed:0,actorTextPassed:0,regressionVisualPassed:0,coverage:{},region3Coverage:{},region3Excluded:{},regressionCoverage:{},sourceMapFrames:{},routes:[],errors:[],method:'Full state + native framebuffer + coordinate/16-texel actor/text SHA256 every native frame. Same byte starts and frame inputs. No denominator/mask changes. Region 3 world totals keep the native eligible count and credit only the matching authored plate. Battle banks 2b–2d and nonzero native world-mode byte are logged separately.'};
 try{const c=await page(browser,roots.candidate),a=await page(browser,roots.adopted);for(const x of [c,a])await instrument(x.p);
 for(const b of JSON.parse(fs.readFileSync(W+'/inputs/qa-routes.json'))){await proxy();verifyFreeze();const start=Array.from(fs.readFileSync(b.source));for(const x of [c,a])await x.p.evaluate(s=>shuihu.loadState(s),start);
 // Explicit start verification before any input (including presentation-only load drawing).
 const starts=await Promise.all([c,a].map(x=>x.p.evaluate(()=>__qaFrame(false))));
 if(starts[0].state!==starts[1].state||starts[0].native!==starts[1].native)throw Error('Initial bytes/native unequal '+b.name);
 const route={name:b.name,source:b.source,sourceSHA256:require('./common.cjs').sha(Buffer.from(start)),group:b.group,frames:0,actions:0,startStateSHA256:starts[0].state,startNativeSHA256:starts[0].native};
 const endpointChecks=[];
 for(let ai=0;ai<b.actions.length;ai++){
  const runs=[];for(const x of [c,a])runs.push(await x.p.evaluate(async({action,regression})=>{const rows=[],[key,hold,wait]=action;if(key)shuihu.input(key,true);for(let i=0;i<hold;i++){shuihu.step(1);rows.push(await __qaFrame(regression));}if(key)shuihu.input(key,false);for(let i=0;i<wait;i++){shuihu.step(1);rows.push(await __qaFrame(regression));}return {rows,contract:shuihu.presentationContract()};},{action:b.actions[ai],regression:b.regressionVisualExact}));
  const [cr,ar]=runs;if(cr.rows.length!==ar.rows.length)throw Error('Native frame count differs');
  for(let fi=0;fi<cr.rows.length;fi++){
   const u=cr.rows[fi],v=ar.rows[fi];report.frames++;route.frames++;
   const state=u.state===v.state,native=u.native===v.native&&u.ticks===v.ticks&&u.map===v.map&&u.story===v.story;
   const actors=u.actorHD===u.actorNative&&u.textHD===u.textNative&&u.actorNative===v.actorNative&&u.textNative===v.textNative&&v.actorHD===v.actorNative&&v.textHD===v.textNative;
   report.statePassed+=+state;report.nativePassed+=+native;report.actorTextPassed+=+actors;
   if(b.regressionVisualExact){report.regressionFrames++;const same=u.hd===v.hd&&JSON.stringify(u.coverage)===JSON.stringify(v.coverage);report.regressionVisualPassed+=+same;if(!same)throw Error('Old-region HD/coverage regression '+b.name+'/'+ai+'/'+fi);}
   if(u.coverage.eligible!==u.coverage.covered+u.coverage.gap||u.coverage.gap<0)throw Error('Invalid denominator');
   const k=u.map,cv=report.coverage[k]??={frames:0,eligible:0,covered:0,gap:0,full:0,reasons:{}};cv.frames++;cv.eligible+=u.coverage.eligible;cv.covered+=u.coverage.covered;cv.gap+=u.coverage.gap;cv.full+=+(u.coverage.gap===0);
   const src=u.mapResult?.mapId||'no-region-source';report.sourceMapFrames[k]??={};report.sourceMapFrames[k][src]=(report.sourceMapFrames[k][src]||0)+1;
   if(b.regressionVisualExact){const old=report.regressionCoverage[k]??={frames:0,eligible:0,covered:0,gap:0};old.frames++;for(const field of ['eligible','covered','gap'])old[field]+=u.coverage[field];}
   let reasonPixels=0;for(const g of u.mapResult?.uncoveredTiles||[]){const reason=gapReason(u,g);cv.reasons[reason]=(cv.reasons[reason]||0)+g.pixels;reasonPixels+=g.pixels;}
   const remainder=u.coverage.gap-reasonPixels;if(remainder>0){const reason=u.mapResult?.mapId?'native gap outside region audit':'native transition/menu/legacy: no certified region source';cv.reasons[reason]=(cv.reasons[reason]||0)+remainder;}
   if(newMaps.has(k)){
    const reason=exclusion(u);
    if(reason){
     const excluded=report.region3Excluded[k]??={};
     excluded[reason]=(excluded[reason]||0)+1;
    }else addRegion3Coverage(report.region3Coverage,u);
   }
   if(!state||!native||!actors){write(out+'/mismatch.json',{route:b.name,action:ai,frameInAction:fi,candidate:u,adopted:v});throw Error('Formal invariant failed '+b.name+'/'+ai+'/'+fi);}
  }
  fs.writeFileSync(out+'/'+b.name+'-'+String(ai).padStart(4,'0')+'.json.gz',zlib.gzipSync(JSON.stringify({input:b.actions[ai],candidate:cr,adopted:ar})));
  if(cr.contract.actorErrors||cr.contract.textErrors||ar.contract.actorErrors||ar.contract.textErrors)throw Error('Endpoint contract failed');
  const last=cr.rows.at(-1);endpointChecks.push({action:ai,state:last.state,native:last.native,actor:last.actorHD,text:last.textHD});
  report.actions++;route.actions++;if(b.regressionVisualExact)report.regressionActions++;
  if(b.saveAt===ai){
   if(last.map!==b.target)throw Error('Wrong target map '+b.name);
   await saveViews(c.p,out,b.target);
   // Keep the historical Stage A redraw sequence on both sides of old-route comparisons.
   if(b.regressionVisualExact)for(const x of [c,a])await x.p.evaluate(()=>{shuihu.setHD(false);shuihu.setHD(true);});
  }
  if(ai%10===0){console.log('qa',b.name,ai,report.frames);write(out+'/progress.json',report);}
 }
 const final=await c.p.evaluate(()=>({map:[shuihu.read(0xff9a),shuihu.read(0xff9b)].map(v=>v.toString(16).padStart(2,'0')).join('-'),story:shuihu.read(0xffba)}));
 if(b.endStory!==undefined&&final.story!==b.endStory)throw Error('Story endpoint failed '+b.name);
 route.endpoint=final;route.endpointChecks=endpointChecks;report.routes.push(route);write(out+'/progress.json',report);
 }
 report.errors=[...c.errors,...a.errors];
 report.pass=report.actions===expected.formalQAActions&&report.frames===expected.formalQAFrames&&report.regressionActions===442&&report.regressionFrames===31396&&report.frames===report.statePassed&&report.frames===report.nativePassed&&report.frames===report.actorTextPassed&&report.regressionVisualPassed===31396&&!report.errors.length;
 await proxy();verifyFreeze();if(!report.pass)throw Error('Required formal totals not satisfied');
 }catch(e){report.error=e.stack;throw e;}finally{write(out+'/report.json',report);await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
