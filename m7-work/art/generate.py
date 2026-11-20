from pathlib import Path
import subprocess,time,sys,json
from concurrent.futures import ThreadPoolExecutor,as_completed
r=Path(__file__).parent
items=json.loads((r/'batch-manifest.json').read_text())
def worker(item):
 code=item['id']
 for attempt in range(1,6):
  if (r/item['output']).exists():return {'id':code,'ok':True,'attempt':attempt-1}
  print(json.dumps({'id':code,'attempt':attempt,'status':'started','wallLimitSeconds':620}),flush=True)
  start=time.time()
  try:
   with (r/f'{code}_retry_{attempt}.log').open('w') as f:res=subprocess.run([sys.executable,str(r/'gateway_one.py'),code,str(attempt)],stdout=f,stderr=subprocess.STDOUT,timeout=620)
   status={'exitCode':res.returncode}
  except subprocess.TimeoutExpired:
   status={'ok':False,'status':'hard wall timeout','elapsed_seconds':620}
  (r/f'{code}_attempt_{attempt}.json').write_text(json.dumps({'id':code,'attempt':attempt,'elapsed':time.time()-start,**status}))
  print(json.dumps({'id':code,'attempt':attempt,**status}),flush=True)
  if (r/item['output']).exists():return {'id':code,'ok':True,'attempt':attempt}
  if attempt<5:time.sleep(min(20*2**(attempt-1),120))
 return {'id':code,'ok':False}
with ThreadPoolExecutor(max_workers=4) as ex:
 results=[f.result() for f in as_completed(ex.submit(worker,i) for i in items)]
(r/'batch-results.json').write_text(json.dumps(results,indent=2));print(json.dumps(results),flush=True)
