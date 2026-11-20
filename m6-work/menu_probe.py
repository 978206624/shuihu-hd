from pathlib import Path
from pyboy import PyBoy
from PIL import Image,ImageDraw
r=Path('/workspace/shawu');o=r/'m6-work';p=PyBoy(str(r/'game.gbc'),window='null',sound_emulated=False);p.set_emulation_speed(0)
with (o/'states/poke_074.state').open('rb') as f:p.load_state(f)
p.memory[0xffba]=3
for i,k in enumerate(['start','a','b','down','a','b','down','a','b','down','a','b','down','a','b','down','a','b','down','a','b']):
 p.button_press(k);p.tick(8,True);p.button_release(k);p.tick(90,True);p.screen.image.save(o/'screens'/f'menu_probe_{i:02d}_{k}.png')
 with (o/'states'/f'menu_probe_{i:02d}_{k}.state').open('wb') as f:p.save_state(f)
p.stop(save=False)
qs=sorted((o/'screens').glob('menu_probe*.png'));im=Image.new('RGB',(6*164,((len(qs)+5)//6)*162),(25,25,30));d=ImageDraw.Draw(im)
for i,f in enumerate(qs):x=i%6*164;y=i//6*162;im.paste(Image.open(f),(x,y));d.text((x+2,y+145),f.stem,fill='white')
im.save(o/'menu_contact.png')
