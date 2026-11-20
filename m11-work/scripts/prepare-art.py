"""Prepare Region 6 background geometry, scope, and prompts offline.

The ROM decoder and nearest-neighbor references follow M10's prepare-art.py.
"""

import hashlib
import json
import struct
from io import BytesIO
from pathlib import Path

from PIL import Image


WORK = Path(__file__).resolve().parents[1]
ROOT = WORK.parent
ART = WORK / "art"
ROM = Path("m8-work/runtime/assets/game.gbc")
CATALOG = Path("m6-work/raw_maps.json")
BROWSER = Path("m11-work/play/region6-official")
CHAIN = Path("m11-work/official-chain")
CHECKPOINTS = Path("m11-work/checkpoints")
ROM_SHA256 = "ab42ec7ab339125dc685f4aa56eedfafaa2a8ecf46a4659e3c0f05eedd57ff95"
START_SHA256 = "c41b4188203bc45d2d0c5eeb24f8b307040be0644ce861ffbcc6281d4060c8f1"
END_SHA256 = "f8e87d6ae1b9b23261c2e0a2800151391dd93aed3bd0c4b6267985d32e22f428"
STYLE_ROOT = Path("m8-work/art")
PRIOR = {
    milestone: (Path(f"m{milestone}-work/region{milestone - 5}-scope.json"),
                Path(f"m{milestone}-work/runtime/assets/region1/maps.json"))
    for milestone in (10, 9, 8)
}
REUSED = {
    "00-2a": (10, "00-2a_gpt.png", "feaaafb20609c6404ba2d4c09240f6c54fbd44d637672e0aaf20b6722cc07290"),
    "00-0b": (10, "00-0b_gpt.png", "23e24cf442e74cca71b3fd63bab9befabc1d1c6086e7a028461e9ed9fda944b3"),
    "00-09": (8, "00-09_gpt.png", "ce5f58afabbfa937a68cbb1a211a891eff1658514f1411eb80e3a2d32911804c"),
    "00-00": (8, "00-00_gpt.png", "91df59c53ab4bb4e11c70288e636198e948ab307ae35b7572c2e5821b1a5a717"),
    "00-06": (8, "00-06_gpt_v2.png", "91125e14a469c162db6454acd0d573b812d9908ae8c1c45a90a26fb39676316a"),
}
STYLES = {
    "00-2a": ("forest", "石阶两侧的林冠和灌木适合林地图参考。"),
    "00-0b": ("forest", "林道、树丛和溪流与林地图参考的材质相符。"),
    "00-09": ("forest", "林间通路及其两侧植被适合林地图参考。"),
    "00-00": ("town", "村落建筑、院落和道路适合城镇参考。"),
    "00-06": ("room", "庙内墙面、地板和家具适合室内参考。"),
    "00-25": ("town", "城镇参考的屋瓦、立面与植被笔触适合塔楼外景。"),
    "00-26": ("room", "迷宫以成排围墙、铺面与固定摆设为主，采用室内参考的材质笔触。"),
    "00-27": ("room", "云间迷宫的围墙、铺面与地面机关适合室内参考。"),
    "00-28": ("room", "云台围墙和铺地延续相邻迷宫的建筑材质，采用同一室内参考。"),
    "00-29": ("room", "殿内铺面、墙板、家具和花盆适合室内参考。"),
    "00-2e": ("room", "室内参考的石墙、木构和灯具笔触适合洞内砌体、护栏与火把。"),
}
NEW_NAMES = {
    "00-25": ("云中塔门", "蓝天白云下有绿顶多层塔楼、紫栏与入塔石路。"),
    "00-26": ("回廊迷宫", "方形金边围墙内有折转绿篱、菱格地面与固定金像。"),
    "00-27": ("云台迷宫", "蓝天白云围绕金边方台，台内绿篱分隔出多个格区。"),
    "00-28": ("云台回廊", "较小的金边云台上有相连绿篱、狭道和方形下行口。"),
    "00-29": ("双像殿", "殿堂中并排摆放两尊金像，后墙有盆栽与成对小面板。"),
    "00-2e": ("石洞", "蓝灰砌壁围出曲折的灰色地道，沿路有火把、木栏和红箱。"),
}
NEW_ART = {
    "00-25": (
        "Preserve the tall blue sky, isolated clouds and bank of white clouds behind the "
        "green tiered tower. Keep the tower entrance, horizontal purple railing, rows of "
        "trees and shrubs, pale south approach, stone edging and full-height black strip at right.",
        "Keep the exact marks along the purple rail and tower trim as they appear. Add no text.",
    ),
    "00-26": (
        "Keep the gold stepped rectangular enclosure, black corner voids, pale diamond floor "
        "and gap centered on the south wall. Preserve the exact angular hedge network, including "
        "each corridor gap and dead end, the three fixed gold statues, and every green and gray "
        "floor fixture, circular mark and red-rimmed fixture at its original position.",
        "Copy the diamonds, narrow marked panels and bands on the pale perimeter masonry directly "
        "from image 1, with their exact spacing and strokes. Add no text.",
    ),
    "00-27": (
        "Keep the gold enclosure and pale diamond paving surrounded by bright blue sky and "
        "small white clouds. Preserve the asymmetrical hedge cells and their narrow gaps, all "
        "square stair openings, green floor fixtures, orange star-shaped ground details, "
        "red-rimmed fixtures and the fixed gold statue in the lower-left interior.",
        "Copy the repeated diamond motifs and short strokes along the pale border panels directly "
        "from image 1. Keep the orange star shapes on the ground exactly as shown. Add no text.",
    ),
    "00-28": (
        "Keep the compact gold-walled platform amid blue sky and scattered white clouds. Keep "
        "the pale diamond paving, connected angular hedge loops and narrow passages, each square "
        "stair opening, the small gray-green floor fixture, two orange star-shaped details and "
        "the red-rimmed fixture near the lower right.",
        "Preserve the repeated diamond motifs, panel marks and paving details in their original "
        "positions and forms. Add no text.",
    ),
    "00-29": (
        "Keep the two fixed gold statues on their bases, the gold rail perimeter against blue "
        "sky, the pale diamond paving and the square stair opening below and just right of center. "
        "Keep the paired green cabinets and planters along the rear wall, the low plants in the "
        "room corners and the plant and geometric border details along the outside front wall.",
        "The two narrow plaques centered on the rear wall carry small brown strokes. They lie "
        "within native pixel boxes x 80–95 and x 96–111, both y 16–31 from the top-left. Copy the "
        "exact stacked strokes, light gaps and outlined pale faces without assigning a reading. "
        "Keep the flanking dark diamond motifs and meander border as drawn. Add no text.",
    ),
}
CAVE_TILES = (
    ("north", (0, 0, 480, 256),
     "Keep the upper east–west passage, its west bend, the pair of upper-right bays divided by "
     "wood, the long railing below them and the narrow middle branches around the black recesses."),
    ("south", (0, 224, 480, 480),
     "Keep the chest alcoves at left and right with all four red chests, the winding lower "
     "passages and deep black gaps, the narrow openings at the bottom and each wooden railing."),
)
CAVE_SEAM = (
    "Align both strips to the native crops at one common scale. Compare the shared rows against "
    "each other and the ROM geometry. Start seam review at native y=240 (assembled y=960). "
    "Approve the join only when corridor edges, masonry, fixtures, colors and black voids agree. "
    "Return mismatched strips for repaint and review."
)
# Observed in memory during an in-order replay of all accepted actions.
MAZE_LAYOUT = {
    "00-26": ("6ca4b2ab0749f941284bdc6907c4733b28548e43b7f787be034986153f6dc8c3",
              {0: 28191, 10: 35465, 11: 36007, 6: 59841}),
    "00-27": ("8763b56747aa89751c930872f2288718b63a2ed45e666c36ed75319607713b98",
              {0: 31537, 6: 35780, 2: 52118, 9: 59524}),
}


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def rom_read(rom, bank, address, length):
    offset = (bank - 1) * 0x4000 + address if address >= 0x4000 else address
    data = rom[offset:offset + length]
    if len(data) != length:
        raise ValueError(f"Incomplete ROM read at {bank:02x}:{address:04x}")
    return data


def render_map(rom, row):
    """Follow M8's background-only tile decoding, including CGB tile flips."""
    bank, address = (int(part, 16) for part in row["data"].split(":"))
    width, height, *pointers = struct.unpack("<BB9H", rom_read(rom, bank, address, 20))
    layout = rom_read(rom, bank, pointers[0] + 1, width * height)
    blocks = rom_read(rom, bank, pointers[1], 1024)
    subblocks = rom_read(rom, bank, pointers[2], 1024)
    attributes = rom_read(rom, bank, pointers[3], 256)
    palette_bytes = rom_read(rom, bank, pointers[4], 64)
    graphics = bytearray(0x2000)
    for copy in row["tileset_graphics"]:
        start = copy["dest"] - 0x8000
        length = copy["length"]
        graphics[start:start + length] = rom_read(rom, copy["bank"], copy["src"], length)

    geometry = sha256(bytes((width, height)) + layout + blocks + subblocks
                      + attributes + graphics + palette_bytes)
    if geometry != row["geometry_sha256"]:
        raise ValueError(f"{row['id']}: ROM geometry differs from the map catalog")

    palette = [((color & 31) * 8, ((color >> 5) & 31) * 8, ((color >> 10) & 31) * 8)
               for color in struct.unpack("<32H", palette_bytes)]
    tiles = []
    for index, attribute in enumerate(attributes):
        address = 0x1000 + (index if index < 128 else index - 256) * 16
        palette_offset = (attribute & 7) * 4
        pixels = []
        for y in range(8):
            source_y = 7 - y if attribute & 0x40 else y
            low, high = graphics[address + source_y * 2:address + source_y * 2 + 2]
            for x in range(8):
                bit = x if attribute & 0x20 else 7 - x
                color_index = ((low >> bit) & 1) | (((high >> bit) & 1) << 1)
                pixels.append(palette[palette_offset + color_index])
        tile = Image.new("RGB", (8, 8))
        tile.putdata(pixels)
        tiles.append(tile)

    image = Image.new("RGB", (width * 32, height * 32))
    for y in range(height * 4):
        for x in range(width * 4):
            block = layout[(y // 4) * width + x // 4]
            subblock = blocks[block * 4 + (y % 4) // 2 * 2 + (x % 4) // 2]
            tile = subblocks[subblock * 4 + (y % 2) * 2 + x % 2]
            image.paste(tiles[tile], (x * 8, y * 8))
    return image


def write_prepared(path, data):
    if path.exists():
        if path.read_bytes() != data:
            raise ValueError(f"Existing prepared file differs: {path}")
        return
    path.write_bytes(data)


def write_png(path, image):
    output = BytesIO()
    image.save(output, format="PNG")
    write_prepared(path, output.getvalue())


def read_json(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def write_json(path, value):
    data = json.dumps(value, ensure_ascii=False, indent=2) + "\n"
    write_prepared(path, data.encode("utf-8"))


def checked_hash(path, expected):
    digest = sha256((ROOT / path).read_bytes())
    if digest != expected:
        raise ValueError(f"SHA-256 mismatch: {path}")
    return digest


def enlarged(image):
    return image.resize((image.width * 4, image.height * 4), Image.Resampling.NEAREST)


def official_visits():
    start = CHECKPOINTS / "story19-00-2a-official.bin"
    end = CHECKPOINTS / "region6-end-native.bin"
    checked_hash(start, START_SHA256)
    checked_hash(end, END_SHA256)
    actions = CHAIN / "official-region6-actions.json"
    native = read_json(CHAIN / "official-region6-replay/result.json")
    browser = read_json(BROWSER / "result.json")
    checked_hash(actions, native["actionsSHA256"])
    for result in (native, browser):
        if (result["status"], result["sourceSHA256"], result["totalActions"],
                result["totalFrames"]) != ("COMPLETE", START_SHA256, 717, 63131):
            raise ValueError("Official replay metadata differs")
        last = result["end"]
        if (last["map"], last["entry"], last["cell"], last["facing"], last["story"],
                last["settled"], last["D2AC"]) != ("00-2e", 3, [25, 5], 2, 22, True, ["10", "01"]):
            raise ValueError("Official replay cutoff differs")
    if browser["errors"] or browser["initial"]["romSHA256"] != ROM_SHA256 or native["end"]["sha256"] != END_SHA256:
        raise ValueError("Official replay error or hash mismatch")

    visits = {}
    for record in browser["records"]:
        if not {"initial", "map-change", "end"}.intersection(record["reasons"]):
            continue
        path = BROWSER / f"{record['name']}.bin"
        visits.setdefault(record["map"], []).append({
            "snapshot": path.as_posix(),
            "snapshotSHA256": checked_hash(path, record["stateSHA256"]),
            "frame": record["frame"],
            "entry": record["entry"],
            "story": record["story"],
        })
    if visits.keys() != (REUSED.keys() | NEW_NAMES.keys()):
        raise ValueError("Official route map set differs")
    return visits


def prior_maps():
    return {
        milestone: (
            {row["id"]: row for row in read_json(scope)["maps"]},
            {row["id"]: row for row in read_json(registry)},
        )
        for milestone, (scope, registry) in PRIOR.items()
    }


def reuse_plate(map_id, native_size, geometry, prior):
    milestone, filename, expected_sha = REUSED[map_id]
    comparisons = {}
    for version, (scope, registry) in prior.items():
        prior_scope = scope.get(map_id)
        prior_registry = registry.get(map_id)
        comparisons[f"M{version}"] = {
            "scope": "MATCH" if prior_scope else "ABSENT",
            "registry": "MATCH" if prior_registry else "ABSENT",
        }
        if prior_scope and (prior_scope["nativeSize"], prior_scope["geometrySHA256"]) != (native_size, geometry):
            raise ValueError(f"{map_id}: geometry or native size differs from M{version} scope")
        if prior_registry and ([prior_registry["width"], prior_registry["height"]],
                               prior_registry["geometrySHA256"]) != (native_size, geometry):
            raise ValueError(f"{map_id}: geometry or native size differs from M{version} registry")

    scope, registry = prior[milestone]
    accepted = registry[map_id]
    if not accepted["artReady"]:
        raise ValueError(f"{map_id}: accepted registry plate is missing")
    source = Path(f"m{milestone}-work/art") / filename
    checked_hash(source, expected_sha)
    checked_hash(Path(f"m{milestone}-work/runtime") / accepted["image"], expected_sha)
    note = f"原生尺寸和几何 SHA-256 与 M{milestone} 范围及运行时登记一致，沿用已验收画板。"
    fields = {"name": scope[map_id]["name"], "artStatus": f"REUSED_M{milestone}",
              "reusePlate": source.as_posix(), "reusePlateSHA256": expected_sha,
              "geometryComparison": comparisons, "reuseNote": note}
    if map_id == "00-06":
        fields["reuseNote"] += " M8 监督记录及 integration/provenance.json 确认 v2，且 v2 源图与 M8 在用画板逐字节一致。"
    return fields


def accepted_size_evidence():
    successes = []
    for milestone in (9, 10):
        art = Path(f"m{milestone}-work/art")
        for item in read_json(art / "batch-manifest.json"):
            output = art / item["output"]
            meta_path = output.with_suffix(".png.meta.json")
            meta = read_json(meta_path)
            if meta["ok"] and meta["size"] == item["size"] and any(
                    attempt["status"] == 200 for attempt in meta["attempts"]):
                successes.append((tuple(item["requestedSize"]), meta_path, output))
    largest, meta_path, output = max(successes, key=lambda entry: entry[0][0] * entry[0][1])
    with Image.open(ROOT / output) as image:
        returned = image.size
    return largest, meta_path, returned


def fits_request(size, envelope):
    return all(dimension <= limit for dimension, limit in zip(sorted(size), sorted(envelope)))


def art_prompt(map_id, native_size, requested_size, layout_note, glyph_note, tile=None):
    width, height = native_size
    target_width, target_height = requested_size
    subject = f"one full-map painted HD 2D JRPG background plate for map {map_id}"
    geometry = "the character-free original ROM background"
    if tile:
        left, top, right, bottom = tile["nativeBox"]
        subject = f"the {tile['part']} strip of one painted HD 2D JRPG background plate for map {map_id}"
        geometry = (f"the character-free ROM crop at x [{left}, {right}) and y [{top}, {bottom}) "
                    "within the 480×480 native map")
        layout_note += (" Continue the exact material scale and colors through the shared 32 native rows "
                        "(map y [224, 256)). Keep the full-width overlap and match corridor edges, "
                        "masonry and black voids up to the crop boundary.")
    return f"""Create {subject} in the approved V4 style.

Image 1 is {geometry} at exact 4× nearest-neighbor. Its native size is {width}×{height}. Paint the entire rectangle at {target_width}×{target_height}. Retain its exact aspect ratio, extent, axes, framing and aligned overhead orthographic view. Keep every edge flush with the provided rectangle.

Image 2 supplies V4 brushwork, lighting and material texture only. Use crisp, deliberate painted detail and retain the original map's palette identities. Take the layout, fixtures and marks exclusively from image 1. Paint the complete rectangle with original brushwork.

Lock the original count, positions, sizes and exact footprints of all walls, doors, paths, openings, furnishings, plants, floor features and terrain edges in image 1. Keep walkable routes and obstacles where they are. Keep pure black voids and their exact boundaries. {layout_note}

BACKGROUND GLYPHS ARE LOCKED. Copy every visible background glyph or glyph-like mark from image 1, including its strokes, colors, scale, spacing, count, order and position. {glyph_note}

ZERO characters, people, monsters, animals, portraits, sprites, silhouettes, character shadows, UI, dialogue, speech bubbles, watermarks or overlay text. Fixed fixtures and statues drawn into the native background stay in place. Layout and background glyph fidelity take priority over decoration.
"""


def prepare_request(request_id, map_id, image, geometry_name, scale, style, layout, glyphs, tile=None):
    requested_size = (image.width * scale, image.height * scale)
    prompt = f"{request_id}_prompt.txt"
    write_prepared(ART / prompt, art_prompt(map_id, image.size, requested_size, layout, glyphs, tile).encode("utf-8"))
    item = {
        "id": request_id,
        "refs": [geometry_name, f"{style}_style.png"],
        "prompt": prompt,
        "output": f"{request_id}_gpt.png",
        "size": f"{requested_size[0]}x{requested_size[1]}",
        "quality": "medium",
        "model": "gpt-image-2",
        "nativeSize": image.size,
        "requestedSize": requested_size,
        "reviewRequired": True,
    }
    if tile:
        item["tile"] = tile
    return item


def prepare_cave(image, map_scope, scale, envelope):
    if image.size != (480, 480) or scale != 4 or fits_request(map_scope["requestedSize"], envelope):
        raise ValueError("Cave geometry or size envelope differs from the reviewed plan")
    tiles = []
    requests = []
    for part, box, layout in CAVE_TILES:
        crop = image.crop(box)
        request_id = f"00-2e-{part}"
        geometry_name = f"{request_id}_native_4x.png"
        write_png(ART / geometry_name, enlarged(crop))
        tile = {
            "mapId": "00-2e",
            "part": part,
            "nativeBox": box,
            "boxConvention": "zero-based half-open [left, top, right, bottom]",
            "nativeOverlapBox": [0, 224, 480, 256],
            "nativeOverlapPixels": 32,
            "outputOverlapPixels": 128,
            "assemblySize": map_scope["requestedSize"],
            "assemblyOrigin": [box[0] * scale, box[1] * scale],
            "seamReview": CAVE_SEAM,
        }
        layout += (" Keep the rough gray corridor floors, blue-gray masonry, torches and woodwork "
                   "within the crop at their exact footprints.")
        glyphs = "Keep the small marks in the masonry, railings and floor as drawn. Add no text."
        request = prepare_request(request_id, "00-2e", crop, geometry_name, scale, "room", layout, glyphs, tile)
        if not fits_request(request["requestedSize"], envelope):
            raise ValueError(f"{request_id}: exceeds observed request envelope")
        requests.append(request)
        tiles.append({"id": request_id, "nativeBox": box, "requestedSize": request["requestedSize"],
                      "assemblyOrigin": tile["assemblyOrigin"], "geometryRef": f"m11-work/art/{geometry_name}"})
    map_scope["tiling"] = {
        "reason": "Full 1920×1920 request exceeds the largest observed accepted M9/M10 request.",
        "boxConvention": tile["boxConvention"],
        "assemblySize": tile["assemblySize"],
        "nativeOverlapBox": tile["nativeOverlapBox"],
        "nativeOverlapPixels": tile["nativeOverlapPixels"],
        "outputOverlapPixels": tile["outputOverlapPixels"],
        "seamReview": CAVE_SEAM,
        "tiles": tiles,
    }
    return requests


def prepare_map(rom, row, visits, prior, envelope):
    map_id = row["id"]
    image = render_map(rom, row)
    geometry = row["geometry_sha256"]
    style, style_basis = STYLES[map_id]
    native_name = f"{map_id}_native.png"
    geometry_name = f"{map_id}_native_4x.png"
    write_png(ART / native_name, image)
    # M10 uses these exact 4× nearest-neighbor PNGs as geometry inputs.
    write_png(ART / geometry_name, enlarged(image))

    entry = {
        "id": map_id,
        "nativeSize": list(image.size),
        "geometrySHA256": geometry,
        "naturalReplay": visits[0]["snapshot"],
        "naturalReplayVisits": visits,
        "independentDoorSurvey": False,
        "nativePNG": f"m11-work/art/{native_name}",
        "geometryRef": f"m11-work/art/{geometry_name}",
        "styleRef": f"m11-work/art/{style}_style.png",
        "styleBasis": style_basis,
    }
    native_checkpoints = {
        "00-2a": "story19-00-2a-official", "00-06": "r6-party-restored",
        "00-26": "r6-maze-entrance", "00-29": "r6-story21-fan", "00-2e": "region6-end-native",
    }
    if map_id in native_checkpoints:
        checkpoint = CHECKPOINTS / native_checkpoints[map_id]
        metadata = read_json(checkpoint.with_suffix(".json"))
        if metadata["map"] != map_id:
            raise ValueError(f"{map_id}: native checkpoint map differs")
        path = checkpoint.with_suffix(".bin")
        entry.update(nativeCheckpoint=path.as_posix(), nativeEndSHA256=checked_hash(path, metadata["sha256"]))

    if map_id in REUSED:
        entry.update(reuse_plate(map_id, list(image.size), geometry, prior))
        entry["nameBasis"] = f"沿用已验收的 {entry['artStatus'].removeprefix('REUSED_')} 名称。"
        return entry, []

    name, name_basis = NEW_NAMES[map_id]
    scale = 4 if image.width * image.height * 16 >= 655360 else 5
    target = [image.width * scale, image.height * scale]
    entry.update(name=name, nameBasis=name_basis, artStatus="PREPARED_NOT_GENERATED",
                 requestedSize=target, requestScale=scale)
    if map_id in MAZE_LAYOUT:
        layout_sha, match_frames = MAZE_LAYOUT[map_id]
        if set(match_frames) != {visit["entry"] for visit in visits}:
            raise ValueError(f"{map_id}: maze entry coverage differs")
        entry["plateGranularity"] = {
            "runtimeMapKey": map_id,
            "plates": 1,
            "entries": list(match_frames),
            "loadedLayoutAddress": "C100",
            "layoutBlockCount": 144,
            "layoutSHA256": layout_sha,
            "layoutMatchFrameByEntry": match_frames,
            "evidence": "Each official entry loaded the same 144-block ROM layout for this map ID. "
                        "During initial transition frames the buffer can still contain the outgoing map. "
                        "M10 keys plates by FF9A/FF9B and validates visible tile geometry. FF9C is the entry field.",
        }

    if map_id == "00-2e":
        return entry, prepare_cave(image, entry, scale, envelope)
    if not fits_request(target, envelope):
        raise ValueError(f"{map_id}: a reviewed tiling plan is required for {target}")
    layout, glyphs = NEW_ART[map_id]
    request = prepare_request(map_id, map_id, image, geometry_name, scale, style, layout, glyphs)
    return entry, [request]


def main():
    rom = (ROOT / ROM).read_bytes()
    if sha256(rom) != ROM_SHA256:
        raise ValueError("Accepted ROM SHA-256 mismatch")
    rows = {row["id"]: row for row in read_json(CATALOG)["maps"]}
    visits = official_visits()
    prior = prior_maps()
    envelope, size_metadata, returned = accepted_size_evidence()
    ART.mkdir(exist_ok=True)
    for style in ("town", "room", "forest"):
        filename = f"{style}_style.png"
        write_prepared(ART / filename, (ROOT / STYLE_ROOT / filename).read_bytes())

    maps = []
    manifest = []
    for map_id, map_visits in visits.items():
        entry, requests = prepare_map(rom, rows[map_id], map_visits, prior, envelope)
        maps.append(entry)
        manifest.extend(requests)
        width, height = entry["nativeSize"]
        sizes = ", ".join(item["size"] for item in requests)
        print(f"{map_id} {width}x{height} {entry['geometrySHA256']} | {entry['artStatus']} {sizes}".rstrip())

    scope = {
        "candidateMapCount": len(maps),
        "maps": maps,
        "identificationEvidence": [
            f"{ROM} 为已验收 ROM，SHA-256 {ROM_SHA256}。角色为空的原生底图及几何校验使用 {CATALOG}。",
            f"{CHECKPOINTS}/story19-00-2a-official.bin 为正式起点，00-2a e0 (5,8)，story 19，SHA-256 {START_SHA256}。",
            f"{CHAIN}/official-region6-actions.json 含 717 个动作及 63131 帧。"
            f"{CHAIN}/official-region6-replay/result.json 为连续原生回放记录。",
            f"{BROWSER}/result.json 为监督者验收的浏览器回放，COMPLETE，errors=[]。"
            "m11-work/REQUEST_READY.md 记录路线顺序，m11-work/rom-gate-analysis.md 记录剧情门槛。",
            "路线经 00-0b、00-09、00-00 至 00-06 恢复队伍，再返回 00-2a。"
            "随后经 00-25 进入 00-26、00-27、00-28、00-29，取得伏魔扇后返回至 00-2e。",
            f"{CHECKPOINTS}/region6-end-native.bin SHA-256 {END_SHA256}。"
            f"对应浏览器 {BROWSER}/end.bin，第 63131 帧为 00-2e e3 (25,5)，朝左，story 22，D2AC=10 01（伏魔扇）。",
            "M10 的 m10-work/runtime/region-renderer.js 和 assets/region1/maps.json 使用地图 ID 查找画板，"
            "并校验视窗的图块几何。两座 384×384 迷宫的原生几何 SHA-256 各异，每张地图的正式入口共用其各自的底图。",
            f"M9/M10 的 batch-manifest.json 及 *_gpt.png.meta.json 中，面积最大的 HTTP 200 请求为 "
            f"{envelope[0]}×{envelope[1]}（{size_metadata}），返图为 {returned[0]}×{returned[1]}。"
            "这是已观察到的请求尺寸，返图尺寸须在画板审核时核对。尺寸规则为原生 4 倍面积达到 655360 时请求 4 倍，否则 5 倍。",
        ],
        "nextStoryGate": "定格于 00-2e e3 (25,5)，朝左，story 22，已取得伏魔扇。"
                         "范围止于向左踏上 (24,5) 触发 story 23 之前。",
        "exclusions": [
            "战斗画面与系统菜单不计作地图画板。",
            "00-2e (24,5) 的 story 23 触发、其后路线及未自然进入的连通地图均排除。",
            "00-2e 画板保留整张 480×480 原生几何。路线证据截止于 (25,5)。",
        ],
        "artStatus": "PREPARED_NOT_GENERATED",
        "notAllConnectedWorldMaps": True,
    }
    write_json(ART / "batch-manifest.json", manifest)
    write_json(WORK / "region6-scope.json", scope)


if __name__ == "__main__":
    main()
