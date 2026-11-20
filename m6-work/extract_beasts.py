from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib
R=Path('/workspace/shawu');O=R/'m6-work';b=(R/'game.gbc').read_bytes()
def rd(bk,a,n):i=bk*0x4000+a-0x4000;return b[i:i+n]
def w(x):return int.from_bytes(x,'little')
rows=[];im=Image.new('RGB',(12*104,11*120),(28,29,34));d=ImageDraw.Draw(im);font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',12)
for sid in range(131):
 bk=0x27 if sid<28 else 0x28 if sid<56 else 0x29 if sid<84 else 0x2a if sid<111 else 0x63;addr=w(b[0xa22+sid*2:0xa24+sid*2]);gfx=rd(bk,addr,0x240);pp=w(rd(0x26,0x4d45+sid*2,2));pr=rd(0x26,pp,8);pal=[]
 for j in range(4):v=w(pr[j*2:j*2+2]);pal.append(((v&31)*8,((v>>5)&31)*8,((v>>10)&31)*8,255 if j else 0))
 pic=Image.new('RGBA',(48,48));p=pic.load()
 for ty in range(6):
  for tx in range(6):
   tid=ty*6+tx
   for y in range(8):
    aa,bb=gfx[tid*16+y*2:tid*16+y*2+2]
    for x in range(8):z=(aa>>(7-x)&1)|((bb>>(7-x)&1)<<1);p[tx*8+x,ty*8+y]=pal[z]
 path=O/'screens'/f'beast_{sid:03d}.png';pic.save(path);x=sid%12*104;y=sid//12*120;scaled=pic.resize((96,96),Image.Resampling.NEAREST);im.paste(scaled,(x+4,y),scaled);d.text((x+4,y+98),f'beast {sid:03d}',fill='white',font=font)
 rows.append(dict(id=sid,graphics=f'{bk:02x}:{addr:04x}',palette=f'26:{pp:04x}',nonzero_bytes=sum(c!=0 for c in gfx),distinct_colors=len(set(pr[i:i+2] for i in range(0,8,2))),graphics_sha256=hashlib.sha256(gfx).hexdigest(),screenshot=str(path)))
im.save(O/'beast_catalog.png');(O/'beast_catalog.json').write_text(json.dumps(rows,indent=2));print('slots',len(rows),'nonblank',sum(q['nonzero_bytes']>0 for q in rows),'uniquegfx',len(set(q['graphics_sha256'] for q in rows)));print('blank',[q for q in rows if q['nonzero_bytes']==0])
