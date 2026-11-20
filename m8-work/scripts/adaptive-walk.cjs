// Natural controls only. Interrupt directional holds at native wild-battle bank
// observation, use the established M7 flee menu, then resume remaining frames.
const fs=require('fs'),path=require('path'),zlib=require('zlib');
const {core,sha}=require('./native-play.cjs');
(async()=>{
 const [src,tag,file]=process.argv.slice(2);if(!/^[\w-]+$/.test(tag))throw Error('tag');
 const out=path.resolve(__dirname,'../play',tag);if(fs.existsSync(out))throw Error('Existing attempt');fs.mkdirSync(out,{recursive:true});
 const c=await core(),bytes=fs.readFileSync(src),fd=fs.openSync(out+'/frames.jsonl','wx');c.setLog(fd);c.setBranch('natural-adaptive-walk');c.state(bytes);fs.writeFileSync(out+'/start.bin',bytes);
 const spec=JSON.parse(fs.readFileSync(file)),actions=[],records=[],battle=()=>[43,44,45].includes(c.read(0xd08f)),started=Date.now();
 const write=(name,v)=>fs.writeFileSync(out+'/'+name,JSON.stringify(v,null,2)+'\n');
 const save=a=>{actions.push(a);const b=c.state();records.push({input:a,stateSHA256:sha(b),nativeFramebufferSHA256:sha(c.fb()),...c.meta()});fs.writeFileSync(out+'/latest.bin',b);c.snap(out+'/page_'+String(actions.length-1).padStart(4,'0')+'.png');write('actions.json',actions);write('checkpoints.json',records);console.log(actions.length-1,JSON.stringify(records.at(-1)));};
 const act=a=>{c.action(a);save(a);};
 const flee=()=>{act([null,360,0]);act(['B',6,160]);for(let n=0;n<8&&battle();n++)for(const a of [['right',6,12],['down',6,12],['A',6,240],['B',6,100]])act(a);if(battle())throw Error('Bounded flee attempt exhausted; inspect native pages');};
 let status='COMPLETE',error;
 try{for(const [k,h,w] of spec){
  if(!k||!['up','down','left','right'].includes(k)){act([k,h,w]);continue;}
  let left=h;while(left>0){if(Date.now()-started>90000)throw Error('Walk deadline');if(battle())flee();c.input(k,true);let held=0;while(left>0){c.step(1);held++;left--;if(battle())break;}c.input(k,false);save([k,held,0]);if(battle())flee();}
  if(w)act([null,w,0]);
 }}catch(e){status='STOPPED';error=e.message;process.exitCode=2;}
 finally{fs.closeSync(fd);fs.writeFileSync(out+'/frames.jsonl.gz',zlib.gzipSync(fs.readFileSync(out+'/frames.jsonl')));fs.unlinkSync(out+'/frames.jsonl');write('result.json',{source:path.resolve(src),sourceSHA256:sha(bytes),scriptSHA256:sha(fs.readFileSync(__filename)),mode:'natural-adaptive-walk',accepted:false,status,error,actions,records,end:c.meta(),pid:process.pid,finished:new Date().toISOString()});}
 console.log('OUTPUT',out,status,error||'');
})().catch(e=>{console.error(e);process.exitCode=1;});
