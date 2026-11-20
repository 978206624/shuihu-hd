import importlib.util,json
from pathlib import Path
from PIL import Image
s=importlib.util.spec_from_file_location('gateway','/workspace/shawu/concepts_v4/_work/edit_api.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
r=Path('/workspace/shawu/m4-work');r.joinpath('art').mkdir(exist_ok=True)
for source,name in [('/workspace/shawu/web/assets/title_hd.png','approved_title'),('/tmp/title25.png','native_clear')]:
 im=Image.open(source).convert('RGB');im.thumbnail((320,320));im.save(r/'art'/f'{name}_compact.png')
prompt='''Use case: precise-object-edit. Edit image 1, the approved painterly game title image, into the MENU-CLEARED version of the SAME title scene. Image 2 is the actual native cleared frame and is exact layout authority for what is left after menu/mascot removal. Remove BOTH central menu text lines, their cursor, and the central flying creature/mascot completely. Fill the removed region with continuous bright blue sky, distant misty blue Chinese mountain silhouettes and evergreen trees as shown at those exact normalized positions in image 2, in the painterly style of image 1. Preserve the top title scroll and its existing text and the bottom copyright/logo positions from image 1. NO new text, NO people, NO creatures, NO sprites or portraits; no dialogue or UI. Exact 10:9 composition, same framing and scale, no new objects. Finished clean background title plate, not pixel scaling.'''
(r/'art/title_clear_compact_prompt.txt').write_text(prompt)
fields=[('model','gpt-image-2'),('prompt',prompt),('n','1'),('quality','low'),('size','auto')]
files=[('image[]',f'{n}_compact.png','image/png',(r/'art'/f'{n}_compact.png').read_bytes()) for n in ['approved_title','native_clear']]
res=m.post_edit(fields,files,timeout=560);summary=m.summarize(res);(r/'art/title_clear_compact_meta.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary),flush=True)
if not res['ok']:raise SystemExit(1)
m.save_image(res['body'],r/'art/title_clear_compact_hd.png')
