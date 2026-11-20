# Authorized existing helper keeps gateway credentials out of logs and bundles.
import importlib.util,json
from pathlib import Path
spec=importlib.util.spec_from_file_location('gateway','/workspace/shawu/concepts_v4/_work/edit_api.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
p=Path('/workspace/shawu/m2-work');m.OUT=p;m.WORK=p
import sys
scene=sys.argv[1]
m.FILES[scene]=(p/f'{scene}-reference.png',p/'style.jpg')
m.PROMPTS[scene]='''Use case: style-transfer. Create a continuous hand-painted premium HD 2D JRPG BACKGROUND MAP texture. Image 1 is the exact top-down 256x256 game tilemap layout authority, enlarged 2x. Image 2 is ONLY a painterly material and lighting style reference. Match image 1 geometry exactly, including every path, forest boundary, lake, stone platform, architecture, and empty ground. Keep the exact overhead camera and scale. Redraw as one continuous coherent landscape, not independent tile illustrations: no tile grid lines, no seams, no unrelated tree trunks. ZERO people, humans, animals, creatures, sprites, portraits, text, menu, UI, icons, or additional objects. The game will overlay original sprites separately. Do not copy title text or creature from style reference. The repeated empty areas of image 1 are intentional: retain their terrain type and positions. Preserve exact proportions; output one square map only. Fine painted textures, natural coherent lighting, readable traversable ground.'''
result=m.attempt(scene,quality='medium',tag='m2');print('result',scene,bool(result),flush=True)
