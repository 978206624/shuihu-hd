#!/usr/bin/env bash
set -euo pipefail
export TZ=America/New_York
cd /workspace/shawu
ART=m9-work/art
LOGDIR=m9-work/outer-runs/gpt-plates
mkdir -p "$LOGDIR"
export GPT_IMAGE_ENV=${GPT_IMAGE_ENV:-/home/box/.config/gpt-image/api.env}
echo "$(date --iso-8601=seconds) sequential GPT retry for failed plates only"

run_one() {
  local id=$1 style=$2 size=$3
  local out="$ART/${id}_gpt.png"
  if [[ -f $out ]]; then
    echo "$(date --iso-8601=seconds) skip $id, output exists"
    return 0
  fi
  local stylepath="$ART/${style}_style.png"
  if [[ -f $ART/upload-refs/${style}_style.png ]]; then
    stylepath="$ART/upload-refs/${style}_style.png"
  fi
  # unique log for this retry wave
  local log="$LOGDIR/${id}-retry.log"
  echo "$(date --iso-8601=seconds) start $id style=$stylepath"
  python3 /home/box/opt/gpt-image/gpt_image.py edit \
    --prompt-file "$ART/${id}_prompt.txt" \
    -i "$ART/${id}_native_4x.png" \
    -i "$stylepath" \
    -o "$out" \
    --model gpt-image-2 --quality medium --size "$size" \
    --retries 5 --deadline 620 \
    > "$log" 2>&1
  local st=$?
  echo "$(date --iso-8601=seconds) $id exit $st png=$([[ -f $out ]] && echo yes || echo no)"
  return 0
}

run_one 00-1f forest 1536x1024
run_one 00-24 town 1024x1024
run_one 00-2b room 960x800
echo "$(date --iso-8601=seconds) sequential retry finished"
