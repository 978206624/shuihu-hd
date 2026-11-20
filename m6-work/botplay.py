from pathlib import Path
from pyboy import PyBoy
from PIL import Image,ImageDraw
import json
r=Path('/workspace/shawu');o=r/'m6-work';p=PyBoy(str(r/'game.gbc'),window='null',sound_emulated=False);p.set_emulation_speed(0)
with (r/'advance_300.state').open('rb') as f:p.load_state(f)
steps=[]
def snap(tag):
 p.screen.image.save(o/'screens'/f'play_{tag}.png');steps.append(dict(tag=tag,frame=p.frame_count,map=[p.memory[0xff9a],p.memory[0xff9b]],worldstate=p.memory[0xd0fa]));
 with (o/'states'/f'play_{tag}.state').open('wb') as f:p.save_state(f)
def press(k,n=1,wait=90):p.button(k,n);p.tick(wait,True)
press('up',32,32);snap('00_up')
for i in range(60):press('a',1,100);snap(f'{i+1:02d}_a')
for key in ['start','select','b']:
 press(key,1,90);snap(f'{key}')
p.stop(save=False);(o/'botplay.json').write_text(json.dumps(steps,indent=2))
qs=sorted((o/'screens').glob('play*.png'));im=Image.new('RGB',(8*164,((len(qs)+7)//8)*162),(25,25,30));d=ImageDraw.Draw(im)
for i,f in enumerate(qs):x=i%8*164;y=i//8*162;im.paste(Image.open(f),(x,y));d.text((x+2,y+145),f.stem,fill='white')
im.save(o/'botplay_contact.png')
