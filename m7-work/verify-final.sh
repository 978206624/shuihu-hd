#!/bin/bash
set -euo pipefail
cd /workspace/shawu
export NODE_PATH=/home/box/opt/test-tools/node_modules
export PLAYWRIGHT_BROWSERS_PATH=/home/box/opt/playwright-browsers
# Exclusive: no other QA, replay, or recording task may run concurrently.
python3 m7-work/build_region_data.py
python3 m7-work/verify_sources.py
node m7-work/qa-routes.cjs
node m7-work/perf-region.cjs baseline
node m7-work/perf-region.cjs candidate
node m7-work/record-region.cjs
