"""Freeze and verify evidence without network, browser, gameplay or generation."""
from pathlib import Path
import json,hashlib,subprocess,ast,sys,collections,datetime
R=Path(__file__).resolve().parents[2];W=R/'m8-work';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
manifest=W/'freeze-sha256.json'
dirs=['m8-work/runtime','m8-work/inputs','m8-work/scripts','m8-work/integration',
      'm7-work/stage-a/v3/runtime']
def inventory():
    paths=[p for d in dirs for p in (R/d).rglob('*') if p.is_file() and '__pycache__' not in str(p)]
    paths += list((W/'frozen-starts').glob('*'))
    paths += list((W/'checkpoints').glob('*.json'))
    paths += [W/'region3-scope.json',W/'art/native-map-metadata.json',W/'art/input-freeze-sha256.json',
      W/'art/SUPERVISOR_VISUAL_REVIEW.md',W/'art/batch-manifest.json',R/'m7-work/STAGE_A_FINAL_DECISION_zh.md']
    paths += list((W/'art').glob('*_gpt.png'))+list((W/'art').glob('*_gpt.png.meta.json'))
    paths += [W/'art'/name for name in (
        '00-06_gpt_v2.png', '00-06_gpt_v2.png.meta.json',
        '00-06_prompt_v2.txt', '00-06_glyphs_before_after.png',
    )]
    paths += [p for p in (W/'art/cli-generation/20261111T112050Z').rglob('*') if p.is_file()]
    # Original art input freeze also covers old region artwork and native references.
    paths += [R/p for p in json.loads((W/'art/input-freeze-sha256.json').read_text())]
    return {str(p.relative_to(R)):sha(p) for p in sorted(set(paths)) if p.is_file()}
if '--freeze' in sys.argv:
    assert not manifest.exists(),'Existing freeze is immutable'
    manifest.write_text(json.dumps(inventory(),indent=2)+'\n')
expected=json.loads(manifest.read_text());actual=inventory();errors=[]
if actual!=expected:errors.append('Frozen inventory/hash mismatch')
adopted=json.loads((W/'integrity/adopted-runtime-sha256.json').read_text());changes=[]
for rel,h in adopted.items():
    if sha(W/'runtime'/rel)!=h:changes.append(rel)
if changes!=['assets/region1/maps.json']:errors.append('Unexpected original-runtime modifications '+repr(changes))
base=json.loads((R/'m7-work/stage-a/v3/runtime/assets/region1/maps.json').read_text())
spec=json.loads((W/'runtime/assets/region1/maps.json').read_text());added=spec[len(base):]
if spec[:len(base)]!=base or len(added)!=8:errors.append('Original map data changed / wrong new map count')
for item in json.loads((W/'integration/provenance.json').read_text())['newMaps']:
    if sha(R/item['source'])!=sha(R/item['runtimeAsset']):errors.append('PNG copy differs '+item['id'])
history=json.loads((W/'integrity/pre-stage-b-protected-sha256.json').read_text());missing=[];changed=[]
for rel,h in history.items():
    p=R/rel
    if not p.is_file():missing.append(rel)
    elif sha(p)!=h:changed.append(rel)
if changed:errors.append('Protected history modified')
unexpected_missing=[p for p in missing if not p.startswith('m6-work/venv/') and '__pycache__/' not in p]
if unexpected_missing:errors.append('Unexpected missing protected history')
checks=[]
for p in sorted((W/'scripts').glob('*')):
    if p.suffix=='.py':
        ast.parse(p.read_text());checks.append({'file':p.name,'pass':True})
    elif p.suffix in ['.cjs','.sh']:
        proc=subprocess.run(['node','--check',str(p)] if p.suffix=='.cjs' else ['bash','-n',str(p)],capture_output=True,text=True)
        checks.append({'file':p.name,'pass':proc.returncode==0,'error':proc.stderr})
if not all(c['pass'] for c in checks):errors.append('Syntax check failed')
result=dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),pass_=not errors,
    freezeSHA256=sha(manifest),frozenFiles=len(expected),runtimeChanges=changes,newMaps=len(added),
    oldRuntimeFiles=len(adopted),codeROMCoreUnchanged=True,
    protectedHistory=dict(total=len(history),changed=changed,missing=missing,
      missingGroups=dict(collections.Counter('m6-work/venv' if p.startswith('m6-work/venv/') else '__pycache__' if '__pycache__/' in p else 'other' for p in missing))),
    syntax=checks,errors=errors,browserQA='NOT_RUN',coverage='NOT_MEASURED',performance='NOT_MEASURED')
dest=W/'offline/integration-checks.json'
if '--verify-only' not in sys.argv:dest.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k not in ['protectedHistory','syntax']}|{'protectedChanged':len(changed),'protectedMissing':len(missing),'missingGroups':result['protectedHistory']['missingGroups']}))
raise SystemExit(bool(errors))
