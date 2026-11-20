from pyboy import PyBoy
from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
import json,hashlib
root=Path('/workspace/shawu');out=root/'m6-work';p=PyBoy(str(root/'game.gbc'),window='null',sound_emulated=False);p.set_emulation_speed(0)
files=sorted(root.glob('*.state'),key=lambda a:(not a.stem.startswith('advance'),int(a.stem[8:]) if a.stem[8:].isdigit() else 999,a.name))
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',11)
cs=Image.new('RGB',(8*164,((len(files)+7)//8)*166),(30,30,35));rows=[]
for i,f in enumerate(files):
 with f.open('rb') as fp:p.load_state(fp)
 im=p.screen.image.convert('RGB');im.save(out/'screens'/f'{f.stem}.png');x=i%8*164;y=i//8*166;cs.paste(im,(x,y));ImageDraw.Draw(cs).text((x,y+145),f.stem,fill='white',font=font)
 ram=bytes(p.memory[0xc000:0x10000]);(out/'raw'/f'{f.stem}.ram').write_bytes(ram)
 rows.append(dict(state=f.name,screen_sha=hashlib.sha256(im.tobytes()).hexdigest(),lcdc=p.memory[0xff40],scx=p.memory[0xff43],scy=p.memory[0xff42]))
cs.save(out/'states_contact.png');(out/'state_survey.json').write_text(json.dumps(rows,indent=2));p.stop(save=False)
