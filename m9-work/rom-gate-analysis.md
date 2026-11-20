# Story 12 ROM analysis for 黄泥岗客栈

The inn is reachable at story 12 by the east edge of `00-08`. The ROM checks the two inn conversations in order. The first writes story 13 and the second writes story 14.

## Route evidence

Addresses use `bank:CPU address`. Positions are zero-based 16-pixel cells. M6's warp and dynamic-map catalogs located the map data. The route below comes from the ROM headers, warp records, collision tables, and handlers. M8's final 吴用 meeting and region handoff identify the mission as 黄泥岗客栈.

| From | Crossing | Destination | ROM evidence |
| --- | --- | --- | --- |
| `00-08` | East edge `(23,9)` or `(23,10)` | `00-1f` entry 0, `(1,5)` | `07:4a01` has `17 ee 00 1f 00 0d`. `ee` matches any row, and collision exposes these two rows. `0d` starts the arrival banner, which clears `FFC1` at `0d:403b`. |
| `00-1f` | West edge `(0,10)` or `(0,11)` | `00-21` entry 3, `(22,13)` | Type 0 in table `07:4c16`. |
| `00-21` | North edge `(16,0)` or `(17,0)` | `00-24` entry 0, `(4,14)` | Type 0 in table `07:4c7e`. |
| `00-24` | `酒` at `(6,4)` | `00-2b` entry 0, `(3,8)` | In table `07:4ced`, the type-1 record checks story 16. The handler at `05:414e` advances to the next record at story 12, which is the normal door. |
| `00-2b` | North edge `(8,0)` or `(9,0)` | `00-2c` entry 0, `(6,8)` | Type 0 with a wildcard column in table `07:4deb`. |

The type-0 handler at `05:412a` writes the destination map, entry and banner without comparing the story byte. All six `00-08` entries share the same map data, actor list and warp table. The two dry north crossings in `00-00` at `(4,0)` and `(5,0)` use entry 0. The other village crossings to `00-08` entry 5 and `00-35` have collision value 3 in the base layout. The maps in the inn route have base `layout_flag=0`. The verified village approach uses the usual north crossing and requires only walking.

The archived door survey excluded battle states from its walking queue. Its 24-move branch `uuuuullluuurrrrrruururru` from the settled `00-08` entry reached `(19,18)` in field bank `05` (node 684, up, queued as node 732). One step east entered battle bank `2b` at `(20,18)` (node 732, right). The queue stopped short of dry cell `(20,17)` and the eastern exit. The supervisor's official-start browser replay reproduced the approach and encounter.

To verify the dry walking legs, read the group-0 header pointer from `07:4000 + 2 × map index`. In the referenced map-data header, pointer 0 plus 1 holds the 32-pixel blocks, pointer 1 expands each block to four 16-pixel subtiles, and pointer 8 gives each subtile's collision byte. The planned walking legs use collision value 0 and avoid unrelated map exits and active NPC locations. Entry coordinates follow the first four bytes of the entry record, with `x = 2*raw[0] + (raw[2]-8)/16` and `y = 2*raw[1] + (raw[3]-16)/16`.

## Inn scripts and expected observations

The official save has `FF9A/FF9B=00/05`, `FFBA=0c` (12), `DAA1=b2`, `DAA2=00` and `DAA3=38`. The end of the meeting script at `21:44e3–44fa` sets `DAA1` bits 4, 5 and 7 before writing story 12. Bit 6 is clear. For these serialized 199608-byte saves, fixed WRAM starts at offset 147568, bank 1 at 151664, and HRAM at 199440.

- **Front room `00-2b`, entry 0.** NPC list `21:4857` loads two visible NPCs on `DAA1` bit 5. The record for sprite `04` puts the actor at `(4,2)` and points to `21:48b2`. Talk from `(4,3)` facing up. The script tests bit 6 and takes the scene when clear. At `21:48d9` it sets bit 6, then at `21:48dd` it writes story 13. The NPC at `(1,6)` uses `21:4884` and has no story write.
- **Rear room `00-2c`, entry 0.** NPC list `21:4a92` loads sprite `06` at `(4,3)` while `DAA1` bit 7 is set. Talk from `(4,4)` facing up. The handler `21:4aa9` tests bit 6. Before the front scene it gives an alternate line. Afterward it branches to `21:4ab3`, plays the scene and removes the talking actor at `21:4ae6`. It clears `DAA1` bit 7 at `21:4ae8`, sets `DAA2` bit 0 at `21:4aec` and writes story 14 at `21:4af0`. The NPC at `(3,3)` uses `21:4af3`.

The actor record reads sprite, x and y in that order at `00:0670–06a7`. `05:465a–467b` matches the selected flag bit to the record's required value. VM opcode `1f` writes `FFBA` at `0b:47be`. On outer play, check the mapped room, the target interaction, the complete dialogue and the settled story values 13 and 14. The expected flag bytes after the two scenes are `DAA1=f2` and then `DAA1=72, DAA2=01` if no other flags change.

## The 00-09 rock and 00-0b

- `00-09 → 00-0b` uses a **separate** northern crossing at `(16..18,0)`. The three type-0 records start at `07:4a56`, with no story or party test in their handler. The base collision grid has a dry eastern approach. This crossing remains unconfirmed by natural play from the official save.
- The rock occupies `00-09 (11,4)`. Its north opening at `(10..12,0)` leads to `02-1f` via type 3. The type-5 records at `(11,3)` and `(11,5)` set `D0EE=1` and select scripts `21:41e6` and `21:41f4` respectively. From the south, stand at `(11,5)`, face up and press A with a qualified active beast. The A handler at `05:4cdf` reaches `05:4d67`, which increments the tile selector to internal ability ID 2 and checks the active party at `25:406a`. On success, the script faces the rock, runs the animation and changes the map block through VM opcode `2e`. Those are the observable signs of removal.
- The party check first looks for innate ability 2 in the species table at `25:46c2`. It then tests for learned value `11` in either slot at hexadecimal offsets `+14/+15` and checks the species list at `25:47cd` (`0d 16 26 3d 55 61 58 63 42`). The official party contains only beast ID `02`, whose innate table entry is zero and whose slot bytes are `20 00`. It fails the check. The repository character guide associates 鲁智深 with rock breaking. The earliest acquisition of a qualifying beast and ability remains unverified. The ROM establishes a party gate for `02-1f` and a type-0 crossing to `00-0b`. Both branches are outside the inn route.

The supervisor confirmed the approach and encounter from the official save. The crossing and inn conversations await continuous confirmation on the supervisor host. See [REQUEST_READY.md](REQUEST_READY.md).
