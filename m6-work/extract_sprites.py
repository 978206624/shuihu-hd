from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib
R=Path('/workspace/shawu');O=R/'m6-work';b=(R/'game.gbc').read_bytes()
def rd(bk,a,n):i=bk*0x4000+a-0x4000;return b[i:i+n]
def w(x):return int.from_bytes(x,'little')
rows=[];im=Image.new('RGB',(15*96,7*104),(28,29,34));d=ImageDraw.Draw(im);font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',11)
for sid in range(105):
 if sid<18:bk,tab,ix=4,0x4762,sid
 elif sid<51:bk,tab,ix=0x22,0x4000,sid-18
 elif sid<104:bk,tab,ix=0x14,0x4000,sid-51
 else:bk,tab,ix=0xc,0x51ae,sid-104
 dp=w(rd(bk,tab+ix*2,2));seq=w(rd(bk,dp,2));frame=w(rd(bk,seq,2));gfx=rd(bk,frame,64);palptr=w(rd(4,0x421f+sid*2,2));pr=rd(4,palptr,8);pal=[]
 for j in range(4):v=w(pr[j*2:j*2+2]);pal.append(((v&31)*8,((v>>5)&31)*8,((v>>10)&31)*8,255 if j else 0))
 pic=Image.new('RGBA',(16,16));p=pic.load()
 for ty in range(2):
  for tx in range(2):
   tid=tx*2+ty
   for y in range(8):
    aa,bb=gfx[tid*16+y*2:tid*16+y*2+2]
    for x in range(8):z=(aa>>(7-x)&1)|((bb>>(7-x)&1)<<1);p[tx*8+x,ty*8+y]=pal[z]
 path=O/'screens'/f'actor_{sid:03d}.png';pic.save(path);x=sid%15*96;y=sid//15*104;scaled=pic.resize((64,64),Image.Resampling.NEAREST);im.paste(scaled,(x+16,y+4),scaled);d.text((x+4,y+72),f'actor {sid:03d}',fill='white',font=font);d.text((x+4,y+87),f'{bk:02x}:{dp:04x}',fill='#bbb',font=font)
 rows.append(dict(id=sid,bank=bk,direction_table=f'{dp:04x}',first_frame=f'{frame:04x}',palette_pointer=f'04:{palptr:04x}',first_frame_sha256=hashlib.sha256(gfx).hexdigest(),screenshot=str(path),note='animation resource ID, not necessarily one human identity'))
im.save(O/'actor_catalog.png');(O/'actor_catalog.json').write_text(json.dumps(rows,indent=2));print('actor IDs',len(rows),'unique firstframe patterns',len(set(r['first_frame_sha256'] for r in rows)))
