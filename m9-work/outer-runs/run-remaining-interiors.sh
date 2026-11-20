#!/usr/bin/env bash
set -euo pipefail
cd /workspace/shawu
for spec in \
  00-02:story12-interact-00-02-s01 \
  00-03:story12-interact-00-03-s01 \
  00-04:story12-interact-00-04-s01 \
  00-06:story12-interact-00-06-s01 \
  00-09:story12-interact-00-09-s01
do
  map=${spec%%:*}
  tag=${spec##*:}
  echo "=== $tag ==="
  setsid --wait bash m9-work/outer-runs/run-play.sh native "$tag" interact \
    "m9-work/search/village-doors/${map}.bin" 3000 240 \
    || echo "WARN $tag exit $?"
done
echo DONE_REMAINING
