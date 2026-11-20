from pathlib import Path
from pyboy import PyBoy
from PIL import Image,ImageDraw
import json
r=Path('/workspace/shawu');o=r/'m6-work';p=PyBoy(str(r/'game.gbc'),window='null',sound_emulated=False);p.set_emulation_speed(0)
with (o/'states/manual.state').open('rb') as f:p.load_state(f)
steps=[]
def snap(tag):
 p.screen.image.save(o/'screens'/f'play3_{tag}.png');steps.append(dict(tag=tag,frame=p.frame_count,map=[p.memory[0xff9a],p.memory[0xff9b]],worldstate=p.memory[0xd0fa]));
 with (o/'states'/f'play3_{tag}.state').open('wb') as f:p.save_state(f)
def press(k,n=8,wait=90):
 p.button_press(k);p.tick(n,True);p.button_release(k);p.tick(wait,True)
press('left',8,20);snap('00_up')
for i in range(60):press('a',8,100);snap(f'{i+1:02d}_a')
for key in ['start','select','b']:
 press(key,8,90);snap(f'{key}')
p.stop(save=False);(o/'botplay.json').write_text(json.dumps(steps,indent=2))
qs=sorted((o/'screens').glob('play3*.png'));im=Image.new('RGB',(8*164,((len(qs)+7)//8)*162),(25,25,30));d=ImageDraw.Draw(im)
for i,f in enumerate(qs):x=i%8*164;y=i//8*162;im.paste(Image.open(f),(x,y));d.text((x+2,y+145),f.stem,fill='white')
im.save(o/'botplay3_contact.png')
