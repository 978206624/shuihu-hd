"""M8 adapter of m7-work/art/gateway_one.py; same authorized GPT transport.
Only this network worker imports the established helper that reads the env.
No key, config value, raw response, endpoint or upstream error body is logged.
"""
from pathlib import Path
import importlib.util,json,sys,time,hashlib,os
from PIL import Image
R=Path('/workspace/shawu'); A=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    code=sys.argv[1]; attempt=Path(sys.argv[2]).resolve()
    assert A/'attempts' in attempt.parents and attempt.is_dir()
    item=next(i for i in json.loads((A/'batch-manifest.json').read_text()) if i['id']==code)
    assert item['model']=='gpt-image-2' and item['quality'] in ['low','medium']
    output=A/item['output']; assert not output.exists(), 'Successful output already exists'
    meta=dict(id=code,model=item['model'],requestedQuality=item['quality'],requestedSize=item['size'],
      promptSHA256=sha(A/item['prompt']),references=[dict(file=f,sha256=sha(A/f)) for f in item['refs']],
      transportSource='concepts_v4/_work/edit_api.py',
      transportSourceSHA256=sha(R/'concepts_v4/_work/edit_api.py'),
      m7HarnessSHA256=sha(R/'m7-work/art/gateway_one.py'),
      started=time.time(),pid=os.getpid(),redacted=True)
    try:
        spec=importlib.util.spec_from_file_location('authorized_gateway',R/'concepts_v4/_work/edit_api.py')
        gateway=importlib.util.module_from_spec(spec);spec.loader.exec_module(gateway)
        res=gateway.post_edit([('model',item['model']),('prompt',(A/item['prompt']).read_text()),
          ('n','1'),('quality',item['quality']),('size',item['size'])],
          [('image[]',f,'image/png',(A/f).read_bytes()) for f in item['refs']],timeout=590)
        meta.update(httpStatus=int(res.get('status',0)),elapsedSeconds=round(res.get('elapsed',0),3),
                    responseBytes=res.get('nbytes',0),requestSucceeded=bool(res.get('ok')))
        body=res.get('body')
        if not res.get('ok'):
            meta['failure']='HTTP_OR_TRANSPORT_FAILURE_REDACTED'; return 1
        if not isinstance(body,dict) or not body.get('data'):
            meta['failure']='MISSING_IMAGE_DATA'; return 1
        returned=body.get('quality');meta['returnedQuality']=returned if returned in ['low','medium','high','auto'] else 'not reported'
        meta['qualityViolation']=returned in ['high','auto']
        # Preserve original image bytes and metadata even when geometry needs
        # human rejection. Never silently regenerate an already successful image.
        raw=attempt/'response-image.png'; gateway.save_image(body,raw)
        with Image.open(raw) as im:
            im.load(); dims=list(im.size);meta.update(actualImageSize=dims,actualImageFormat=im.format)
        target=item['requestedSize'];native=item['nativeSize']
        meta.update(exactRequestedSize=dims==target,exactAspectRatio=dims[0]*native[1]==dims[1]*native[0],
          outputSHA256=sha(raw),outputBytes=raw.stat().st_size,humanArtReview='PENDING',generationSucceeded=True)
        # Atomic final path; parent generation lock prevents competing workers.
        os.link(raw,output)
        meta['output']=output.name
        return 2 if meta['qualityViolation'] else 0
    except Exception as e:
        meta['failure']='WORKER_EXCEPTION_REDACTED';meta['exceptionClass']=type(e).__name__
        return 1
    finally:
        meta['finished']=time.time();(attempt/'worker-meta.json').write_text(json.dumps(meta,indent=2)+'\n')
        print(json.dumps({k:meta.get(k) for k in ['id','httpStatus','elapsedSeconds','generationSucceeded','qualityViolation','actualImageSize','failure','exceptionClass']}),flush=True)
if __name__=='__main__':sys.exit(main())
