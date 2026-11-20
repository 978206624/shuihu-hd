"""Copy existing successes into the final immutable QA input set; no gameplay."""
from pathlib import Path
import json, hashlib
R=Path(__file__).resolve().parents[2]; W=R/'m8-work'; D=W/'inputs'; D.mkdir(exist_ok=True)
sha=lambda b:hashlib.sha256(b).hexdigest()
def frozen(source):
    p=Path(source)
    if not p.is_absolute(): p=R/p
    data=p.read_bytes(); dest=D/(sha(data)[:16]+'-'+p.name)
    if dest.exists(): assert dest.read_bytes()==data
    else: dest.write_bytes(data)
    return str(dest)
def write(name,value):
    data=(json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode(); dest=D/name
    if dest.exists(): assert dest.read_bytes()==data,name
    else: dest.write_bytes(data)
old=json.loads((R/'m7-work/stage-a/frozen-inputs/qa-routes.json').read_text())
for b in old:
    b['source']=frozen(b['source']); b['group']='regions1-2'; b['regressionVisualExact']=True
new=[]
for name,start,actions,story in [
    ('formal-letter-9-to11','m8-work/frozen-starts/region2-story9-end.bin','letter-natural-actions.json',11),
    ('formal-meeting-11-to12','m8-work/frozen-starts/story11-letter-delivered.bin','story11-to12-actions.json',12)]:
    new.append(dict(name=name,source=frozen(start),actions=json.loads((W/'checkpoints'/actions).read_text()),
                    group='region3-story',endStory=story,regressionVisualExact=False))
scope=json.loads((W/'region3-scope.json').read_text())
preview=[]; perf=[]
for s in scope['maps']:
    p=R/s['naturalReplay']; aa=json.loads((p/'actions.json').read_text())
    new.append(dict(name='formal-door-'+s['id'],source=frozen(p/'start.bin'),actions=aa,
        group='region3-doors',target=s['id'],saveAt=len(aa)-1,regressionVisualExact=False,
        independentDoorSurvey=s['independentDoorSurvey']))
    preview.append(dict(id=s['id'],name=s['name'],source=frozen(p/'latest.bin'),
        sourceProvenance=str(p.relative_to(R)),actions=[['up',16,8],['left',16,8],['right',16,8],['down',16,8]]))
    perf.append(dict(id='region3-'+s['id'],source=frozen(p/'start.bin'),actions=aa))
perf_old=json.loads((R/'m7-work/stage-a/frozen-inputs/perf-routes.json').read_text())
for b in perf_old: b['source']=frozen(b['source'])
write('qa-routes.json',old+new);write('perf-routes.json',perf_old+perf);write('preview.json',preview)
write('route-disclosures.json',dict(oldRegressionActions=sum(len(b['actions']) for b in old),
    formalQAActions=sum(len(b['actions']) for b in old+new),
    formalQAFrames=sum(a[1]+a[2] for b in old+new for a in b['actions']),
    oldRegressionNativeFrames=31396, newMapIDs=[s['id'] for s in scope['maps']],
    route='23 original region1/2 branches + 185-action letter chain + 281-action meeting chain + eight existing doorway surveys; all baseline/candidate pairs use identical byte starts and native-frame inputs.',
    preview='Eight separate natural-save excerpts at original rAF speed. State loads between excerpts, no audio. Not a continuous journey.',
    exclusions=scope['exclusions'],
    serialization='Historical 26711-frame segmented/continuous replay has three final save bytes different; retained in checkpoints/story11-to12-continuous-proof.json. Formal paired QA compares identical byte starts, never different segment boundaries.'))
print(json.dumps(dict(routes=len(old+new),actions=sum(len(b['actions']) for b in old+new),perfRoutes=len(perf_old+perf))))
