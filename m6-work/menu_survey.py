from pathlib import Path
from pyboy import PyBoy
from PIL import Image,ImageDraw
import json
r=Path('/workspace/shawu');o=r/'m6-work';p=PyBoy(str(r/'game.gbc'),window='null',sound_emulated=False);p.set_emulation_speed(0);rom=(r/'game.gbc').read_bytes();rows=[]
for i in range(25):
 with (o/'states/poke_074.state').open('rb') as f:p.load_state(f)
 p.memory[0xffba]=3;p.memory[0xffc5]=i;p.memory[0xd087]=1;p.memory[0xd0ef]=0
 p.tick(120,True);fn=o/'screens'/f'menu_script_{i:02d}.png';p.screen.image.save(fn);ptr=int.from_bytes(rom[0x24*0x4000+0xc3+i*2:0x24*0x4000+0xc5+i*2],'little');rows.append(dict(id=i,entry=f'24:{ptr:04x}',screenshot=str(fn),current_menu=p.memory[0xffc5],menu_state=p.memory[0xd087]))
(o/'menu_survey.json').write_text(json.dumps(rows,indent=2));p.stop(save=False);im=Image.new('RGB',(5*164,5*162),(26,27,31));d=ImageDraw.Draw(im)
for i,q in enumerate(rows):x=i%5*164;y=i//5*162;im.paste(Image.open(q['screenshot']),(x,y));d.text((x+2,y+145),f"script {i:02d} {q['entry']}",fill='white')
im.save(o/'menu_script_contact.png');print('DONE',len(rows),flush=True)
