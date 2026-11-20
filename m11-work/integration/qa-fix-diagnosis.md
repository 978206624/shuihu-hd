# M11 Region 6 QA diagnosis

## Reproduction

Replayed `official-chain/official-region6-actions.json` natively from
`checkpoints/story19-00-2a-official.bin` using the pinned ROM and binjgb WASM
through `scripts/native-play.cjs`. The checkpoint SHA-256 is
`c41b4188203bc45d2d0c5eeb24f8b307040be0644ce861ffbcc6281d4060c8f1`.
The failed QA coordinates are zero-based action 705 and frame 83 within
`["A",6,120]`. This is official action 706, cumulative frame **61,811**,
at tick 19,298,475,356. The failure and native replay agree on map `00-2a`,
entry 2, story 21, bank `0x0a`, mode 0, script 1 and dialogue 1.

| SHA-256 at the failing frame | Value |
| --- | --- |
| Save state | `cef1ffbdecd1a0941dde2d52a4817b978f9dcb635734b61c12ade0ac0702512b` |
| Native framebuffer | `fc25121efb4a45f650f86e5ba6acb8f0916478fe3c99ae04f5dbf1102a650462` |
| Native text samples | `dc54019e38f189022b14cf272be3987747e5b04cedf0d4dd7b40bf01524417cb` |
| HD text samples, both runtimes (failed run) | `3af37820647455cc61a9abe4f37dee771976b4917552900d380ffce006970598` |

The observer sees LCDC `0xc7`, WX `0` (effective x = −7), WY `0`,
SCX `0`, SCY `0`, LY `20`, LYC `143`, STAT `0xc0`, VBK `0xfe`.
LCDC selects BG map `0x9800` and signed tile addressing. Its window-enable
bit is clear. The window map selection is `0x9c00`, whose top rows contain
residual tile IDs (e.g. row 1 has `6d 6e` in columns 2–3) and whose rows
10–17 have zero tile IDs over the visible 20 columns. Neither its contents
nor WX/WY contribute to the raster here.

Selected `0x9800` rows from the replay, with matching CGB attributes from
VRAM bank 1. The values start at column 0 and are hexadecimal.

| BG row | Tile IDs | Attributes |
| --- | --- | --- |
| 10 | `a1 a2 a2 a2 a2 a2 a2 a2 a2 a2 a1` | `06 06 06 06 06 06 06 06 06 06 06` |
| 11 | `a3 f0 f1 f2 f3 e0 e2 e4 e6 e8 a3` | `06 07 07 07 07 00 00 00 00 00 06` |
| 12 | `a3 f4 f5 f6 f7 e1 e3 e5 e7 e9 a3` | `06 07 07 07 07 00 00 00 00 00 06` |
| 13 | `a3 f8 f9 fa fb a0 a0 a0 a0 00 00` | `06 07 07 07 07 00 00 00 00 00 06` |

## Cause

The completed framebuffer still contains 23,040 opaque black pixels.
The live VRAM already contains a partially written BG dialogue. The
observer detects a rectangle at x=0, y=80, w=88, h=64, and marks 2,688
pixels. QA uses the observer mask, excludes visible actors and BG frame
tiles `a1`–`a4`, then hashes each selected pixel's screen index and all
sixteen 4× RGBA texels in row-major order. There are 1,664 text/portrait
samples within x=8–79, y=88–111. Each expected texel is black. There are
zero actor samples. At frame 61,810 the framebuffer is equally black and
the observer finds no rectangle or text. At frame 61,812 the framebuffer
displays the portrait and text in color.

`Renderer.prepareFlat` accepts the uniform framebuffer and the empty
actor mask. `Renderer.drawFlat` then covers the native raster with the
tinted `assets/maps/intertitle_hd.png` transition plate. Even its black
tint contains nonzero texture, which changes the sampled texels. Both
runtimes report `verified-flat-transition`, 23,040 covered pixels and
zero map-source pixels on this frame. The plate covering the text samples
is the shared transition plate. The `00-2a` map plate is bypassed.
The observer and text hash expose the difference between the live BG
snapshot and the completed raster. They continue to check the same pixels
in the fixed runtime.

Failed evidence is under
[`results/m11-region6-20261120T140423261638555Z`](../results/m11-region6-20261120T140423261638555Z/),
including [the mismatch](../results/m11-region6-20261120T140423261638555Z/qa/official-region6/mismatch.json).

## Fix and verification

M11 keeps the full native blackout when the flat renderer sees black RGB
and the observer selects protected dialogue/window content. The full
blackout also avoids drawing the outline of the unpresented dialogue as
a black patch over the plate. Both the previous black frame without UI
and the first colored dialogue frame retain their respective render paths.
The flat-transition branch still updates map presentation history in the
same order.

The candidate must pass the same per-frame actor and text comparisons and
the action-end presentation contract. QA accepts the M10 text mismatch
only when save state, native framebuffer, ticks, map, story, mode, bank,
actor hashes and native text agree, and the candidate's complete 640×576
output hashes as opaque black
(`b4c4ef9ea935ae7ea7e09d0ca937589322a2091db5d6b920aeea67f1357377f7`).
The comparator also checks that M10 reported a verified flat plate and
that coverage is exactly 23,040 eligible pixels with 23,040 covered in
M10 and zero covered in M11. M11 counts those background pixels as native
gap. For earlier-region frames, exact HD and coverage matches are counted
in `earlierVisualPassed`. Verified exceptions are counted in
`earlierKnownDefectFrames`. The sum must account for every earlier-region
frame. `baselineKnownDefectFrames` and `baselineKnownDefects` give the
total and individual frame evidence across all routes, including any
instances on the 35 inherited routes.

`node m11-work/scripts/qa-flat-ui-unit.cjs` performed the native replay and
tested the renderer's flat-path decision with an integer-copy Canvas
stub. The repaired text hash matched the native hash at frame 61,811,
and the comparator rejected an unchanged M10-style mismatch, candidate
pixel/hash and coverage changes, and a mismatch outside the flat path.
JavaScript and shell syntax checks, the revised jq acceptance fixture
and `verifyFreeze()` passed. Formal browser QA and the inherited-route
exception counts are pending the supervisor's fresh run.
