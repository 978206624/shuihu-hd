from pyboy import PyBoy
from pathlib import Path
import json,hashlib
r=Path('/workspace/shawu');o=r/'m6-work';p=PyBoy(str(r/'game.gbc'),window='null',sound_emulated=False);p.set_emulation_speed(0)
with (r/'advance_300.state').open('rb') as f:p.load_state(f)
log=[]
def snap(s):
 p.screen.image.save(o/'screens'/f'exp_{s}.png');(o/'raw'/f'exp_{s}.ram').write_bytes(bytes(p.memory[0xc000:0x10000]));
 with (o/'states'/f'exp_{s}.state').open('wb') as f:p.save_state(f)
 log.append(dict(tag=s,frame=p.frame_count,scx=p.memory[0xff43],scy=p.memory[0xff42]))
for i in range(35):
 p.button('a',10);p.tick(120,True);snap(f'a{i:02d}')
for d in ['down','down','down','left','down','down','right','up']:
 p.button(d,90);p.tick(90,True);snap(f'{len(log):02d}_{d}')
(o/'explore-log.json').write_text(json.dumps(log,indent=2));p.stop(save=False)
