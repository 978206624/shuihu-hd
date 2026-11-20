import json,collections,hashlib
from pathlib import Path
from PIL import Image,ImageDraw
R=Path('/workspace/shawu/m3-work');S=json.loads((R/'states.json').read_text());groups=[]
for s in S:
 valid=[i for i,t in enumerate(s['tiles']) if t<160]
 best=None;score=0
 for g in groups:
  inds=[i for i in valid if g['tiles'][i]<160];n=sum(s['tiles'][i]==g['tiles'][i] and s['attrs'][i]==g['attrs'][i] for i in inds)
  ratio=n/len(inds) if inds else 0
  if ratio>score:best,score=g,ratio
 if score<.94:
  best={'id':'map_%02d'%len(groups),'tiles':s['tiles'].copy(),'attrs':s['attrs'].copy(),'states':[]};groups.append(best)
 best['states'].append(s);s['group']=best['id']
 for i in valid:
  if best['tiles'][i]>=160:best['tiles'][i]=s['tiles'][i];best['attrs'][i]=s['attrs'][i]
(R/'catalog').mkdir(exist_ok=True)
summary=[]
for g in groups:
 states=g['states'];im=Image.new('RGBA',(256,256));seen=set();observed=set();sources={}
 # Prefer snapshots with richest colors, avoiding fades and stale black palettes.
 candidates=sorted(states,key=lambda s:len(Image.open(R/(s['path']+'_map.png')).getcolors(65536) or []),reverse=True)
 for s in candidates:
  bg=Image.open(R/(s['path']+'_map.png')).convert('RGBA');sx,sy=s['scroll']
  for k,t in enumerate(s['tiles']):
   if t>=160:continue
   x=k%32*8;y=k//32*8
   if k not in seen:im.paste(bg.crop((x,y,x+8,y+8)),(x,y));seen.add(k);sources[str(k)]=s['frame']
   if any(0<=((x-sx+i)%256)<160 for i in range(8)) and any(0<=((y-sy+i)%256)<144 for i in range(8)):observed.add(k)
 im.save(R/'catalog'/f"{g['id']}_map_reference.png")
 rep=max(states,key=lambda s:len(Image.open(R/(s['path']+'_orig.png')).getcolors(65536) or []));Image.open(R/(rep['path']+'_orig.png')).save(R/'catalog'/f"{g['id']}_orig.png")
 item={'id':g['id'],'firstFrame':min(s['frame'] for s in states),'lastFrame':max(s['frame'] for s in states),'stateCount':len(states),'representativeFrame':rep['frame'],'representative':rep['path'],'scrolls':sorted(set(tuple(s['scroll']) for s in states)),'tilemapSHA256':hashlib.sha256(bytes(g['tiles'])+bytes(g['attrs'])).hexdigest(),'nativeBounds':[0,0,256,256],'actualObservedCells':sorted(observed),'referenceCells':len(seen),'unknownCells':1024-len(seen),'sourceFrames':sources,'gaps':['尚未生成/验收 M3 GPT 图','透明区域为没有获得无 UI 几何的格，不得臆造']}
 summary.append(item)
json.dump(summary,open(R/'catalog/maps.json','w'),ensure_ascii=False,indent=2);json.dump([{k:v for k,v in s.items() if k not in ['tiles','attrs']} for s in S],open(R/'catalog/states.json','w'),ensure_ascii=False)
c=Image.new('RGB',(800,((len(summary)+3)//4)*180),'#222');d=ImageDraw.Draw(c)
for i,g in enumerate(summary):
 x=i%4*200;y=i//4*180;c.paste(Image.open(R/'catalog'/f"{g['id']}_orig.png"),(x,y));d.text((x,y+146),f"{g['id']} {g['firstFrame']}-{g['lastFrame']}",fill='white')
c.save(R/'catalog/contact.png');print([(g['id'],g['firstFrame'],g['lastFrame'],g['stateCount']) for g in summary])
