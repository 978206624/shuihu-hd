import importlib.util,json,time
from pathlib import Path
r=Path('/workspace/shawu/m5-work/art')
s=importlib.util.spec_from_file_location('gateway','/workspace/shawu/concepts_v4/_work/edit_api.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
prompt=(r/'impact_late_prompt.txt').read_text()
for attempt in range(1,6):
 fields=[('model','gpt-image-2'),('prompt',prompt),('n','1'),('quality','low'),('size','auto')]
 files=[('image[]',n,'image/png',(r/n).read_bytes()) for n in ['impact_late_native.png','impact_style.png']]
 print(json.dumps({'request':'impact_late','attempt':attempt,'status':'started'}),flush=True)
 res=m.post_edit(fields,files,timeout=590);summary=m.summarize(res)
 (r/f'impact_late_attempt_{attempt}_meta.json').write_text(json.dumps(summary,indent=2))
 print(json.dumps({'request':'impact_late','attempt':attempt,**summary}),flush=True)
 if res['ok']:
  m.save_image(res['body'],r/'impact_late_hd.png');(r/'IMPACT_READY.txt').write_text('GPT late four-burst background succeeded; validate geometry visually then integrate matched late phases. Native authority probe_5411_orig.png. No roles or UI.');break
 if attempt<5:time.sleep(min(15*2**(attempt-1),120))
else:raise SystemExit('all 5 image attempts failed; metadata saved without credentials')
