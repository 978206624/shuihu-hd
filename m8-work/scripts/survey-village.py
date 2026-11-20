"""Replay discovered natural door routes independently, never as one chain."""
from pathlib import Path
import json, subprocess, hashlib, datetime, os
R=Path('/workspace/shawu'); W=R/'m8-work'
search=W/'search/south-village-doors'; result=json.loads((search/'result.json').read_text())
source=W/'play/village-decline-duel/latest.bin'
for code,door in result['found'].items():
    if code=='00-08': continue
    tag='survey-'+code; out=W/'play'/tag
    actions=door['actions']+[[None,180,0]]
    spec=W/'checkpoints'/f'{tag}-actions.json'
    if not spec.exists(): spec.write_text(json.dumps(actions,indent=2)+'\n')
    assert json.loads(spec.read_text())==actions
    if out.exists():
        prior=json.loads((out/'result.json').read_text())
        assert prior['actions']==actions and (out/'start.bin').read_bytes()==source.read_bytes()
        print('RESUME_SUCCESS',tag,flush=True); continue
    log=W/'logs'/f'{tag}.log'
    with log.open('x') as f:
        p=subprocess.run(['node',str(W/'scripts/native-play.cjs'),'replay',str(source),tag,str(spec)],cwd=R,stdout=f,stderr=subprocess.STDOUT,timeout=90)
    if p.returncode: raise SystemExit(f'Inspect {log}; exit {p.returncode}')
    with (W/'progress.md').open('a') as f:
        f.write(f'\n- {datetime.datetime.now(datetime.timezone.utc).isoformat()} 原生门路独立回放 {code} 完成；非连续主线，PID {os.getpid()}，日志 {log.relative_to(R)}；下一项自动续跑，已有成功不重复。\n')
print('SURVEY_COMPLETE',flush=True)
