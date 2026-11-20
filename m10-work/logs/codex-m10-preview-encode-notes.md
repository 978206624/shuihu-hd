# Region 5 preview encode

- `m10-work/scripts/region5-preview.cjs` now trims each of the six excerpts to its live playback duration. Each closed white marker interval must cover that duration within 41 ms of timestamp slack. The final 350 ms marker hold is excluded from the trim duration.
- `m10-work/integration/outer-freeze.json` now records the updated script SHA-256, `5761a3508077b6c34c543c1bd3c7dea22c6494f78d8399038edbeb95b07f8137`.
- `m10-work/logs/codex-m10-preview-encode-notes.md` records this change for the supervisor’s encode-only rerun.
