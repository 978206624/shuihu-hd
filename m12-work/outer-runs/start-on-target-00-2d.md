# Region 7 performance route, 2026-11-23

Replaced action-1300 with frame-069435 at (31,7) on 00-2d. The sample measures rendering on 00-2d without testing the warp transition, following the 00-2f design. Both runtimes in both modes recorded their first target frame at 1 and stayed on target for 1792/1792 frames each. The four traces and derived route are under diag-00-2d/frame-069435-*.json. The action window comprises 7 released frames, 744 remaining input frames and 1041 idle frames.

The runbook now expects 47 non-initial evidence checks across 48 records after registration of five checkpoints. The generator's final printed 43-record message is stale. The replay validator checks 48. The owner accepted the focused replay action-1300 serialized hash 9fa3b9b5… versus official 4dd4bc4d… with matching observations and framebuffer.

Verified 884/884 freeze entries. Prior SHA-256 07ffb0ce82f6888a9c43ed1fba717f9d2b8e337f0c034586f5b1af85ac334040. New SHA-256 a5bc60b7d47a33464cdddd700d377a70a5d46264fd8e4d6b083eb177f3b81238. The other 29 routes match the prior plan.
