// Actual bundled WASM. Tests observation/history contracts, not browser pixels
// or realtime performance. Canvas calls are stubs and cannot certify HD RGBA.
const fs=require('fs'),path=require('path'),assert=require('assert/strict'),crypto=require('crypto');
const root=path.resolve(__dirname,'..'),base='/tmp/shawu-m52-phase1',out=process.argv[2]||'/workspace/shawu/m5-work/perf/m52/phase2-native-contract.json';
const modules=new Map();function url(file){if(modules.has(file))return modules.get(file);const s=fs.readFileSync(file,'utf8').replace(/from '(\.\/[^']+)'/g,(_,f)=>`from '${url(path.resolve(path.dirname(file),f))}'`),u='data:text/javascript;base64,'+Buffer.from(s).toString('base64');modules.set(file,u);return u;}
class Data{constructor(a,w,h){if(typeof a==='number'){this.width=a;this.height=w;this.data=new Uint8ClampedArray(a*w*4);}else{this.width=w;this.height=h;this.data=a;}}}
class Canvas{constructor(){this.width=300;this.height=150;}getContext(){return this.ctx??={canvas:this,drawImage(){},clearRect(){},putImageData(){},createImageData:(w,h)=>new Data(w,h),getImageData:(x,y,w,h)=>new Data(w,h)};}}
global.ImageData=Data;global.document={createElement:()=>new Canvas()};
(async()=>{const O=(await import(url(base+'/observer.js'))).Observer,N=(await import(url(root+'/observer.js'))).Observer,A=(await import(url(base+'/map-renderer.js'))).MapRenderer,B=(await import(url(root+'/map-renderer.js'))).MapRenderer;
 const m=await require(root+'/vendor/binjgb.js')({wasmBinary:fs.readFileSync(root+'/vendor/binjgb.wasm')}),rom=fs.readFileSync(root+'/assets/game.gbc'),rp=m._malloc(rom.length);m.HEAPU8.set(rom,rp);const e=m._emulator_new_simple(rp,rom.length,48000,2048,0),joy=m._joypad_new();m._emulator_set_default_joypad_callback(e,joy);const oa=new O(m,e),ob=new N(m,e);
 const specs=JSON.parse(fs.readFileSync(root+'/assets/maps/m3_signatures.json')),title=JSON.parse(fs.readFileSync(root+'/assets/title_native.json')).cells;
 function make(K){const r=new K();r.auditEnabled=true;r.backdropOpaque=true;r.maps=specs.map(s=>({...s,image:{},sets:s.cellKeys.map(a=>new Set(a)),cache:new Map()}));r.faded=()=>new Canvas();r.fadedRow=r.fadedStrip=(map,o,y)=>({image:new Canvas(),y:y*4});r.dialogue={width:120,height:48};return r;}
 const a=make(A),b=make(B),ctx=new Canvas().getContext('2d');let samples=0,maps=0,occluded=0,uiSnapshots=0,retained=[];const digest=o=>crypto.createHash('sha256').update(Buffer.from(o.bg.buffer)).update(Buffer.from(o.indices.buffer)).update(Buffer.from(o.mask.buffer)).update(Buffer.from(o.actorMask.buffer)).update(JSON.stringify([o.cellKeys,o.palettes,o.tiles,o.attrs])).digest('hex');
 function one(){const t=m._emulator_get_ticks_f64(e)+70224;while(!(m._emulator_run_until_f64(e,t)&4)){}const p=m.HEAPU8.slice(m._get_frame_buffer_ptr(e),m._get_frame_buffer_ptr(e)+92160),x=oa.sample(p),y=ob.sample(p);assert.deepEqual(y,x,'Observer at '+samples);samples++;
 if(samples%120===0){for(const q of retained)assert.equal(digest(q.o),q.hash,'Retained snapshot mutated');retained.push({o:y,hash:digest(y)});if(retained.length>8)retained.shift();}
 if(!x||Object.entries(title).every(([k,v])=>x.cellKeys[k]===v))return;
 let flat=!x.actorMask.some(Boolean);for(let i=4;flat&&i<p.length;i+=4)if(p[i]!==p[0]||p[i+1]!==p[1]||p[i+2]!==p[2])flat=false;
 const ra=a.draw(ctx,x,p),rb=b.draw(ctx,y,p,{fullyOccluded:flat});assert.deepEqual(rb,ra,'Map metadata at '+samples);maps++;occluded+=!!b.lastOccluded;uiSnapshots+=!!b.uiPresentation;
 const ui=r=>{const q=r.uiPresentation;return q?{native:q.native,keys:q.keys,attrs:q.attrs,tiles:q.tiles,palettes:q.palettes,rect:q.rect,active:q.active,attributeClose:q.attributeClose,ticks:q.ticks}:null;};assert.deepEqual(ui(b),ui(a),'Certified UI at '+samples);
 const hist=r=>r.history.map(q=>({o:q.o,rasterUI:q.rasterUI.o,historyKey:q.historyKey,score:q.score,visible:q.visible,map:q.map?.name}));assert.deepEqual(hist(b),hist(a),'Native history at '+samples);
 }
 for(let i=0;i<3301;i++)one();m._set_joyp_start(e,1);one();one();m._set_joyp_start(e,0);for(let i=0;i<120;i++)one();for(let f=0;f<730;f++){m._set_joyp_A(e,+(f%120<2));one();}
 const result={pass:true,nativeSamples:samples,bootSamples:3301,postStartSamples:730,mapMetadataAndHistoryChecks:maps,fullyOccludedMapFrames:occluded,certifiedUIFrames:uiSnapshots,retainedSnapshotChecks:true,note:'WASM/native observation and history only. Stub Canvas: no HD pixel or performance claim.'};fs.writeFileSync(out,JSON.stringify(result,null,2));console.log(JSON.stringify(result));
})().catch(e=>{console.error(e);process.exitCode=1;});
