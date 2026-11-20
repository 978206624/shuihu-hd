"""Bounded, resumable M7 generation harness, at most three independent jobs.
Supervisor executes outside the Codex socket sandbox. No provider fallback.
"""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor,as_completed
import argparse,subprocess,time,json,sys,hashlib,fcntl,socket,datetime,os,threading,signal
ABORT=threading.Event()
from PIL import Image
A=Path(__file__).resolve().parent;W=A.parent;R=W.parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):
    tmp=p.with_suffix(p.suffix+'.writing');tmp.write_text(json.dumps(v,indent=2)+'\n');tmp.replace(p)
def proxy():
    try:
        with socket.create_connection(('127.0.0.1',38811),3):pass
    except OSError as e:
        note=f'BLOCKER: 38811 unavailable ({type(e).__name__}); no retries, auth or route changes.'
        with (W/'STATUS.md').open('a') as f:f.write('\n'+note+'\n')
        raise RuntimeError(note) from None
def verify():
    frozen=json.loads((A/'input-freeze-sha256.json').read_text())
    for rel,h in frozen.items():
        if sha(R/rel)!=h:raise RuntimeError('Frozen art input changed: '+rel)
def success(item):
    output=A/item['output']
    if not output.exists():return None
    for meta in sorted((A/'attempts'/item['id']).glob('*/worker-meta.json')):
        data=json.loads(meta.read_text())
        if data.get('generationSucceeded') and data.get('outputSHA256')==sha(output):
            return dict(id=item['id'],generationSucceeded=True,resumedSuccess=True,
              output=item['output'],sha256=data['outputSHA256'],provenance=str(meta.relative_to(R)),
              qualityViolation=data.get('qualityViolation'),review='PENDING')
    raise RuntimeError('Existing output lacks matching success provenance: '+item['id'])
def worker(item,dry=False):
    code=item['id']
    if ABORT.is_set():raise RuntimeError('BLOCKER: batch cancelled')
    prior=success(item)
    if prior:return prior
    attempts=A/'attempts'/code
    used=len(list(attempts.glob('attempt-*/attempt.json'))) if attempts.exists() else 0
    if dry:return dict(id=code,validation='READY',priorAttempts=used,refs=item['refs'],requestedSize=item['size'])
    start=time.monotonic()
    for number in range(used+1,4):
        verify();proxy()
        if time.monotonic()-start>1900:break
        d=attempts/f'attempt-{number:02d}';d.mkdir(parents=True,exist_ok=False)
        record=dict(id=code,attempt=number,status='STARTED',started=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                    pid=os.getpid(),hardDeadlineSeconds=620)
        write(d/'attempt.json',record);print(json.dumps(record),flush=True)
        try:
            with (d/'worker.log').open('x') as log:
                proc=subprocess.Popen([sys.executable,str(A/'gateway_one.py'),code,str(d)],stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
                stop=time.monotonic()+620
                try:
                    while proc.poll() is None:
                        if ABORT.wait(5):raise RuntimeError('BLOCKER: batch cancelled after service loss or signal')
                        proxy()
                        if time.monotonic()>stop:raise subprocess.TimeoutExpired('authorized gateway worker',620)
                except BaseException:
                    os.killpg(proc.pid,signal.SIGTERM)
                    try:proc.wait(timeout=5)
                    except subprocess.TimeoutExpired:os.killpg(proc.pid,signal.SIGKILL);proc.wait(timeout=5)
                    raise
            record.update(status='WORKER_FINISHED',exitCode=proc.returncode)
        except subprocess.TimeoutExpired:
            record.update(status='HARD_WALL_TIMEOUT',exitCode=None)
        except Exception as e:
            ABORT.set();record.update(status='BLOCKER',errorClass=type(e).__name__);write(d/'attempt.json',record);raise
        record['finished']=datetime.datetime.now(datetime.timezone.utc).isoformat();write(d/'attempt.json',record)
        verify();proxy()
        prior=success(item)
        if prior:return prior
        if (d/'worker-meta.json').exists():
            m=json.loads((d/'worker-meta.json').read_text())
            if m.get('httpStatus') in [401,403]:
                ABORT.set();raise RuntimeError('BLOCKER: authorized image gateway rejected authentication; no credential inspection or retry')
            if m.get('httpStatus') not in [0,408,429] and not 500<=m.get('httpStatus',0)<600:
                ABORT.set();raise RuntimeError('BLOCKER: authorized gateway returned a permanent or unusable response; preserved attempt, no parameter/provider fallback')
        if number<3 and ABORT.wait(min(20*2**(number-1),40)):raise RuntimeError('BLOCKER: batch cancelled')
    return dict(id=code,generationSucceeded=False,status='BOUNDED_ATTEMPTS_EXHAUSTED',review='NOT_GENERATED')
def main():
    p=argparse.ArgumentParser();p.add_argument('--ids',required=True);p.add_argument('--workers',type=int,default=3);p.add_argument('--dry-run',action='store_true');args=p.parse_args()
    assert 1<=args.workers<=3
    ids=args.ids.split(',');items=json.loads((A/'batch-manifest.json').read_text());selected=[i for i in items if i['id'] in ids]
    assert len(selected)==len(set(ids))==len(ids)
    verify()
    signal.signal(signal.SIGTERM,lambda *_:ABORT.set())
    signal.signal(signal.SIGINT,lambda *_:ABORT.set())
    if args.dry_run:
        print(json.dumps([worker(i,True) for i in selected],indent=2));return 0
    lock=(A/'generate.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);proxy()
    batch=A/'batches'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');batch.mkdir(parents=True)
    write(batch/'started.json',dict(ids=ids,workers=args.workers,pid=os.getpid(),inputFreezeSHA256=sha(A/'input-freeze-sha256.json')))
    results=[];error=None
    try:
        with ThreadPoolExecutor(max_workers=args.workers) as ex:
            futures={ex.submit(worker,i):i['id'] for i in selected}
            for f in as_completed(futures):
                try:result=f.result()
                except Exception:
                    ABORT.set();raise
                results.append(result);write(batch/'results.json',results)
    except Exception as e:
        ABORT.set()
        error=str(e) if str(e).startswith(('BLOCKER:','Frozen art input changed:','Existing output lacks')) else type(e).__name__
        write(batch/'blocker.json',dict(status='BLOCKER',reason=error));print('BLOCKER',error,flush=True)
    write(batch/'summary.json',dict(results=results,error=error,artAcceptance=False,reviewRequired=True))
    with (W/'progress.md').open('a') as f:f.write(f'\n- {datetime.datetime.now(datetime.timezone.utc).isoformat()} GPT外层批次结束 PID {os.getpid()}，证据{batch.relative_to(R)}；status={"BLOCKER" if error else "REVIEW_REQUIRED"}。下一步Codex目检原生/HD全图；不自动集成、不重复成功生图。\n')
    return 2 if error or any(not x.get('generationSucceeded') or x.get('qualityViolation') for x in results) else 0
if __name__=='__main__':sys.exit(main())
