from pathlib import Path
from PIL import Image,ImageDraw
import json,math
root=Path('/workspace/shawu');work=root/'m1-work';caps=json.load(open(work/'forest-captures.json'));tiles={}
for ci,c in enumerate(caps):
 
 if all(v==255 for v in c['oam']):continue
 r=c['reference'];im=Image.frombytes('RGBA',(160,144),bytes(r['pixels']));im.save(work/f'forest_source_{ci}.png');mask=Image.new('L',(160,144),255);d=ImageDraw.Draw(mask)
 for i in range(0,160,4):
  sy,sx=c['oam'][i]-16,c['oam'][i+1]-8
  d.rectangle((sx-8,sy-8,sx+15,sy+(16 if c['lcdc']&4 else 8)+7),fill=0)
 if c['lcdc']&32 and c['wx']<167 and c['wy']<144:d.rectangle((max(0,c['wx']-7),c['wy'],159,143),fill=0)
 mask.save(work/f'forest_preserve_mask_{ci}.png')
 for t in r['tiles']:
  x,y=t['x'],t['y']
  if mask.crop((x,y,x+8,y+8)).getextrema()[0]!=255:continue
  tiles.setdefault(t['key'],dict(source=[ci,x,y],image=im.crop((x,y,x+8,y+8))))
cols=16;rows=math.ceil(len(tiles)/cols);atlas=Image.new('RGB',(cols*32,rows*32),(255,0,255));mapping=[]
for i,(key,t) in enumerate(tiles.items()):
 atlas.paste(t['image'].resize((32,32),Image.Resampling.NEAREST),(i%cols*32,i//cols*32));mapping.append(dict(index=i,key=key,source=t['source']))
atlas.save(work/'forest_reference.png');json.dump(dict(version=1,tileSize=32,columns=cols,rows=rows,tiles=mapping,status='awaiting approved GPT atlas',provenance='Exact browser framebuffer RGB cells; OAM and window masked; no art generated'),open(root/'web/assets/forest/mapping.json','w'))
req=json.load(open(work/'asset-request.json'));req.update(status='ready for GPT edit',width=cols*32,height=rows*32,tile_count=len(tiles),rows=rows,columns=cols,reference_atlas_path=str(work/'forest_reference.png'),source_screenshot_path=str(work/'forest_source_1.png'),preserve_mask_path=str(work/'forest_preserve_mask_1.png'),unused_cells='Trailing magenta cells are unused; keep them magenta',instructions='Redraw each 32x32 cell in place as detailed top-down RPG forest texture. Each is one original 8x8 tile, not a whole tree or scene. Preserve exact edge connections, terrain geometry, water/land boundaries, major color regions. Never move, merge or rearrange cells. No actors, letters, UI or perspective. Output exactly the same atlas dimensions. Use source screenshot only for environmental context.');req['grid'].update(rows=rows,columns=cols);json.dump(req,open(work/'asset-request.json','w'),ensure_ascii=False,indent=2)
print({'tiles':len(tiles),'atlas':[cols*32,rows*32]})
