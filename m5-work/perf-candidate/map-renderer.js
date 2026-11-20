const load=src=>new Promise((resolve,reject)=>{const i=new Image();i.onload=()=>resolve(i);i.onerror=reject;i.src=src;});
export class MapRenderer {
 constructor(){this.auditEnabled=new URLSearchParams(globalThis.location?.search||'').get('audit')==='1';this.usedCache=new WeakMap();this.usedByMask=new WeakMap();}
 usedPalettes(o){let used=this.usedCache.get(o);if(used!==undefined)return used;let byAttrs=this.usedByMask.get(o.mask);if(!byAttrs){byAttrs=new WeakMap();this.usedByMask.set(o.mask,byAttrs);}let byScroll=byAttrs.get(o.attrs);if(!byScroll){byScroll=new Map();byAttrs.set(o.attrs,byScroll);}const scroll=o.scx+256*o.scy;used=byScroll.get(scroll);if(used!==undefined){this.usedCache.set(o,used);return used;}used=0;
 for(let y=0;y<144;y++)for(let x=0;x<160;x++)if(!o.mask[y*160+x])used|=1<<(o.attrs[((((y+o.scy)&255)>>3)*32)+(((x+o.scx)&255)>>3)]&7);
 this.usedCache.set(o,used);byScroll.set(scroll,used);return used;}
 arrayKey(a){this.arrayKeys??=new WeakMap();let key=this.arrayKeys.get(a);if(key===undefined){key=a.join(',');this.arrayKeys.set(a,key);}return key;}
 same(a,b){if(!a||!b||a.length!==b.length)return false;for(let i=0;i<a.length;i++)if(a[i]!==b[i])return false;return true;}

 static async create(){const r=new MapRenderer();r.maps=[];const specs=await(await fetch('assets/maps/m3_signatures.json')).json();for(const s of specs){const image=await load(s.image);r.maps.push({...s,image,sets:s.cellKeys.map(a=>new Set(a)),cache:new Map()});}r.overlay=document.createElement('canvas');r.overlay.width=160;r.overlay.height=144;try{r.dialogue=await load('assets/maps/dialogue_hd.png');}catch{}return r;}
 faded(map,o){const bits=this.usedPalettes(o),used=[];for(let i=0;i<8;i++)if(bits&(1<<i))used.push(i);const key=Array.from(used).sort().map(p=>o.palettes.slice(p*16,p*16+16).join(',')).join(';');if(map.cache.has(key))return map.cache.get(key);
 const c=document.createElement('canvas');c.width=map.imageNativeSize*4;c.height=(map.imageNativeHeight||map.imageNativeSize)*4;const g=c.getContext('2d');g.drawImage(map.image,0,0,c.width,c.height);const fit=[];for(let ch=0;ch<3;ch++){let n=0,sx=0,sy=0,sxx=0,sxy=0;for(const p of used)for(let i=0;i<4;i++){const k=p*16+i*4+ch,x=map.palettes[k],y=o.palettes[k];n++;sx+=x;sy+=y;sxx+=x*x;sxy+=x*y;}const den=n*sxx-sx*sx,a=den?(n*sxy-sx*sy)/den:1,b=n?(sy-a*sx)/n:0;fit.push([a,b]);}
 if(map.flatPaletteIndex!==undefined)for(let ch=0;ch<3;ch++)fit[ch]=[0,o.palettes[map.flatPaletteIndex*4+ch]];
 if(fit.some(([a,b])=>Math.abs(a-1)>.0001||Math.abs(b)>.0001)){const d=g.getImageData(0,0,c.width,c.height);for(let i=0;i<d.data.length;i+=4)for(let ch=0;ch<3;ch++)d.data[i+ch]=Math.max(0,Math.min(255,fit[ch][0]*d.data[i+ch]+fit[ch][1]));g.putImageData(d,0,0);}if(map.cache.size>=8)map.cache.delete(map.cache.keys().next().value);map.cache.set(key,c);return c;}
 // Raster palette recovery consumes a single sheet scanline. Recolor exactly
 // that source row, using the same fit and Uint8Clamped rounding as faded().
 fadedRow(map,o,my){const bits=this.usedPalettes(o),used=[];for(let i=0;i<8;i++)if(bits&(1<<i))used.push(i);
 const key=used.map(p=>o.palettes.slice(p*16,p*16+16).join(',')).join(';')+'@'+my;
 map.rowCache??=new Map();let row=map.rowCache.get(key);if(row)return row;
 const fit=[];for(let ch=0;ch<3;ch++){let n=0,sx=0,sy=0,sxx=0,sxy=0;for(const p of used)for(let i=0;i<4;i++){const k=p*16+i*4+ch,x=map.palettes[k],y=o.palettes[k];n++;sx+=x;sy+=y;sxx+=x*x;sxy+=x*y;}const den=n*sxx-sx*sx,a=den?(n*sxy-sx*sy)/den:1,b=n?(sy-a*sx)/n:0;fit.push([a,b]);}
 if(map.flatPaletteIndex!==undefined)for(let ch=0;ch<3;ch++)fit[ch]=[0,o.palettes[map.flatPaletteIndex*4+ch]];
 if(!map.basePixels){const c=document.createElement('canvas');c.width=map.imageNativeSize*4;c.height=(map.imageNativeHeight||map.imageNativeSize)*4;const g=c.getContext('2d',{willReadFrequently:true});g.drawImage(map.image,0,0,c.width,c.height);map.baseCanvas=c;map.basePixels=g.getImageData(0,0,c.width,c.height);}
 if(!fit.some(([a,b])=>Math.abs(a-1)>.0001||Math.abs(b)>.0001))return {image:map.baseCanvas,y:my*4};
 const c=document.createElement('canvas');c.width=map.basePixels.width;c.height=4;const g=c.getContext('2d'),data=g.createImageData(c.width,4),start=my*4*c.width*4;
 // Out-of-image rows remain transparent, exactly as the original drawImage.
 for(let i=0;i<data.data.length;i+=4)if(start+i<map.basePixels.data.length){for(let ch=0;ch<3;ch++)data.data[i+ch]=Math.max(0,Math.min(255,fit[ch][0]*map.basePixels.data[start+i+ch]+fit[ch][1]));data.data[i+3]=map.basePixels.data[start+i+3];}
 g.putImageData(data,0,0);row={image:c,y:0};if(map.rowCache.size>=96)map.rowCache.delete(map.rowCache.keys().next().value);map.rowCache.set(key,row);return row;}
 identify(o){const visible=new Set();for(let y=0;y<144;y++)for(let x=0;x<160;x++)if(!o.mask[y*160+x])visible.add(((((y+o.scy)&255)>>3)*32)+(((x+o.scx)&255)>>3));let best=null,score=0;for(const map of this.maps){let n=0;for(const k of visible)if(map.sets[k].has(o.cellKeys[k]))n++;if(n>score){score=n;best=map;}}return {map:best&&score/visible.size>=.85?best:null,score,visible:visible.size};}
 draw(ctx,o,p){if(!o){this.uiPresentation=null;this.history=[];this.lastUITicks=undefined;return null;}
 const now={o,...this.identify(o)};this.history??=[];
 // No render-count timers: discontinuous native time invalidates presentations.
 if(this.lastUITicks!==undefined&&o.ticks!==this.lastUITicks&&(o.ticks-this.lastUITicks<70224||o.ticks-this.lastUITicks>70240)){this.uiPresentation=null;this.history=[];}
 this.lastUITicks=o.ticks;
 // End-of-frame VRAM can already contain the next dialogue row/palette.
 // A prior native snapshot is used only where its complete 8px scanline
 // exactly agrees with the displayed framebuffer (excluding native OAM).
 const candidates=[now,...this.history,...this.history.map(q=>q.rasterUI).filter(Boolean)];
 const anchors=[...new Set([now,...this.history].map(q=>q.map).filter(Boolean))];for(const anchor of anchors){
 if(anchor?.nativeReference){const ref=anchor.nativeReference,seen=new Set();anchor.nativeCache??=new Map();for(const q of [now,...this.history])for(const attrs of [ref.attrs,q.o.attrs]){const a=q.o,key=this.arrayKey(a.palettes)+';'+this.arrayKey(attrs);if(seen.has(key))continue;seen.add(key);let bg=anchor.nativeCache.get(key);if(!bg){bg=new Uint8ClampedArray(256*256*4);for(let j=0;j<65536;j++){const pal=(attrs[((j>>8)>>3)*32+((j&255)>>3)]&7)*16+ref.indices[j]*4;const i=j*4;bg[i]=a.palettes[pal];bg[i+1]=a.palettes[pal+1];bg[i+2]=a.palettes[pal+2];bg[i+3]=a.palettes[pal+3];}if(anchor.nativeCache.size>=12)anchor.nativeCache.delete(anchor.nativeCache.keys().next().value);anchor.nativeCache.set(key,bg);}candidates.push({map:anchor,score:now.score,visible:now.visible,o:{...a,...ref,attrs,paletteReferenceAttrs:ref.attrs,bg,mask:(this.emptyMask??=new Uint8Array(23040)),dialogueRects:[]}});}}}// Recover palette writes that occurred during the scanline, using the
 // verified native index geometry. Every non-OAM pixel across the complete
 // native row must agree with one exact mapping of palette/index to RGB.
 let needsRows=!now.map;for(let y=0;!needsRows&&y<144;y++)for(let x=0;x<160;x++){const i=y*160+x;if(o.mask[i])continue;const j=(((y+o.scy)&255)*256+((x+o.scx)&255))*4,k=((((y+o.scy)&255)>>3)*32)+(((x+o.scx)&255)>>3);if(!now.map.sets[k].has(o.cellKeys[k])||o.bg[j]!==p[i*4]||o.bg[j+1]!==p[i*4+1]||o.bg[j+2]!==p[i*4+2]){needsRows=true;break;}}
 if(needsRows)for(const anchor of anchors){const ref=anchor.nativeReference;if(!ref)continue;const a=now.o,rowPalettes=[],bg=new Uint8ClampedArray(256*256*4);let useful=false;for(let y=0;y<144;y++){const palettes=a.palettes.slice(),seen=new Int32Array(32).fill(-1);let valid=true;for(let x=0;x<160;x++){if(o.actorMask[y*160+x])continue;const mx=(x+a.scx)&255,my=(y+a.scy)&255,k=(my>>3)*32+(mx>>3),pi=(ref.attrs[k]&7)*4+ref.indices[my*256+mx],i=(y*160+x)*4,rgb=p[i]|(p[i+1]<<8)|(p[i+2]<<16);if(seen[pi]!==-1&&seen[pi]!==rgb){valid=false;break;}seen[pi]=rgb;}if(!valid)continue;for(let pi=0;pi<32;pi++)if(seen[pi]!==-1){const rgb=seen[pi];palettes[pi*4]=rgb&255;palettes[pi*4+1]=(rgb>>8)&255;palettes[pi*4+2]=rgb>>16;}rowPalettes[y]=palettes;useful=true;for(let x=0;x<160;x++){const mx=(x+a.scx)&255,my=(y+a.scy)&255,k=(my>>3)*32+(mx>>3),pi=(ref.attrs[k]&7)*16+ref.indices[my*256+mx]*4;const i=(my*256+mx)*4;bg[i]=palettes[pi];bg[i+1]=palettes[pi+1];bg[i+2]=palettes[pi+2];bg[i+3]=palettes[pi+3];}}if(useful)candidates.push({map:anchor,score:now.score,visible:now.visible,o:{...a,...ref,bg,rowPalettes,mask:(this.emptyMask??=new Uint8Array(23040)),dialogueRects:[]}});}

 const sources=new Int16Array(23040).fill(-1),covered=new Uint8Array(23040),effectiveMask=o.actorMask.slice(),eligibleMask=new Uint8Array(23040),gaps=this.auditEnabled?new Map():null;let background=0,eligible=0,rasterMismatch=0,recovered=0;
 const eq=(a,x,y)=>{const j=(((y+a.scy)&255)*256+((x+a.scx)&255))*4,i=(y*160+x)*4;return a.bg[j]===p[i]&&a.bg[j+1]===p[i+1]&&a.bg[j+2]===p[i+2];};
 for(let y=0;y<144;y++)for(let x0=0;x0<160;x0+=8){let chosen=-1,quality=-1;for(let n=0;n<candidates.length;n++){const a=candidates[n].o;let ok=true;for(let x=x0;x<x0+8;x++)if(!o.actorMask[y*160+x]&&!eq(a,x,y)){ok=false;break;}if(ok){let rank=0;const m=candidates[n].map;for(let x=x0;x<x0+8;x++){const k=((((y+a.scy)&255)>>3)*32)+(((x+a.scx)&255)>>3);if(a.mask[y*160+x]||m?.sets[k].has(a.cellKeys[k]))rank++;}if(rank>quality){chosen=n;quality=rank;if(rank===8)break;}}}
 for(let x=x0;x<x0+8;x++){const i=y*160+x;if(o.actorMask[i])continue;
 const currentCell=((((y+o.scy)&255)>>3)*32)+(((x+o.scx)&255)>>3);if(o.mask[i]&&![161,162,163,164].includes(o.tiles[currentCell])){effectiveMask[i]=1;continue;}
 // Raster writes can split even one tile row. Prefer an exact native UI
 // reference, then exact verified scenery, without inferring glyph shapes.
 let pixelSource=chosen;
 if(pixelSource>=0){const q=candidates[pixelSource],a=q.o,k=((((y+a.scy)&255)>>3)*32)+(((x+a.scx)&255)>>3);if(!a.mask[i]&&!q.map?.sets[k].has(a.cellKeys[k]))pixelSource=-1;}
 if(pixelSource<0){let scenery=-1;for(let n=0;n<candidates.length;n++){const q=candidates[n],a=q.o;if(!eq(a,x,y))continue;const mx=(x+a.scx)&255,my=(y+a.scy)&255,k=(my>>3)*32+(mx>>3);if(a.mask[i]&&!a.actorMask[i]){pixelSource=n;break;}if(scenery<0&&q.map?.sets[k].has(a.cellKeys[k]))scenery=n;}if(pixelSource<0)pixelSource=scenery;}
 const q=pixelSource>=0?candidates[pixelSource]:now,a=q.o,m=q.map,mx=(x+a.scx)&255,my=(y+a.scy)&255,k=(my>>3)*32+(mx>>3);sources[i]=pixelSource;
 if(pixelSource>=0&&((a.mask[i]&&!a.actorMask[i])||(m?.nativeTextCells?.[k]===a.cellKeys[k]))){effectiveMask[i]=1;continue;}if(pixelSource<0&&o.mask[i]&&!o.actorMask[i]){effectiveMask[i]=1;continue;}eligible++;eligibleMask[i]=1;if(this.auditEnabled&&!eq(o,x,y))rasterMismatch++;
 const known=pixelSource>=0&&m&&mx>=m.bounds[0]&&my>=m.bounds[1]&&mx<m.bounds[2]&&my<m.bounds[3]&&(!m.verifiedYRanges||m.verifiedYRanges.some(([lo,hi])=>my>=lo&&my<hi))&&m.sets[k].has(a.cellKeys[k]);if(known){covered[i]=1;background++;if(pixelSource>0)recovered++;}else if(gaps){const id=k+':'+a.cellKeys[k],g=gaps.get(id)||{tile:k,signature:a.cellKeys[k],pixels:0,screenBounds:[x,y,x,y]};g.pixels++;g.screenBounds[0]=Math.min(g.screenBounds[0],x);g.screenBounds[1]=Math.min(g.screenBounds[1],y);g.screenBounds[2]=Math.max(g.screenBounds[2],x);g.screenBounds[3]=Math.max(g.screenBounds[3],y);gaps.set(id,g);}}}
 // Draw only verified horizontal runs, using each snapshot's own camera and
 // palette. No interpolation of native pixels and no invented map extension.
 // Only materialize palette sheets actually selected by visible runs.
 const images=[],variantImages=new Map();const palettePair=(a,x,y)=>{const k=((((y+a.scy)&255)>>3)*32)+(((x+a.scx)&255)>>3);return a.paletteReferenceAttrs?((a.paletteReferenceAttrs[k]&7)*8+(a.attrs[k]&7)):null;};for(let y=0;y<144;y++)for(let x=0;x<160;){const i=y*160+x,n=sources[i];if(!covered[i]){x++;continue;}let end=x+1;const pair=palettePair(candidates[n].o,x,y);while(end<160&&covered[y*160+end]&&sources[y*160+end]===n&&palettePair(candidates[n].o,end,y)===pair)end++;const q=candidates[n],a=q.o,mx=(x+a.scx)&255,my=(y+a.scy)&255;let sourceY=my*4,im;if(a.rowPalettes?.[y]){const row=this.fadedRow(q.map,{...a,palettes:a.rowPalettes[y]},my);im=row.image;sourceY=row.y;}else im=images[n]??=this.faded(q.map,q.o);if(pair!==null&&(pair>>3)!==(pair&7)){sourceY=my*4;const key=n+':'+pair;im=variantImages.get(key);if(!im){const palettes=q.map.palettes.slice();palettes.splice((pair>>3)*16,16,...a.palettes.slice((pair&7)*16,(pair&7)*16+16));im=this.faded(q.map,{...a,palettes,attrs:new Array(1024).fill(pair>>3),mask:new Uint8Array(23040)});variantImages.set(key,im);}}let width=Math.min(end-x,256-mx);ctx.drawImage(im,mx*4,sourceY,width*4,4,x*4,y*4,width*4,4);if(width<end-x)ctx.drawImage(im,0,sourceY,(end-x-width)*4,4,(x+width)*4,y*4,(end-x-width)*4,4);x=end;}
 let uiPixels=0,uiCovered=0;const rects=[];for(let n=0;n<candidates.length;n++){if(!sources.includes(n))continue;const a=candidates[n].o;const ui=this.drawUI(ctx,{...a,actorMask:o.actorMask,presentationSources:sources,presentationSource:n},p);uiPixels+=ui.dialogueBorderPixels;uiCovered+=ui.dialogueBorderCoveredPixels;for(const r of ui.dialogueRects)if(!rects.some(v=>JSON.stringify(v)===JSON.stringify(r)))rects.push(r);}
 const uiTransition=this.presentUITransition(ctx,o,p,now.map,eligible===background&&uiPixels===uiCovered,eq);
 if(uiTransition){for(let i=0;i<23040;i++)if(uiTransition.mask[i]&&eligibleMask[i]&&!covered[i]){covered[i]=1;background++;}
 // Recompute residuals from individual pixels, including partially intersected cells.
 if(gaps){gaps.clear();for(let y=0;y<144;y++)for(let x=0;x<160;x++){const i=y*160+x;if(!eligibleMask[i]||covered[i])continue;const a=(candidates[sources[i]]||now).o,k=((((y+a.scy)&255)>>3)*32)+(((x+a.scx)&255)>>3),id=k+':'+a.cellKeys[k],g=gaps.get(id)||{tile:k,signature:a.cellKeys[k],pixels:0,screenBounds:[x,y,x,y]};g.pixels++;g.screenBounds[0]=Math.min(g.screenBounds[0],x);g.screenBounds[1]=Math.min(g.screenBounds[1],y);g.screenBounds[2]=Math.max(g.screenBounds[2],x);g.screenBounds[3]=Math.max(g.screenBounds[3],y);gaps.set(id,g);}}}
 // Retain only UI pixels whose presentation was established this frame.
 // Unlike end-of-frame VRAM, this is the raster actually seen by the player.
 let hasUI=false;for(let i=0;i<23040;i++)if(effectiveMask[i]&&!o.actorMask[i]){hasUI=true;break;}
 const uiBG=hasUI?new Int16Array(256*256*4).fill(-1):(this.emptyUIBG??=new Int16Array(256*256*4).fill(-1));if(hasUI)for(let y=0;y<144;y++)for(let x=0;x<160;x++){const i=y*160+x;if(effectiveMask[i]&&!o.actorMask[i]){const j=(((y+o.scy)&255)*256+((x+o.scx)&255))*4;uiBG.set(p.subarray(i*4,i*4+4),j);}}
 now.rasterUI={map:null,o:{...o,bg:uiBG,mask:effectiveMask,dialogueRects:[]}};
 const historyKey=this.arrayKey(o.cellKeys)+';'+this.arrayKey(o.palettes)+';'+o.scx+','+o.scy;now.historyKey=historyKey;if(this.history[0]?.historyKey===historyKey)this.history[0]=now;else this.history.unshift(now);this.history.length=Math.min(this.history.length,6);
 const principal=now.map?now:candidates.find(q=>q.map);return {scene:principal?.map?.name||'unsupported',matchedCells:principal?.score||0,visibleCells:now.visible,preservedPixels:23040-background,backgroundPixels:background,eligiblePixels:eligible,unsupportedPixels:eligible-background,uncoveredTiles:gaps?[...gaps.values()]:[],rasterMismatchPixels:this.auditEnabled?rasterMismatch:null,rasterRecoveredPixels:recovered,uiTransition:uiTransition?.evidence||null,dialogueRects:rects,dialogueBorderPixels:uiPixels,dialogueBorderCoveredPixels:uiCovered,dialogueFrameCovered:uiPixels===uiCovered};
 }

 // Certified UI presentations contain HD borders and native BG foreground, but
 // no OAM. Closing replaces only the native UI rectangle, in native write order.
 presentUITransition(ctx,o,p,map,fullyCovered,eq){
 const prior=this.uiPresentation;
 // Partial UI cells may lower whole-screen identification. Independently
 // retain the certified scene only when exterior BG geometry still agrees.
 if(!map&&prior){let n=0,ok=0;const r=prior.rect;for(let y=0;y<144;y+=8)for(let x=0;x<160;x+=8){if(x>=r.x&&x<r.x+r.w&&y>=r.y&&y<r.y+r.h)continue;const k=(y>>3)*32+(x>>3);n++;if(prior.map.sets[k].has(o.cellKeys[k]))ok++;}if(n&&ok/n>=.85)map=prior.map;}
 const ref=map?.nativeReference;
 if(!ref||o.scx||o.scy){this.uiPresentation=null;return null;}
 if(prior&&(prior.map!==map||prior.scx!==o.scx||prior.scy!==o.scy))this.uiPresentation=null;
 const saved=this.uiPresentation;let effect=null;
 if(saved){const r=saved.rect;
 if(r.x<map.bounds[0]||r.y<map.bounds[1]||r.x+r.w>map.bounds[2]||r.y+r.h>map.bounds[3]||(map.verifiedYRanges&&!Array.from({length:r.h},(_,i)=>r.y+i).every(y=>map.verifiedYRanges.some(([lo,hi])=>y>=lo&&y<hi)))){this.uiPresentation=null;return null;}
 let changedScene=0,topScene=0,distinct=0,restoredCells=0,uiCells=0,mismatch=0,changedUI=0,uiSamples=0,attributeCells=0,attributeTop=0;
 for(let y=r.y;y<r.y+r.h;y++)for(let x=r.x;x<r.x+r.w;x++){const i=y*160+x,j=y*256+x,k=(y>>3)*32+(x>>3),pal=(ref.attrs[k]&7)*16+ref.indices[j]*4;
 if(x%8===0&&y%8===0){if(saved.attrs&&o.attrs[k]!==saved.attrs[k]&&o.attrs[k]===ref.attrs[k]&&o.tiles[k]===saved.tiles[k]){attributeCells++;if(y===r.y)attributeTop++;}if(map.sets[k].has(o.cellKeys[k]))restoredCells++;else uiCells++;}
 if(o.actorMask[i])continue;uiSamples++;const j4=i*4,native=saved.native,palettes=o.palettes;if(p[j4]!==native[j4]||p[j4+1]!==native[j4+1]||p[j4+2]!==native[j4+2])changedUI++;const differs=palettes[pal]!==native[j4]||palettes[pal+1]!==native[j4+1]||palettes[pal+2]!==native[j4+2];if(differs){distinct++;if(palettes[pal]===p[j4]&&palettes[pal+1]===p[j4+1]&&palettes[pal+2]===p[j4+2]){changedScene++;if(y<r.y+8)topScene++;}}if(!eq(o,x,y))mismatch++;}
 // A changed glyph alone cannot trigger this: require a native raster mismatch
 // and newly displayed verified scenery, or a decoded partial BG restoration.
 const partial=restoredCells>0&&uiCells>0;
 const sameRect=o.dialogueRects.some(v=>v.x===r.x&&v.y===r.y&&v.w===r.w&&v.h===r.h);
 const attributeClose=sameRect&&attributeTop>=Math.ceil(r.w/16)&&attributeCells>=attributeTop;
 if((changedScene>=8||attributeClose||saved.active)&&mismatch>0&&(partial||sameRect&&topScene>=8||attributeClose||saved.active)&&(!sameRect||topScene>=8||attributeClose||saved.active)){
 saved.active=true;saved.attributeClose ||= attributeClose;
 const progress=Math.min(1,Math.max(changedScene/Math.max(1,distinct),attributeClose||saved.attributeClose?changedUI/Math.max(1,uiSamples):0)),cut=r.y+progress*r.h;
 const layer=document.createElement('canvas');layer.width=640;layer.height=576;const g=layer.getContext('2d');g.imageSmoothingEnabled=false;
 const scene=this.faded(map,{...o,...ref,mask:new Uint8Array(23040)});
 g.drawImage(scene,r.x*4,r.y*4,r.w*4,r.h*4,r.x*4,r.y*4,r.w*4,r.h*4);
 // A top-to-bottom HD wipe follows displayed restoration progress, rather
 // than replay frames or a timer. The old native text participates in closing.
 const top=Math.ceil(cut*4);if(top<(r.y+r.h)*4)g.drawImage(saved.image,r.x*4,top,r.w*4,(r.y+r.h)*4-top,r.x*4,top,r.w*4,(r.y+r.h)*4-top);
 const mask=new Uint8Array(23040),repairs=[];let pixels=0;
 for(let y=r.y;y<r.y+r.h;y++)for(let x=r.x;x<r.x+r.w;x++){const i=y*160+x,k=(y>>3)*32+(x>>3);mask[i]=1;pixels++;
 // Current OAM is always last. Newly decoded native UI content is also last;
 // cached text cannot obscure a new native text/portrait trigger.
 const newContent=o.mask[i]&&!o.actorMask[i]&&![161,162,163,164].includes(o.tiles[k])&&o.cellKeys[k]!==saved.keys[k]&&eq(o,x,y);
 if(o.actorMask[i]||newContent)repairs.push(i);}
 if(repairs.length){const nativeCanvas=document.createElement('canvas');nativeCanvas.width=160;nativeCanvas.height=144;nativeCanvas.getContext('2d').putImageData(new ImageData(new Uint8ClampedArray(p),160,144),0,0);
 for(const i of repairs){const x=i%160,y=(i/160)|0;g.drawImage(nativeCanvas,x,y,1,1,x*4,y*4,4,4);}}
 ctx.drawImage(layer,r.x*4,r.y*4,r.w*4,r.h*4,r.x*4,r.y*4,r.w*4,r.h*4);
 effect={mask,evidence:{kind:'native-ui-close-wipe',rect:r,progress,changedScene,topScene,distinct,changedUI,attributeCells,attributeTop,restoredCells,uiCells,mismatch,pixels,ticks:o.ticks,certifiedTicks:saved.ticks}};
 }else if(!sameRect&&!partial){this.uiPresentation=null;}
 }
 // Only a complete, exact native UI raster over a gap-free HD scene can seed
 // a future close. OAM holes are reconstructed from decoded BG, never cached.
 if(!effect&&fullyCovered&&o.dialogueRects.length===1){const r=o.dialogueRects[0];let coherent=r.x>=0&&r.y>=0&&r.x+r.w<=160&&r.y+r.h<=144;
 for(let y=r.y;coherent&&y<r.y+r.h;y++)for(let x=r.x;x<r.x+r.w;x++){const k=(y>>3)*32+(x>>3),t=o.tiles[k],a=o.attrs[k],ui=(t>=160&&a===0)||(t>=240&&a===7)||([161,162,163,164].includes(t)&&a===6);if(!ui||!o.actorMask[y*160+x]&&!eq(o,x,y)){coherent=false;break;}}
 if(coherent){const old=this.uiPresentation;
 let reusable=old&&!old.active&&old.map===map&&old.rect.x===r.x&&old.rect.y===r.y&&old.rect.w===r.w&&old.rect.h===r.h&&this.same(old.keys,o.cellKeys)&&this.same(old.attrs,o.attrs)&&this.same(old.tiles,o.tiles)&&this.same(old.palettes,o.palettes);
 for(let y=r.y;reusable&&y<r.y+r.h;y++)for(let x=r.x;x<r.x+r.w;x++){const i=(y*160+x)*4,j=(y*256+x)*4;for(let ch=0;ch<4;ch++)if(old.native[i+ch]!==o.bg[j+ch]){reusable=false;break;}}
 if(reusable){old.ticks=o.ticks;return effect;}
 const image=document.createElement('canvas');image.width=640;image.height=576;const g=image.getContext('2d');g.imageSmoothingEnabled=false;g.drawImage(ctx.canvas,0,0);const native=new Uint8ClampedArray(23040*4),repairs=[];
 for(let y=r.y;y<r.y+r.h;y++)for(let x=r.x;x<r.x+r.w;x++){const i=y*160+x,j=(y*256+x)*4;native.set(o.bg.subarray(j,j+4),i*4);if(o.actorMask[i])repairs.push(i);}
 if(repairs.length){const bgCanvas=document.createElement('canvas');bgCanvas.width=160;bgCanvas.height=144;bgCanvas.getContext('2d').putImageData(new ImageData(native,160,144),0,0);
 for(const i of repairs){const x=i%160,y=(i/160)|0;g.drawImage(bgCanvas,x,y,1,1,x*4,y*4,4,4);}}
 this.drawUI(g,{...o,actorMask:new Uint8Array(23040)},p);
 this.uiPresentation={map,rect:{...r},image,native,keys:o.cellKeys.slice(),attrs:o.attrs.slice(),tiles:o.tiles.slice(),scx:o.scx,scy:o.scy,palettes:o.palettes.slice(),ticks:o.ticks};}}
 return effect;
 }

 dialogueImage(o){const base=[248,248,248,248,144,144,120,0,0,0,0,0],key=o.palettes.slice(96,112).join(',');this.uiCache??=new Map();if(this.uiCache.has(key))return this.uiCache.get(key);const c=document.createElement('canvas');c.width=this.dialogue.width;c.height=this.dialogue.height;const g=c.getContext('2d');g.drawImage(this.dialogue,0,0);const data=g.getImageData(0,0,c.width,c.height);for(let ch=0;ch<3;ch++){let sx=0,sy=0,sxx=0,sxy=0;for(let i=0;i<4;i++){const x=base[i*3+ch],y=o.palettes[96+i*4+ch];sx+=x;sy+=y;sxx+=x*x;sxy+=x*y;}const den=4*sxx-sx*sx,a=den?(4*sxy-sx*sy)/den:1,b=(sy-a*sx)/4;if(Math.abs(a-1)<.0001&&Math.abs(b)<.0001)continue;for(let i=ch;i<data.data.length;i+=4)data.data[i]=Math.max(0,Math.min(255,a*data.data[i]+b));}g.putImageData(data,0,0);if(this.uiCache.size>=8)this.uiCache.delete(this.uiCache.keys().next().value);this.uiCache.set(key,c);return c;}

 uiArt(o,rects){const key=o.palettes.slice(96,112).join(',')+';'+rects.map(r=>[r.x,r.y,r.w,r.h].join(',')).join(';');
 this.uiArtCache??=new Map();let layer=this.uiArtCache.get(key);if(layer)return layer;
 layer=document.createElement('canvas');layer.width=640;layer.height=576;const g=layer.getContext('2d',{willReadFrequently:true});
 for(const r of rects){const im=this.dialogueImage(o),s=Math.min(im.width,im.height)/12,d=32;
 const xs=[0,s,im.width-s,im.width],ys=[0,s,im.height-s,im.height],dx=[r.x*4,r.x*4+d,(r.x+r.w)*4-d,(r.x+r.w)*4],dy=[r.y*4,r.y*4+d,(r.y+r.h)*4-d,(r.y+r.h)*4];
 for(let j=0;j<3;j++)for(let i=0;i<3;i++)g.drawImage(im,xs[i],ys[j],xs[i+1]-xs[i],ys[j+1]-ys[j],dx[i],dy[j],dx[i+1]-dx[i],dy[j+1]-dy[j]);}
 // Preserve M5's unpremultiply/put roundtrip once, then copy exact integer crops.
 const art=g.getImageData(0,0,640,576);g.putImageData(art,0,0);
 if(this.uiArtCache.size>=8)this.uiArtCache.delete(this.uiArtCache.keys().next().value);this.uiArtCache.set(key,layer);return layer;}
 drawUI(ctx,o,p){let eligible=0,covered=0;const rects=o.dialogueRects||[];
 if(!rects.length)return {dialogueRects:rects,dialogueBorderPixels:0,dialogueBorderCoveredPixels:0,dialogueFrameCovered:true};
 const layer=this.dialogue?this.uiArt(o,rects):null;
 // The mask is still evaluated at every native pixel, every frame. Only the
 // static HD border art is cached; current actors/text/source selection win.
 for(let y=0;y<144;y++){let start=-1;
 for(let x=0;x<=160;x++){let selected=false;if(x<160){const i=y*160+x,t=o.tiles[(((((y+o.scy)&255)>>3)*32)+(((x+o.scx)&255)>>3))];
 selected=!o.actorMask[i]&&(!o.presentationSources||o.presentationSources[i]===o.presentationSource)&&[161,162,163,164].includes(t)&&rects.some(r=>x>=r.x&&x<r.x+r.w&&y>=r.y&&y<r.y+r.h);}
 if(selected){eligible++;if(layer)covered++;if(start<0)start=x;}else if(start>=0){if(layer)ctx.drawImage(layer,start*4,y*4,(x-start)*4,4,start*4,y*4,(x-start)*4,4);start=-1;}}
 }
 return {dialogueRects:rects,dialogueBorderPixels:eligible,dialogueBorderCoveredPixels:covered,dialogueFrameCovered:eligible===covered};}
}
