from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json
r=Path('/workspace/shawu/m6-work');rows=json.loads((r/'raw_maps.json').read_text())['maps'];font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',12)
for group in range(4):
 ms=[m for m in rows if m['group']==group]
 for part in range((len(ms)+47)//48):
  qs=ms[part*48:part*48+48];im=Image.new('RGB',(8*166,((len(qs)+7)//8)*152),(28,29,34));d=ImageDraw.Draw(im)
  for i,m in enumerate(qs):
   x=i%8*166;y=i//8*152;pic=Image.open(m['screenshot']);pic.thumbnail((160,124),Image.Resampling.NEAREST);im.paste(pic,(x+(160-pic.width)//2,y));d.text((x+2,y+126),f"{m['id']} {m['width_tiles']}x{m['height_tiles']}",font=font,fill='white')
  im.save(r/f'maps_group{group}_{part}.png')
