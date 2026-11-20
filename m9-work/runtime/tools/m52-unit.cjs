// No browser/PPU image fidelity claim: arithmetic, startup gating and state contracts.
const fs=require('fs'),path=require('path'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'..');
const moduleURL=(name)=>{let s=fs.readFileSync(path.join(root,name),'utf8');s=s.replace(/from '(\.\/[^']+)'/g,(_,f)=>`from '${moduleURL(f.slice(2))}'`);return 'data:text/javascript;base64,'+Buffer.from(s).toString('base64');};
class Data{constructor(a,w,h){if(typeof a==='number'){this.width=a;this.height=w;this.data=new Uint8ClampedArray(a*w*4);}else{this.width=w;this.height=h;this.data=a;}}}
let calls=0;
class Canvas{constructor(){this.width=300;this.height=150;}getContext(){return this.ctx??={canvas:this,drawImage(){calls++;},clearRect(){},fillText(){},putImageData(d){this.data={width:d.width,height:d.height,data:d.data.slice()};},createImageData:(w,h)=>new Data(w,h),getImageData:(x,y,w,h)=>new Data(w,h)};}}
global.ImageData=Data;global.document={createElement:()=>new Canvas()};
(async()=>{
 const assets=await import(moduleURL('asset-loader.js'));
 // All representable bytes, negative/positive slopes and half-way rounding.
 for(const fit of [[[1,0],[.5,.5],[-.5,128.5]],[[.966327446872194,6.967255312780606],[.9700926197416306,5.8572931578675025],[.9660101098134913,7.181453721457205]],[[0,248],[2,-200],[1,8]]]){
 const src=new Uint8ClampedArray(256*4);for(let i=0;i<256;i++)src.set([i,255-i,i,(i*17)%256],i*4);
 const expected=src.slice(),out=src.slice();for(let i=0;i<src.length;i+=4)for(let ch=0;ch<3;ch++)expected[i+ch]=Math.max(0,Math.min(255,fit[ch][0]*src[i+ch]+fit[ch][1]));assets.recolor(src,out,assets.colorTables(fit));assert.deepEqual(out,expected);
 }
 let decodeResolve,decoded=false,constructed=0;
 global.Image=class{constructor(){constructed++;}set src(s){queueMicrotask(()=>this.onload());}decode(){return new Promise(r=>decodeResolve=()=>{decoded=true;r();});}};
 let resolved=false;const loading=assets.loadImage('unit.png').then(()=>{resolved=true;});assert.equal(assets.loadImage('unit.png'),assets.loadImage('unit.png'));await new Promise(r=>setTimeout(r,0));assert.equal(resolved,false);assert.equal(constructed,1);decodeResolve();await loading;assert.ok(decoded&&resolved);
 const {MapRenderer}=await import(moduleURL('map-renderer.js')),{Renderer}=await import(moduleURL('renderer.js'));
 // Skip map writes only; compare actual observation/history objects and metadata.
 function make(){const m=new MapRenderer();m.auditEnabled=true;m.backdropOpaque=true;m.maps=[{name:'test',bounds:[0,0,256,256],sets:Array.from({length:1024},()=>new Set([1]))}];m.faded=()=>new Canvas();m.fadedStrip=(map,o,y)=>({image:new Canvas(),y:y*4});return m;}
 const a=make(),b=make(),ctx=new Canvas().getContext('2d');let ticks=0;
 function observation(){const bg=new Uint8ClampedArray(256*256*4);for(let i=3;i<bg.length;i+=4)bg[i]=255;return {ticks:ticks+=70224,mask:new Uint8Array(23040),actorMask:new Uint8Array(23040),dialogueRects:[],bg,cellKeys:new Array(1024).fill(1),attrs:new Array(1024).fill(0),tiles:new Array(1024).fill(0),palettes:new Array(128).fill(0),scx:0,scy:0};}
 const p=new Uint8Array(92160);for(let i=3;i<p.length;i+=4)p[i]=255;
 for(let f=0;f<9;f++){const o=observation();o.palettes[0]=f%3;const before=calls,ra=a.draw(ctx,o,p);assert.ok(calls>before);const mid=calls,rb=b.draw(ctx,o,p,{fullyOccluded:true});assert.equal(calls,mid);assert.ok(b.lastOccluded);assert.deepEqual(rb,ra);assert.deepEqual(b.history.map(q=>({historyKey:q.historyKey,o:q.o,rasterUI:q.rasterUI})),a.history.map(q=>({historyKey:q.historyKey,o:q.o,rasterUI:q.rasterUI})));}
 b.backdropOpaque=false;b.draw(ctx,observation(),p,{fullyOccluded:true});assert.equal(b.lastOccluded,false);
 b.backdropOpaque=true;const ui=observation();ui.dialogueRects=[{x:0,y:0,w:8,h:8}];b.drawUI=()=>({dialogueRects:[],dialogueBorderPixels:0,dialogueBorderCoveredPixels:0});b.draw(ctx,ui,p,{fullyOccluded:true});assert.equal(b.lastOccluded,false);
 // Card full and partial bands: verify background and alpha art inputs exactly.
 const r=Object.create(Renderer.prototype);r.ctx=new Canvas().getContext('2d');r.backdrop={};const art=new Data(640,576),back=new Data(640,576);for(let i=0;i<art.data.length;i+=4){art.data.set([37,48,59,i%12?255:0],i);back.data.set([i%251,99,220,255],i);}r.artPixels=im=>im===r.backdrop?back:art;
 r.cards=[{name:'unit',keys:{0:1},indices:new Array(23040).fill(0),art:{}}];const o={actorMask:new Uint8Array(23040),cellKeys:[1]},cp=p.slice();for(let i=0;i<cp.length;i+=4)cp.set([17,29,41,255],i);
 let card=r.prepareCard(cp,o);assert.equal(card.covered,23040);r.drawCard(cp,o,card);const expected=back.data.slice();for(let i=0;i<expected.length;i+=4)for(let ch=0;ch<3;ch++)expected[i+ch]=Math.min(255,expected[i+ch]+cp[ch]);assert.deepEqual(r.cards[0].workBackground.data,expected);assert.equal(r.prepareCard(cp,o),card);
 cp[50*160*4]=18;card=r.prepareCard(cp,o);assert.equal(card.covered,23040-160);assert.equal(card.rows[50],0);o.actorMask[0]=1;assert.equal(r.prepareCard(cp,o),null);
 // Warmup cannot step the emulator; the core object is deliberately absent.
 const warm=Object.create(Renderer.prototype);Object.assign(warm,{title:{},titleClear:{},backdrop:{},impactLate:{},cards:[],maps:{warmup:async()=>{}},artPixels:()=>back});await warm.warmup(()=>{});assert.ok(warm.maps.backdropOpaque);
 // Production flat path passes a Uint8Array: typed .map must not coerce fits.
 r.plateCache=new Map();const plate=r.makePlate(new Uint8Array([17,29,41]));assert.deepEqual(plate.getContext('2d').data.data,expected);
 const pinned=r.plate([0,0,0]);for(let k=1;k<40;k++)r.plate([k,0,0]);assert.equal(r.plateCache.size,16);
 assert.ok(r.prepareFlat(p,{actorMask:new Uint8Array(23040)}));assert.equal(r.prepareFlat(cp,{actorMask:new Uint8Array(23040)}),null);
 // Band materialization must match full-image bytes, including alpha, bounds,
 // independent palette observations, and LRU reuse of only retired surfaces.
 const bands=new MapRenderer(),baseData=new Data(32,32);for(let i=0;i<baseData.data.length;i+=4)baseData.data.set([i%251,(i/4)%249,131,255],i);
 const map={imageNativeSize:8,palettes:Array.from({length:128},(_,i)=>(i%16)*8),cache:new Map(),baseCanvas:new Canvas(),basePixels:baseData,workPixels:new Data(32,32)};
 const bo={mask:new Uint8Array(23040),attrs:new Array(1024).fill(0),scx:0,scy:0,palettes:map.palettes.map(v=>v+8)};
 const full=bands.faded(map,bo).getContext('2d').data.data;
 const strip=bands.fadedStrip(map,bo,3);assert.deepEqual(strip.image.getContext('2d').data.data,full);assert.equal(strip.y,12);
 const row=bands.fadedRow(map,bo,3);assert.deepEqual(row.image.getContext('2d').data.data,full.slice(3*4*32*4,4*4*32*4));
 const outside=bands.fadedRow(map,bo,8);assert.ok(outside.image.getContext('2d').data.data.every(v=>v===0));
 for(let y=0;y<8;y++)bands.paletteBand(map,bo,y,1,'testCache',2);assert.equal(map.testCache.size,2);
 const changed={...bo,palettes:bo.palettes.map(v=>v+8)},newFull=bands.faded(map,changed).getContext('2d').data.data,newStrip=bands.fadedStrip(map,changed,0).image.getContext('2d').data.data;assert.deepEqual(newStrip,newFull);assert.notDeepEqual(newStrip,full);
 // Execute the actual rAF body with a synthetic clock and deliberately slow
 // draws. A 200ms stall must remain as debt and drain without dropping steps.
 const vm=require('node:vm'),app=fs.readFileSync(path.join(root,'app.js'),'utf8'),begin=app.indexOf('function raf(t)'),end=app.indexOf("$('#play').onclick",begin);
 let callback,now=0,steps=0;const timing={paused:false,last:0,acc:0,frames:0,rafProbe:null,performance:{now:()=>now},requestAnimationFrame:fn=>callback=fn,step:()=>{steps++;timing.frames++;now+=8;}};
 vm.createContext(timing);vm.runInContext(app.slice(begin,end),timing);callback(100);now+=200;callback(300);assert.equal(steps,2);assert.ok(timing.acc>160);
 for(let i=0;i<30;i++){now+=16.7;callback(316.7+i*16.7);}const expectedFrames=Math.floor((801-100)/(1000*70224/4194304));assert.equal(steps,expectedFrames);assert.ok(timing.acc<1000*70224/4194304);
 console.log(JSON.stringify({pass:true,checks:['LUT byte equivalence + alpha','decode awaited + request dedup','occlusion history/metadata equality over 9 native observations','opacity and UI guards','card full/partial/native OAM guards','card background bytes','zero-core startup warmup','rAF catch-up budget preserves and drains wall-clock debt','typed RGB plate LUT + bounded LRU','full/strip/row RGBA byte equivalence + bounds + palette updates']},null,2));
})().catch(e=>{console.error(e);process.exitCode=1;});
