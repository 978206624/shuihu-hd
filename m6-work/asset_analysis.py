from pathlib import Path
import json,hashlib,collections,struct
R=Path('/workspace/shawu');O=R/'m6-work';rom=(R/'game.gbc').read_bytes();ms=json.loads((O/'raw_maps.json').read_text())['maps'];specs=json.loads((R/'web/assets/maps/m3_signatures.json').read_text());specs=[s for s in specs if s['name']!='intertitle-backdrop']
def off(b,a):return b*0x4000+a-0x4000 if a>=0x4000 else a
def rd(b,a,n):return rom[off(b,a):off(b,a)+n]
results=[];ts={};gfxset={};sigs={};alltiles=set()
for m in ms:
 bk=int(m['data'].split(':')[0],16);ps=m['pointers'];gfx=bytearray(8192)
 for c in m['tileset_graphics']:gfx[c['dest']-0x8000:c['dest']-0x8000+c['length']]=rd(c['bank'],c['src'],c['length'])
 attrs=rd(bk,ps[3],256);grid=rd(bk,ps[0]+1,m['area_tiles']//16);bs=rd(bk,ps[1],1024);sm=rd(bk,ps[2],1024);w=m['width_tiles'];h=m['height_tiles'];keys=[];tileids=[];pats=[]
 for y in range(h):
  for x in range(w):
   bid=grid[(y//4)*(w//4)+x//4];sub=bs[bid*4+(y//2%2)*2+(x//2%2)];t=sm[sub*4+y%2*2+x%2];a=attrs[t];addr=0x1000+(t if t<128 else t-256)*16;tile=gfx[addr:addr+16];hv=((2166136261^(a&7))*16777619)&0xffffffff
   for yy in range(8):
    for xx in range(8):ci=(tile[2*yy]>>(7-xx)&1)|((tile[2*yy+1]>>(7-xx)&1)<<1);hv=((hv^ci)*16777619)&0xffffffff
   keys.append(hv);tileids.append(t);pats.append(bytes(tile));alltiles.add(bytes(tile))
 gfxid=hashlib.sha256(gfx).hexdigest()[:12];gfxset.setdefault(gfxid,[]).append(m['id']);tsid=hashlib.sha256(gfx+attrs).hexdigest()[:12];ts.setdefault(tsid,[]).append(m['id'])
 matches=[]
 for s in specs:
  ks=s['cellKeys'];bounds=s['bounds'];good=0;visible=0;okview=0
  for y in range(min(h,32)):
   for x in range(min(w,32)):
    hv=keys[y*w+x];hit=(hv in ks[y*32+x] and bounds[0]<=x*8<bounds[2] and bounds[1]<=y*8<bounds[3] and (not s.get('verifiedYRanges') or any(lo<=y*8<hi for lo,hi in s['verifiedYRanges'])))
    good+=hit
    if x<20 and y<18:visible+=1;okview+=hit
  matches.append(dict(name=s['name'],matched_area_tiles=good,total_area_tiles=w*h,top_left_view_ratio=okview/visible))
 results.append(dict(id=m['id'],gfx_id=gfxid,tileset_geometry_id=tsid,used_native_tile_count=len(set(tileids)),unique_tile_patterns=len(set(pats)),best_hd_match=max(matches,key=lambda x:x['top_left_view_ratio']),hd_matches=matches,cellkeys=keys))
(O/'map_asset_analysis.json').write_text(json.dumps(results,indent=2));(O/'tileset_catalog.json').write_text(json.dumps(dict(graphics_bundles=gfxset,graphics_attribute_bundles=ts,unique_native_bg_patterns=len(alltiles)),indent=2));print('gfx',len(gfxset),'gfx+attrs',len(ts),'unique tiles',len(alltiles))
for m in results:
 if m['best_hd_match']['top_left_view_ratio']>=.80:print(m['id'],m['best_hd_match'])
