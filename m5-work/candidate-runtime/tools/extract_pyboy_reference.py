"""Reference only. PyBoy states are not compatible with Binjgb states."""
from pyboy import PyBoy
from PIL import Image
import json, math
from pathlib import Path
root=Path('/workspace/shawu'); out=root/'m1-work'
p=PyBoy(str(root/'game.gbc'),window='null',sound_emulated=False)
with open(root/'current.state','rb') as f:p.load_state(f)
im=p.screen.image.convert('RGB'); sprites=[p.get_sprite(i) for i in range(40) if p.get_sprite(i).on_screen]
unique={}
for y in range(0,137,8):
 for x in range(0,153,8):
  if any(x<s.x+s.shape[0] and x+8>s.x and y<s.y+s.shape[1] and y+8>s.y for s in sprites):continue
  tile=im.crop((x,y,x+8,y+8));key=tile.tobytes().hex()
  unique.setdefault(key,{'image':tile,'x':x,'y':y})
cols=16;rows=math.ceil(len(unique)/cols);atlas=Image.new('RGB',(cols*8,rows*8),(255,0,255));mapping=[]
for i,(key,t) in enumerate(unique.items()):
 atlas.paste(t['image'],(i%cols*8,i//cols*8));mapping.append({'index':i,'key':key,'source':[t['x'],t['y']]})
atlas.resize((cols*32,rows*32),Image.Resampling.NEAREST).save(out/'forest_reference_pyboy.png')
json.dump({'tiles':mapping,'note':'PyBoy RGB palette; browser RGB mapping must be extracted separately'},open(out/'pyboy_mapping.json','w'))
p.stop(save=False)
