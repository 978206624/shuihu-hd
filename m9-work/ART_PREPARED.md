# Region 4 art prepared

Status `PREPARED_NOT_GENERATED`. The inputs come from the accepted ROM's background tile data. The 4× files are nearest-neighbor geometry references. The copied V4 style reference is the second input for each map.

| Map | Native | 4× geometry input | Prompt | V4 style |
| --- | --- | --- | --- | --- |
| `00-1f` 黄泥岗林道 | [384×256](art/00-1f_native.png) | [1536×1024](art/00-1f_native_4x.png) | [00-1f](art/00-1f_prompt.txt) | [forest](art/forest_style.png) |
| `00-21` 黄泥岗街区 | [384×256](art/00-21_native.png) | [1536×1024](art/00-21_native_4x.png) | [00-21](art/00-21_prompt.txt) | [forest](art/forest_style.png) |
| `00-24` 黄泥岗客栈外 | [256×256](art/00-24_native.png) | [1024×1024](art/00-24_native_4x.png) | [00-24](art/00-24_prompt.txt) | [town](art/town_style.png) |
| `00-2b` 黄泥岗客栈前厅 | [192×160](art/00-2b_native.png) | [768×640](art/00-2b_native_4x.png) | [00-2b](art/00-2b_prompt.txt) | [room](art/room_style.png) |
| `00-2c` 黄泥岗客栈后室 | [192×160](art/00-2c_native.png) | [768×640](art/00-2c_native_4x.png) | [00-2c](art/00-2c_prompt.txt) | [room](art/room_style.png) |

`00-21` uses the forest style because the native geometry is a wooded passage. The room entries follow M8's requested-output sizing at 960×800. Their geometry inputs are 768×640.

- Batch manifest for `gpt-image-2`, quality `medium`. [art/batch-manifest.json](art/batch-manifest.json)
- Scope and settled save hashes. Each endpoint is part of the official-start route, so `independentDoorSurvey` is `false` throughout. [region4-scope.json](region4-scope.json)
- Offline extraction and preparation script. [scripts/prepare-art.py](scripts/prepare-art.py)

## Supervisor glyph check before GPT

- **`00-24` has one confirmed background glyph.** Check the black `酒` on the pale plaque immediately left of the entrance. The plaque occupies native x 64–79 and y 64–79 from the upper-left. Check both thin red doorway strips and preserve their dark marks exactly as shown. [4× geometry](art/00-24_native_4x.png)
- **`00-2b` has small marks to cross-check.** Inspect the two cropped red strips at the lower entrance and the two red counter fixtures. Their marks have no readable transcription at native resolution. The prompt preserves the visible marks as drawn. [4× geometry](art/00-2b_native_4x.png)
- `00-1f`, `00-21`, and `00-2c` have no visible background glyphs. The `黄泥岗` banner on arrival in `00-1f` belongs to the game UI.
