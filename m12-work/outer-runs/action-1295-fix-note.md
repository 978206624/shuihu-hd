M12 region 7 — action-1295 registered, rerun blocked at Step 3

Focused replay from action-1290 matched every official observation from frame 68,974 through 70,186. Action-1295 at frame 69,262 has state SHA-256 09e349b097bb4347b850d77666f4d9999c2667adae5b9f7b970096e4ddeb4799. At action-1300 the native framebuffer matched dc5d60ba440fe96692befa47dde08607c5ea1c41f0e46407b60d3113027c5674. The serialized state reproduced the owner-approved deviation (9fa3b9b5… versus official 4dd4bc4d…). The separate replay from the registered action-1295 matched all observations through frame 70,186, story 24 at 00-2d (7,8).

The validator passed with 48 records (its success message still prints 43). The registration freeze verified 884/884, SHA-256 07ffb0ce82f6888a9c43ed1fba717f9d2b8e337f0c034586f5b1af85ac334040, including all 883 previous paths and all 674 M11 hashes. The production approach remains action-1300. Pending runbook reconciliation before a future run: 42 → 47 evidence checks, reflecting 48 records including initial.

The generated diagnostic route reports coldFirstTarget 173. Official frame 69,263 is input frame one after the save, and frame 69,435 first shows 00-2d. The brief requested 174 for the generated field.

Old run m12-region7-20261123T011200267902939Z retains QA 37/37 and perf 58/360 (302 remaining). New RUN_ID: none. New formal QA routes 0/37, perf samples 0/360. Contact and preview pending. M11 had 496 flagged mean timings, including 167 worse across all three paired repeats and 329 mixed or equal; prioritize the 167 for review. Timing flags carry no acceptance verdict. New M12 comparison unavailable.

| Runtime | Mode | First measured target frame | Target frames / measured | Map switches | Browser errors |
|---|---|---:|---:|---:|---:|
| m11 | legacy | none | 0 / 1792 | 0 | 0 |
| m11 | cold | 173 | 1620 / 1792 | 1 | 0 |
| candidate | legacy | none | 0 / 1792 | 0 | 0 |
| candidate | cold | 173 | 1620 / 1792 | 1 | 0 |

Traces and derived route: m12-work/outer-runs/diag-00-2d/action-1295-*.json. Both legacy traces stayed on 00-0b throughout. Unblocking requires separate owner approval for another approach, evidence of crossing under the existing four combinations, and reconciliation of the cold-frame expectation with official observations.

Finished 11:08:59 UTC. Approximate wall time 5 minutes.
