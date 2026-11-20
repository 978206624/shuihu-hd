from pathlib import Path
from pyboy import PyBoy
from PIL import Image,ImageDraw
import json
r=Path('/workspace/shawu');o=r/'m6-work';rom=(r/'game.gbc').read_bytes();p=PyBoy(str(r/'game.gbc'),window='null',sound_emulated=False);p.set_emulation_speed(0);rows=[]
for i in range(1,23):
 bk=rom[0x257+i*3];ad=int.from_bytes(rom[0x258+i*3:0x25a+i*3],'little')
 with (o/'states/manual.state').open('rb') as f:p.load_state(f)
 p.memory[0x2000]=bk;p.memory[0xd08f]=bk;p.memory[0xd0fa]=i;p.register_file.PC=ad
 try:
  p.tick(150,True);path=o/'screens'/f'mode_{i:02d}.png';p.screen.image.save(path)
  with (o/'states'/f'mode_{i:02d}.state').open('wb') as f:p.save_state(f)
  rows.append(dict(mode=i,entry=f'{bk:02x}:{ad:04x}',screenshot=str(path),current_mode=p.memory[0xd0fa],pc=p.register_file.PC));print(i,f'{bk:02x}:{ad:04x}',p.memory[0xd0fa],flush=True)
 except Exception as e:rows.append(dict(mode=i,error=repr(e)))
 (o/'mode_survey.json').write_text(json.dumps(rows,indent=2))
p.stop(save=False)
qs=sorted((o/'screens').glob('mode*.png'));im=Image.new('RGB',(6*164,((len(qs)+5)//6)*162),(25,25,30));d=ImageDraw.Draw(im)
for i,f in enumerate(qs):x=i%6*164;y=i//6*162;im.paste(Image.open(f),(x,y));d.text((x+2,y+145),f.stem,fill='white')
im.save(o/'mode_contact.png')
