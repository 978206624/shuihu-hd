from pathlib import Path
import importlib.util,json,sys
r=Path(__file__).parent;code=sys.argv[1];attempt=sys.argv[2]
s=importlib.util.spec_from_file_location('gateway','/workspace/shawu/concepts_v4/_work/edit_api.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
item=next((i for i in json.loads((r/'batch-manifest.json').read_text()) if i['id']==code),{'refs':['00-07_native_4x.png','forest_style.png'],'prompt':'00-07_prompt.txt','output':'00-07_gpt.png'})
res=m.post_edit([('model','gpt-image-2'),('prompt',(r/item['prompt']).read_text()),('n','1'),('quality','low' if code=='00-1e' and int(attempt)>=3 else 'medium'),('size','auto')],[('image[]',n,('image/jpeg' if n.endswith('.jpg') else 'image/png'),(r/n).read_bytes()) for n in item['refs']],timeout=590)
meta=m.summarize(res);(r/f'{code}_retry_{attempt}_meta.json').write_text(json.dumps(meta,indent=2));print(json.dumps(meta),flush=True)
if res['ok']:m.save_image(res['body'],r/item['output'])
else:sys.exit(1)
