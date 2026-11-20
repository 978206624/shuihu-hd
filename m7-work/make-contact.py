from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json
r=Path('/workspace/shawu');o=r/'m7-work';items=json.loads((o/'region2-scope.json').read_text())['maps']
font=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',18)
w=1260;row=350;im=Image.new('RGB',(w,60+row*len(items)),(24,29,33));d=ImageDraw.Draw(im)
d.text((20,15),'M7 大名城区域 · 左：原生整图 / 右：GPT高清整图（人物与文字仍由原引擎绘制）',font=font,fill='white')
for i,item in enumerate(items):
 code=item['id'];top=60+i*row;d.text((20,top),code+' '+item['name'],font=font,fill=(224,220,180))
 for j,p in enumerate([r/f'm6-work/screens/map_{code}.png',o/f'art/{code}_gpt.png']):
  a=Image.open(p).convert('RGB');scale=min(590/a.width,300/a.height);a=a.resize((round(a.width*scale),round(a.height*scale)),Image.Resampling.NEAREST if not j else Image.Resampling.LANCZOS);im.paste(a,(j*630+(630-a.width)//2,top+28))
im.save(r/'shots/m7_region2_contact.png');print(im.size)
