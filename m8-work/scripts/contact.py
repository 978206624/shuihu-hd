from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import os,json
R=Path(__file__).resolve().parents[2];W=R/'m8-work';out=Path(os.environ['M8_RESULTS'])
items=json.loads((W/'inputs/preview.json').read_text());dest=R/'shots/m8_region3_contact.png'
assert not dest.exists(),'Refusing to replace contact evidence'
font=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',22)
small=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',17)
im=Image.new('RGB',(1320,90+len(items)*635),(22,28,33));d=ImageDraw.Draw(im)
d.text((18,10),'M8 东溪村及连通林道：左原生 / 右整合后运行画面',font=font,fill='white')
d.text((18,44),'同一自然按键终点；原人物与文字；8个独立门路摘录，不代表连续旅程或全部世界',font=small,fill=(195,205,213))
for i,item in enumerate(items):
    top=90+i*635;d.text((18,top),item['id']+' '+item['name'],font=font,fill=(232,220,177))
    for j,suffix in enumerate(['native','hd']):
        a=Image.open(out/'qa'/f"{item['id']}-{suffix}.png").convert('RGB');assert a.size==(640,576)
        im.paste(a,(10+j*660,top+36))
dest.parent.mkdir(exist_ok=True);im.save(dest)
print(str(dest),im.size)
