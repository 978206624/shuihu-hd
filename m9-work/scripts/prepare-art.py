"""Extract Region 4 background geometry from the accepted ROM, offline."""

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
ROM_SHA256 = "ab42ec7ab339125dc685f4aa56eedfafaa2a8ecf46a4659e3c0f05eedd57ff95"
MAP_ART = {
    "00-1f": (
        "forest",
        "Preserve the winding green forest corridors and clearings, foliage banks, tree "
        "clusters, flower patches, ochre details, and every map-edge opening.",
        "The native background has no text glyphs. The transient 黄泥岗 arrival banner "
        "belongs to the game UI. Never paint it or invent any text.",
    ),
    "00-21": (
        "forest",
        "Preserve this map's own winding green corridors, clearings, tree clusters, flower "
        "patches, ochre details, and openings. Keep the wooded layout in image 1 in full.",
        "The native background has no text glyphs. Invent no text.",
    ),
    "00-24": (
        "town",
        "Keep the single inn building, exact roof outline, black entrance, pale walls, "
        "adjoining sign, and every terrace edge, path, grass patch, tree bank, and opening.",
        "The plaque immediately left of the inn entrance displays one black 酒 glyph on a "
        "pale face. It occupies the plaque tile at native x 64–79, y 64–79, measured from "
        "the top-left. Preserve that exact glyph, color, footprint and location. Keep the "
        "two narrow red strips flanking the doorway and copy their tiny dark marks directly "
        "from image 1. Do not reinterpret the marks as new characters or add any lettering.",
    ),
    "00-2b": (
        "room",
        "Keep the left L-shaped counter, four square tables, eight stools, cabinets, plants, "
        "and two red rugs in place. Retain the upper opening toward the right and the lower "
        "entrance left of center, including the portions of the facade at the bottom edge.",
        "The native background has no readable text glyphs. Preserve the exact dark marks "
        "on the two cropped red strips at the lower entrance and the pale marks on the two "
        "red counter fixtures. Do not turn these marks into new lettering or invent any text.",
    ),
    "00-2c": (
        "room",
        "Keep the narrow centered room and its centered bottom opening. Preserve the pair "
        "of upper-left fixtures, worktop, shelving, the table on the right, all stools and "
        "plants, and the two large jars in the lower half of the room.",
        "The native background has no text glyphs. Retain the visible fixture markings "
        "and invent no text.",
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
    ART.mkdir(exist_ok=True)
    for style in ("town", "room", "forest"):
        filename = f"{style}_style.png"
        write_prepared(ART / filename, (M8 / "art" / filename).read_bytes())
    manifest = []
    for map_id, (style, layout_note, glyph_note) in MAP_ART.items():
        image = render_map(rom, rows[map_id])
        write_png(ART / f"{map_id}_native.png", image)
        # Geometry reference only. It is never a runtime background or gap fill.
        geometry = image.resize((image.width * 4, image.height * 4), Image.Resampling.NEAREST)
        geometry_name = f"{map_id}_native_4x.png"
        write_png(ART / geometry_name, geometry)

        # Match M8's requested-output sizing while keeping the input at exactly 4×.
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
        print(f"{map_id} {image.width}x{image.height} {rows[map_id]['geometry_sha256']}")
    manifest_text = json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"
    write_prepared(ART / "batch-manifest.json", manifest_text.encode("utf-8"))


if __name__ == "__main__":
    main()
