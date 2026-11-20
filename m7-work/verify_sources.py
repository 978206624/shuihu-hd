from pathlib import Path
import hashlib,json
r=Path('/workspace/shawu');base=r/'m6-work/region1/runtime';cand=r/'m7-work/runtime'
rows=[]
for p in sorted(base.rglob('*')):
 if not p.is_file():continue
 rel=p.relative_to(base)
 if str(rel)=='assets/region1/maps.json':continue
 q=cand/rel
 sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
 rows.append({'file':str(rel),'exists':q.exists(),'same':q.exists() and sha(p)==sha(q),'sha256':sha(p)})
rom=hashlib.sha256((r/'game.gbc').read_bytes()).hexdigest()
result={'allExistingRuntimeFilesUnchanged':all(x['same'] for x in rows),'protected':rows,'romSHA256':rom,'romUnchanged':rom=='ab42ec7ab339125dc685f4aa56eedfafaa2a8ecf46a4659e3c0f05eedd57ff95'}
(r/'m7-work/integrity.json').write_text(json.dumps(result,indent=2));print(json.dumps({k:v for k,v in result.items() if k!='protected'}))
