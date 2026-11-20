// Read-only PPU inspection. Never selects VRAM banks or writes emulator memory.
export class Observer {
 constructor(m,e){this.m=m;this.e=e;this.ptr=0;this.colors={};}
 read(a){return this.m._emulator_read_mem(this.e,a);}
 sample(p){const m=this.m,r=a=>this.read(a),lcdc=r(0xff40),scx=r(0xff43),scy=r(0xff42);
 // Pinned bundled binjgb layout, independently verified against accessible buses.
 const candidate=m._get_frame_buffer_ptr(this.e)-199508;
 if(candidate!==this.e+8356||candidate<0||candidate+199508+92160>m.HEAPU8.length)return null;
 const accessible=r(0x8000)!==255||r(0x8001)!==255;
 if(accessible)for(let j=0;j<8192;j+=127)if(m.HEAPU8[candidate+(r(0xff4f)&1)*8192+j]!==r(0x8000+j))return null;
 this.ptr=candidate;
 const raw=m.HEAPU8,ob=this.ptr+180252;
 const bus=Array.from({length:160},(_,i)=>r(0xfe00+i));
 if(!bus.every(x=>x===255))for(let n=0;n<40;n++)for(let j=0;j<4;j++){
 const expected=j===0?(raw[ob+n*20]+16)&255:j===1?(raw[ob+n*20+1]+8)&255:raw[ob+n*20+j];
 if(expected!==bus[n*4+j])return null;
 }
 if(!this.ptr)return null;
 const v=m.HEAPU8.slice(this.ptr,this.ptr+16384),base=lcdc&8?0x1c00:0x1800,tiles=Array.from(v.slice(base,base+1024)),attrs=Array.from(v.slice(base+8192,base+9216));
 const index=(x,y,t,a)=>{if(a&32)x=7-x;if(a&64)y=7-y;let n=lcdc&16?t:256+(t<128?t:t-256);let q=(a&8?8192:0)+n*16+y*2;return ((v[q]>>(7-x))&1)|(((v[q+1]>>(7-x))&1)<<1);};
 const sprites=[];const mask=new Uint8Array(160*144),boxes=new Uint8Array(160*144),height=lcdc&4?16:8;
 if(lcdc&2)for(let n=0;n<40;n++){const a=ob+n*20,sy=raw[a]>=240?raw[a]-256:raw[a],sx=raw[a+1]>=248?raw[a+1]-256:raw[a+1],t=raw[a+2],flags=raw[a+3];if(sx<=-8||sx>=160||sy<=-height||sy>=144)continue;sprites.push({sx,sy,t,flags});for(let j=0;j<height;j++)for(let i=0;i<8;i++){const x=sx+i,y=sy+j;if(x<0||x>=160||y<0||y>=144)continue;boxes[y*160+x]=1;let yy=flags&64?height-1-j:j,xx=flags&32?7-i:i,tt=height===16?(t&254)+(yy>>3):t,q=(flags&8?8192:0)+tt*16+(yy&7)*2,ci=(v[q]>>(7-xx)&1)|(v[q+1]>>(7-xx)&1)<<1;if(ci){const mx=(x+scx)&255,my=(y+scy)&255,k=(my>>3)*32+(mx>>3),bc=index(mx&7,my&7,tiles[k],attrs[k]);if(!(lcdc&1)||(!(attrs[k]&128)&&!(flags&128))||bc===0)mask[y*160+x]=1;}}}
 const actorMask=mask.slice(),dialogueRects=[];
 // Dialogue is drawn into BG tiles, not necessarily the hardware window.
 // Validate complete horizontal border before treating any BG tiles as UI.
 for(let ty=0;ty<32;ty++)for(let tx=0;tx<31;tx++){const k=ty*32+tx;if(tiles[k]!==161||tiles[k+1]!==162)continue;let ex=tx+1;while(ex<32&&tiles[ty*32+ex]===162)ex++;if(ex>=32||tiles[ty*32+ex]!==161||ex-tx<2)continue;let ey=ty+1;while(ey<32&&tiles[ey*32+tx]===163&&tiles[ey*32+ex]===163)ey++;if(ey<32&&tiles[ey*32+tx]===164&&tiles[ey*32+ex]===164)ey++;if(ey-ty<2)ey=ty+8;
 // A top edge is written before its sides/interior. Keep the intended
 // 64px frame geometry, but exclude only already-written UI cells below.
 if(ey-ty<8 && ey<32 && tiles[ey*32+tx]!==164)ey=Math.min(32,ty+8);
 for(let oy=-scy;oy<144;oy+=256)for(let ox=-scx;ox<160;ox+=256){const x=tx*8+ox,y=ty*8+oy,w=(ex-tx+1)*8,h=(ey-ty)*8;if(x>=160||y>=144||x+w<=0||y+h<=0)continue;dialogueRects.push({x,y,w,h});for(let yy=Math.max(0,y);yy<Math.min(144,y+h);yy++)for(let xx=Math.max(0,x);xx<Math.min(160,x+w);xx++){const mk=((((yy+scy)&255)>>3)*32)+(((xx+scx)&255)>>3),t=tiles[mk],a=attrs[mk];if((t>=160&&a===0)||(t>=240&&a===7)||([161,162,163,164].includes(t)&&a===6))mask[yy*160+xx]=1;}}}
 const wx=r(0xff4b)-7,wy=r(0xff4a),window=lcdc&32&&wx<160&&wy<144;
 // Pinned native CGB PaletteRGBA block: derived from bundled source layout,
 // verified byte-for-byte against unoccluded framebuffer pixels in four scenes.
 const palettes=Array.from(raw.slice(this.ptr+198648,this.ptr+198776));
 if(palettes.some((x,i)=>i%4===3&&x!==255))return null;
 // Exact tile-byte keys: no probabilistic invalidation and no emulator writes.
 // Local to this sample so bank/tile writes and state restores cannot go stale.
 const decoded=new Map(),cellKeys=[];
 const geometry=(t,a)=>{const n=lcdc&16?t:256+(t<128?t:t-256),q=(a&8?8192:0)+n*16;
 let key=String(a);for(let j=0;j<16;j++)key+=','+v[q+j];
 let d=decoded.get(key);if(d)return d;
 const pixels=new Uint8Array(64);let h=2166136261;h=Math.imul(h^(a&7),16777619);
 for(let y=0;y<8;y++)for(let x=0;x<8;x++){const ci=index(x,y,t,a);pixels[y*8+x]=ci;h=Math.imul(h^ci,16777619);}
 d={pixels,hash:h>>>0};decoded.set(key,d);return d;};
 const cells=tiles.map((t,k)=>geometry(t,attrs[k]));for(const d of cells)cellKeys.push(d.hash);
 const indices=new Uint8Array(256*256),bg=new Uint8ClampedArray(256*256*4);for(let y=0;y<256;y++)for(let x=0;x<256;x++){let k=(y>>3)*32+(x>>3),a=attrs[k],ci=cells[k].pixels[(y&7)*8+(x&7)],q=(a&7)*16+ci*4,i=(y*256+x)*4;indices[y*256+x]=ci;bg[i]=palettes[q];bg[i+1]=palettes[q+1];bg[i+2]=palettes[q+2];bg[i+3]=255;}
 if(window)for(let y=Math.max(0,wy);y<144;y++)for(let x=Math.max(0,wx);x<160;x++)mask[y*160+x]=1;
 return {ticks:m._emulator_get_ticks_f64(this.e),bg,indices,mask,actorMask,dialogueRects,tiles,attrs,cellKeys,palettes,lcdc,scx,scy,sprites,window:!!window,wx,wy,ptr:this.ptr,oamValidated:true};
 }
}
