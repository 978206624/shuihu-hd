// rAF + wall-clock pacing only. Deterministic offline replay is setup, excluded.
// Usage: NODE_PATH=... PLAYWRIGHT_BROWSERS_PATH=... node perf-realtime.cjs ROOT PORT OUT
// Optional PERF_SEGMENTS='title,card,normal walking' PERF_DURATION_MS=12000.
const {chromium}=require('playwright'),fs=require('fs'),http=require('http'),path=require('path');
const root=path.resolve(process.argv[2]),port=Number(process.argv[3]||19881),out=process.argv[4]||'perf.json';
const duration=Number(process.env.PERF_DURATION_MS||12000);
const all=[['boot',-2],['title',-1],['title fade',0],['card',100],['opening story',240],['impact',5260],['heaven card',7220],['heaven exit',7350],['title entry',-3],['forest',18400],['normal walking',29160]];
const segments=process.env.PERF_SEGMENTS?all.filter(([s])=>process.env.PERF_SEGMENTS.split(',').includes(s)):all;
const labels=['core','draw','observer','map','readback','canvasDraw','canvasWrite','ui','uiSnapshot','faded','fadedRow','titleFade','cardPrepare','card','impact'];
const mime={'.js':'text/javascript','.json':'application/json','.wasm':'application/wasm','.html':'text/html','.png':'image/png','.webp':'image/webp','.css':'text/css'};
const stats=a=>{a=a.slice().sort((a,b)=>a-b);return {samples:a.length,mean:a.length?a.reduce((s,x)=>s+x,0)/a.length:null,p95:a.length?a[Math.ceil(a.length*.95)-1]:null,max:a.length?a.at(-1):null};};
let baselineInstrumented=false;
const server=http.createServer((req,res)=>{try{let rel=decodeURIComponent(new URL(req.url,'http://localhost').pathname);if(rel==='/')rel='/index.html';if(!/^\/[\w\-./]+$/.test(rel)||rel.includes('..')||rel.split('/').some(x=>x.startsWith('.')))throw Error('path');const f=path.join(root,rel);let data=fs.readFileSync(f);
// The immutable M5 baseline lacks a probe API. Instrument its exact known app
// in the response only, with explicit compatibility checks. New app uses API.
if(rel==='/app.js'){let s=data.toString();if(!s.includes('setFrameProbe:')){if(!s.includes('function step(n=1){')||!s.includes('renderer.draw(hd);return meta();'))throw Error('Unknown app without setFrameProbe API');s=s.replace('function step(n=1){','function step(n=1){const perfStart=window.__perf?.active?performance.now():0;');s=s.replace('renderer.draw(hd);return meta();','const perfCore=window.__perf?.active?performance.now():0;renderer.draw(hd);if(window.__perf?.active)window.__perf.core.push(perfCore-perfStart);return meta();');baselineInstrumented=true;}data=Buffer.from(s);}res.setHeader('Content-Type',mime[path.extname(f)]||'application/octet-stream');res.end(data);}catch(e){res.writeHead(404);res.end(e.message);}});
(async()=>{let browser;const results=[];try{await new Promise((r,j)=>{server.once('error',j);server.listen(port,'127.0.0.1',r)});browser=await chromium.launch({args:['--no-sandbox']});for(const [segment,start] of segments){
const context=await browser.newContext({viewport:{width:1180,height:1000}}),p=await context.newPage(),errors=[],external=[];
p.on('pageerror',e=>errors.push(e.message));await context.route('**/*',r=>{const u=new URL(r.request().url());if(u.hostname!=='127.0.0.1'){external.push(u.origin);return r.abort();}return r.continue();});await p.goto(`http://127.0.0.1:${port}`);await p.waitForFunction(()=>window.shuihu?.ready);
await p.evaluate(async ({start,segment,labels})=>{const R=(await import('./renderer.js')).Renderer,O=(await import('./observer.js')).Observer,M=(await import('./map-renderer.js')).MapRenderer;
window.__perf={active:false,raf:[],frameTotals:{},scenes:{},longFrames:[]};for(const k of labels){__perf[k]=[];__perf.frameTotals[k]=[];}
const pairs=[[R.prototype,'draw','draw'],[O.prototype,'sample','observer'],[M.prototype,'draw','map'],[M.prototype,'drawUI','ui'],[M.prototype,'presentUITransition','uiSnapshot'],[M.prototype,'faded','faded'],[M.prototype,'fadedRow','fadedRow'],[R.prototype,'drawTitleFade','titleFade'],[R.prototype,'prepareCard','cardPrepare'],[R.prototype,'drawCard','card'],[R.prototype,'drawImpact','impact'],[CanvasRenderingContext2D.prototype,'getImageData','readback'],[CanvasRenderingContext2D.prototype,'drawImage','canvasDraw'],[CanvasRenderingContext2D.prototype,'putImageData','canvasWrite']];
for(const [proto,key,label] of pairs){const fn=proto[key];if(!fn)continue;proto[key]=function(...args){if(!__perf.active)return fn.apply(this,args);const t=performance.now();try{return fn.apply(this,args)}finally{__perf[label].push(performance.now()-t)}};}
if(shuihu.setFrameProbe)shuihu.setFrameProbe(r=>{if(__perf.active)__perf.core.push(r.coreMs);});
// Preserve map history: replay setup one native frame at a time after Start.
if(start!==-2)shuihu.step(start===-3?2980:3300);if(start>=0){shuihu.input('start',true);shuihu.step(2);shuihu.input('start',false);shuihu.step(120);for(let f=0;f<start;){if(f%120===0&&f+360<start){shuihu.input('A',true);shuihu.step(2);shuihu.input('A',false);shuihu.step(118);f+=120;}else{shuihu.input('A',f%120<2);shuihu.step();f++;}}}shuihu.input('A',false);
window.__segmentStart=shuihu.meta().frames;window.__segmentName=segment;window.__segmentReplay=start;
const beforeCounts=Object.fromEntries(labels.map(k=>[k,0]));
const fn=R.prototype.draw;R.prototype.draw=function(...a){const result=fn.apply(this,a);if(__perf.active){
for(const k of labels){if(k==='core')continue;const begin=beforeCounts[k],v=__perf[k];let sum=0;for(let i=begin;i<v.length;i++)sum+=v[i];__perf.frameTotals[k].push(sum);beforeCounts[k]=v.length;}
const m=shuihu.meta();if(__perf.frameTotals.draw.at(-1)>35){const sums={};for(const k of labels)sums[k]=__perf.frameTotals[k].at(-1);__perf.longFrames.push({frame:m.frames,scene:m.renderer.scene,sums});}__perf.scenes[m.renderer.scene]=(__perf.scenes[m.renderer.scene]||0)+1;
const f=m.frames-__segmentStart;
if(segment==='normal walking'){for(const [i,key] of ['right','down','left','up'].entries())shuihu.input(key,Math.floor(f/120)%4===i);}
else if(segment!=='title')shuihu.input('A',(f+start)%120<2);
}return result;};
}, {start,segment,labels});
const initial=await p.evaluate(()=>shuihu.meta());
const raw=await p.evaluate(duration=>new Promise(resolve=>{let prev=0;function tick(t){if(__perf.active&&prev)__perf.raf.push(t-prev);prev=t;if(__perf.active)requestAnimationFrame(tick);}shuihu.pause(false);if(__segmentName==='normal walking')shuihu.input('right',true);else if(__segmentName!=='title')shuihu.input('A',__segmentReplay%120<2);
const begin=performance.now(),frame=shuihu.meta().frames;__perf.active=true;requestAnimationFrame(tick);setTimeout(()=>{__perf.active=false;const elapsed=performance.now()-begin,frames=shuihu.meta().frames-frame,final=shuihu.meta();shuihu.pause();resolve({...__perf,elapsed,frames,final});},duration);}),duration);
const r={segment,setupReplayFrames:start<0?0:start,durationRequestedMs:duration,elapsedMs:raw.elapsed,gameFrames:raw.frames,gameFPS:raw.frames/(raw.elapsed/1000),expectedFPS:4194304/70224,rafPacingMs:stats(raw.raf),rafFPS:raw.raf.length/(raw.elapsed/1000),rafDropEstimate:raw.raf.reduce((s,x)=>s+Math.max(0,Math.round(x/(1000/60))-1),0),scenes:raw.scenes,initialScene:initial.renderer.scene,finalScene:raw.final.renderer.scene,initialScroll:initial.scroll,finalScroll:raw.final.scroll,errors,externalRequests:external,longFrames:raw.longFrames};
for(const k of labels){r[k+'Ms']=stats(raw[k]);if(k!=='core')r[k+'PerFrameMs']=stats(raw.frameTotals[k]);}results.push(r);fs.writeFileSync(out,JSON.stringify({status:'measured',platform:'headless Linux Chromium; no Windows GPU',root,baselineAppResponseInstrumented:baselineInstrumented,measurement:'12s default per segment, no offline steps inside measured interval; timings are inclusive/nested; per-frame sums include zero-call frames',results},null,2));await context.close();console.log(JSON.stringify({segment,gameFPS:r.gameFPS,renderMean:r.drawMs.mean,renderP95:r.drawMs.p95,scene:r.scenes}));}
}catch(e){fs.writeFileSync(out,JSON.stringify({status:results.length?'partial':'blocked',root,error:e.message,results},null,2));console.error(e.message);process.exitCode=1;}finally{if(browser)await browser.close();server.close();}})();
