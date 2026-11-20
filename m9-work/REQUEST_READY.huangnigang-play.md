# M9 supervisor replay for 黄泥岗客栈

Run from the supervisor host. Every browser command starts at the official `m9-work/checkpoints/story12-meeting-end.bin` and replays the accumulated joypad inputs. Review each endpoint before running the next command. If the launcher reports a 38811 drop, stop and report the stage and timestamp from `m9-work/outer-runs/<tag>/port-stop.txt`. Use a fresh tag for any extra run. Coordinates below are zero-based 16-pixel cells.

## Load the replay command

```bash
cd /workspace/shawu

source m9-work/outer-runs/m9_play.sh
```

Each command prints the final screenshot path and save observations. `m9_show <tag> <zero-based-action-index>` shows an earlier checkpoint. Read cell and facing on settled field frames. Facing `1` is up. Keep the action PNGs and the matching JSON and byte logs with each run.

## Cross 00-08

The supervisor has already recorded these inputs from the official save. Each row gives the base replay and the appended inputs. Use the saved tags to continue.

| Saved tag | Base | Appended inputs | Observed endpoint |
| --- | --- | --- | --- |
| `m9-huangnigang-s01-approach` | `@yard` | `uuuuullluuurrrrrruururru` | Story 12, `00-08` entry 0, field cell `(19,18)` |
| `m9-huangnigang-s01-east-step` | `m9-huangnigang-s01-approach` | `r battle-wait` | Wild encounter triggered at `(20,18)`, followed by the player's intro dialogue |
| `m9-huangnigang-s01-east-intro` | `m9-huangnigang-s01-east-step` | `page` | Both beasts visible, battle command menu still pending |
| `m9-huangnigang-s01-flee` | `m9-huangnigang-s01-east-intro` | `flee` | Opened 道具 during the intro transition. The last B returned to the command menu with the cursor on 攻击. |

Resume from the [confirmed command menu](play/m9-huangnigang-s01-flee/action-0089.png). The archived sequence moves right and down from 攻击 to 逃跑, confirms with A, and clears the result with B.

```bash
m9_play m9-huangnigang-s01-menu-flee m9-huangnigang-s01-flee flee
```

Once back on the settled field at `(20,18)`, walk eight cells up to `(20,10)` and three right. At the east crossing `(23,10)`, expect `00-1f`, entry 0, arrival cell `(1,5)`, story 12. Keep the crossing and settled action checkpoints and the per-frame log.

```bash
m9_play m9-huangnigang-s01-forest m9-huangnigang-s01-menu-flee uuuuuuuurrr wait
```

If an encounter interrupts a walking leg, inspect its per-action screenshots and the frame log. Replay through the first encounter action with `m9_play <fresh-tag> <interrupted-tag>:<nextActionIndex> battle-wait`, using the value printed by `m9_show` for that action. Advance visible intro text with `page`. From the 攻击 menu position, run `m9_play <fresh-tag> <battle-ready-tag> flee`. If the cursor differs, choose 逃跑 one input at a time with `m9_play <fresh-tag> <last-tag> tap-<key>`. Use `up`, `down`, `left`, `right`, `A` or `B` for the key. Verify the return to the field and resume with the remaining moves from the observed cell along that leg. If an arrival banner is still on screen, let it settle before walking.

## Walk to the inn and talk in order

Run each line individually after reviewing the preceding endpoint. If an encounter or a banner required extra inputs, use the tag that reached the expected endpoint as the next command's base. These legs use dry cells in the ROM collision tables. The first two maps can have wild encounters.

```bash
m9_play m9-huangnigang-s01-maze m9-huangnigang-s01-forest rrrrrrddrddddllllllll wait
```

Expect `00-21`, entry 3, `(22,13)`, story 12. The crossing out of `00-1f` is `(0,11)`.

```bash
m9_play m9-huangnigang-s01-town m9-huangnigang-s01-maze lulullullluuuuuuuruuu wait
```

Expect `00-24`, entry 0, `(4,14)`, story 12. The crossing out of `00-21` is `(16,0)`.

```bash
m9_play m9-huangnigang-s01-inn m9-huangnigang-s01-town uuuuuuuurruu wait
```

The walk passes south of the NPC at `(5,5)`. The `酒` door at `00-24 (6,4)` leads to `00-2b`, entry 0, `(3,8)`, story 12.

```bash
m9_play m9-huangnigang-s01-front-talk m9-huangnigang-s01-inn ruuuuu page
```

This approaches from `(4,3)` facing up and presses A at the NPC at `(4,2)`. Advance each visible dialogue page when prompted. Use `m9_play <fresh-tag> <last-tag> page` for each additional A press. If the scene is animating, use `wait`. End the first conversation on settled `00-2b`, story **13**, with `DAA1` bit 6 set. The NPC at `(1,6)` has a separate line.

From the confirmed `(4,3)` endpoint, take the north opening at `(8,0)` and enter `00-2c`, entry 0, `(6,8)`. Set `front_done` to the tag that finished the front-room conversation. If the first A press completed it, use `front_done=m9-huangnigang-s01-front-talk`.

```bash
m9_play m9-huangnigang-s01-rear "$front_done" rurrruu wait
```

```bash
m9_play m9-huangnigang-s01-rear-talk m9-huangnigang-s01-rear ulluuu page
```

This approaches from `(4,4) facing up and presses A at the NPC at `(4,3)`. Advance the visible dialogue with the same single-page command until the scene finishes. Stop at settled `00-2c`, story **14**. Capture the dialogue, the NPC's departure, `DAA1` bit 7 clear and `DAA2` bit 0 set. These are the two inn triggers requested from the official start.
