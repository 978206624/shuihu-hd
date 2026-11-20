// Exclusive Chromium, no screenshots, trace, recording, audit or canvas reads.
const {fs,path,PROJECT,roots,output,stats,proxy,verifyFreeze,page,sha,plan:inputPlan}=require('./outer-common.cjs');
const {randomUUID}=require('crypto'),{isDeepStrictEqual}=require('util'),os=require('os');
const TARGET=1792,WARMUP=60,REPEATS=3;
const MODES=['legacy','cold'];
const read=file=>JSON.parse(fs.readFileSync(file,'utf8'));
async function measure(browser,which,route,mode,repeat){
  const x=await page(browser,roots[which]),p=x.p;
  try {
    const load=await p.evaluate(s=>{const start=performance.now();shuihu.loadState(s);return {durationMs:performance.now()-start,frames:shuihu.meta().frames};},Array.from(fs.readFileSync(path.join(PROJECT,route.source))));
    await p.evaluate(({actions,mode,TARGET,WARMUP,allowRow4})=>{
      if(shuihu.perfVersion!==3||!shuihu.meta().hd)throw Error('Expected v3 performance probes with HD enabled');
      shuihu.setAudit(false);
      const read=address=>shuihu.read(address);
      const map=()=>[read(0xff9a),read(0xff9b)].map(v=>v.toString(16).padStart(2,'0')).join('-');
      const r=window.__stagePerf={mode,warm:mode==='legacy'?WARMUP:0,frames:0,index:0,phase:0,left:actions[0][1],records:[],rafs:[],switches:[],current:map(),previous:map()};
      let active=false;
      function begin(){
        active=true;r.start=performance.now();r.startFrames=shuihu.meta().frames;
        if(actions[0][0])shuihu.input(actions[0][0],true);
      }
      shuihu.setFrameProbe(f=>{
        const current=map();
        if(!allowRow4&&current==='00-2a'){
          const fineY=((read(0xffb0)|read(0xffb1)<<8)<<16)>>16;
          const row=2*read(0xff97)+(fineY+read(0xcd00)-16)/16;
          if(row>=4&&row<5){
            r.error='Forbidden stairs row';
            shuihu.pause();shuihu.setFrameProbe(null);shuihu.setRafProbe(null);r.done=true;
            return;
          }
        }
        if(r.warm){if(--r.warm===0)begin();return;}
        r.frames++;r.previous=r.current;r.current=current;
        const rec={frame:r.frames,map:r.current,coreMs:f.coreMs,renderMs:f.renderMs,frameMs:f.coreMs+f.renderMs};r.records.push(rec);
        if(r.current!==r.previous)r.switches.push({frame:r.frames,from:r.previous,to:r.current});
        const a=actions[r.index];
        if(--r.left===0){
          if(!r.phase&&a[0])shuihu.input(a[0],false);
          if(!r.phase&&a[2]>0){r.phase=1;r.left=a[2];}
          else{
            r.index=(r.index+1)%actions.length;r.phase=0;
            const next=actions[r.index];r.left=next[1];
            if(next[0])shuihu.input(next[0],true);
          }
        }
        if(r.frames===TARGET){r.end=performance.now();r.endFrames=shuihu.meta().frames;shuihu.pause();shuihu.setFrameProbe(null);shuihu.setRafProbe(null);r.done=true;}
      });
      shuihu.setRafProbe(f=>{if(active)r.rafs.push({...f,frame:r.frames});});
      // cold includes frames 1..60 rather than moving warmup off the record.
      // legacy reproduces the old 60-idle-native-frame warmup exactly.
      shuihu.pause(false);if(!r.warm)begin();
    },{actions:route.actions,mode,TARGET,WARMUP,allowRow4:route.allowRow4===true});
    await p.waitForFunction(()=>__stagePerf.done,{},{timeout:120000});
    const raw=await p.evaluate(()=>{shuihu.setRafProbe(null);return {...__stagePerf,state:shuihu.state(),pixels:shuihu.pixels()};});
    if(raw.error)throw Error(route.id+': '+raw.error);
    const {records,rafs}=raw,elapsed=raw.end-raw.start;
    const summarize=a=>({render:stats(a.map(x=>x.renderMs)),frame:stats(a.map(x=>x.frameMs)),core:stats(a.map(x=>x.coreMs))});
    // Native map-ID frame may precede visible raster. Fixed +/-60 native-frame
    // windows include native fade, historical-source recovery and post-switch work.
    const windows=raw.switches.map(s=>{
      const lo=Math.max(1,s.frame-60),hi=Math.min(TARGET,s.frame+60),rows=records.filter(x=>x.frame>=lo&&x.frame<=hi);
      return {...s,lo,hi,...summarize(rows),debt:stats(rafs.filter(x=>x.frame>=lo&&x.frame<=hi).map(x=>x.backlogMs))};
    });
    const selected=records.filter(x=>windows.some(w=>x.frame>=w.lo&&x.frame<=w.hi));
    const result={which,id:route.id,mode,repeat,startup:x.startup,loadState:load,elapsedMs:elapsed,frames:raw.endFrames-raw.startFrames,gameFPS:(raw.endFrames-raw.startFrames)*1000/elapsed,...summarize(records),raf:stats(rafs.map(x=>x.callbackMs)),debt:stats(rafs.map(x=>x.backlogMs)),finalDebtMs:rafs.at(-1)?.backlogMs,switchWindows:windows,switchAggregate:summarize(selected),firstSwitch:windows[0]||null,initial60:summarize(records.slice(0,60)),over50:records.filter(x=>x.frameMs>50),stateSha256:sha(Buffer.from(raw.state)),framebufferSha256:sha(Buffer.from(raw.pixels)),errors:x.errors,records,rafs};
    if(result.frames!==TARGET||x.errors.length)throw Error('Invalid perf sample');
    if(route.target){
      const onMap=records.filter(r=>r.map===route.target);
      if(!onMap.length)throw Error('Perf sample never reached '+route.target);
      result.target={id:route.target,frames:onMap.length,...summarize(onMap)};
    }
    return result;
  } finally {await x.context.close();}
}
function plan(out){
  const routes=inputPlan().perf;
  if(routes.length!==27||new Set(routes.map(r=>r.id)).size!==27||
      routes.some(r=>!isDeepStrictEqual(r.controls,['m10'])))throw Error('Expected 27 distinct M10-paired perf routes');
  const jobs=[];
  for(let repeat=1;repeat<=REPEATS;repeat++)for(const mode of MODES)for(const route of routes){
    // Alternate the pair order across repeats and warmup modes.
    const variants=[...route.controls,'candidate'],offset=(repeat-1+MODES.indexOf(mode))%variants.length;
    const order=variants.slice(offset).concat(variants.slice(0,offset));
    for(const which of order)jobs.push({mode,route,which,repeat,file:path.join(out,`${mode}-${route.id}-${which}-r${repeat}.json`)});
  }
  return jobs;
}

const nonnegative=value=>Number.isFinite(value)&&value>=0;
const digest=value=>typeof value==='string'&&/^[0-9a-f]{64}$/.test(value)&&!/^0+$/.test(value);
const validStats=(v,count)=>v?.samples===count&&['min','max','mean','p95','stddev'].every(k=>nonnegative(v[k]));
function validate(s,{mode,route,which,repeat,file}){
  const validFrames=Array.isArray(s?.records)&&s.records.length===TARGET&&s.records.every((row,i)=>
    row?.frame===i+1&&typeof row.map==='string'&&/^[0-9a-f]{2}-[0-9a-f]{2}$/.test(row.map)&&
    nonnegative(row.coreMs)&&nonnegative(row.renderMs)&&row.frameMs===row.coreMs+row.renderMs);
  const validRafs=Array.isArray(s?.rafs)&&s.rafs.length>0&&s.rafs.every(row=>
    nonnegative(row?.callbackMs)&&nonnegative(row.backlogMs)&&Number.isInteger(row.frame)&&row.frame>=0&&row.frame<=TARGET);
  const validTimings=validRafs&&nonnegative(s.elapsedMs)&&s.elapsedMs>0&&Number.isFinite(s.gameFPS)&&s.gameFPS>0&&
    ['render','frame','core'].every(k=>validStats(s[k],TARGET)&&validStats(s.initial60?.[k],60))&&
    ['debt','raf'].every(k=>validStats(s[k],s.rafs.length))&&Array.isArray(s.switchWindows)&&!!s.switchAggregate;
  if(!s||s.which!==which||s.id!==route.id||s.mode!==mode||s.repeat!==repeat||s.frames!==TARGET||
    !s.measurementRun?.id||
    (route.target&&(s.target?.id!==route.target||s.target.frames!==s.records?.filter(r=>r.map===route.target).length||s.target.frames<1))||
    !Array.isArray(s.errors)||s.errors.length||!digest(s.stateSha256)||!digest(s.framebufferSha256)||!validFrames||!validTimings)
    throw Error('Invalid perf sample; retain file for supervisor review: '+file);
}

function inventory(jobs){
  const found=new Map();
  for(const job of jobs){
    if(!fs.existsSync(job.file))continue;
    let sample;
    try{sample=read(job.file);}catch(e){throw Error('Unreadable perf sample; retain file for supervisor review: '+job.file,{cause:e});}
    validate(sample,job);
    found.set(job.file,sample);
  }
  return found;
}

function publish(file,data,{replace=false}={}){
  const temp=file+'.partial-'+randomUUID();
  try {
    fs.writeFileSync(temp,JSON.stringify(data,null,2)+'\n',{flag:'wx',flush:true});
    // A hard link atomically publishes a complete file and refuses to replace evidence.
    if(replace)fs.renameSync(temp,file);
    else fs.linkSync(temp,file);
    const dir=fs.openSync(path.dirname(file),'r');
    try{fs.fsyncSync(dir);}finally{fs.closeSync(dir);}
  } finally {
    fs.rmSync(temp,{force:true});
  }
}

async function main(){
  verifyFreeze();
  const runDir=output(),runFreeze=path.join(runDir,'run-freeze.sha256');
  if(fs.existsSync(runFreeze)){
    const digest=sha(fs.readFileSync(path.join(PROJECT,'m11-work/integration/outer-freeze.json')));
    if(readRunFreeze(runFreeze)!==digest)throw Error('Freeze changed. Use a fresh run ID.');
  }
  const out=path.join(runDir,'perf'),jobs=plan(out),found=inventory(jobs),reused=found.size;
  const missing=jobs.filter(job=>!found.has(job.file));
  const reportPath=out+'/report.json';
  const counts=()=>({expected:jobs.length,complete:found.size,remaining:jobs.length-found.size});
  console.log('perf inventory',JSON.stringify(counts()));
  if(process.argv[2]==='--inventory')return;
  if(process.argv.length>2)throw Error('Usage: perf.cjs [--inventory]');
  await proxy();
  if(fs.existsSync(reportPath)){
    // Recover the gap between publishing the complete report and writing perf.done.
    const existing=read(reportPath);
    if(missing.length||existing.error||!isDeepStrictEqual(existing.samples,jobs.map(job=>found.get(job.file))))
      throw Error('Existing perf report disagrees with sample files; retain for supervisor review: '+reportPath);
    return;
  }
  fs.mkdirSync(out,{recursive:true});
  const measurementRuns=new Map();
  for(const [file,sample] of found){
    const run=sample.measurementRun;
    if(!run?.id)throw Error('Saved sample has no measurement-run provenance: '+file);
    measurementRuns.set(run.id,run);
  }
  const progress=()=>publish(out+'/resume-progress.json',{...counts(),reusedAtStart:reused},{replace:true});
  progress();
  if(missing.length){
    const {chromium}=require('playwright');
    const browser=await chromium.launch({args:['--no-sandbox']});
    try{
      const run={id:randomUUID(),startedUtc:new Date().toISOString(),machine:{platform:os.platform(),release:os.release(),cpu:os.cpus()[0]?.model,cpuCount:os.cpus().length,browser:await browser.version(),node:process.version}};
      measurementRuns.set(run.id,run);
      for(const job of missing){
        await proxy();
        const sample=await measure(browser,job.which,job.route,job.mode,job.repeat);
        sample.measurementRun=run;
        validate(sample,job);
        publish(job.file,sample);
        found.set(job.file,sample);
        progress();
        console.log('perf',job.repeat,job.mode,job.route.id,job.which,sample.gameFPS,sample.render,sample.debt.max,counts());
      }
    }finally{await browser.close();}
  }
  await proxy();verifyFreeze();
  const report={pass:null,method:{version:3,TARGET,WARMUP,REPEATS,modes:['legacy: 60 idle warmup frames then 1792 measured frames','cold: input from first native frame, all first 60 included'],switchWindow:'map ID change +/-60 native frames (inclusive); overlapping frames counted once in aggregate',isolation:'Supervisor must confirm no competing QA/recording/CPU work',audit:false,recording:false,freshPageAndContextPerSample:true},machine:[...measurementRuns.values()].at(-1)?.machine,measurementRuns:[...measurementRuns.values()],reusedAtStart:reused,samples:jobs.map(job=>found.get(job.file))};
  publish(reportPath,report);
}
function readRunFreeze(file){return fs.readFileSync(file,'utf8').trim().split(/\s+/)[0];}
if(require.main!==module)module.exports={measure,TARGET,WARMUP,REPEATS};
else main().catch(e=>{console.error(e);process.exitCode=1;});
