import {RegionRenderer} from './region-renderer.js';
import {MapRenderer} from './map-renderer.js';
import {Observer} from './observer.js';
import {loadImage,setAssetProgress,yieldStartup,colorTables,recolor} from './asset-loader.js';
// Presentation only: no writes to emulator memory or registers.
export function tileKey(p,x,y){let s='';for(let j=0;j<8;j++)for(let i=0;i<8;i++){const k=((y+j)*160+x+i)*4;s+=p[k].toString(16).padStart(2,'0')+p[k+1].toString(16).padStart(2,'0')+p[k+2].toString(16).padStart(2,'0');}return s;}
export class Renderer{
 static async create(c,m,e,progress=()=>{}){
 const r=new Renderer(c,m,e);setAssetProgress((done,total)=>progress(`图像解码 ${done}/${total}`));
 const json=async path=>(await fetch(path)).json();
 const [specs,cards,titleNative,mapping,signatures,impactKeys]=await Promise.all(['assets/maps/m3_signatures.json','assets/maps/cards_m4.json','assets/title_native.json','assets/forest/mapping.json','assets/signatures.json','assets/maps/impact_keys.json'].map(json));
 r.titleNative=titleNative;r.mapping=mapping;r.signatures=signatures;
 // Start all requests together; onload alone does not guarantee decoded pixels.
 const paths=[...new Set([...specs.map(s=>s.image),...cards.map(s=>s.image),'assets/title_hd.png','assets/title_clear_hd.png','assets/maps/dialogue_hd.png','assets/maps/impact_hd.png','assets/maps/impact_late_hd.png','assets/maps/intertitle_hd.png',...(mapping.tiles.length?['assets/forest/atlas_hd.png']:[])])];
 await Promise.all(paths.map(loadImage));
 r.maps=await MapRenderer.create(specs);r.title=await loadImage('assets/title_hd.png');r.titleClear=await loadImage('assets/title_clear_hd.png');
 r.region=await RegionRenderer.create(m,e,r.maps);await r.loadM4(cards,impactKeys);
 if(mapping.tiles.length){const a=await loadImage('assets/forest/atlas_hd.png');if(a.width!==mapping.columns*mapping.tileSize||a.height!==mapping.rows*mapping.tileSize)throw Error('atlas dimensions mismatch');r.atlas=a;}
 await r.warmup(progress);return r;
 }
 async warmup(progress){
 const art=[this.title,this.titleClear,this.backdrop,this.impactLate,...this.cards.map(c=>c.art)];
 for(let i=0;i<art.length;i++){progress(`准备高清画布 ${i+1}/${art.length}`);this.artPixels(art[i]);await yieldStartup();}
 this.maps.backdropOpaque=this.artPixels(this.backdrop).data.every((v,i)=>i%4!==3||v===255);
 await this.maps.warmup(progress);await this.region.warmup(progress);
 // Known CGB neutral fade shades, rasterized without advancing the emulator.
 this.plateWork??=new ImageData(640,576);this.pinnedPlates??=new Map();
 for(let shade=0;shade<=248;shade+=8){progress(`准备转场底图 ${shade/8+1}/32`);const rgb=[shade,shade,shade];this.pinnedPlates.set(rgb.join(','),this.makePlate(rgb));await yieldStartup();}
 this.titleFadeData=new ImageData(640,576);
 this.impactLatePixels=this.artPixels(this.impactLate);this.impactLateOutput=new ImageData(640,576);
 this.impactLateLayer=document.createElement('canvas');this.impactLateLayer.width=640;this.impactLateLayer.height=576;
 for(const card of this.cards){card.layer=document.createElement('canvas');card.backLayer=document.createElement('canvas');card.layer.width=card.backLayer.width=640;card.layer.height=card.backLayer.height=576;card.workArt=new ImageData(640,576);card.workBackground=new ImageData(640,576);await yieldStartup();}
 // Exercise upload/copy paths on disposable surfaces; never advance emulator.
 const scratch=document.createElement('canvas');scratch.width=640;scratch.height=576;
 const g=scratch.getContext('2d');for(const a of [...art,this.impact,this.maps.dialogue,this.atlas].filter(Boolean)){g.clearRect(0,0,640,576);g.drawImage(a,0,0,640,576);g.getImageData(0,0,1,1);await yieldStartup();}
 g.font='bold 30px serif';g.fillText('▸ 重新开始 继续游戏',0,40);g.getImageData(0,0,1,1);
 progress('高清资源准备完成');await yieldStartup();
 }
 constructor(c,m,e){this.observer=new Observer(m,e);this.c=c;this.ctx=c.getContext('2d');this.m=m;this.e=e;this.raw=document.createElement('canvas');this.raw.width=160;this.raw.height=144;this.rc=this.raw.getContext('2d');this.nativeData=new ImageData(160,144);}
 pixels(){return this.m.HEAPU8.slice(this.m._get_frame_buffer_ptr(this.e),this.m._get_frame_buffer_ptr(this.e)+160*144*4);}
 draw(hd){const p=this.pixels();this.observation=this.observer.sample(p);this.nativeData.data.set(p);this.rc.putImageData(this.nativeData,0,0);const c=this.ctx;c.imageSmoothingEnabled=false;const fallback=hd?'nearest-original-gap':'original';c.drawImage(this.raw,0,0,640,576);
 const title=this.signatures.title?.length>=4&&this.signatures.title.every(t=>tileKey(p,t.x,t.y)===t.key)||false;
 const titleFade=!title&&this.observation&&Object.entries(this.titleNative.cells).every(([k,v])=>this.observation.cellKeys[k]===v);let titleFadePixels=0;
 let matches=0,known=0;const scx=this.m._emulator_read_mem(this.e,0xff43),scy=this.m._emulator_read_mem(this.e,0xff42);
 let titleSelection=null;
 if(title){const score=y=>{let n=0;for(let j=y;j<y+10;j++)for(let x=45;x<56;x++){const i=(j*160+x)*4;if(p[i]>150&&p[i+1]>100&&p[i+2]<80)n++;}return n;};titleSelection=score(103)>score(87)?1:0;}
 if(hd&&title){c.drawImage(this.title,0,0,640,576);c.fillStyle='#142a25';c.fillRect(178,324,284,164);c.strokeStyle='#c5a76a';c.lineWidth=2;c.strokeRect(182,328,276,156);c.font='bold 30px serif';c.textBaseline='middle';for(let i=0;i<2;i++){c.fillStyle=i===titleSelection?'#ffe2a0':'#b7c5b2';c.fillText((i===titleSelection?'▸ ':'  ')+['重新开始','继续游戏'][i],208,382+i*60);}}
 if(hd&&titleFade)titleFadePixels=this.drawTitleFade(p);
 const preparedCard=hd&&!title&&!titleFade?this.prepareCard(p,this.observation):null;
 const flat=hd&&!title&&!titleFade&&!preparedCard?this.prepareFlat(p,this.observation):null;
 // Preparation renders special plates to a private surface, so no transient
 // map pixels can leak into a cached full-screen presentation.
 const impact=hd&&!title&&!titleFade&&!preparedCard&&!flat?this.prepareImpact(p,this.observation):null;
 const fullyOccluded=preparedCard?.covered===23040||!!flat||!!impact;
 let mapResult=null;if(hd&&!title&&!titleFade){if(!fullyOccluded)mapResult=this.region.draw(c,this.observation,p,this.raw);if(!mapResult)mapResult=this.maps.draw(c,this.observation,p,{fullyOccluded});}
 if(hd&&!title&&!titleFade){const card=this.drawCard(p,this.observation,preparedCard);if(card)mapResult=card;else if(flat)mapResult=this.drawFlat(p,this.observation,flat);else if(impact){c.drawImage(impact.image,0,0);mapResult=impact.result;}}

 if(mapResult){matches=mapResult.matchedCells;known=matches;}
 const eligible=this.observation?this.observation.mask.reduce((n,x)=>n+!x,0):null;
 const coverage={eligibleBackgroundPixels:title||titleFade?23040:mapResult?.eligiblePixels??eligible,gptBackgroundPixels:title&&hd?23040:titleFade?titleFadePixels:mapResult?.backgroundPixels||0,uncoveredBackgroundPixels:title&&hd?0:titleFade?23040-titleFadePixels:eligible===null?null:(mapResult?.eligiblePixels??eligible)-(mapResult?.backgroundPixels||0),observerValid:!!this.observation,gap:!title&&(!mapResult||mapResult.backgroundPixels<eligible),dialogueFrameCovered:title||titleFade||mapResult?.dialogueFrameCovered||false};
 this.meta={coverage,scene:title?'title':titleFade?'title-fade':mapResult?.scene||'unsupported',mapResult,titleRedrawn:hd&&title,titleSelection,knownBackgroundCells:known,forestTilesRedrawn:matches,forestAtlasAvailable:!!this.atlas,fallback:hd?fallback:'original',matching:'palette-independent decoded tile geometry; native CGB palettes; validated read-only VRAM/OAM; exact original gap pixels'};
 }
 // Immutable source art is rasterized once with the original canvas scaling.
 artPixels(image,w=640,h=576){this.artCache??=new WeakMap();let a=this.artCache.get(image);if(!a){const c=document.createElement('canvas');c.width=w;c.height=h;const g=c.getContext('2d',{willReadFrequently:true});g.drawImage(image,0,0,w,h);a=g.getImageData(0,0,w,h);this.artCache.set(image,a);}return a;}
 rowRuns(rows,draw){for(let y=0;y<144;){if(!rows[y]){y++;continue;}let end=y+1;while(end<144&&rows[end])end++;draw(y,end);y=end;}}
 drawTitleFade(p){const canvas=this.titleFadeLayer??=document.createElement('canvas');if(canvas.width!==640||canvas.height!==576){canvas.width=640;canvas.height=576;}const g=canvas.getContext('2d');const art=this.titleFadeData??=new ImageData(640,576),rows=this.titleRows??=new Uint8Array(144);art.data.set(this.artPixels(this.titleClear).data);rows.fill(0);let covered=0;for(let y=0;y<144;y++){let chosen=null;for(const ref of this.titleNative.fadeReferences){const pairs=new Map();let valid=true;for(let x=0;x<160;x++){const j=y*256+x,k=(ref.attrs[(y>>3)*32+(x>>3)]&7)*4+ref.indices[j],rgb=p.slice((y*160+x)*4,(y*160+x)*4+3);if(pairs.has(k)&&pairs.get(k).some((v,ch)=>v!==rgb[ch])){valid=false;break;}pairs.set(k,rgb);}if(valid){chosen={ref,pairs};break;}}if(!chosen)continue;
 const {ref,pairs}=chosen;const shifts=[];for(let ch=0;ch<3;ch++){const diffs=[...pairs].filter(([k,v])=>v[ch]>0&&v[ch]<248).map(([k,v])=>v[ch]-this.titleNative.fadeReferences[0].palettes[k*4+ch]);diffs.sort((a,b)=>a-b);const shift=diffs.length?diffs[Math.floor(diffs.length/2)]:p[y*160*4+ch]===248?248:0;shifts.push([...pairs].every(([k,v])=>Math.max(0,Math.min(248,this.titleNative.fadeReferences[0].palettes[k*4+ch]+shift))===v[ch])?shift:null);}
 if(shifts.every(v=>v!==null)){for(let yy=y*4;yy<y*4+4;yy++)for(let xx=0;xx<640;xx++)for(let ch=0;ch<3;ch++){const k=(yy*640+xx)*4+ch;art.data[k]=Math.max(0,Math.min(255,art.data[k]+shifts[ch]));}covered+=160;rows[y]=1;continue;}
 for(let x0=0;x0<160;x0+=8){const pal=ref.attrs[(y>>3)*32+(x0>>3)]&7,fit=[];for(let ch=0;ch<3;ch++){let n=0,sx=0,sy=0,sxx=0,sxy=0;for(let i=0;i<4;i++){const rgb=pairs.get(pal*4+i);if(!rgb)continue;const a=this.titleNative.fadeReferences[0].palettes[pal*16+i*4+ch],b=rgb[ch];n++;sx+=a;sy+=b;sxx+=a*a;sxy+=a*b;}const den=n*sxx-sx*sx,a=den?(n*sxy-sx*sy)/den:0,b=n?(sy-a*sx)/n:0;fit.push([a,b]);}for(let yy=y*4;yy<y*4+4;yy++)for(let xx=x0*4;xx<x0*4+32;xx++)for(let ch=0;ch<3;ch++){const k=(yy*640+xx)*4+ch;art.data[k]=Math.max(0,Math.min(255,fit[ch][0]*art.data[k]+fit[ch][1]));}}covered+=160;rows[y]=1;}g.putImageData(art,0,0);this.rowRuns(rows,(y,end)=>this.ctx.drawImage(canvas,0,y*4,640,(end-y)*4,0,y*4,640,(end-y)*4));return covered;}

 async loadM4(cards,impactKeys){this.cards=cards;await Promise.all(this.cards.map(async card=>{card.art=await loadImage(card.image);}));this.impact=await loadImage('assets/maps/impact_hd.png');this.impactLate=await loadImage('assets/maps/impact_late_hd.png');
 // Exact visible BG layout from probe_5411; later raster probes share these keys.
 this.impactLateCells=[4025657951,4025657951,4025657951,347844006,3837066731,2840118021,3925205630,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,3967952836,132494238,2965020959,171830797,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,2355378462,2965020959,2965020959,2674152443,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,2687788817,1274734900,717210748,4025657951,4025657951,4025657951,4025657951,3754500572,3934147985,1766014731,329089193,4025657951,4025657951,4025657951,674723435,3030941795,718764237,4025657951,4025657951,4025657951,1848204852,2965020959,3093355165,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,2459946135,2636930376,2965020959,3406588598,292683610,4025657951,4025657951,1284498416,4287273700,1769944728,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,1447176294,4096741684,4025657951,312510761,2965020959,2965020959,2965020959,381909467,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,1764324095,8507365,4025657951,3941865557,812532335,2965020959,853563034,3503579598,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,2201329469,923607830,3714120078,3281725606,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951,4025657951];this.backdrop=await loadImage('assets/maps/intertitle_hd.png');this.impactKeys=new Set(impactKeys);this.plateCache=new Map();}
 makePlate(rgb,canvas=null){const c=canvas||document.createElement('canvas');if(c.width!==640||c.height!==576){c.width=640;c.height=576;}const d=this.plateWork??=new ImageData(640,576);
 recolor(this.artPixels(this.backdrop).data,d.data,colorTables(Array.from(rgb,v=>[1,v])));c.getContext('2d').putImageData(d,0,0);return c;}
 plate(rgb){const key=rgb.join(',');const pinned=this.pinnedPlates?.get(key);if(pinned)return pinned;
 this.plateCache??=new Map();let c=this.plateCache.get(key);if(c){this.plateCache.delete(key);this.plateCache.set(key,c);return c;}
 // A returned plate is consumed immediately by drawImage; cache values never
 // enter map/history/UI snapshots. Recycling one LRU surface cannot alias them.
 if(this.plateCache.size>=16){const oldest=this.plateCache.keys().next().value;c=this.plateCache.get(oldest);this.plateCache.delete(oldest);}
 c=this.makePlate(rgb,c);this.plateCache.set(key,c);return c;}
 prepareFlat(p,o){if(!o||o.actorMask.some(Boolean))return null;for(let i=4;i<p.length;i+=4)if(p[i]!==p[0]||p[i+1]!==p[1]||p[i+2]!==p[2])return null;return p.subarray(0,3);}
 drawFlat(p,o,flat=this.prepareFlat(p,o)){if(!flat)return null;
 // Uniform displayed framebuffer, exact same validation as the old drawFlat.
 this.ctx.drawImage(this.plate(flat),0,0);return {scene:'verified-flat-transition',eligiblePixels:23040,backgroundPixels:23040,unsupportedPixels:0,dialogueFrameCovered:true,uncoveredTiles:[]};}
 prepareImpact(p,o){const saved=this.impactPresentation;
 if(saved&&o&&!o.scx&&!o.scy&&!o.dialogueRects.length&&this.sameBytes(saved.p,p)&&this.sameBytes(saved.keys,o.cellKeys)&&this.sameBytes(saved.attrs,o.attrs)&&this.sameBytes(saved.indices,o.indices)&&this.sameBytes(saved.actors,o.actorMask))return saved;
 if(!o||o.scx||o.scy||o.dialogueRects.length)return null;for(let y=0;y<18;y++)for(let x=0;x<20;x++){const k=y*32+x;if(o.attrs[k]!==0||!this.impactKeys.has(o.cellKeys[k]))return null;}
 this.impactPresentation=null;const canvas=this.impactSurface??=document.createElement('canvas');if(canvas.width!==640||canvas.height!==576){canvas.width=640;canvas.height=576;}
 const previous=this.ctx;this.ctx=canvas.getContext('2d');this.ctx.clearRect(0,0,640,576);let result;try{result=this.renderImpact(p,o);}finally{this.ctx=previous;}
 if(!result)return null;
 // Both impact branches prove no OAM and write every pixel: either an opaque
 // plate plus effect, or late-impact RGBA whose alpha is set to 255 everywhere.
 const state=saved||{p:new Uint8Array(p.length),keys:new Array(o.cellKeys.length),attrs:new Array(o.attrs.length),indices:new Uint8Array(o.indices.length),actors:new Uint8Array(o.actorMask.length)};
 state.image=canvas;state.result=result;state.p.set(p);for(let i=0;i<o.cellKeys.length;i++)state.keys[i]=o.cellKeys[i];for(let i=0;i<o.attrs.length;i++)state.attrs[i]=o.attrs[i];state.indices.set(o.indices);state.actors.set(o.actorMask);this.impactPresentation=state;return state;}
 sameBytes(a,b){if(!a||!b||a.length!==b.length)return false;for(let i=0;i<a.length;i++)if(a[i]!==b[i])return false;return true;}
 drawImpact(p,o){const impact=this.prepareImpact(p,o);if(!impact)return null;this.ctx.drawImage(impact.image,0,0);return impact.result;}
 renderImpact(p,o){if(!o||o.scx||o.scy||o.dialogueRects.length)return null;for(let y=0;y<18;y++)for(let x=0;x<20;x++){const k=y*32+x;if(o.attrs[k]!==0||!this.impactKeys.has(o.cellKeys[k]))return null;}
 if(this.impactLateCells.every((key,i)=>o.cellKeys[Math.floor(i/20)*32+i%20]===key)){const late=this.drawLateImpact(p,o);if(late)return late;}
 const red=this.impactRed??=new Uint8Array(23040),seen=this.impactSeen??=new Uint8Array(23040);red.fill(0);seen.fill(0);let count=0;for(let i=0;i<23040;i++){if(o.actorMask[i])return null;const r=p[i*4],g=p[i*4+1],b=p[i*4+2];if(r===0&&g===0&&b===0)continue;if(r>0&&g===0&&b===0){red[i]=1;count++;}else return null;}
 const components=[];for(let i=0;i<23040;i++)if(red[i]&&!seen[i]){const stack=[i],points=[];seen[i]=1;let left=160,right=0,top=144,bottom=0;while(stack.length){const j=stack.pop(),x=j%160,y=Math.floor(j/160);points.push(j);left=Math.min(left,x);right=Math.max(right,x);top=Math.min(top,y);bottom=Math.max(bottom,y);for(const k of [j-160,j+160,...(x?[j-1]:[]),...(x<159?[j+1]:[])])if(k>=0&&k<23040&&red[k]&&!seen[k]){seen[k]=1;stack.push(k);}}components.push({points,left,right,top,bottom});}
 this.ctx.drawImage(this.plate([0,0,0]),0,0);const layer=this.impactEffect??=document.createElement('canvas');if(layer.width!==640||layer.height!==576){layer.width=640;layer.height=576;}const g=layer.getContext('2d');g.clearRect(0,0,640,576);for(const a of components){const w=a.right-a.left+1,h=a.bottom-a.top+1;g.drawImage(this.impact,420,420,400,400,a.left*4,a.top*4,w*4,h*4);}const d=g.getImageData(0,0,640,576);for(let y=0;y<576;y++)for(let x=0;x<640;x++){const i=(y*640+x)*4,j=Math.floor(y/4)*160+Math.floor(x/4);if(!red[j])d.data[i+3]=0;else {d.data[i]=d.data[i]*p[j*4]/232;d.data[i+1]=0;d.data[i+2]=0;}}g.putImageData(d,0,0);this.ctx.drawImage(layer,0,0);return {scene:count?'impact-bg':'verified-empty-plate',backgroundPixels:23040,eligiblePixels:23040,unsupportedPixels:0,dialogueFrameCovered:true,uncoveredTiles:[]};}
 drawLateImpact(p,o){if(o.actorMask.some(Boolean))return null;
 // Exact late BG keys/attributes/scroll/UI are checked by drawImpact. Read
 // raster timing directly from each row's native index-to-color relation.
 const rows=[];for(let y=0;y<144;y++){const colors=new Map();for(let x=0;x<160;x++){const index=o.indices[y*256+x],i=(y*160+x)*4,rgb=[p[i],p[i+1],p[i+2]];if(index!==2&&index!==3)return null;if(colors.has(index)&&colors.get(index).some((v,ch)=>v!==rgb[ch]))return null;colors.set(index,rgb);}if(!colors.has(3))return null;rows.push({bg:colors.get(3),fg:colors.get(2)});}
 // Empty native rows have no foreground sample; extend the closest measured
 // foreground color across the authored plate's glow without copying pixels.
 const samples=rows.map((row,y)=>row.fg?y:-1).filter(y=>y>=0);if(!samples.length)return null;
 if(!this.impactLatePixels){const canvas=document.createElement('canvas');canvas.width=640;canvas.height=576;const g=canvas.getContext('2d');g.drawImage(this.impactLate,0,0,640,576);this.impactLatePixels=g.getImageData(0,0,640,576);this.impactLateLayer=canvas;}
 const g=this.impactLateLayer.getContext('2d'),art=this.impactLatePixels.data,out=this.impactLateOutput??=g.createImageData(640,576);
 for(let y=0;y<576;y++){const row=rows[y>>2],bg=row.bg,fg=row.fg||rows[samples.reduce((a,b)=>Math.abs(b-(y>>2))<Math.abs(a-(y>>2))?b:a)].fg,contrast=Math.max(...fg.map((v,ch)=>Math.abs(v-bg[ch])))/232;
 for(let x=0;x<640;x++){const i=(y*640+x)*4;for(let ch=0;ch<3;ch++)out.data[i+ch]=bg[ch]+art[i]*(fg[ch]-bg[ch])/232+(ch?art[i+ch]*contrast:0);out.data[i+3]=255;}}
 g.putImageData(out,0,0);this.ctx.drawImage(this.impactLateLayer,0,0);return {scene:'impact-late-bg',backgroundPixels:23040,eligiblePixels:23040,unsupportedPixels:0,dialogueFrameCovered:true,uncoveredTiles:[]};}
 // Validate every native row before deciding whether a card hides the map.
 prepareCard(p,o){if(!o||o.actorMask.some(Boolean))return null;const card=this.cards.find(a=>(a.keyEntries??=Object.entries(a.keys)).every(([k,v])=>o.cellKeys[k]===v));if(!card)return null;
 if(card.presentation&&this.sameBytes(card.presentation.p,p))return card.presentation;
 card.slots??=Array.from({length:2},()=>({card,p:new Uint8Array(p.length),rows:new Uint8Array(144),backgrounds:Array.from({length:144},()=>new Uint8Array(3)),brights:Array.from({length:144},()=>new Uint8Array(3)),covered:0}));
 const slot=card.slots[card.presentation===card.slots[0]?1:0],{rows,backgrounds,brights}=slot;rows.fill(0);slot.p.set(p);let covered=0;
 const seen=this.cardSeen??=new Int32Array(256),order=this.cardOrder??=new Uint16Array(256);
 for(let y=0;y<144;y++){seen.fill(-1);let valid=true,n=0;for(let x=0;x<160;x++){const i=y*160+x,k=card.indices[i],rgb=p[i*4]|(p[i*4+1]<<8)|(p[i*4+2]<<16);if(seen[k]!==-1&&seen[k]!==rgb){valid=false;break;}if(seen[k]===-1)order[n++]=k;seen[k]=rgb;}if(!valid)continue;
 const rowBackground=card.indices[y*160],bg=seen[rowBackground];if(bg===-1)continue;let bright=bg,score=-1;
 for(let j=0;j<n;j++){const k=order[j];if(k===rowBackground)continue;const color=seen[k],sum=(color&255)+((color>>8)&255)+(color>>16);if(sum>score){score=sum;bright=color;}}
 for(let ch=0;ch<3;ch++){backgrounds[y][ch]=(bg>>(ch*8))&255;brights[y][ch]=(bright>>(ch*8))&255;}rows[y]=1;covered+=160;}
 slot.covered=covered;return slot;
 }
 drawCard(p,o,prepared=this.prepareCard(p,o)){if(!prepared)return null;const {card,rows,backgrounds,brights,covered}=prepared;
 if(card.presentation!==prepared){
 const layer=card.layer??=document.createElement('canvas'),back=card.backLayer??=document.createElement('canvas');
 if(layer.width!==640||layer.height!==576){layer.width=back.width=640;layer.height=back.height=576;}
 const art=card.workArt??=new ImageData(640,576),bgArt=card.workBackground??=new ImageData(640,576);
 art.data.set(this.artPixels(card.art).data);const source=this.artPixels(this.backdrop).data;
 // Only the requested four scanlines of each plate are needed. This replaces
 // up to 144 full-frame recolors/uploads while preserving Canvas alpha blend.
 for(let y=0;y<144;y++){if(!rows[y])continue;const bg=backgrounds[y],bright=brights[y];
 for(let k=y*4*640*4,end=(y+1)*4*640*4;k<end;k+=4){for(let ch=0;ch<3;ch++)bgArt.data[k+ch]=Math.min(255,source[k+ch]+bg[ch]);bgArt.data[k+3]=source[k+3];if(art.data[k+3])for(let ch=0;ch<3;ch++)art.data[k+ch]=bright[ch];}}
 layer.getContext('2d').putImageData(art,0,0);back.getContext('2d').putImageData(bgArt,0,0);card.presentation=prepared;
 }
 this.rowRuns(rows,(y,end)=>this.ctx.drawImage(card.backLayer,0,y*4,640,(end-y)*4,0,y*4,640,(end-y)*4));
 this.rowRuns(rows,(y,end)=>this.ctx.drawImage(card.layer,0,y*4,640,(end-y)*4,0,y*4,640,(end-y)*4));
 return {scene:'card-'+card.name,backgroundPixels:covered,eligiblePixels:23040,unsupportedPixels:23040-covered,dialogueFrameCovered:true,dialogueBorderPixels:0,dialogueBorderCoveredPixels:0,uncoveredTiles:[]};}

 setAudit(v=true){this.maps.auditEnabled=!!v;}
 audit(){if(!this.maps.auditEnabled){this.setAudit(true);this.draw(this.meta?.fallback!=='original');}const o=this.observation,p=this.pixels(),hash=a=>{let h=2166136261;for(const v of a)h=Math.imul(h^v,16777619);return (h>>>0).toString(16).padStart(8,'0');};let same=true;for(let i=4;i<p.length;i+=4)if(p[i]!==p[0]||p[i+1]!==p[1]||p[i+2]!==p[2]){same=false;break;}const mr=this.meta.mapResult,scene=this.meta.scene,ref=this.maps.maps.find(m=>m.name===scene);const used=new Set();if(o)for(let y=0;y<144;y++)for(let x=0;x<160;x++)if(!o.mask[y*160+x])used.add(o.attrs[(((((y+o.scy)&255)>>3)*32)+(((x+o.scx)&255)>>3))]&7);const faded=!!(o&&ref&&o.palettes.some((v,i)=>i%4!==3&&used.has(Math.floor(i/16))&&v!==ref.palettes[i]));return {scene,classification:same?'blank':mr?.rasterMismatchPixels?'raster-transition':faded?'palette-change':scene==='unsupported'?'unsupported':'scene',observerValid:!!o,geometry:o?hash([...o.tiles,...o.attrs]):null,structural:o?hash(o.cellKeys.flatMap(x=>[x&255,(x>>>8)&255,(x>>>16)&255,x>>>24])):null,palette:o?hash(o.palettes):null,scroll:o?[o.scx,o.scy]:null,window:o?[o.window,o.wx,o.wy]:null,dialogueRects:o?.dialogueRects||[],eligibleBackgroundPixels:this.meta.coverage.eligibleBackgroundPixels??23040,gptBackgroundPixels:this.meta.coverage.gptBackgroundPixels,uncoveredBackgroundPixels:this.meta.coverage.uncoveredBackgroundPixels??23040,uncoveredTiles:mr?.uncoveredTiles||[],dialogueBorderPixels:mr?.dialogueBorderPixels||0,dialogueBorderCoveredPixels:mr?.dialogueBorderCoveredPixels||0,dialogueFrameCovered:!!this.meta.coverage.dialogueFrameCovered,pixelHash:hash(p)};}
 captureReference(){const p=this.pixels(),scx=this.m._emulator_read_mem(this.e,0xff43),scy=this.m._emulator_read_mem(this.e,0xff42),tiles=[];for(let y=(8-scy%8)%8;y<=136;y+=8)for(let x=(8-scx%8)%8;x<=152;x+=8)tiles.push({x,y,key:tileKey(p,x,y)});return {tiles,scroll:[scx,scy],pixels:Array.from(p)};}
}
