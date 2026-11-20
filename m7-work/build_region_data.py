from pathlib import Path
from PIL import Image
import struct,json,hashlib
r=Path('/workspace/shawu');o=r/'m7-work';dest=o/'runtime/assets/region2';dest.mkdir(parents=True,exist_ok=True);rom=(r/'game.gbc').read_bytes()
def off(b,a):return b*0x4000+a-0x4000 if a>=0x4000 else a
def read(b,a,n):return rom[off(b,a):off(b,a)+n]
rows={x['id']:x for x in json.loads((r/'m6-work/raw_maps.json').read_text())['maps']};spec=[]
for code in [f'00-{i:02x}' for i in range(0x12,0x1f)]:
 row=rows[code];b,a=[int(x,16) for x in row['data'].split(':')];w,h=read(b,a,2);ps=list(struct.unpack('<9H',read(b,a+2,18)));layout=read(b,ps[0]+1,w*h);blocks=read(b,ps[1],1024);subs=read(b,ps[2],1024);attrs=list(read(b,ps[3],256));gfx=bytearray(8192)
 for cp in row['tileset_graphics']:gfx[cp['dest']-0x8000:cp['dest']-0x8000+cp['length']]=read(cp['bank'],cp['src'],cp['length'])
 palettes=[]
 for j in range(32):
  v=int.from_bytes(read(b,ps[4]+j*2,2),'little');palettes.extend([(v&31)*8,((v>>5)&31)*8,((v>>10)&31)*8,255])
 keys=[];tileAttrs=[];tiles=[]
 for y in range(h*4):
  for x in range(w*4):
   big=layout[(y//4)*w+x//4];sub=subs[blocks[big*4+(y%4)//2*2+(x%4)//2]*4+(y%2)*2+(x%2)];at=attrs[sub];q=0x1000+(sub if sub<128 else sub-256)*16;hh=2166136261;hh=((hh^(at&7))*16777619)&0xffffffff
   for yy in range(8):
    for xx in range(8):
     cx=7-xx if at&32 else xx;cy=7-yy if at&64 else yy;ci=((gfx[q+cy*2]>>(7-cx))&1)|(((gfx[q+cy*2+1]>>(7-cx))&1)<<1);hh=((hh^ci)*16777619)&0xffffffff
   keys.append(hh);tileAttrs.append(at);tiles.append(sub)
 art=o/'art'/f'{code}_gpt.png';impath=f'assets/region2/{code}_hd.webp'
 if art.exists():
  im=Image.open(art).convert('RGB');im.resize((w*32*4,h*32*4),Image.Resampling.LANCZOS).save(dest/f'{code}_hd.webp',quality=92,method=6)
 spec.append(dict(id=code,name={'00-12':'大名城外城','00-17':'大名城内城','00-1e':'大名府','00-19':'白胜家','00-1b':'醉仙楼'}.get(code,'大名城室内 '+code),width=w*32,height=h*32,widthTiles=w*4,heightTiles=h*4,image=impath,imageNativeSize=w*32,imageNativeHeight=h*32,cellKeys=keys,tiles=tiles,attrs=tileAttrs,palettes=palettes,geometrySHA256=row['geometry_sha256'],native=str(r/f'm6-work/screens/map_{code}.png'),gptSource=str(art),artReady=art.exists()))
(dest/'maps.json').write_text(json.dumps(spec,separators=(',',':'),ensure_ascii=False))
base=json.loads((r/'m6-work/region1/runtime/assets/region1/maps.json').read_text())
(o/'runtime/assets/region1/maps.json').write_text(json.dumps(base+spec,separators=(',',':'),ensure_ascii=False))
(o/'region2-scope.json').write_text(json.dumps({'region':'大名城','maps':[{'id':s['id'],'name':s['name'],'dimensions':[s['width'],s['height']],'native':s['native'],'artReady':s['artReady']} for s in spec]},indent=2,ensure_ascii=False))
print('region2 metadata',len(spec),'artReady',sum(s['artReady'] for s in spec),'total',len(base+spec))
