"""Prepare Region 5 background geometry and new-plate prompts offline."""

import hashlib
import json
import struct
from io import BytesIO
from pathlib import Path

from PIL import Image


WORK = Path(__file__).resolve().parents[1]
ROOT = WORK.parent
ART = WORK / "art"
M8 = ROOT / "m8-work"
M9 = ROOT / "m9-work"
ROM_SHA256 = "ab42ec7ab339125dc685f4aa56eedfafaa2a8ecf46a4659e3c0f05eedd57ff95"
MAP_IDS = ("00-2c", "00-2b", "00-24", "00-21", "00-23", "00-0a", "00-0b", "00-2a")
NEW_MAP_ART = {
    "00-23": (
        "forest",
        "Keep the broad western clearing with rows of red and cream flowers in its upper "
        "lobe, the lower-left spur, and each pale-green grass patch. Preserve the narrow "
        "low connector around the deep black recess from the top, the eastern path rising "
        "to the right-edge opening, and the exact leafy banks and ochre clusters.",
        "There are no text glyphs in the native background. Preserve the red and cream "
        "flower pattern and ochre marks as terrain details. Add no text.",
    ),
    "00-0a": (
        "forest",
        "Keep the tall map's irregular pale path from the upper-left edge opening through "
        "the upper and middle clearings to the lower-center edge opening. Preserve every "
        "narrow bend, stippled patch, intervening strip of grass, and contrasting round "
        "trees, conifers, shrubs, and grass tufts along the margins.",
        "The native background has no signs or text glyphs. Preserve the path stippling "
        "as texture and add no text.",
    ),
    "00-0b": (
        "forest",
        "Keep the branching pale woodland trails, their dotted ground patches and green "
        "islands, the two openings on the top edge, and the lower-left edge opening. "
        "Preserve the irregular blue stream and its broad bend across the lower middle, "
        "including both short plank bridges at their exact crossings. Keep the tree "
        "belts, clearings, and two wooden signboards in place.",
        "Two identical wooden sign tiles occupy native x 256–271, y 112–127 and "
        "x 464–479, y 64–79, measured from the top-left. Preserve the exact small dark "
        "strokes on both tan sign faces, including their arrangement and spacing. Copy "
        "the visible marks directly from image 1 without assigning a reading, adding "
        "legible lettering, or replacing the marks with ornaments.",
    ),
    "00-2a": (
        "forest",
        "Keep the vertical gray stone stairway slightly left of center, all visible "
        "flights and both pale-gray landings, and the purple edging along each side. "
        "Preserve the two horizontal pale stone rails across the wooded sides, each "
        "interruption at the stairway, the surrounding conifers and shrubs, and the stair "
        "openings at the top and bottom edges.",
        "There are no text glyphs in the native background. Preserve the marks on the "
        "steps, rails, and edging as stone details. Add no text.",
    ),
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


def art_prompt(map_id, native_size, requested_size, layout_note, glyph_note):
    width, height = native_size
    target_width, target_height = requested_size
    return f"""Create one full-map, newly painted HD 2D JRPG background plate in the approved V4 style for map {map_id}.

Image 1 is the character-free original ROM background at exact 4× nearest-neighbor, provided as a geometry input. Its native size is {width}×{height}. Paint the entire rectangle at {target_width}×{target_height}, retaining its exact aspect ratio and aligned overhead orthographic view. Keep the original extent, axes and framing. No cropping, margin, frame, vignette, perspective change or comparison panel.

Image 2 supplies V4 brushwork, lighting and material texture only. Use crisp, deliberate painted detail and retain the original map's palette identities. Do not import any layout, fixtures, signs, text or actors from image 2. Output a complete painted plate, never a tileset, an upscale, a smoothing pass or a filtered fallback.

Lock the original identity, count, positions, sizes and exact footprints of every building, roof, door, window, path, road, opening, furniture piece, tree, shrub, wall, floor, step, terrain boundary and decoration in image 1. Keep walkable routes and obstacles where they are. Keep the pure black void regions pure black with their original boundaries. {layout_note}

BACKGROUND GLYPHS ARE LOCKED. Faithfully preserve every glyph painted into image 1, including signs, plaques, labels and background banners, with the same characters, count, order, colors and positions. Never blank a written sign into a decorative panel, substitute floral ornaments or invent text. {glyph_note}

ZERO characters, people, monsters, animals, portraits, sprites, silhouettes, character shadows, UI, dialogue, speech bubbles, watermarks or overlay text. Layout and background glyph fidelity take priority over decoration.
"""


def main():
    rom = (M8 / "runtime/assets/game.gbc").read_bytes()
    if sha256(rom) != ROM_SHA256:
        raise ValueError("Accepted ROM SHA-256 mismatch")
    catalog = json.loads((ROOT / "m6-work/raw_maps.json").read_text(encoding="utf-8"))
    rows = {row["id"]: row for row in catalog["maps"]}
    m9_scope = json.loads((M9 / "region4-scope.json").read_text(encoding="utf-8"))
    m9_maps = {row["id"]: row for row in m9_scope["maps"]}
    ART.mkdir(exist_ok=True)
    for style in ("town", "room", "forest"):
        filename = f"{style}_style.png"
        write_prepared(ART / filename, (M8 / "art" / filename).read_bytes())
    manifest = []
    for map_id in MAP_IDS:
        row = rows[map_id]
        image = render_map(rom, row)
        geometry_sha256 = row["geometry_sha256"]
        needs_plate = map_id in NEW_MAP_ART
        if not needs_plate:
            accepted = m9_maps[map_id]
            if (list(image.size) != accepted["nativeSize"]
                    or geometry_sha256 != accepted["geometrySHA256"]):
                raise ValueError(f"{map_id}: geometry or native size differs from M9")

        write_png(ART / f"{map_id}_native.png", image)
        # Geometry reference only. It is never a runtime background or gap fill.
        geometry = image.resize((image.width * 4, image.height * 4), Image.Resampling.NEAREST)
        geometry_name = f"{map_id}_native_4x.png"
        write_png(ART / geometry_name, geometry)
        status = "new plate prepared" if needs_plate else "reuse accepted M9 plate"
        print(f"{map_id} {image.width}x{image.height} {geometry_sha256} | {status}")
        if not needs_plate:
            continue

        style, layout_note, glyph_note = NEW_MAP_ART[map_id]
        # Match M9's requested-output sizing while keeping the input at exactly 4×.
        scale = 4 if geometry.width * geometry.height >= 655360 else 5
        requested_size = (image.width * scale, image.height * scale)
        prompt_name = f"{map_id}_prompt.txt"
        prompt = art_prompt(map_id, image.size, requested_size, layout_note, glyph_note)
        write_prepared(ART / prompt_name, prompt.encode("utf-8"))
        manifest.append({
            "id": map_id,
            "refs": [geometry_name, f"{style}_style.png"],
            "prompt": prompt_name,
            "output": f"{map_id}_gpt.png",
            "size": f"{requested_size[0]}x{requested_size[1]}",
            "quality": "medium",
            "model": "gpt-image-2",
            "nativeSize": image.size,
            "requestedSize": requested_size,
            "reviewRequired": True,
        })
    manifest_text = json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"
    write_prepared(ART / "batch-manifest.json", manifest_text.encode("utf-8"))


if __name__ == "__main__":
    main()
