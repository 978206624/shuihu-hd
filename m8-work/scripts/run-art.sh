#!/bin/bash
set -euo pipefail
cd /workspace/shawu
ids=${1:?Use comma-separated prepared map IDs}
# No environment file is sourced or printed. Only gateway_one.py reads it via
# the unchanged approved transport helper; no service is started or replaced.
python3 m8-work/art/generate.py --ids "$ids" --workers 3
