# Region 7 checkpoint removal

The owner approved removal on 2026-11-24 at approximately 01:02 CST. At action-1260 three audio-accumulator bytes differed because the save omits the resampling counter. See `~/workspace/tools/codex-m12-diag-1260-report.md`.

| Record | Index | Frame | State SHA-256 |
|---|---:|---:|---|
| action-1260 | 1260 | 68066 | a527af7b12e1f2b8560848438547e090164e317d385a7642cc520c9910f07e53 |
| action-1270 | 1270 | 68342 | 0762dff534ab9a31705de5170fe5acc8c83d91932c32b79496c695c9a63eaf89 |
| action-1280 | 1280 | 68722 | fb1e1f0b496712632005c1f9dd564abb81dd8988a84a008a9acbbf7d785d5586 |
| action-1290 | 1290 | 68974 | e6e504dc9f5e83ff16380d7b4bfcc2afd22b6723539243462cc02fb676c642d6 |
| action-1295 | 1295 | 69262 | 09e349b097bb4347b850d77666f4d9999c2667adae5b9f7b970096e4ddeb4799 |

Archive: `m12-work/outer-runs/removed-staged-checkpoints`. Official records decrease from 48 to 43, evidence checks from 47 to 42, and expected freeze entries from 884 to 879. The 00-2d perf route still uses frame-069435.
