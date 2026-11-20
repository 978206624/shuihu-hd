import importlib.util,json
from pathlib import Path
s=importlib.util.spec_from_file_location('gateway','/workspace/shawu/concepts_v4/_work/edit_api.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
r=Path('/workspace/shawu/m3-work');m.OUT=r/'art';m.WORK=r/'art'
p='Use case: background-extraction. Create the empty background plate for an intertitle card in this historical Chinese JRPG. The native reference is pure black behind bitmap lettering; remove ALL lettering and retain a perfectly uniform pure black background across the entire image. Absolutely zero text, glyphs, symbols, people, characters, portraits, animals, scenery, decoration, borders, highlights or gradients. Output one completely black rectangular background only, same 10:9 proportions. This is a deliberately blank transition plate, not new scenery. Do not invent details.'
m.FILES['intertitle']=(r/'references/gap_130.png',r/'art_requests/style.jpg');m.PROMPTS['intertitle']=p
(r/'art/intertitle_prompt.txt').write_text(p)
print(json.dumps(m.attempt('intertitle',quality='medium',use_style=False,use_fidelity=False,tag='m3-gap')))
