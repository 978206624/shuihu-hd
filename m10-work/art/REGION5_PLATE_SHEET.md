# 区域5 画板对照表

对照图：`m10-work/art/region5_plate_sheet.png`

生成接口：gpt-image-2，quality=medium，参考为各图 `_native_4x.png` + `forest_style.png`。禁止使用放大/平滑兜底。

## 新绘（已验收）

| 地图 | 名称 | 原生尺寸 | GPT 输出 | 文件 |
| --- | --- | ---: | ---: | --- |
| 00-23 | 黄泥岗西林 | 256×160 | 1586×992 | `00-23_gpt.png` |
| 00-0a | 出岗小径 | 192×256 | 1086×1448 | `00-0a_gpt.png` |
| 00-0b | 密林山道 | 512×384 | 1448×1086 | `00-0b_gpt.png` |
| 00-2a | 石阶密林 | 192×160 | 1374×1145 | `00-2a_gpt.png` |

纵横比均与原生一致。无角色、无新造文字；00-0b 两块木牌保留原暗纹。

## 复用 M9（几何 SHA 与原生尺寸一致）

- 00-2c 黄泥岗客栈后室 → `m9-work/art/00-2c_gpt.png`
- 00-2b 黄泥岗客栈前厅（含接水果同一地图） → `m9-work/art/00-2b_gpt.png`
- 00-24 黄泥岗客栈外 → `m9-work/art/00-24_gpt.png`
- 00-21 黄泥岗街区 → `m9-work/art/00-21_gpt.png`

范围见 `m10-work/region5-scope.json`。
