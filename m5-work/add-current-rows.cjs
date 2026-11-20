const fs=require('fs'),f='m5-work/candidate-runtime/map-renderer.js';let s=fs.readFileSync(f,'utf8');const at=' const sources=new Int16Array';let code=`
 // Current decoded scenery is also a native reference when every visible
 // cell on that scanline is signature verified. Some saved references still
 // contain a dialogue overlay. Infer only complete, consistent native rows.
 if(needsRows&&now.map){const a=o,m=now.map,models=[],validRows=new Uint8Array(144);
 for(let y=0;y<144;y++){const seen=new Map();let valid=true;for(let x=0;x<160;x++){const i=y*160+x,mx=(x+a.scx)&255,my=(y+a.scy)&255,k=(my>>3)*32+(mx>>3);if(o.actorMask[i])continue;if(o.mask[i]||!m.sets[k].has(a.cellKeys[k])){valid=false;break;}const pi=(a.attrs[k]&7)*4+a.indices[my*256+mx],rgb=p.slice(i*4,i*4+3);if(seen.has(pi)&&seen.get(pi).some((v,c)=>v!==rgb[c])){valid=false;break;}seen.set(pi,rgb);}if(valid&&seen.size){const palettes=a.palettes.slice();for(const [pi,rgb] of seen)palettes.splice(pi*4,3,...rgb);models[y]={palettes,seen};validRows[y]=1;}}
 // Palette writes may split a scanline. Only colors independently observed on
 // the nearest coherent preceding/following rows may bridge that split; the
 // regular exact eight-pixel match still decides every rendered segment.
 for(const phase of [0,-1,1]){const bg=new Uint8ClampedArray(256*256*4),rowPalettes=[];let useful=false;for(let y=0;y<144;y++){let model=phase===0?models[y]:null;if(phase){if(validRows[y])continue;for(let yy=y+phase;yy>=0&&yy<144;yy+=phase)if(models[yy]){model=models[yy];break;}}if(!model)continue;const palettes=model.palettes;rowPalettes[y]=palettes;useful=true;for(let x=0;x<160;x++){const mx=(x+a.scx)&255,my=(y+a.scy)&255,k=(my>>3)*32+(mx>>3),pi=(a.attrs[k]&7)*4+a.indices[my*256+mx];if(!m.sets[k].has(a.cellKeys[k])||!model.seen.has(pi))continue;bg.set(palettes.slice(pi*4,pi*4+4),(my*256+mx)*4);}}if(useful)candidates.push({map:m,score:now.score,visible:now.visible,o:{...a,bg,rowPalettes,mask:new Uint8Array(23040),dialogueRects:[]}});}
 }
`;
s=s.replace(at,code+at);fs.writeFileSync(f,s);
