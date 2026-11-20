from pathlib import Path
from pyboy import PyBoy
import json
r=Path('/workspace/shawu');o=r/'m6-work';p=PyBoy(str(r/'game.gbc'),window='null',sound_emulated=False);p.set_emulation_speed(0)
for g,m in [(0,7),(0,0),(0,8),(1,0),(2,0),(3,0)]:
 with (o/'states/exp_42_up.state').open('rb') as f:p.load_state(f)
 for addr,val in [(0xff9a,g),(0xff9b,m),(0xff9c,0),(0xd9d2,0),(0xd0ef,0),(0x2000,5),(0xd08f,5)]:p.memory[addr]=val
 p.register_file.PC=0x41d9
 for t in [30,30,60]:p.tick(t,True)
 p.screen.image.save(o/'screens'/f'warp_{g:02x}-{m:02x}.png')
 with (o/'states'/f'warp_{g:02x}-{m:02x}.state').open('wb') as f:p.save_state(f)
 print(g,m,hex(p.register_file.PC),bytes(p.memory[0xff96:0xff9d]).hex(' '),bytes(p.memory[0xd0cb:0xd0cf]).hex(' '),flush=True)
p.stop(save=False)
