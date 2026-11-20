"""Supervisor-reviewed optional helper. Run explicitly; never prints credentials/response bodies."""
import json,base64,uuid,urllib.request
from pathlib import Path
cfg={}
for line in Path('/workspace/shawu/.image_api.env').read_text().splitlines():
 line=line.strip()
 if not line or line.startswith('#') or '=' not in line:continue
 k,v=line.split('=',1)
 if k in ('IMAGE_API_BASE','IMAGE_API_KEY'):cfg[k]=v.strip().strip('"\'')
req=json.loads(Path('/workspace/shawu/m1-work/asset-request.json').read_text())
boundary=uuid.uuid4().hex;parts=[]
def field(k,v):parts.append(f'--{boundary}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode())
field('model','gpt-image-2');field('prompt',req['instructions']+f" Atlas dimensions {req['width']}x{req['height']}; 16 columns, 6 rows, 32px cells. Last two cells are unused magenta. Output atlas only.")
for path in (req['reference_atlas_path'],req['source_screenshot_path']):
 p=Path(path);parts.append(f'--{boundary}\r\nContent-Disposition: form-data; name="image[]"; filename="{p.name}"\r\nContent-Type: image/png\r\n\r\n'.encode()+p.read_bytes()+b'\r\n')
parts.append(f'--{boundary}--\r\n'.encode())
url=cfg['IMAGE_API_BASE'].rstrip('/')
if not url.endswith('/v1'):url+='/v1'
r=urllib.request.Request(url+'/images/edits',data=b''.join(parts),headers={'Authorization':'Bearer '+cfg['IMAGE_API_KEY'],'Content-Type':'multipart/form-data; boundary='+boundary})
try:
 with urllib.request.urlopen(r,timeout=600) as response:result=json.load(response)
 data=base64.b64decode(result['data'][0]['b64_json'],validate=True)
 Path(req['target_output_path']).write_bytes(data)
 print('Saved forest atlas; validate grid and dimensions before use.')
except Exception:
 raise SystemExit('Image request failed; no response body logged.')
