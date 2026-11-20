from pathlib import Path
from pyboy import PyBoy
from PIL import Image
import json,numpy as np,hashlib,traceback
r=Path('/workspace/shawu');o=r/'m6-work';rows=json.loads((o/'raw_maps.json').read_text())['maps'];p=PyBoy(str(r/'game.gbc'),window='null',sound_emulated=False);p.set_emulation_speed(0);results=[]
for k,m in enumerate(rows):
 try:
  with (o/'states/exp_42_up.state').open('rb') as f:p.load_state(f)
  for addr,val in [(0xff9a,m['group']),(0xff9b,m['map_index']),(0xff9c,0),(0xd9d2,0),(0xd0ef,0),(0x2000,5),(0xd08f,5)]:p.memory[addr]=val
  p.register_file.PC=0x41d9;shots=[];target=None
  for fnum in [30,60,120]:
   p.tick(30 if fnum<120 else 60,True);arr=p.screen.ndarray.copy();actual=[p.memory[0xff9a],p.memory[0xff9b]];detail=dict(frame=fnum,actual=actual,std=float(arr[:,:,:3].std()),pc=p.register_file.PC,dimensions=[p.memory[0xff98]*4,p.memory[0xff99]*4],data=f'{p.memory[0xffb2]:02x}:{p.memory[0xd0cb]+256*p.memory[0xd0cc]:04x}')
   shots.append(detail)
   if actual==[m['group'],m['map_index']] and detail['std']>10:
    path=o/'screens'/f"native_{m['id']}.png";p.screen.image.save(path);target=detail|dict(screenshot=str(path));(o/'raw'/f"native_{m['id']}.ram").write_bytes(bytes(p.memory[0xc000:0x10000]))
  results.append(dict(id=m['id'],verified=target is not None,best=target,samples=shots))
 except Exception as e:results.append(dict(id=m['id'],verified=False,error=repr(e)))
 (o/'dynamic_maps.json').write_text(json.dumps(results,indent=2))
 if k%10==0:print(k,m['id'],'verified',sum(x['verified'] for x in results),flush=True)
p.stop(save=False);print('DONE',len(results),sum(x['verified'] for x in results),flush=True)
