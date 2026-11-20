from pathlib import Path
from pyboy import PyBoy
from PIL import Image,ImageDraw
import json
r=Path('/workspace/shawu');o=r/'m6-work';p=PyBoy(str(r/'game.gbc'),window='null',sound_emulated=False);p.set_emulation_speed(0)
with (o/'states/manual.state').open('rb') as f:p.load_state(f)
def walk(k,a,target):
 p.button_press(k)
 for _ in range(200):
  p.tick(1,True)
  if p.memory[a]==target:break
 p.button_release(k);p.tick(20,True);print(k,bytes(p.memory[0xcd00:0xcd08]).hex(' '),flush=True)
def press(k,n=8,wait=90):p.button_press(k);p.tick(n,True);p.button_release(k);p.tick(wait,True)
def snap(i):
 p.screen.image.save(o/'screens'/f'tut_{i:03d}.png')
 with (o/'states'/f'tut_{i:03d}.state').open('wb') as f:p.save_state(f)
walk('down',0xcd00,64);walk('left',0xcd01,88);press('up',8,20);snap(0)
for i in range(1,100):press('a',8,100);snap(i)
press('start');snap(100)
p.stop(save=False)
qs=sorted((o/'screens').glob('tut*.png'));im=Image.new('RGB',(8*164,((len(qs)+7)//8)*162),(25,25,30));d=ImageDraw.Draw(im)
for i,f in enumerate(qs):x=i%8*164;y=i//8*162;im.paste(Image.open(f),(x,y));d.text((x+2,y+145),f.stem,fill='white')
im.save(o/'tutorial_contact.png')
