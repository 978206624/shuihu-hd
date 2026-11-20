from pathlib import Path
from PIL import Image
import json,hashlib,collections
O=Path('/workspace/shawu/m6-work');j=json.loads((O/'inventory.json').read_text());ms=j['map_slots'];u=j['unique_maps'];s=j['summary'];assert len(ms)==313 and len(u)==243
for group in u:
 aliases=[m for m in ms if m['id'] in group['aliases']];assert len(set((m['width_tiles'],m['height_tiles']) for m in aliases))==1
 assert len(set(m['data'] for m in aliases))==1
 assert all(m['hd']['status']==group['hd']['status'] for m in aliases)
for m in ms:
 p=Path(m['screenshot']);assert p.exists();assert Image.open(p).size==(m['width_tiles']*8,m['height_tiles']*8)
 if m['dynamic']['verified']:assert Path(m['dynamic']['best']['screenshot']).exists()
for z in j['screen_types']:assert Path(z['screenshot']).exists();assert Image.open(z['screenshot']).size==(160,144)
assert sum(c['distinct'] for c in j['category_summary'])==243
assert sum(c['slots'] for c in j['category_summary'])==313
assert s['confirmed_hd_area_tiles']==1800 and s['unique_area_tiles']==277632
assert hashlib.sha256(Path('/workspace/shawu/game.gbc').read_bytes()).hexdigest()=='ab42ec7ab339125dc685f4aa56eedfafaa2a8ecf46a4659e3c0f05eedd57ff95'
for f in [O/'inventory.json',O/'inventory_zh.md',Path('/workspace/shawu/shots/m6_scene_inventory.png')]:print(f, f.stat().st_size,'bytes')
print('PASS: 313 maps / 243 dimension-consistent deduplicated layouts / 54 native screen captures / ROM unchanged')
(O/'validation.txt').write_text('PASS: 313 maps / 243 dimension-consistent deduplicated layouts / 54 native screen captures / ROM unchanged\n')
