from pathlib import Path
import json,collections
O=Path('/workspace/shawu/m6-work');rom=Path('/workspace/shawu/game.gbc').read_bytes();j=json.loads((O/'raw_maps.json').read_text());ms=j['maps']
def rd(b,a,n):i=b*16384+a-16384;return rom[i:i+n]
def w(b):return int.from_bytes(b,'little')
headers=collections.defaultdict(set);warps=collections.defaultdict(set)
for m in ms:
 b,a=(int(q,16) for q in m['header'].split(':'));headers[b].add(a);v=rd(b,a+6,12);q=w(v[10:12]);
 if 0x4000<=q<0x8000:warps[b].add(q)
allwarps={};npcids=set();bad=[];edges=[]
for m in ms:
 b,a=(int(q,16) for q in m['header'].split(':'));end=min([x for x in headers[b]|warps[b] if x>a]+[0x8000]);vs=[]
 for p in range(a+6,end-11,12):
  v=rd(b,p,12);q=w(v[10:]);nb=v[4];np=w(v[8:10]);wr=[];term=False
  for z in range(42):
   raw=rd(b,q+z*6,6)
   if not raw:break
   if raw[0]==255:term=True;break
   wr.append(dict(x=raw[0],y=raw[1],type=raw[2],args=list(raw[3:]),raw=raw.hex(' ')))
   if raw[2] in (0,3):
    group=m['group'] if raw[2]==0 else raw[5];dest=f'{group:02x}-{raw[3]:02x}'
    if dest in {x['id'] for x in ms}:edges.append(dict(source=m['id'],variant=len(vs),dest=dest,dest_entry=raw[4],warp_pointer=f'{b:02x}:{q:04x}'))
  key=f'{b:02x}:{q:04x}'
  if not (0x4000<=q<0x8000 and term):
   bad.append((m['id'],p,key));break
  allwarps[key]=dict(pointer=key,terminated=term,records=wr)
  nr=[];nt=False
  if 0x4000<=np<0x8000 and nb<128:
   for z in range(64):
    rec=rd(nb,np+11*z,11)
    if not rec:break
    if rec[0]==0x88:nt=True;break
    nr.append(rec[0]);npcids.add(rec[0])
  # rejected trailing unrelated resource data is excluded
  vs.append(dict(offset=f'{b:02x}:{p:04x}',raw=v.hex(' '),start_xy=list(v[:2]),camera_raw=list(v[2:4]),npc_bank=nb,npc_pointer=np,npc_record_count=len(nr) if nt else None,npc_actor_ids=nr if nt else [],warp_pointer=q,warp_table=key,warp_count=len(wr),warp_terminated=term))
 m['variants']=vs;m['entrance_boundary']=f'{b:02x}:{end:04x}';m['entrance_padding_bytes']=(end-a-6)%12
edges=[e for e in edges if e['variant']<len(next(m for m in ms if m['id']==e['source'])['variants'])]
(O/'raw_maps.json').write_text(json.dumps(j,indent=2));(O/'warp_catalog.json').write_text(json.dumps(dict(warp_tables=allwarps,known_map_edges=edges,npc_actor_ids=sorted(npcids)),indent=2))
print('variants',sum(len(m['variants']) for m in ms),'max',max(len(m['variants']) for m in ms),'warptables',len(allwarps),'records',sum(len(x['records']) for x in allwarps.values()),'edges',len(edges),'bad',bad);print('last',[(m['id'],len(m['variants']),m['entrance_padding_bytes']) for m in ms if m['id'] in ['00-35','01-87','02-4c','03-2d']]);print('npc ids',sorted(npcids))
