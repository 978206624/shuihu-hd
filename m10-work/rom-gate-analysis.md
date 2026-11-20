# ROM gates after the 黄泥岗 inn

The next progression interaction is in `00-23`. Its actor becomes visible after the rear-room scene, then writes stories 15 and 16 in one interaction. Story 16 makes the `酒` door check for beast `24`. Bringing that beast back opens the second inn sequence, which ends at story 19 with pocket-2 item `04`. The recommended region endpoint is the first settled arrival at `00-2a e0 (5,8)`, before the item is used at row 4.

## Starting state and evidence

The official save is 199608 bytes with SHA-256 `f389cebc3fc59a310571c66538d38808c32483c7632164f35d207f0738e8d6c0`. It settles at `00-2c e0 (4,4)`, facing up (`1`), field bank `05`, dialogue and mode `00`, `FFBA=0e`, `DAA0..3=e6 72 01 38`, and `DABB=00`. The first player bytes at `CD00` are `50 48 01 01` (`80,72,1,1` in decimal). The active roster at `D200` starts with beast `02`, the second slot at `D216` is empty, storage at `DB20` is empty, and pocket 2 at `D284` is empty. Serialized offsets are 147568 for fixed WRAM (`C000`), 151664 for bank 1 (`D000`), and 199440 for HRAM (`FF80`). [Official checkpoint](checkpoints/story14-inn-end.bin)

Addresses use hexadecimal `bank:CPU address`, story numbers use decimal, and coordinates use zero-based 16-pixel cells. `eN` is the destination entry. Warp records are six bytes and `ee` matches either coordinate independently. The map table is at `07:4000`, and the entry record holds the warp-table pointer and NPC bank. Standable edge cells come from the map's 32-pixel blocks, 16-pixel subtile table and collision bytes as documented in the M9 analysis. The tables below show collision-zero cells, with entry, actor and flag restrictions called out where they affect the route. [Raw gate records and collision output](logs/codex-m10-rom-gate.log#L2149) · [M9 analysis](../m9-work/rom-gate-analysis.md)

At `05:40e3–4129`, the field code reads the resident warp table at `DF00` and dispatches by record type. Type 0 at `05:412a` loads map, entry and banner unconditionally. Type 1 at `05:414e` matches the exact story, with operand zero accepting any story. Type 6 at `05:41bb` accepts stories strictly below a nonzero operand. A failed story test advances to the next record. Type 3 at `05:413a` loads a map in another group. Type 2 at `05:4175` writes a selector to `D1E3` without moving maps. Type 5 at `05:41a5` sets the ability selector at `D0EE` and a script pointer. VM opcode `1f` writes the story byte `FFBA` at `0b:47be`.

## Inn and forest exits

| From | Trigger cells or door | Destination and condition | ROM record |
| --- | --- | --- | --- |
| `00-2c e0` | South `(6..7,9)` | `00-2b e1 (8,1)` | `07:4dff` |
| `00-2c e1` | South `(6..7,9)` | Exactly 17. Runs `21:4b6b` via `00-2b e2`, with the fruit game returning to `00-2b e3 (9,1)` | `07:4e06` |
| `00-2b e0/e1` | South `(3..4,9)` | `00-24 e2 (6,5)` | `07:4deb` |
| `00-2b e0/e1` | North `(8..9,0)` | `00-2c e0 (6,8)` | `07:4df1` |
| `00-2b e2/e3` | South `(3..4,9)` | Exactly 18. Runs `21:4958` and loads `00-24 e3 (6,7)` | `07:4df8` |
| `00-24` | South `(3..4,15)` | `00-21 e5 (16,1)` | `07:4ced` |
| `00-24` | East `(15,10..11)` | `00-0a e1 (1,3)` | `07:4cf3` |
| `00-24` | `酒` at `(6,4)` | At exactly 16, `21:4b07` chooses `00-2c e1 (6,3)` if the beast test passes, or `00-2b e0 (3,8)` otherwise. At other stories the type-0 record goes to `00-2b e0 (3,8)` | `07:4cf9/4cff` |
| `00-21` | West `(0,5..6)` | `00-23 e0 (14,2)` | `07:4c7e/4c84` |
| `00-21` | West `(0,10..11)` | `00-20 e2 (12,5)` | `07:4c8a/4c90` |
| `00-21` | South `(10..11,15)` | `00-1f e5 (16,1)` | `07:4c96` |
| `00-21` | East `(23,13..14)` | `00-1f e1 (1,11)` | `07:4c9c/4ca2` |
| `00-21` | East `(23,2..3)` | `00-1f e4 (22,2)` | `07:4ca8/4cae` |
| `00-21` | North `(16..17,0)` | `00-24 e0 (4,14)` | `07:4cb4/4cba` |
| `00-21` | North `(8..9,0)` | `00-22 e1 (14,8)` | `07:4cc0/4cc6` |
| `00-1f` | West `(0,5..6)` | `00-08 e3 (22,9)` | `07:4c16/4c1c` |
| `00-1f` | West `(0,10..11)` | `00-21 e3 (22,13)` | `07:4c22/4c28` |
| `00-1f` | South `(10..11,15)` | `00-20 e3 (10,1)` | `07:4c2e` |
| `00-1f` | East `(23,2..3)` or `(23,13..14)` | `00-20 e0 (1,3)` | `07:4c34/4c3a/4c40/4c46` |
| `00-1f` | North `(16..17,0)` | `00-21 e2 (10,14)` | `07:4c4c/4c52` |
| `00-1f` | North `(8..9,0)` | `00-22 e0 (6,8)` | `07:4c58/4c5e` |
| `00-20` | West `(0,3..4)` | `00-1f e3 (22,13)` | `07:4c65` |
| `00-20` | South `(12..13,15)` | `00-21 e5 (16,1)` | `07:4c6b` |
| `00-20` | East `(15,4..5)` | `00-1f e0 (1,5)` | `07:4c71` |
| `00-20` | North `(10..11,0)` | `00-1f e2 (10,14)` | `07:4c77` |
| `00-22` | South `(6..7,9)` | `00-1f e6 (8,1)`, from the western half | `07:4ccd/4cd3` |
| `00-22` | South `(14..15,9)` | `00-21 e6 (8,1)`, from the eastern half | `07:4cd9/4cdf` |
| `00-23` | East `(15,2..3)` | `00-21 e0 (1,5)` | `07:4ce6` |

The `00-2c e1` and `00-2b e2/e3` tables each contain just the scripted south crossing. Their exact-story tests apply even at the other room's normal exit coordinates. The earlier inn entries retain their own type-0 exits. [Entry and collision dump](logs/codex-m10-rom-gate.log#L7488)

The listed inn and forest type-0 exits have the same conditions at stories 12 and 14, including the crossings to `00-20`, `00-22`, `00-23` and `00-0a`. The `酒` door's special branch still requires exact story 16. The rear scene clears `DAA1.7` and sets `DAA2.0` at `21:4ae8–4aef`. The first change removes 史进 from the rear room, and the second enables the actor at `00-23 (12,6)`. That actor was unavailable at story 12 with `DAA2.0=0`. The remaining rear-room NPC 惠农 at `(3,3)` uses `21:4af3` and native talk settled at story 14. `00-22` has two disconnected entry halves with the official bytes. Its layout selector `0d` reads `DABB.0–3` at `1e:4a8f–4aa9`. The native 金翅鸟羽 chest interaction settled at story 14. [Rear talk](native/story14-talk-00-2c-npc33/result.json) · [Chest interaction](native/story14-talk-00-22-uuuu/result.json)

## Eastern route and side gates

| From | Trigger cells | Destination or effect | ROM record |
| --- | --- | --- | --- |
| `00-0a` | South `(4..6,15)` | `00-0b e2 (26,1)` | `07:4a8d` |
| `00-0a` | West `(0,2..4)` | `00-24 e1 (14,10)`, with banner `0d` | `07:4a93` |
| `00-0b` | South `(2..4,23)` | `00-09 e1 (18,1)` | `07:4a9a` |
| `00-0b` | North `(16..18,0)` | `00-2a e0 (5,8)` | `07:4aa0/4aa6/4aac` |
| `00-0b` | North `(25..27,0)` | `00-0a e0 (5,14)` | `07:4ab2/4ab8/4abe` |
| `00-0b` | East `(31,5..7)` | `00-2d e0 (1,2)` | `07:4ac4` |
| `00-0b` | `(16,8)` or `(29,5)` | Type 2 sets `D1E3` to `08` or `09`, respectively | `07:4aca/4ad0` |
| `00-09` | North `(1..3,0)` | `00-00 e7`, with banner `01` | `07:4a44/4a4a/4a50` |
| `00-09` | North `(16..18,0)` | Dry eastern crossing to `00-0b e0 (2,22)` | `07:4a56/4a5c/4a62` |
| `00-09` | North `(10..12,0)` | `02-1f e0 (6,10)`, beyond the rock | `07:4a68/4a6e/4a74` |
| `00-09` | `(4,2)` | Type 2 sets `D1E3=0a` | `07:4a7a` |
| `00-09` | `(11,5)` or `(11,3)` | Type 5 selects the rock interaction `21:41f4` or `21:41e6` | `07:4a80/4a86` |
| `00-2d` | West `(0,2..3)` | `00-0b e3 (28,5)` | `07:4e13` |
| `00-2d` | Upper area `(4,1..2)` | Below 24, gate script `21:452a` | `07:4e0d` |
| `00-2d` | Lower area south `(7..8,9)` | Group change to `01-00 e0`. Reachable from lower entry `e1 (7,8)` in the base grid | `07:4e19` |
| `00-2a e0` | Row 4 `(4..6,4)` | Below 21, item gate `08:50f2` | `07:4dd8` |
| `00-2a e0/e1/e2` | North `(4..6,0)` | Story operand zero. `08:4bc8` loads `00-25 e1`, then `00-26 e0 (11,22)` | `07:4dde/4dd1` |
| `00-2a e0/e1/e2` | South `(4..6,9)` | `00-0b e1 (17,1)` | `07:4de4/4dcb` |

- **神木林.** The rock at `00-09 (11,4)` separates the usual south approach from the group-2 crossing. Stand `(11,5)`, face up and press A. `05:4cdf→05:4d67` converts the tile selector `01` to internal ability 2. `25:406a` checks innate ability (`25:46c2`) or learned value `11` in slots `+14/+15` of one of the eligible species at `25:47cd`. Official beast `02` fails. The inn flags leave this check in place. From `02-1f` its south `(5..6,11)` returns to `00-09 e2 (11,1)`, north `(8,0)` leads to `02-20 e0`, and `(4,6)` leads to `02-23 e0`, at `50:4e5a/4e60/4e66`. The dry `00-09 → 00-0b` crossing has no story or ability test. [M9 rock analysis and NPC evidence](../m9-work/rom-gate-analysis.md#the-00-09-rock-and-00-0b)
- **`00-2d` 山门.** `21:451d` puts sprite `19` at `(4,1)` while `DAA2.5=0`. In `21:452a`, bit `.5` clear selects dialogue `21:4d90` and script bytes `05 02; 0f 4c 41`. Bit `.5` set selects `21:6e6c` and `05 03; 0f 4e 41`. The supervisor saw the 伏魔扇 refusal at story 14. The gate script tests the flag, which the story-21 fan reward sets. Neither branch writes story or loads a map. The base grid has collision 2 between the upper and lower areas. Arrival from `00-0b` enters the upper area, so the lower group change is a separate, conditional reachability question. The story-14 native interaction settled in the upper area at 14. [Native gate result](native/story14-talk-00-2d-gate2/result.json) · [Base collision and gate bytes](logs/codex-m10-rom-gate.log#L4707)

Native surveys reached `00-2c`, `00-2b`, `00-24`, `00-21`, `00-1f`, `00-20`, `00-22`, `00-0a`, `00-0b` and `00-2d` at story 14. The `00-21` survey had 1801 nodes, frontier zero and battle recovery disabled. Its archive has a field state at `(4,5)` and only non-field states at `(3,5)` on the west approach. The `00-0b` archive has field states at `(24,18)` and only battle states at `(23,18)` on the route to the north crossing. Directed walking through those encounters remains a host check. [Native chain summary](outer-runs/story14-door-chain-summary.json) · [`00-21` branch data](search/story14-doors-00-21-full/branches.jsonl) · [`00-0b` branch data](search/story14-doors-00-0b/branches.jsonl) · [Survey settings](search/story14-doors-00-21-full/provenance.json)

## Next story writes

| Story write | Trigger with standing cell and facing | Script and requirements | Expected settled state |
| --- | --- | --- | --- |
| **15 → 16** | `00-23`, stand `(12,7)` facing up and press A on sprite `06` at `(12,6)` | Actor record `21:4cb8` requires `DAA2.0=1`. `21:4cc4` plays the scene, removes the actor and grants beast `17`. `21:4d2f` calls VM `38` at `0b:4d59`, then `2d:50a7` loads record `2d:523d`. `21:4d32` clears `DAA2.0`. `21:4d36` has `1f 0f 1f 10 09`. | `00-23`, `FFBA=10`, `DAA1/DAA2=72/00`. Story 15 is a transient write. |
| **17** | `00-24`, walk up from `(6,5)` into the `酒` door `(6,4)` | Exact 16 at `07:4cf9→21:4b07`. `6f 24` recomputes `DAA3.3` via `0b:5878–58c7`. The second active slot must be occupied before the script scans party and storage for `24`. With `24` it loads `00-2c e1` and writes 17 at `21:4b68`. Without `24` it loads `00-2b e0` and stays at 16. | Success `00-2c e1 (6,3)`, `FFBA=11`, `72/00`, `DAA3.3=1`. Failure `00-2b e0 (3,8)`, `FFBA=10`, `72/00`, `DAA3.3=0`. |
| **18** | `00-2c e1`, walk down from `(6,8)` onto `(6,9)`. Column 7 also matches. | Exact 17 at `07:4e06→21:4b6b`. Stages `00-2b e2`, then `34 01 2b 03` at `21:4bec` launches fruit-catching mode 1 with return `00-2b e3`. `0b:4c4a` dispatches the mode through `00:025a→23:4000`. Score `CD0A≥23` hex (35 decimal) sets `DAA2.1` at `23:41ee–4223`. `21:4bf3` tests it and the failure branch at `21:4c1f` restarts the game. Success writes 18 at `21:4cb1` and clears `DAA1.5` at `21:4cb3`. | `00-2b e3 (9,1)`, `FFBA=12`, `52/02`, field mode. |
| **19** | `00-2b e2/e3`, walk down from `(3,8)` or `(4,8)` onto row 9. | Exact 18 at `07:4df8→21:4958`. The scene loads `00-24 e3`, removes the exterior actors, and grants pocket-2 ID `04` via `48 02 04` at `21:4a05→0b:50c2→39:47b5`. `39:4808` supplies pocket 2's pointer `D284`. `21:4a6b–4a74` clears `DAA1.5`, sets `DAA2.2`, then writes 19 at `21:4a73`. | `00-24 e3`, `FFBA=13`, `52/06`, `D284=04 01` from the official empty pocket. |

The gift fills the second active slot on the official route. The checkpoint already has `DAA3.3=1`, so the preexisting bit gives no evidence of beast `24`. The exact-16 door recomputes the bit from the roster every time. Keep the gifted beast with the starter and capture `24` through battle before returning. [Party scan and encounter data](logs/codex-m10-rom-gate.log#L21340)

The scripted entry cells in the warp table are the initial placements. VM `0f` at `0b:4513` starts a player movement list in bank `0b`. `0b:59c3` and `0b:5a25–5a75` move the player 16 pixels per direction byte until `ff`. The lists at `0b:414c`, `414e`, `418e` and `4190` are left, right, down and up, respectively. The predicted settled cells from the route below are `(13,7)` after the story-16 talk (left, right, right at `21:4ccc/4cf5/4d08`), `(8,3)` after the story-18 scene (down, down, left at `21:4c39/4c3c/4c41`), and `(6,5)` after the story-19 scene (down, up, up, up at `21:49d3/49dc/49df/49e2`). [Script bytes](logs/codex-m10-rom-gate.log#L21111)

`00-23` has a dedicated encounter table in the western area at `x<4, y<8` once story is at least 15. The field path at `05:4b83–4cad` reaches `2d:5c89`, and selector `2d:4ed4–4ef2` chooses group `07`. Its pointer goes through `2d:5e73` to the 16 entries at `2d:6185`. Indices 0, 4, 8 and 12 point to `2d:61a5`, whose initial bytes `01 24 09 19 00` specify one level-9 beast `24`. Other entries include `08` and `21`. `2d:5ca6–5cb5` increments `FFD8` and uses its low nibble for this lookup. The map and the encounter record are established from ROM. Capture inputs and the resulting natural roster still need host verification. [Encounter records](logs/codex-m10-rom-gate.log#L21622)

## Recommended official-start route

The first-time maps on this route are `00-23 → 00-0a → 00-0b → 00-2a`, with the inn revisits between `00-23` and `00-0a`. Directions below are single-cell moves from the stated entry or standing cell. Confirm position after battles, dialogue and scripted movement.

1. From the official rear room, use the native prefix `DDDRDRD` to enter `00-2b e1`. Walk south to `(3..4,9)` for `00-24 e2`, then leave the inn exterior via south `(3..4,15)` for `00-21 e5 (16,1)`. [Native prefix](search/story14-doors-00-2c/00-2b-actions.json) · [Door survey](outer-runs/story14-door-chain.log)
2. From `00-21 e5`, follow `DDDDDDDLDLLLLUUULULLLLLLLLLL` to west `(0,5)` and enter `00-23 e0 (14,2)`. Use `DLDDDDL` to reach `(12,7)`. Face up, press A and settle the story-16 scene. [ROM-derived walking paths](logs/codex-m10-rom-gate.log#L8838)
3. From the predicted settled cell `(13,7)`, row 7 connects west to `(3,7)`. Walk between `(2,7)` and `(3,7)` or between `(3,6)` and `(3,7)` to encounter beast `24`. Capture it with the normal battle controls and confirm the party entry. Return through east `(15,2..3) → 00-21 e0`. Leave at north `(16..17,0) → 00-24 e0`. Step onto `酒` from below and settle story 17 in the rear room.
4. From `00-2c e1 (6,3)` walk `DDDDDD` to the south trigger. Score at least 35 and settle at story 18. From the predicted settled cell `00-2b e3 (8,3)`, `LLDDLLDDDD` reaches `(4,9)` and avoids the listed front-room actor placements. Let the exterior scene finish, then verify story 19 and pocket-2 ID `04`.
5. From the predicted settled cell `00-24 e3 (6,5)`, `DRRRRRDDDDRRRR` reaches `(15,10) → 00-0a e1`. In `00-0a`, `DRRDRRDDDDDDDDDD` reaches south `(5,15) → 00-0b e2 (26,1)`. In `00-0b`, `DDRDDDDDDDDDDLDDDDDLLLLULLLLLLLUULUULULUUUURRRRRUUUUUUUU` reaches north `(17,0) → 00-2a e0`. Stop on settled arrival at `(5,8)`, story 19, `DAA1/DAA2=52/06`, pocket `04 01` intact. [Eastern crossing paths](logs/codex-m10-rom-gate.log#L8815)

## Boundary gate and subsequent writes

At `00-2a e0`, walk north from `(5,5)` onto `(5,4)` to test the gate. The row-4 record runs `08:50f2` below story 21. If `DAA2.2` is clear, the script gives the rejection dialogue and moves the player down. With `.2` set and `.3` clear, the scene sets `.3` at `08:5137` and removes pocket-2 ID `04` at `08:513b`. Story stays at 19 and `DAA2` becomes `0e`. With `.3` set, `08:5107` takes the short branch and skips consumption. The item-removal VM at `0b:5247–5285` searches for a matching ID without testing an empty terminator, so inconsistent flag and inventory bytes can stall the scan. The normal story-19 award supplies both the flag and the item. The north exit subsequently stages `00-25 e1` and loads `00-26 e0` via `08:4bc8`. [Gate VM bytes](logs/codex-m10-rom-gate.log#L3319)

| Later write | Trigger | ROM evidence and expected state |
| --- | --- | --- |
| **20** | `00-26`, walk down from `(12,7)` onto `(12,8)` after reaching that part of the maze. | Exact 19 at `07:4d3d→08:4e69`. Sets `DAA2.4` at `08:4ed4` and writes `FFBA=14` at `08:4ed8`. Expected `52/1e`. The `00-26` maze doors to `00-27` are at `07:4d1f–4d37`. Follow their entry-dependent passages to this cell. |
| **21** | `00-29`, stand `(6,3)` facing up and press A on sprite `2e` at `(6,2)`. | `00-28 (7,10)` leads to `00-29 e0` via `07:4dab`. Actor `08:4f73→08:4f7f` tests `DAA2.5`. With the bit clear it writes `FFBA=15` at `08:4f97`, grants pocket-1 ID `10` at `08:4f99`, and sets `.5` at `08:4f9d`. Expected `52/3e` via the story-20 route. Repeated talk takes the alternate dialogue. |
| **22** | `00-25 e0`, walk down from `(4,18)` onto south `(4,19)`. Columns 3 and 5 also match. | Exact 21 at `07:4d06→08:5090`. Stages `00-2a e2`, then loads `00-2e e3 (26,4)` and writes `FFBA=16` at `08:50de`. Expected `52/3e`. Outside story 21 the south fallback `07:4d0c` returns to `00-2a e1`. Cell `(4,17)` leads to `00-26 e0` at `07:4d12`. |

`00-2e (24,5)` has the next exact-22 trigger at `07:4e20→08:53ca`. The maze, fan reward and `00-2e` are beyond the proposed endpoint. The recommended cutoff keeps the completed inn reward intact and gives the next region a save immediately before its item gate. [Continuation records and story writes](logs/codex-m10-rom-gate.log#L7550) · [Outer verification request](REQUEST_READY.md)
