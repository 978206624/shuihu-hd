import {loadImage,yieldStartup} from './asset-loader.js';
// M6 full-world plates. Presentation only; memory is never written.
export class RegionRenderer {
 static async create(m,e,painter){const self=new RegionRenderer(m,e,painter),specs=await(await fetch('assets/region1/maps.json')).json();self.maps=new Map();for(const s of specs){if(!s.artReady)continue;const map={...s,cache:new Map(),image:await loadImage(s.image),positions:new Map()};for(let k=0;k<s.cellKeys.length;k++){const key=s.cellKeys[k];if(!map.positions.has(key))map.positions.set(key,[]);map.positions.get(key).push(k);}self.maps.set(s.id,map);}return self;}
 constructor(m,e,painter){this.m=m;this.e=e;this.painter=painter;this.last=null;this.failure=null;}
 async warmup(progress){const upload=document.createElement('canvas');upload.width=640;upload.height=576;const g=upload.getContext('2d');for(const map of this.maps.values()){progress('准备整图 '+map.name);const base=this.painter.prepareBase(map);map.opaque=true;for(let i=3;i<base.data.length;i+=4)if(base.data[i]!==255){map.opaque=false;break;}
 // Prepare the immutable texel view and exercise Canvas upload/copy before
 // ready. No palette/history entries or emulator frames are manufactured.
 map.base32=new Uint32Array(base.data.buffer,base.data.byteOffset,base.data.length/4);g.clearRect(0,0,640,576);g.drawImage(map.baseCanvas,0,0,640,576,0,0,640,576);g.getImageData(0,0,1,1);await yieldStartup();}this.preparePixelOutput();this.prepareIdentityPlan();}
 read(a){return this.m._emulator_read_mem(this.e,a);}
 id(){return [this.read(0xff9a),this.read(0xff9b)].map(v=>v.toString(16).padStart(2,'0')).join('-');}
 cells(o){const out=[];for(let y=0;y<144;y+=8)for(let x=0;x<160;x+=8){const sx=Math.min(159,x+3),sy=Math.min(143,y+3);if(o.mask[sy*160+sx]&&!o.actorMask[sy*160+sx])continue;const rx=Math.floor((sx+(o.scx&7))/8),ry=Math.floor((sy+(o.scy&7))/8),k=((((sy+o.scy)&255)>>3)*32)+(((sx+o.scx)&255)>>3);out.push({rx,ry,k,key:o.cellKeys[k]});}return out;}
 agreement(map,o,cells,x,y){if(x<0||y<0||x+160>map.width||y+144>map.height)return -1;const tx=Math.floor(x/8),ty=Math.floor(y/8);let good=0;for(const a of cells){const k=(ty+a.ry)*map.widthTiles+tx+a.rx;if(map.cellKeys[k]===a.key||(map.tiles[k]===o.tiles[a.k]&&map.attrs[k]===o.attrs[a.k]))good++;}return good/Math.max(1,cells.length);}
 locate(map,o){const cells=this.cells(o);if(cells.length<30)return null;const dx=o.scx&7,dy=o.scy&7,prior=this.last;
 if(prior?.id===map.id&&o.ticks-prior.ticks>=0&&o.ticks-prior.ticks<=70240){const delta=(a,b)=>((a-b+128)&255)-128,x=prior.x+delta(o.scx,prior.scx),y=prior.y+delta(o.scy,prior.scy),score=this.agreement(map,o,cells,x,y);if(score>=.85)return {x,y,score,evidence:'continuous-camera+native-geometry'};}
 // The loader origin is only a hypothesis, always validated against actual VRAM.
 const hx=this.read(0xff96)*32+o.scx,hy=this.read(0xff97)*32+o.scy,hs=this.agreement(map,o,cells,hx,hy);if(hs>=.85)return {x:hx,y:hy,score:hs,evidence:'loader-origin+native-geometry'};
 const anchors=cells.filter(a=>map.positions.has(a.key)).sort((a,b)=>map.positions.get(a.key).length-map.positions.get(b.key).length).slice(0,8),candidates=new Set();for(const a of anchors)for(const k of map.positions.get(a.key)){const x=(k%map.widthTiles-a.rx)*8+dx,y=(Math.floor(k/map.widthTiles)-a.ry)*8+dy;if(x>=0&&y>=0&&x+160<=map.width&&y+144<=map.height)candidates.add(x+map.width*y);}
 let best=null,ties=0;for(const v of candidates){const x=v%map.width,y=Math.floor(v/map.width),score=this.agreement(map,o,cells,x,y);if(score<.85)continue;if(!best||score>best.score+.00001){best={x,y,score,evidence:'full-map-native-key-search'};ties=1;}else if(Math.abs(score-best.score)<.00001)ties++;}return ties===1?best:null;}
 exactAgreement(map,o,origin){const cells=this.cells(o),tx=Math.floor(origin.x/8),ty=Math.floor(origin.y/8);let good=0;for(const a of cells)if(map.cellKeys[(ty+a.ry)*map.widthTiles+tx+a.rx]===a.key)good++;return good/Math.max(1,cells.length);}
 transitionOrigin(o,requested){if(!requested)return null;let best=null,ambiguous=false;for(const map of this.maps.values()){if(map===requested)continue;const candidate=this.locate(map,o);if(!candidate)continue;const score=this.exactAgreement(map,o,candidate);if(score<.95)continue;if(!best||score>best.origin.score+.00001){best={map,origin:{...candidate,score,evidence:'unique-transition-native-geometry'}};ambiguous=false;}else if(Math.abs(score-best.origin.score)<.00001)ambiguous=true;}return best&&!ambiguous?best:null;}
 rawGeometry(q,x,y){const wx=q.origin.x+x,wy=q.origin.y+y,k=Math.floor(wy/8)*q.map.widthTiles+Math.floor(wx/8),vk=((((y+q.o.scy)&255)>>3)*32)+(((x+q.o.scx)&255)>>3);return q.map.cellKeys[k]===q.o.cellKeys[vk]||(q.map.tiles[k]===q.o.tiles[vk]&&q.map.attrs[k]===q.o.attrs[vk]);}
 prepareGeometry(q){const cols=Math.ceil((160+(q.o.scx&7))/8),rows=Math.ceil((144+(q.o.scy&7))/8);q.geometryCells=new Uint8Array(cols*rows);q.geometryX=new Uint8Array(160);q.geometryY=new Uint16Array(144);q.sampleX=new Uint16Array(160);q.sampleY=new Uint32Array(144);for(let x=0;x<160;x++){q.geometryX[x]=(x+(q.o.scx&7))>>3;q.sampleX[x]=((x+q.o.scx)&255)*4;}for(let y=0;y<144;y++){q.geometryY[y]=((y+(q.o.scy&7))>>3)*cols;q.sampleY[y]=((y+q.o.scy)&255)*1024;}for(let y=0;y<rows;y++)for(let x=0;x<cols;x++)q.geometryCells[y*cols+x]=+this.rawGeometry(q,Math.max(0,x*8-(q.o.scx&7)),Math.max(0,y*8-(q.o.scy&7)));return q;}
 geometry(q,x,y){return q.geometryCells[q.geometryY[y]+q.geometryX[x]];}
 equal(q,x,y,p){const j=q.sampleY[y]+q.sampleX[x],i=(y*160+x)*4;return p[i]===q.o.bg[j]&&p[i+1]===q.o.bg[j+1]&&p[i+2]===q.o.bg[j+2];}
 recoverRow(q,y,current,p){const seen=this.seenColors??=new Int32Array(32);seen.fill(-1);let samples=0;for(let x=0;x<160;x++){const i=y*160+x;if(current.mask[i]||q.o.mask[i])continue;if(!this.geometry(q,x,y))return null;const mx=(x+q.o.scx)&255,my=(y+q.o.scy)&255,k=(my>>3)*32+(mx>>3),pi=(q.o.attrs[k]&7)*4+q.o.indices[my*256+mx],v=p[i*4]|(p[i*4+1]<<8)|(p[i*4+2]<<16);if(seen[pi]!==-1&&seen[pi]!==v)return null;seen[pi]=v;samples++;}if(samples<24)return null;
 // Evidence above is unchanged. Cache only exact complete 32-color mappings
 // within this immutable source. Hash collisions are misses, never matches.
 // Numeric keys avoid constructing 32-number strings for every recovered row.
 let hash=2166136261;for(let i=0;i<32;i++)hash=Math.imul(hash^seen[i],16777619);const cache=q.recoveredRows??=new Map(),entry=cache.get(hash);let same=!!entry;
 if(entry)for(let i=0;i<32;i++)if(entry.colors[i]!==seen[i]){same=false;break;}if(same)return entry.variant;
 const palettes=q.o.palettes.slice();for(let pi=0;pi<32;pi++)if(seen[pi]!==-1){const v=seen[pi];palettes[pi*4]=v&255;palettes[pi*4+1]=(v>>8)&255;palettes[pi*4+2]=v>>16;}const variant={...q.o,palettes};if(cache.size>=64&&!cache.has(hash))cache.delete(cache.keys().next().value);cache.set(hash,{colors:seen.slice(),variant});return variant;}
 // Same certified sources and descriptor order as the legacy runs. Plan only
 // disjoint identity rectangles. Reuse fixed work arrays instead of allocating
 // two Maps and rectangle objects on each of 144 scanlines on every frame.
 prepareIdentityPlan(){return this.identityPlan??={code:new Int16Array(512),x:new Int16Array(512),y:new Int16Array(512),w:new Int16Array(512),h:new Int16Array(512),previous:new Int16Array(160),next:new Int16Array(160),seen:new Uint8Array(128),ordinary:[],count:0};}
 paintSources(ctx,candidates,rowVariants,sources){
 if(candidates.some(q=>q.map.opaque!==true)){this.paintLegacy(ctx,candidates,rowVariants,sources);return;}
 const plan=this.prepareIdentityPlan(),ordinary=plan.ordinary;ordinary.length=0;plan.count=0;plan.previous.fill(-1);let runs=0;
 for(let y=0;y<144;y++){plan.next.fill(-1);plan.seen.fill(0);for(let x=0;x<160;){const code=sources[y*160+x];if(code<0){x++;continue;}let end=x+1;while(end<160&&sources[y*160+end]===code)end++;
 if(++runs>512){this.paintPixels(ctx,candidates,rowVariants,sources);return;}
 if(!plan.seen[code]){plan.seen[code]=1;const q=candidates[code%64];let d=code<64?ordinary[code]:null;if(!d){d=code<64?this.painter.fullDescriptor(q.map,q.o):this.painter.paletteDescriptor(q.map,rowVariants[code%64][y]);if(code<64)ordinary[code]=d;}if(!d.identity){this.paintPixels(ctx,candidates,rowVariants,sources);return;}}
 let r=plan.previous[x];if(r>=0&&plan.code[r]===code&&plan.w[r]===end-x)plan.h[r]++;else{r=plan.count++;plan.code[r]=code;plan.x[r]=x;plan.y[r]=y;plan.w[r]=end-x;plan.h[r]=1;}plan.next[x]=r;x=end;
 }const old=plan.previous;plan.previous=plan.next;plan.next=old;}
 this.paintIdentity(ctx,candidates,sources,plan);
 }
 paintIdentity(ctx,candidates,sources,plan=this.identityPlan){ctx.imageSmoothingEnabled=false;
 for(let r=0;r<plan.count;r++){const q=candidates[plan.code[r]%64],x=plan.x[r]*4,y=plan.y[r]*4,w=plan.w[r]*4,h=plan.h[r]*4;ctx.drawImage(q.map.baseCanvas,q.origin.x*4+x,q.origin.y*4+y,w,h,x,y,w,h);}
 }
 preparePixelOutput(){this.pixelOutput??=new ImageData(640,576);this.pixelOutput32??=new Uint32Array(this.pixelOutput.data.buffer);const canvas=this.pixelCanvas??=document.createElement('canvas');if(canvas.width!==640||canvas.height!==576){canvas.width=640;canvas.height=576;}return canvas;}
 paintLegacy(ctx,candidates,rowVariants,sources){ctx.imageSmoothingEnabled=false;for(let y=0;y<144;y++)for(let x=0;x<160;){const code=sources[y*160+x];if(code<0){x++;continue;}let end=x+1;while(end<160&&sources[y*160+end]===code)end++;const q=candidates[code%64],wy=q.origin.y+y,wx=q.origin.x+x,variant=code>=64?rowVariants[code%64][y]:null,band=variant?this.painter.fadedRow(q.map,variant,wy):this.painter.fadedStrip(q.map,q.o,wy);ctx.drawImage(band.image,wx*4,band.y,(end-x)*4,4,x*4,y*4,(end-x)*4,4);x=end;}}
 paintPixels(ctx,candidates,rowVariants,sources){
 if(candidates.some(q=>q.map.opaque!==true)||new Uint8Array(new Uint32Array([1]).buffer)[0]!==1){this.paintLegacy(ctx,candidates,rowVariants,sources);return;}
 const canvas=this.preparePixelOutput(),dest=this.pixelOutput32;dest.fill(0);const ordinary=this.pixelOrdinary??=[];ordinary.length=0;
 // Resolve the same descriptor once per certified run, then walk contiguous
 // authored texels. No per-native-pixel reference objects or nested 4x4 loop.
 for(let y=0;y<144;y++)for(let x=0;x<160;){const code=sources[y*160+x];if(code<0){x++;continue;}let end=x+1;while(end<160&&sources[y*160+end]===code)end++;
 const q=candidates[code%64];let d=code<64?ordinary[code]:null;if(!d){d=code<64?this.painter.fullDescriptor(q.map,q.o):this.painter.paletteDescriptor(q.map,rowVariants[code%64][y]);if(code<64)ordinary[code]=d;}
 const base=this.painter.prepareBase(q.map),src=q.map.base32??=new Uint32Array(base.data.buffer,base.data.byteOffset,base.data.length/4),sx=(q.origin.x+x)*4,sy=(q.origin.y+y)*4,width=(end-x)*4,t=d.tables;
 if(t){const red=t[0],green=t[1],blue=t[2];for(let j=0;j<4;j++){let si=(sy+j)*base.width+sx,di=(y*4+j)*640+x*4;for(let k=0;k<width;k++){const v=src[si++];dest[di++]=red[v&255]|(green[(v>>>8)&255]<<8)|(blue[(v>>>16)&255]<<16)|(v&0xff000000);}}}
 else for(let j=0;j<4;j++){let si=(sy+j)*base.width+sx,di=(y*4+j)*640+x*4;for(let k=0;k<width;k++)dest[di++]=src[si++];}x=end;
 }
 canvas.getContext('2d').putImageData(this.pixelOutput,0,0);ctx.imageSmoothingEnabled=false;ctx.drawImage(canvas,0,0);
 }

 draw(ctx,o,p,native){if(!o||this.read(0xd0fa)!==0){this.last=null;this.history=[];return null;}const id=this.id(),requested=this.maps.get(id);this.history??=[];if(this.lastTick!==undefined&&(o.ticks<this.lastTick||o.ticks-this.lastTick>70240)){this.history=[];this.last=null;}this.lastTick=o.ticks;let map=requested,origin=map?this.locate(map,o):null;
 // A warp updates the ROM map ID before the old native screen has vanished.
 // Reuse the prior authored map only while its CURRENT VRAM geometry verifies.
 if(!origin&&this.last){const old=this.maps.get(this.last.id);if(old&&old!==map){const candidate=this.locate(old,o);if(candidate){map=old;origin=candidate;}}}
 // Native warps can clear the previous camera before the old raster fades.
 // A different authored map is admitted only with unique >=95% CURRENT
 // VRAM evidence; per-cell geometry and per-pixel RGB checks still apply.
 if(!origin){const fallback=this.transitionOrigin(o,requested);if(fallback){map=fallback.map;origin=fallback.origin;}}
 const now=origin?this.prepareGeometry({map,origin,o}):null;if(now){this.last={id:map.id,...origin,scx:o.scx,scy:o.scy,ticks:o.ticks};this.failure=null;}else this.failure={id,reason:'ambiguous/unmatched native world camera'};
 const candidates=now?[now,...this.history]:[...this.history];if(!candidates.length)return null;const sources=this.sources??=new Int16Array(23040);sources.fill(-1);let eligible=0,covered=0,recovered=0;const rowVariants=candidates.map(()=>[]),gapTiles=this.painter.auditEnabled?new Map():null;
 for(let y=0;y<144;y++){let rowGaps=0;for(let x=0;x<160;x++){const i=y*160+x;if(o.mask[i])continue;eligible++;for(let n=0;n<candidates.length;n++){const q=candidates[n];if(q.o.mask[i]||!this.geometry(q,x,y)||!this.equal(q,x,y,p))continue;sources[i]=n;covered++;if(n)recovered++;break;}if(sources[i]<0)rowGaps++;}
 if(rowGaps)for(let n=0;n<candidates.length;n++){const q=candidates[n],variant=this.recoverRow(q,y,o,p);if(!variant)continue;rowVariants[n][y]=variant;for(let x=0;x<160;x++){const i=y*160+x;if(o.mask[i]||sources[i]>=0||q.o.mask[i]||!this.geometry(q,x,y))continue;sources[i]=n+64;covered++;recovered++;rowGaps--;}if(!rowGaps)break;}}
 this.paintSources(ctx,candidates,rowVariants,sources);
 if(gapTiles)for(let y=0;y<144;y++)for(let x=0;x<160;x++){const i=y*160+x;if(o.mask[i]||sources[i]>=0)continue;const k=((((y+o.scy)&255)>>3)*32)+(((x+o.scx)&255)>>3),key=k+':'+o.cellKeys[k],reason=now&&!this.geometry(now,x,y)?'native geometry changed':'native raster/foreground not certified',g=gapTiles.get(key)||{tile:k,signature:o.cellKeys[k],pixels:0,reason};g.pixels++;gapTiles.set(key,g);}
 const fullDialogue=o.dialogueRects.filter(r=>r.w===160&&r.h>=56),ui=this.painter.drawUI(ctx,{...o,dialogueRects:fullDialogue},p),principal=now||candidates[0];if(now){this.history.unshift(now);if(this.history.length>6)this.history.pop();}else if(this.history.length&&o.ticks-this.history[0].o.ticks>70224*6)this.history=[];
 return {scene:'region1-'+principal.map.id,mapId:principal.map.id,mapName:principal.map.name,worldCamera:[principal.origin.x,principal.origin.y],cameraEvidence:principal.origin.evidence,matchedCells:Math.round(principal.origin.score*360),visibleCells:360,preservedPixels:23040-covered,backgroundPixels:covered,eligiblePixels:eligible,unsupportedPixels:eligible-covered,uncoveredTiles:gapTiles?[...gapTiles.values()]:[],rasterMismatchPixels:eligible-covered,rasterRecoveredPixels:recovered,dialogueRects:o.dialogueRects,dialogueBorderPixels:ui.dialogueBorderPixels,dialogueBorderCoveredPixels:ui.dialogueBorderCoveredPixels,dialogueFrameCovered:ui.dialogueFrameCovered,fullMapDimensions:[principal.map.width,principal.map.height]};}
}
