from pathlib import Path
from pyboy import PyBoy
from PIL import Image,ImageDraw
r=Path('/workspace/shawu');o=r/'m6-work';p=PyBoy(str(r/'game.gbc'),window='null',sound_emulated=False);p.set_emulation_speed(0)
with (o/'states/manual.state').open('rb') as f:p.load_state(f)
for a,v in [(0xcd00,64),(0xcd01,88),(0xcd03,1),(0xcd05,0),(0xcd06,0),(0xcd07,0)]:p.memory[a]=v
p.tick(30,True);p.screen.image.save(o/'screens/poke_start.png')
for i in range(75):
 p.button_press('a');p.tick(8,True);p.button_release('a');p.tick(100,True);p.screen.image.save(o/'screens'/f'poke_{i:03d}.png')
 with (o/'states'/f'poke_{i:03d}.state').open('wb') as f:p.save_state(f)
p.stop(save=False)
qs=sorted((o/'screens').glob('poke*.png'));im=Image.new('RGB',(8*164,((len(qs)+7)//8)*162),(25,25,30));d=ImageDraw.Draw(im)
for i,f in enumerate(qs):x=i%8*164;y=i//8*162;im.paste(Image.open(f),(x,y));d.text((x+2,y+145),f.stem,fill='white')
im.save(o/'poke_contact.png')
