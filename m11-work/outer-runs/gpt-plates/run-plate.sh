#!/usr/bin/env bash
# usage: run-plate.sh <id> <style.png> <WxH>   (supervisor outer GPT run; key never printed)
set -u
A=/workspace/shawu/m11-work/art; id=$1; style=$2; size=$3
[ -s "$A/${id}_gpt.png" ] && { echo "SKIP exists $id"; exit 0; }
exec python3 /home/box/opt/gpt-image/gpt_image.py edit --prompt-file "$A/${id}_prompt.txt" \
  -i "$A/${id}_native_4x.png" -i "$A/$style" -o "$A/${id}_gpt.png" --quality medium --size "$size" --retries 5 --deadline 620
