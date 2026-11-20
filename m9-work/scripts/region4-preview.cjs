const {fs,path,PROJECT,W,roots,output,write,read,sha,plan,proxy,verifyFreeze,page}=require('./outer-common.cjs');
const assert=require('node:assert/strict');
const {spawnSync}=require('node:child_process');
const {randomUUID}=require('node:crypto');

const nativeFrameMs=1000*70224/4194304;
const verify=(got, expected, label)=>{
  for(const k of ['stateSHA256','nativeFramebufferSHA256','ticks','frame']){
    assert.equal(got[k],expected[k],label+' '+k);
  }
};

async function capture(dir, config) {
  const {chromium}=require('playwright');
  const spec=config.official, official=read(path.join(PROJECT,spec.result));
  const actions=read(path.join(PROJECT,spec.actions));
  const source=fs.readFileSync(path.join(PROJECT,spec.source));
  assert.equal(sha(source),official.sourceSHA256);
  const browser=await chromium.launch({args:['--no-sandbox']});
  let session;
  const clips=[];
  try {
    session=await page(browser,roots.candidate,{
      viewport:{width:640,height:592},recordVideo:{dir,size:{width:640,height:592}},
    });
    const {p,context,errors}=session;
    await p.addStyleTag({content:`
      html,body{margin:0!important;padding:0!important;background:black!important;overflow:hidden!important}
      body *{visibility:hidden}
      #screen{visibility:visible;position:fixed;left:0;top:16px;width:640px!important;height:576px!important;
        max-width:none!important;margin:0!important;padding:0!important;border:0!important;z-index:10}`});
    await p.evaluate(bytes=>{
      const marker=document.createElement('div');
      marker.style.cssText='position:fixed;left:0;top:0;width:640px;height:16px;z-index:11;visibility:visible;background:black';
      document.body.append(marker);
      window.previewMarker=marker;
      window.previewSnapshot=()=>{
        const {frames,ticks}=shuihu.meta();
        return {state:shuihu.state(),pixels:shuihu.pixels(),ticks,frame:frames-1};
      };
      shuihu.loadState(bytes);
      shuihu.setAudit(false);
    },Array.from(source));
    const evidence=({state,pixels,...meta})=>({...meta,stateSHA256:sha(Buffer.from(state)),
      nativeFramebufferSHA256:sha(Buffer.from(pixels))});
    const initial=evidence(await p.evaluate(()=>previewSnapshot()));
    verify(initial,official.initial,'Official start');

    let next=0;
    for(const clip of config.clips){
      await proxy();
      while(next<clip.first){
        const end=Math.min(next+6,clip.first);
        await p.evaluate(inputs=>{
          for(const [key,hold,wait] of inputs){
            if(key)shuihu.input(key,true);
            for(let i=0;i<hold;i++)shuihu.step(1);
            if(key)shuihu.input(key,false);
            for(let i=0;i<wait;i++)shuihu.step(1);
          }
        },actions.slice(next,end));
        next=end;
      }
      const start=evidence(await p.evaluate(()=>previewSnapshot()));
      verify(start,official.records[clip.first-1],clip.name+' start');
      const excerpt=actions.slice(clip.first,clip.last+1);
      const nativeFrames=excerpt.reduce((sum,[,hold,wait])=>sum+hold+wait,0);
      // Let the recorder include an unmarked boundary between excerpts.
      await p.waitForTimeout(220);
      await p.evaluate(inputs=>{
        const phases=inputs.flatMap(([key,hold,wait])=>[[key,true,hold],[key,false,wait]]);
        const playback=window.previewPlayback={started:performance.now()};
        let nextPhase=0,left=0;
        function advance(){
          while(nextPhase<phases.length){
            const [key,on,n]=phases[nextPhase++];
            if(key)shuihu.input(key,on);
            if(n){left=n;return;}
          }
          playback.elapsedMs=performance.now()-playback.started;
          previewMarker.style.background='black';
          playback.endpoint=previewSnapshot();
          shuihu.pause();
          shuihu.setFrameProbe(null);
        }
        previewMarker.style.background='white';
        shuihu.pause(false);
        shuihu.setFrameProbe(()=>{if(--left===0)advance();});
        advance();
      },excerpt);
      await p.waitForFunction(()=>window.previewPlayback?.endpoint,{}, {timeout:120000});
      const {elapsedMs,endpoint}=await p.evaluate(()=>previewPlayback);
      const end=evidence(endpoint);
      verify(end,official.records[clip.last],clip.name+' end');
      assert(elapsedMs>=nativeFrames*nativeFrameMs*.97,clip.name+' ran ahead of real time');
      clips.push({name:clip.name,first:clip.first,last:clip.last,nativeFrames,elapsedMs,start,end});
      next=clip.last+1;
      write(path.join(dir,'progress.json'),{clips,errors});
      console.log('recorded',clip.name,nativeFrames,elapsedMs);
    }
    assert.equal(next,actions.length);
    assert.deepEqual(errors,[]);
    await p.waitForTimeout(220);
    const video=await p.video().path();
    await context.close();
    session=null;
    const raw=path.join(dir,'region4-raw.webm');
    fs.renameSync(video,raw);
    const captureReport={raw,rawSHA256:sha(fs.readFileSync(raw)),sourceSHA256:sha(source),initial,clips};
    write(path.join(dir,'capture.json'),captureReport);
    return captureReport;
  } finally {
    await session?.context.close();
    await browser.close();
  }
}

function run(cmd,args,log,stdout='/dev/null'){
  const err=fs.openSync(log,'w'), out=fs.openSync(stdout,'w');
  try {
    const result=spawnSync(cmd,args,{stdio:['ignore',out,err]});
    if(result.error)throw result.error;
    if(result.status!==0)throw Error(cmd+' failed ('+result.status+'): '+fs.readFileSync(log,'utf8').slice(-1500));
  } finally {
    fs.closeSync(out);
    fs.closeSync(err);
  }
}

function encode(dir,captureReport){
  const {raw,rawSHA256,clips}=captureReport;
  assert.equal(sha(fs.readFileSync(raw)),rawSHA256);
  const markerLog=path.join(dir,'marker-frames.log');
  if(!fs.existsSync(markerLog)){
    const pending=markerLog+'.partial-'+randomUUID();
    try {
      run('ffmpeg',['-hide_banner','-i',raw,'-vf','crop=8:8:8:4,showinfo','-an','-f','null','-'],pending);
      fs.renameSync(pending,markerLog);
    } finally {
      fs.rmSync(pending,{force:true});
    }
  }
  const cuts=[];
  let start=null, last=-1;
  for(const line of fs.readFileSync(markerLog,'utf8').split('\n')){
    const m=line.match(/pts_time:\s*([\d.]+).*mean:\[(\d+)/);
    if(!m)continue;
    const t=Number(m[1]),active=Number(m[2])>128;
    assert(t>last,'Unexpected recording timestamps');
    last=t;
    if(active&&start===null)start=t;
    if(!active&&start!==null){cuts.push({start,end:t});start=null;}
  }
  if(start!==null)cuts.push({start,end:last});
  assert.equal(clips.length,7,'Expected seven official excerpts');
  assert.equal(cuts.length,clips.length,'Recording marker count differs from official excerpt count');
  const timestampSlack=.041; // One 25 fps recording frame plus the WebM timestamp resolution.
  const segments=cuts.map((cut,i)=>{
    const clip=clips[i], duration=clip.elapsedMs/1000;
    const end=cut.start+duration;
    assert(Number.isFinite(duration)&&duration>0,clip.name+' has invalid elapsed time');
    assert(end<=cut.end+timestampSlack,clip.name+' playback exceeds the white marker interval');
    return {...clip,start:cut.start,end,duration};
  });
  const expected=segments.reduce((sum,s)=>sum+s.duration,0);
  const video=path.join(dir,'region4-preview-'+randomUUID()+'.webm');
  const filters=segments.map(({start,end},i)=>
    `[0:v]trim=start=${start}:end=${end},crop=640:576:0:16,setpts=PTS-STARTPTS[c${i}]`);
  filters.push(segments.map((_,i)=>`[c${i}]`).join('')+`concat=n=${segments.length}:v=1:a=0[v]`);
  run('ffmpeg',['-hide_banner','-loglevel','warning','-i',raw,'-filter_complex',filters.join(';'),
    '-map','[v]','-an','-fps_mode','passthrough','-c:v','libvpx-vp9','-b:v','1200k','-maxrate','1600k',
    '-bufsize','2400k','-crf','30',video],path.join(dir,'encode.log'));
  const probe=path.join(dir,'preview-probe.json');
  run('ffprobe',['-v','error','-show_format','-show_streams','-of','json',video],path.join(dir,'probe.log'),probe);
  const probed=read(probe);
  const bytes=fs.statSync(video).size, duration=Number(probed.format.duration);
  assert(bytes>0 && bytes<25_000_000,'Preview exceeds byte limit');
  assert.equal(probed.streams.length,1,'Unexpected extra video or audio streams');
  const {codec_type,width,height}=probed.streams[0];
  assert.deepEqual([codec_type,width,height],['video',640,576]);
  assert(Math.abs(expected-duration)<=.45,'Encoded duration differs from observed cuts');
  write(path.join(dir,'encode-report.json'),{video,videoSHA256:sha(fs.readFileSync(video)),bytes,duration,segments,
    audio:false,speedMultiplier:1,rawSHA256,method:'Continuous official-save replay. Native runtime rAF inside excerpts. Raw timestamps retained within each cut.'});
}

async function main(){
  const dir=path.join(output(),'preview'),rawReport=path.join(dir,'capture.json');
  const encoded=path.join(dir,'encode-report.json'),dest=path.join(W,'region4_preview.webm');
  const config=plan();
  fs.mkdirSync(dir,{recursive:true});
  await proxy();verifyFreeze();
  if(!fs.existsSync(encoded)){
    let report;
    if(fs.existsSync(rawReport))report=read(rawReport);
    else {
      if(fs.readdirSync(dir).length)fs.renameSync(dir,dir+'.interrupted-'+randomUUID());
      fs.mkdirSync(dir,{recursive:true});
      report=await capture(dir,config);
    }
    await proxy();
    encode(dir,report);
  }
  const report=read(encoded),digest=file=>sha(fs.readFileSync(file));
  assert.equal(digest(report.video),report.videoSHA256);
  assert(report.segments.length===config.clips.length && report.bytes>0 && report.bytes<25_000_000);
  await proxy();verifyFreeze();
  if(!fs.existsSync(dest))fs.linkSync(report.video,dest);
  assert.equal(digest(dest),report.videoSHA256,'Existing preview differs; retain it for review');
  console.log('Preview published',dest,report.bytes,report.duration);
}

if(require.main===module)main().catch(e=>{console.error(e);process.exitCode=1;});
else module.exports={encode};
