"""Copy the accepted M8 runtime and add the supervisor-reviewed M9 PNGs offline."""

import json
import shutil
import struct
import tempfile
from pathlib import Path

from PIL import Image
from prepare_art_ref import load_prepare_art

prepare = load_prepare_art()
ROOT, WORK, ART = prepare.ROOT, prepare.WORK, prepare.ART
SOURCE = ROOT / "m8-work/runtime"
DEST = WORK / "runtime"
REGISTRY = Path("assets/region1/maps.json")
IDS = ("00-1f", "00-21", "00-24", "00-2b", "00-2c")
sha = prepare.sha256


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def files(path):
    return {str(p.relative_to(path)): sha(p.read_bytes()) for p in sorted(path.rglob("*"))
            if p.is_file()}


def native_spec(rom, row, scope):
    """Use the same CGB cell keys, attributes and palettes as M8 prepare-art."""
    bank, address = (int(part, 16) for part in row["data"].split(":"))

    def read(address, length):
        return prepare.rom_read(rom, bank, address, length)

    width, height, *pointers = struct.unpack("<BB9H", read(address, 20))
    layout = read(pointers[0] + 1, width * height)
    blocks, subblocks = read(pointers[1], 1024), read(pointers[2], 1024)
    attributes, raw_palette = read(pointers[3], 256), read(pointers[4], 64)
    graphics = bytearray(8192)
    for copy in row["tileset_graphics"]:
        start, length = copy["dest"] - 0x8000, copy["length"]
        require(0 <= start <= start + length <= len(graphics), "Invalid CGB graphics range")
        graphics[start:start + length] = prepare.rom_read(rom, copy["bank"], copy["src"], length)
    geometry = sha(bytes((width, height)) + layout + blocks + subblocks + attributes
                   + graphics + raw_palette)
    map_id = scope["id"]
    require(geometry == row["geometry_sha256"] == scope["geometrySHA256"], f"{map_id}: geometry")
    require([width * 32, height * 32] == scope["nativeSize"], f"{map_id}: native dimensions")
    keys_by_tile = []
    for tile, attr in enumerate(attributes):
        offset = 0x1000 + (tile if tile < 128 else tile - 256) * 16
        key = ((2166136261 ^ (attr & 7)) * 16777619) & 0xffffffff
        for y in range(8):
            row_offset = offset + 2 * (7 - y if attr & 64 else y)
            low, high = graphics[row_offset:row_offset + 2]
            for x in range(8):
                bit = x if attr & 32 else 7 - x
                index = ((low >> bit) & 1) | (((high >> bit) & 1) << 1)
                key = ((key ^ index) * 16777619) & 0xffffffff
        keys_by_tile.append(key)

    tiles = []
    for y in range(height * 4):
        for x in range(width * 4):
            block = layout[(y // 4) * width + x // 4]
            subblock = blocks[block * 4 + (y % 4) // 2 * 2 + (x % 4) // 2]
            tiles.append(subblocks[subblock * 4 + (y % 2) * 2 + x % 2])
    palettes = [v for color in struct.unpack("<32H", raw_palette)
                for v in ((color & 31) * 8, ((color >> 5) & 31) * 8, ((color >> 10) & 31) * 8, 255)]
    return dict(id=map_id, name=scope["name"], width=width * 32, height=height * 32,
                widthTiles=width * 4, heightTiles=height * 4, image=f"assets/region4/{map_id}_hd.png",
                imageNativeSize=width * 32, imageNativeHeight=height * 32,
                cellKeys=[keys_by_tile[tile] for tile in tiles], tiles=tiles,
                attrs=[attributes[tile] for tile in tiles], palettes=palettes,
                geometrySHA256=geometry, native=f"m9-work/art/{map_id}_native.png",
                gptSource=f"m9-work/art/{map_id}_gpt.png", artReady=True)


def main():
    require(not DEST.exists(), f"Runtime already exists: {DEST}")
    require(not any(p.is_symlink() for p in SOURCE.rglob("*")), "Unexpected runtime symlink")
    original = files(SOURCE)
    rom = (SOURCE / "assets/game.gbc").read_bytes()
    require(sha(rom) == prepare.ROM_SHA256, "Accepted ROM mismatch")
    require(original["assets/region3/00-06_hd.png"] ==
            "91125e14a469c162db6454acd0d573b812d9908ae8c1c45a90a26fb39676316a",
            "M8 live 00-06 v2 mismatch")
    catalog = {r["id"]: r for r in read_json(ROOT / "m6-work/raw_maps.json")["maps"]}
    old_specs = read_json(SOURCE / REGISTRY)
    old_ids = {s["id"] for s in old_specs}
    require(len(old_specs) == len(old_ids) == 29 and not old_ids.intersection(IDS), "M8 registry")
    adopted = read_json(ROOT / "m8-work/integrity/adopted-runtime-sha256.json")
    require(all(original.get(p) == h for p, h in adopted.items() if p != str(REGISTRY)),
            "Adopted runtime hash mismatch")
    # Cross-check the metadata implementation against all eight accepted M8 entries.
    for old in read_json(SOURCE / "assets/region3/maps.json"):
        baseline = {"id": old["id"], "name": old["name"], "geometrySHA256": old["geometrySHA256"],
                    "nativeSize": [old["width"], old["height"]]}
        spec = native_spec(rom, catalog[old["id"]], baseline)
        require(all(spec[k] == old[k] for k in ("cellKeys", "tiles", "attrs", "palettes")),
                f"{old['id']}: M8 metadata parity")

    scope = {s["id"]: s for s in read_json(WORK / "region4-scope.json")["maps"]}
    requests = {s["id"]: s for s in read_json(ART / "batch-manifest.json")}
    require(set(scope) == set(requests) == set(IDS), "Unexpected scope")
    review = ART / "SUPERVISOR_VISUAL_REVIEW.md"
    specs, records = [], []
    with tempfile.TemporaryDirectory(prefix=".m9-runtime-", dir=WORK) as temp:
        stage = Path(temp) / "runtime"
        shutil.copytree(SOURCE, stage)
        require(files(stage) == original, "Copied runtime differs from source")
        (stage / "assets/region4").mkdir()
        for map_id in IDS:
            require(f"| {map_id} | Accept |" in review.read_text(), f"{map_id}: missing acceptance")
            spec = native_spec(rom, catalog[map_id], scope[map_id])
            request = requests[map_id]
            source = ART / f"{map_id}_gpt.png"
            meta = source.with_suffix(".png.meta.json")
            request_meta = read_json(meta)
            require(request["output"] == source.name and request_meta["ok"] and
                    request_meta["out"] == str(source.relative_to(ROOT)) and
                    request_meta["model"] == request["model"] == "gpt-image-2" and
                    request_meta["quality"] == request["quality"] == "medium" and
                    request_meta["size"] == request["size"] and
                    request_meta["attempts"][-1]["status"] == 200, f"{map_id}: CLI metadata")
            native_size = [spec["width"], spec["height"]]
            require(request["nativeSize"] == native_size, f"{map_id}: request native size")
            native = prepare.render_map(rom, catalog[map_id])
            with Image.open(ROOT / spec["native"]) as reference:
                require(reference.size == native.size and reference.tobytes() == native.tobytes(),
                        f"{map_id}: native reference differs from ROM")
            with Image.open(source) as image:
                require(image.format == "PNG", f"{map_id}: expected PNG")
                actual = list(image.size)
                image.verify()
            with Image.open(source) as image:
                image.load()
            width, height = native_size
            require(abs(actual[0] * height - actual[1] * width) <= (width + height) / 2,
                    f"{map_id}: actual dimensions break native aspect ratio: {actual}")
            target = stage / spec["image"]
            shutil.copyfile(source, target)
            digest = sha(source.read_bytes())
            require(sha(target.read_bytes()) == digest, f"{map_id}: PNG copy differs")
            specs.append(spec)
            records.append(dict(id=map_id, source=spec["gptSource"], sourceSHA256=digest,
                                originalCLIMetadata=str(meta.relative_to(ROOT)), metadataSHA256=sha(meta.read_bytes()),
                                actualDimensions=actual, requestedDimensions=request["requestedSize"],
                                requestedModel=request_meta["model"], requestedQuality=request_meta["quality"],
                                serverReturnedQuality=None, runtimeAsset=spec["image"], runtimeSHA256=digest))

        native_metadata = ART / "native-map-metadata.json"
        if native_metadata.is_file():
            prepared = {s["id"]: s for s in read_json(native_metadata)}
            require(set(prepared) == set(IDS), "Prepared metadata map IDs differ")
            for spec in specs:
                for key in ("width", "height", "widthTiles", "heightTiles", "cellKeys",
                            "tiles", "attrs", "palettes", "geometrySHA256"):
                    require(prepared[spec["id"]][key] == spec[key], f"Prepared metadata differs: {spec['id']} {key}")
        write_json(stage / "assets/region4/maps.json", specs)
        write_json(stage / REGISTRY, old_specs + specs)
        final = files(stage)
        changed = {p for p, digest in original.items() if final.get(p) != digest}
        added = set(final) - set(original)
        require(changed == {str(REGISTRY)}, f"Unexpected existing file changes: {changed}")
        require(added == {"assets/region4/maps.json", *(s["image"] for s in specs)}, f"Unexpected additions: {added}")
        require(files(SOURCE) == original, "M8 source changed during the copy")
        stage.rename(DEST)

    integration = WORK / "integration"
    integration.mkdir(exist_ok=True)
    write_json(integration / "provenance.json", dict(
        adoptedBase="m8-work/runtime", originalFileCount=len(original), mapRegistryCount=34,
        modifiedExistingFiles=sorted(changed), addedFiles=sorted(added),
        originalCodeROMCoreUnchanged=True, coverage="PENDING_OUTER_QA",
        review=str(review.relative_to(ROOT)), newMaps=records,
        m8RuntimeSHA256=original, m9RuntimeSHA256=final))
    print(f"Verified {len(original)} M8 files, registered 34 maps, copied five PNGs verbatim.")


if __name__ == "__main__":
    main()
