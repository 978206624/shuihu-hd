from pathlib import Path
from pyboy import PyBoy
from PIL import Image,ImageDraw
import random,json
r=Path('/workspace/shawu');o=r/'m6-work';p=PyBoy(str(r/'game.gbc'),window='null',sound_emulated=False);p.set_emulation_speed(0);random.seed(42)
with (o/'states/poke_074.state').open('rb') as f:p.load_state(f)
for a,v in [(0xffba,3),(0xff9a,0),(0xff9b,0),(0xff9c,0),(0xd9d2,0),(0xd0ef,0),(0x2000,5),(0xd08f,5)]:p.memory[a]=v
p.register_file.PC=0x41d9;p.tick(30,True);log=[]
for i in range(150):
 k=random.choice(['up','down','left','right']);p.button_press(k);p.tick(50,True);p.button_release(k);p.tick(30,True)
 if i%7==0:p.button_press('a');p.tick(8,True);p.button_release('a');p.tick(40,True)
 p.screen.image.save(o/'screens'/f'wild_{i:03d}.png');log.append(dict(i=i,button=k,bank=p.memory[0xd08f],pc=p.register_file.PC,map=[p.memory[0xff9a],p.memory[0xff9b]],bc=p.memory[0xffbc],d0fa=p.memory[0xd0fa]))
 if i%10==0:
  with (o/'states'/f'wild_{i:03d}.state').open('wb') as f:p.save_state(f)
 (o/'wild_play.json').write_text(json.dumps(log,indent=2))
p.stop(save=False)
qs=sorted((o/'screens').glob('wild*.png'));im=Image.new('RGB',(10*164,((len(qs)+9)//10)*162),(25,25,30));d=ImageDraw.Draw(im)
for i,f in enumerate(qs):x=i%10*164;y=i//10*162;im.paste(Image.open(f),(x,y));d.text((x+2,y+145),f.stem,fill='white')
im.save(o/'wild_contact.png')
