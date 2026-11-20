const fs=require('fs');const f='web/map-renderer.js';let s=fs.readFileSync(f,'utf8');s=s.replace('const now={o,...this.identify(o)};this.history??=[];',`const now={o,...this.identify(o)};this.history??=[];
 // No render-count timers: discontinuous native time invalidates presentations.
 if(this.lastUITicks!==undefined&&o.ticks!==this.lastUITicks&&o.ticks-this.lastUITicks!==70224){this.uiPresentation=null;this.history=[];}
 this.lastUITicks=o.ticks;`);
s=s.replace('effectiveMask=o.actorMask.slice(),gaps=', 'effectiveMask=o.actorMask.slice(),eligibleMask=new Uint8Array(23040),gaps=');s=s.replace('eligible++;if(!eq(o,x,y))','eligible++;eligibleMask[i]=1;if(!eq(o,x,y))');
let marker=' // Retain only UI pixels whose presentation was established this frame.';
s=s.replace(marker,` const uiTransition=this.presentUITransition(ctx,o,p,now.map,eligible===background&&uiPixels===uiCovered,eq);
 if(uiTransition){for(let i=0;i<23040;i++)if(uiTransition.mask[i]&&eligibleMask[i]&&!covered[i]){covered[i]=1;background++;}
 // Recompute residuals from individual pixels, including partially intersected cells.
 gaps.clear();for(let y=0;y<144;y++)for(let x=0;x<160;x++){const i=y*160+x;if(!eligibleMask[i]||covered[i])continue;const a=(candidates[sources[i]]||now).o,k=((((y+a.scy)&255)>>3)*32)+(((x+a.scx)&255)>>3),id=k+':'+a.cellKeys[k],g=gaps.get(id)||{tile:k,signature:a.cellKeys[k],pixels:0,screenBounds:[x,y,x,y]};g.pixels++;g.screenBounds[0]=Math.min(g.screenBounds[0],x);g.screenBounds[1]=Math.min(g.screenBounds[1],y);g.screenBounds[2]=Math.max(g.screenBounds[2],x);g.screenBounds[3]=Math.max(g.screenBounds[3],y);gaps.set(id,g);}}
${marker}`);
s=s.replace('rasterRecoveredPixels:recovered,dialogueRects','rasterRecoveredPixels:recovered,uiTransition:uiTransition?.evidence||null,dialogueRects');
const method=`
 // Certified UI presentations contain HD borders and native BG foreground, but
 // no OAM. Closing replaces only the native UI rectangle, in native write order.
 presentUITransition(ctx,o,p,map,fullyCovered,eq){
 const prior=this.uiPresentation,ref=map?.nativeReference;
 if(!ref||o.scx||o.scy){this.uiPresentation=null;return null;}
 if(prior&&(prior.map!==map||prior.scx!==o.scx||prior.scy!==o.scy))this.uiPresentation=null;
 const saved=this.uiPresentation;let effect=null;
 if(saved){const r=saved.rect;let changedScene=0,distinct=0,restoredCells=0,uiCells=0,mismatch=0;
 for(let y=r.y;y<r.y+r.h;y++)for(let x=r.x;x<r.x+r.w;x++){const i=y*160+x,j=y*256+x,k=(y>>3)*32+(x>>3),pal=(ref.attrs[k]&7)*16+ref.indices[j]*4;
 if(x%8===0&&y%8===0){if(map.sets[k].has(o.cellKeys[k]))restoredCells++;else uiCells++;}
 if(o.actorMask[i])continue;const scene=[0,1,2].map(c=>o.palettes[pal+c]);const differs=scene.some((v,c)=>v!==saved.native[i*4+c]);if(differs){distinct++;if(scene.every((v,c)=>v===p[i*4+c]))changedScene++;}if(!eq(o,x,y))mismatch++;}
 // A changed glyph alone cannot trigger this: require a native raster mismatch
 // and newly displayed verified scenery, or a decoded partial BG restoration.
 const partial=restoredCells>0&&uiCells>0;
 const sameRect=o.dialogueRects.some(v=>v.x===r.x&&v.y===r.y&&v.w===r.w&&v.h===r.h);
 if(changedScene>=8&&(partial||sameRect&&mismatch>0)&&(!sameRect||mismatch>0)){
 const progress=Math.min(1,changedScene/Math.max(1,distinct)),cut=r.y+progress*r.h;
 const layer=document.createElement('canvas');layer.width=640;layer.height=576;const g=layer.getContext('2d');g.imageSmoothingEnabled=false;
 const scene=this.faded(map,{...o,...ref,mask:new Uint8Array(23040)});
 g.drawImage(scene,r.x*4,r.y*4,r.w*4,r.h*4,r.x*4,r.y*4,r.w*4,r.h*4);
 // A top-to-bottom HD wipe follows displayed restoration progress, rather
 // than replay frames or a timer. The old native text participates in closing.
 const top=Math.ceil(cut*4);if(top<(r.y+r.h)*4)g.drawImage(saved.image,r.x*4,top,r.w*4,(r.y+r.h)*4-top,r.x*4,top,r.w*4,(r.y+r.h)*4-top);
 const out=g.getImageData(0,0,640,576),mask=new Uint8Array(23040);let pixels=0;
 for(let y=r.y;y<r.y+r.h;y++)for(let x=r.x;x<r.x+r.w;x++){const i=y*160+x,k=(y>>3)*32+(x>>3);mask[i]=1;pixels++;
 // Current OAM is always last. Newly decoded native UI content is also last;
 // cached text cannot obscure a new native text/portrait trigger.
 const newContent=o.mask[i]&&!o.actorMask[i]&&![161,162,163,164].includes(o.tiles[k])&&o.cellKeys[k]!==saved.keys[k]&&eq(o,x,y);
 if(o.actorMask[i]||newContent)for(let yy=0;yy<4;yy++)for(let xx=0;xx<4;xx++)out.data.set(p.subarray(i*4,i*4+4),((y*4+yy)*640+x*4+xx)*4);}
 g.putImageData(out,0,0);ctx.drawImage(layer,r.x*4,r.y*4,r.w*4,r.h*4,r.x*4,r.y*4,r.w*4,r.h*4);
 effect={mask,evidence:{kind:'native-ui-close-wipe',rect:r,progress,changedScene,distinct,restoredCells,uiCells,mismatch,pixels,ticks:o.ticks,certifiedTicks:saved.ticks}};
 }else if(!sameRect&&!partial){this.uiPresentation=null;}
 }
 // Only a complete, exact native UI raster over a gap-free HD scene can seed
 // a future close. OAM holes are reconstructed from decoded BG, never cached.
 if(!effect&&fullyCovered&&o.dialogueRects.length===1){const r=o.dialogueRects[0];let coherent=r.x>=0&&r.y>=0&&r.x+r.w<=160&&r.y+r.h<=144;
 for(let y=r.y;coherent&&y<r.y+r.h;y++)for(let x=r.x;x<r.x+r.w;x++)if(!o.actorMask[y*160+x]&&!eq(o,x,y)){coherent=false;break;}
 if(coherent){const image=document.createElement('canvas');image.width=640;image.height=576;const g=image.getContext('2d');g.imageSmoothingEnabled=false;g.drawImage(ctx.canvas,0,0);const data=g.getImageData(0,0,640,576),native=new Uint8ClampedArray(23040*4);
 for(let y=r.y;y<r.y+r.h;y++)for(let x=r.x;x<r.x+r.w;x++){const i=y*160+x,j=(y*256+x)*4;native.set(o.bg.subarray(j,j+4),i*4);if(o.actorMask[i])for(let yy=0;yy<4;yy++)for(let xx=0;xx<4;xx++)data.data.set(o.bg.subarray(j,j+4),((y*4+yy)*640+x*4+xx)*4);}
 g.putImageData(data,0,0);this.drawUI(g,{...o,actorMask:new Uint8Array(23040)},p);
 this.uiPresentation={map,rect:{...r},image,native,keys:o.cellKeys.slice(),scx:o.scx,scy:o.scy,ticks:o.ticks};}}
 return effect;
 }
`;
s=s.replace('\n dialogueImage(o)',method+'\n dialogueImage(o)');fs.writeFileSync(f,s);
