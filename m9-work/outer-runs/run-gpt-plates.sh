#!/usr/bin/env bash
set -euo pipefail
export TZ=America/New_York
cd /workspace/shawu
ART=m9-work/art
LOGDIR=m9-work/outer-runs/gpt-plates
mkdir -p "$LOGDIR"
echo "$(date --iso-8601=seconds) launching region4 GPT plates (medium, gpt-image-2, official gateway only)"
# Do not source or print the env file. gpt_image.py reads it.
export GPT_IMAGE_ENV=${GPT_IMAGE_ENV:-/home/box/.config/gpt-image/api.env}

launch_one() {
  local id=$1 style=$2 size=$3
  local out="$ART/${id}_gpt.png"
  local log="$LOGDIR/${id}.log"
  if [[ -f $out ]]; then
    echo "$(date --iso-8601=seconds) skip $id, output exists"
    return 0
  fi
  nohup python3 /home/box/opt/gpt-image/gpt_image.py edit \
    --prompt-file "$ART/${id}_prompt.txt" \
    -i "$ART/${id}_native_4x.png" \
    -i "$ART/${style}_style.png" \
    -o "$out" \
    --model gpt-image-2 --quality medium --size "$size" \
    --retries 5 --deadline 620 \
    > "$log" 2>&1 &
  echo $! > "$LOGDIR/${id}.pid"
  echo "$(date --iso-8601=seconds) started $id pid $(cat "$LOGDIR/${id}.pid") size=$size"
}

launch_one 00-1f forest 1536x1024
launch_one 00-21 forest 1536x1024
launch_one 00-24 town 1024x1024
launch_one 00-2b room 960x800
launch_one 00-2c room 960x800
wait || true
echo "$(date --iso-8601=seconds) gpt launcher wait returned"
# summarize without printing keys
python3 - <<'PY'
import json
from pathlib import Path
art=Path('m9-work/art')
for mid in ['00-1f','00-21','00-24','00-2b','00-2c']:
    out=art/f'{mid}_gpt.png'
    meta=art/f'{mid}_gpt.png.meta.json'
    log=Path('m9-work/outer-runs/gpt-plates')/f'{mid}.log'
    print(mid, 'png' if out.exists() else 'NO_PNG', 'bytes', out.stat().st_size if out.exists() else 0)
    if meta.exists():
        try:
            d=json.loads(meta.read_text())
            print('  meta ok=', d.get('ok'), 'size=', d.get('size'), 'quality=', d.get('quality'), 'attempts=', len(d.get('attempts') or []))
        except Exception as e:
            print('  meta parse', e)
    if log.exists():
        # last non-secret-looking line
        lines=[ln.strip() for ln in log.read_text(errors='replace').splitlines() if ln.strip()]
        print('  log tail:', (lines[-1][:200] if lines else '(empty)'))
PY
