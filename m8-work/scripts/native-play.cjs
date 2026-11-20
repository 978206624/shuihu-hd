// Offline exploration adapter for the established M7 webplay/pathfind/talk/door
// controls. Bundled, unmodified binjgb WASM; no game RAM/PC writes or network.
// Branches are explicitly isolated searches. Only replay output can be accepted.
const fs=require('fs'),path=require('path'),crypto=require('crypto'),zlib=require('zlib');
const ROOT=path.resolve(__dirname,'../..'),WORK=ROOT+'/m8-work',RUNTIME=WORK+'/runtime';
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
const write=(p,v)=>fs.writeFileSync(p,JSON.stringify(v,null,2)+'\n');
const keys=['up','down','left','right','A','B','start','select'];
function png(rgba,w,h){
 const crc=b=>{let c=0xffffffff;for(const x of b){c^=x;for(let i=0;i<8;i++)c=(c>>>1)^((c&1)?0xedb88320:0);}return (c^0xffffffff)>>>0;};
 const chunk=(s,b)=>{const t=Buffer.from(s),n=Buffer.alloc(4),c=Buffer.alloc(4);n.writeUInt32BE(b.length);c.writeUInt32BE(crc(Buffer.concat([t,b])));return Buffer.concat([n,t,b,c]);};
 const hdr=Buffer.alloc(13);hdr.writeUInt32BE(w);hdr.writeUInt32BE(h,4);hdr[8]=8;hdr[9]=6;
 const raw=Buffer.alloc(h*(w*4+1));for(let y=0;y<h;y++)rgba.copy(raw,y*(w*4+1)+1,y*w*4,(y+1)*w*4);
 return Buffer.concat([Buffer.from([137,80,78,71,13,10,26,10]),chunk('IHDR',hdr),chunk('IDAT',zlib.deflateSync(raw)),chunk('IEND',Buffer.alloc(0))]);
}
async function core(){
 const m=await require(RUNTIME+'/vendor/binjgb.js')({wasmBinary:fs.readFileSync(RUNTIME+'/vendor/binjgb.wasm')});
 const rom=fs.readFileSync(RUNTIME+'/assets/game.gbc'),p=m._malloc(rom.length);m.HEAPU8.set(rom,p);
 const e=m._emulator_new_simple(p,rom.length,48000,2048,0),j=m._joypad_new();m._emulator_set_default_joypad_callback(e,j);
 let frames=0,log,branch=null;
 const read=a=>m._emulator_read_mem(e,a),fb=()=>Buffer.from(m.HEAPU8.slice(m._get_frame_buffer_ptr(e),m._get_frame_buffer_ptr(e)+160*144*4));
 const meta=()=>({frame:frames,ticks:m._emulator_get_ticks_f64(e),map:[read(0xff9a),read(0xff9b)].map(x=>x.toString(16).padStart(2,'0')).join('-'),story:read(0xffba),dialogue:read(0xffbc),mode:read(0xd0fa),bank:read(0xd08f),player:Array.from({length:8},(_,i)=>read(0xcd00+i)),camera:[read(0xff96),read(0xff97)],scroll:[read(0xff43),read(0xff42)]});
 const event=o=>{if(log!==undefined)fs.writeSync(log,JSON.stringify(o)+'\n');};
 const step=n=>{for(let i=0;i<n;i++){const t=m._emulator_get_ticks_f64(e)+70224;let guard=0;while(true){const ev=m._emulator_run_until_f64(e,t);if(ev&4)break;if(++guard>100)throw Error('Native core guard');}frames++;event({type:'frame',branch,...meta()});}};
 const state=data=>{const f=m._state_file_data_new(e);try{const p=m._get_file_data_ptr(f),n=m._get_file_data_size(f);if(data){if(data.length!==n)throw Error('State length');m.HEAPU8.set(data,p);if(m._emulator_read_state(e,f)!==0)throw Error('Invalid save');}else m._emulator_write_state(e,f);return Buffer.from(m.HEAPU8.slice(p,p+n));}finally{m._file_data_delete(f);m._free(f);}};
 const input=(k,on)=>{if(!keys.includes(k))throw Error('Invalid natural key');m['_set_joyp_'+k](e,+on);event({type:'input',branch,frame:frames,key:k,on});};
 const action=a=>{const [k,h,w]=a;if(!Number.isInteger(h)||h<0||!Number.isInteger(w)||w<0)throw Error('Frames');if(k)input(k,true);step(h);if(k)input(k,false);step(w);};
 step(1); // Same native initial frame as app startup; not part of loaded route.
 return {m,e,read,fb,meta,step,state,input,action,event,setLog:fd=>log=fd,setBranch:b=>branch=b,snap:p=>fs.writeFileSync(p,png(fb(),160,144))};
}
async function run(){
 const [mode,srcArg,tag,arg,limitArg]=process.argv.slice(2),src=path.resolve(srcArg||'');
 if(!['inspect','replay','search','doors','talk'].includes(mode)||!tag||!/^[a-zA-Z0-9_-]+$/.test(tag))throw Error('Usage: native-play.cjs inspect|replay|search|doors|talk source.bin unique-tag [actions.json|goal|max-pages] [node-limit]');
 const out=WORK+(mode==='search'||mode==='doors'?'/search/':'/play/')+tag;
 if(fs.existsSync(out))throw Error('Refusing to overwrite attempt '+out);fs.mkdirSync(out,{recursive:true});
 const source=fs.readFileSync(src),c=await core(),fd=fs.openSync(out+'/frames.jsonl','wx');c.setLog(fd);c.state(source);c.setBranch('root');
 const provenance={mode,source:src,sourceSHA256:sha(source),sourceBytes:source.length,started:new Date().toISOString(),pid:process.pid,unmodifiedCoreSHA256:sha(fs.readFileSync(RUNTIME+'/vendor/binjgb.wasm')),romSHA256:sha(fs.readFileSync(RUNTIME+'/assets/game.gbc')),naturalControlsOnly:true,accepted:false,searchHint:process.env.M8_SEARCH_HINT||null,positionalKey:process.env.M8_POSITIONAL_KEY==='1',battleRecovery:process.env.M8_BATTLE_RECOVERY==='1',scriptSHA256:sha(fs.readFileSync(__filename)),initial:c.meta()};write(out+'/provenance.json',provenance);fs.writeFileSync(out+'/start.bin',source);
 try{
  if(mode==='inspect'){c.step(1);c.snap(out+'/native.png');write(out+'/result.json',c.meta());}
  if(mode==='replay'||mode==='talk'){
   const actions=mode==='replay'?JSON.parse(fs.readFileSync(arg)):Array.from({length:Number(arg||80)},()=>['B',6,160]);
   const records=[],executed=[];let quiet=0;for(let i=0;i<actions.length;i++){
    c.action(actions[i]);executed.push(actions[i]);const bytes=c.state(),record={action:i,input:actions[i],stateSHA256:sha(bytes),nativeFramebufferSHA256:sha(c.fb()),...c.meta()};records.push(record);
    c.snap(out+'/page_'+String(i).padStart(4,'0')+'.png');fs.writeFileSync(out+'/latest.bin',bytes);write(out+'/actions.json',executed);write(out+'/checkpoints.json',records);
    console.log(i,JSON.stringify(record));quiet=record.dialogue===0?quiet+1:0;if(mode==='talk'&&quiet>=4&&i>5)break;
   }write(out+'/result.json',{isolatedSearch:false,actions:executed,records,end:c.meta(),endSHA256:sha(c.state())});
  }
  if(mode==='search'||mode==='doors'){
   // M7 BFS with the same 16 held / 8 released controls and natural flee menu.
   // Every node reload and every actual frame is logged; searches are never
   // described as a continuous accepted route. Found actions need fresh replay.
   const limit=Number(limitArg||1800),deadline=Date.now()+90000,settle=120;c.step(settle);
   const read=c.read,origin=c.meta().map,delta=(u,v)=>((u-v+128)&255)-128;
   const pos=(cx,cy)=>[cx+read(0xcd01),cy+read(0xcd00)],key=(cx,cy)=>[c.meta().map,...pos(cx,cy),read(0xffba),read(0xd0fa),...(process.env.M8_POSITIONAL_KEY==='1'?[]:[read(0xd08f),read(0xcd03),read(0xcd05),read(0xcd06),read(0xcd07)])].join(',');
   const cx0=read(0xff96)*32+read(0xff43),cy0=read(0xff97)*32+read(0xff42),q=[{state:c.state(),path:[],cx:cx0,cy:cy0,xy:pos(cx0,cy0)}],seen=new Set([key(cx0,cy0)]),found={},branches=fs.openSync(out+'/branches.jsonl','wx');let idx=0;
   while(idx<q.length&&seen.size<limit&&Date.now()<deadline){if(process.env.M8_SEARCH_HINT){const hint=process.env.M8_SEARCH_HINT.split(',').map(Number);let best=idx,score=Infinity;for(let k=idx;k<q.length;k++){const n=q[k],xy=n.xy||pos(n.cx,n.cy),v=Math.abs(xy[0]-hint[0])+Math.abs(xy[1]-hint[1])+n.path.length*3;if(v<score){score=v;best=k;}}[q[idx],q[best]]=[q[best],q[idx]];}const a=q[idx++];for(const d of ['up','down','left','right']){
    c.state(a.state);c.setBranch([idx-1,d]);c.event({type:'branch-load',node:idx-1,stateSHA256:sha(a.state),path:a.path});const sx=read(0xff43),sy=read(0xff42),actions=[[d,16,8]];c.action(actions[0]);
    if(mode==='search'&&[0x2b,0x2c,0x2d].includes(read(0xd08f))){const flee=[[null,360,0],...(process.env.M8_BATTLE_RECOVERY==='1'?[['B',6,160]]:[]),['right',6,12],['down',6,12],['A',6,240],['B',6,100]];for(const x of flee){c.action(x);actions.push(x);}if(process.env.M8_BATTLE_RECOVERY==='1')for(let n=0;n<7&&[43,44,45].includes(read(0xd08f));n++)for(const x of [['right',6,12],['down',6,12],['A',6,240],['B',6,100]]){c.action(x);actions.push(x);}}
    if(arg==='talk'&&c.meta().map===origin&&![43,44,45].includes(read(0xd08f))){const press=['A',6,160];c.action(press);actions.push(press);}
    const cx=a.cx+delta(read(0xff43),sx),cy=a.cy+delta(read(0xff42),sy),k=key(cx,cy),id=c.meta().map,p=[...a.path,...actions];
    fs.writeSync(branches,JSON.stringify({node:idx-1,d,actions,stateSHA256:sha(c.state()),...c.meta(),xy:pos(cx,cy)})+'\n');
    if(seen.has(k))continue;seen.add(k);const xy=pos(cx,cy),yes=mode==='doors'?id!==origin:arg==='talk'?read(0xffbc)!==0:arg.startsWith('pos:')?arg.slice(4).split(',').map(Number).every((v,i)=>Math.abs(xy[i]-v)<5):id===arg;
    if(yes&&!found[id]){const name=mode==='doors'?id:'goal';found[id]={actions:[[null,settle,0],...p],id,xy,story:read(0xffba),mode:read(0xd0fa),searchStateSHA256:sha(c.state()),branchNode:idx-1};fs.writeFileSync(out+'/'+name+'.bin',c.state());write(out+'/'+name+'-actions.json',found[id].actions);c.snap(out+'/'+name+'.png');console.log('FOUND',id,xy,'actions',p.length);}
    if(mode==='search'&&yes)break;
    if(id===origin&&read(0xd0fa)===0&&![0x2b,0x2c,0x2d].includes(read(0xd08f)))q.push({state:c.state(),path:p,cx,cy,xy});
   }
   if(mode==='search'&&Object.keys(found).length)break;
   if(idx%100===0){console.log('search',idx,seen.size,q.length-idx,Object.keys(found));write(out+'/progress.json',{idx,seen:seen.size,frontier:q.length-idx,found});}
   }
   fs.closeSync(branches);write(out+'/result.json',{isolatedSearch:true,origin,goal:arg,settleFrames:settle,nodes:seen.size,expanded:idx,frontier:q.length-idx,deadlineHit:Date.now()>=deadline,found,positions:[...seen]});
   // Resumable bounded search checkpoint, including exact pending native states.
   fs.writeFileSync(out+'/frontier.v8.gz',zlib.gzipSync(require('v8').serialize({idx,q,seen:[...seen],found,sourceSHA256:sha(source)})));
  }
  provenance.finished=new Date().toISOString();provenance.status='COMPLETE';
 }catch(e){provenance.status='FAILED';provenance.error=e.message;throw e;}finally{write(out+'/provenance.json',provenance);fs.closeSync(fd);fs.writeFileSync(out+'/frames.jsonl.gz',zlib.gzipSync(fs.readFileSync(out+'/frames.jsonl')));fs.unlinkSync(out+'/frames.jsonl');}
 console.log('OUTPUT',out);
}
if(require.main===module)run().catch(e=>{console.error(e);process.exitCode=1;});
module.exports={core,png,sha};
