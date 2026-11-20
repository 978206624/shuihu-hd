#!/bin/bash
set -u
export TZ=America/New_York
cd /workspace/shawu
NP=m10-work/scripts/native-play.cjs
LOG=m10-work/outer-runs/story14-door-chain.log
SUMMARY=m10-work/outer-runs/story14-door-chain-summary.json
echo "chain start $(date --iso-8601=seconds)" | tee -a "$LOG"

# queue: tag|source. Seed only on a fresh start.
mkdir -p m10-work/search m10-work/outer-runs
if [[ "${M10_DOOR_CONTINUE:-}" != 1 ]]; then
  printf '%s\n' 'story14-doors-00-2c|m10-work/checkpoints/story14-inn-end.bin' > /tmp/m10-door-queue.txt
  rm -f /tmp/m10-door-queue-next.txt /tmp/m10-door-queue-more.txt
fi

while IFS='|' read -r tag src; do
  [[ -z "${tag:-}" ]] && continue
  echo "=== SEARCH $tag from $src $(date --iso-8601=seconds) ===" | tee -a "$LOG"
  if [[ -e m10-work/search/$tag ]]; then
    echo "exists, skip $tag" | tee -a "$LOG"
  else
    if ! node "$NP" doors "$src" "$tag" 8000 >>"$LOG" 2>&1; then
      echo "SEARCH_FAILED $tag rc=$?" | tee -a "$LOG"
      # continue to next if a result exists
    fi
  fi
  result=m10-work/search/$tag/result.json
  if [[ ! -f $result ]]; then
    echo "NO_RESULT $tag" | tee -a "$LOG"
    continue
  fi
  python3 - <<PY >>"$LOG"
import json
from pathlib import Path
tag = "$tag"
src = Path("m10-work/search") / tag
r = json.loads((src/"result.json").read_text())
print("result", tag, "found", list(r.get("found", {})), "nodes", r.get("nodes"), "frontier", r.get("frontier"), "deadlineHit", r.get("deadlineHit"))
# enqueue found maps
qpath = Path("/tmp/m10-door-queue-more.txt")
for mid, info in (r.get("found") or {}).items():
    binp = src / f"{mid}.bin"
    if not binp.is_file():
        print("missing bin", mid)
        continue
    newtag = "story14-doors-" + mid
    dest = Path("m10-work/search") / newtag
    if dest.exists():
        print("already searched", mid)
        continue
    with qpath.open("a") as f:
        f.write(f"{newtag}|{binp}\\n")
    print("enqueue", newtag, binp)
PY
  if [[ -f /tmp/m10-door-queue-more.txt ]]; then
    cat /tmp/m10-door-queue-more.txt >> /tmp/m10-door-queue-next.txt
    rm -f /tmp/m10-door-queue-more.txt
  fi
done < /tmp/m10-door-queue.txt

# Process dynamically enqueued maps (one extra wave file to avoid editing the live stdin file)
if [[ -f /tmp/m10-door-queue-next.txt ]]; then
  mv /tmp/m10-door-queue-next.txt /tmp/m10-door-queue.txt
  echo "=== continue queue $(wc -l < /tmp/m10-door-queue.txt) ===" | tee -a "$LOG"
  # recursive via exec to process new queue
  export M10_DOOR_CONTINUE=1
  exec bash m10-work/outer-runs/story14-door-chain.sh
fi

echo "chain complete $(date --iso-8601=seconds)" | tee -a "$LOG"
python3 - <<'PY'
import json
from pathlib import Path
from datetime import datetime
root=Path('/workspace/shawu/m10-work/search')
maps={}
for d in sorted(root.glob('story14-doors-*')):
    rp=d/'result.json'
    if not rp.exists():
        maps[d.name]={'status':'no-result'}
        continue
    r=json.loads(rp.read_text())
    maps[d.name]={'origin':r.get('origin'),'found':{k:{'xy':v.get('xy'),'story':v.get('story')} for k,v in (r.get('found') or {}).items()},
                  'nodes':r.get('nodes'),'frontier':r.get('frontier'),'deadlineHit':r.get('deadlineHit')}
Path('/workspace/shawu/m10-work/outer-runs/story14-door-chain-summary.json').write_text(json.dumps({'finished':datetime.now().isoformat(),'surveys':maps},ensure_ascii=False,indent=2)+'\n')
print('summary written', maps)
PY
