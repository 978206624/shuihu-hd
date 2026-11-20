"""Copy the accepted M9 runtime and append the reviewed Region 5 PNGs offline."""

import json
import shutil
import struct
import tempfile
from pathlib import Path

from PIL import Image
from prepare_art_ref import load_prepare_art

prepare = load_prepare_art()
ROOT, WORK, ART = prepare.ROOT, prepare.WORK, prepare.ART
SOURCE = ROOT / "m9-work/runtime"
DEST = WORK / "runtime"
REGISTRY = Path("assets/region1/maps.json")
NEW = {"00-23": [1586, 992], "00-0a": [1086, 1448],
       "00-0b": [1448, 1086], "00-2a": [1374, 1145]}
REUSED = ("00-21", "00-24", "00-2b", "00-2c")
REGION = Path("assets/region5")
INTEGRATION = WORK / "integration"
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


def rom_map(rom, scope):
    """Resolve a group-00 map header and the graphics copies from the accepted ROM."""
    read = lambda bank, address, size: prepare.rom_read(rom, bank, address, size)
    group, index = (int(part, 16) for part in scope["id"].split("-"))
    require(group == 0, "Expected a group-00 map")
    header, = struct.unpack("<H", read(7, 0x4000 + 2 * index, 2))
    bank, _, _, _, address = struct.unpack("<BBBBH", read(7, header, 6))
    _, _, *pointers = struct.unpack("<BB9H", read(bank, address, 20))
    if pointers[5]:
        copies = [dict(bank=bank, src=pointers[5], dest=0x9000, length=0x800),
                  dict(bank=bank, src=pointers[6], dest=0x8800, length=0x300)]
    else:
        copies = []
        for i in range(50):
            source_bank, dest, length, src = struct.unpack("<BHHH", read(0x3e, pointers[6] + i * 7, 7))
            if source_bank == 0xff:
                break
            copies.append(dict(bank=source_bank, src=src, dest=dest, length=length))
        else:
            raise ValueError(f"{scope['id']}: unterminated graphics list")
    return dict(id=scope["id"], data=f"{bank:02x}:{address:04x}", tileset_graphics=copies,
                geometry_sha256=scope["geometrySHA256"])


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
                widthTiles=width * 4, heightTiles=height * 4, image=f"assets/region5/{map_id}_hd.png",
                imageNativeSize=width * 32, imageNativeHeight=height * 32,
                cellKeys=[keys_by_tile[tile] for tile in tiles], tiles=tiles,
                attrs=[attributes[tile] for tile in tiles], palettes=palettes,
                geometrySHA256=geometry, native=f"m10-work/art/{map_id}_native.png",
                gptSource=f"m10-work/art/{map_id}_gpt.png", artReady=True)


def verify_runtime(runtime, expected):
    actual = files(runtime)
    require(actual == expected, f"Runtime tree differs: {runtime}")
    require(not any(p.is_symlink() for p in runtime.rglob("*")), "Unexpected runtime symlink")


def append_registry(path, original, old_specs, specs):
    prefix = original.rstrip()
    require(prefix.endswith(b"]"), "Unexpected registry ending")
    added = json.dumps(specs, ensure_ascii=False, indent=2).encode("utf-8")
    # Keep every old entry verbatim and replace only the array terminator.
    path.write_bytes(prefix[:-1].rstrip() + b"," + added[1:-1] + b"]" + original[len(prefix):])
    require(read_json(path) == old_specs + specs, "Registry append differs")


def main():
    m9 = SOURCE.parent
    prefix = str(SOURCE.relative_to(ROOT)) + "/"
    original = {file.removeprefix(prefix): digest
                for file, digest in read_json(m9 / "integration/outer-freeze.json").items()
                if file.startswith(prefix)}
    verify_runtime(SOURCE, original)
    rom = (SOURCE / "assets/game.gbc").read_bytes()
    require(sha(rom) == prepare.ROM_SHA256, "Accepted ROM mismatch")
    registry_bytes = (SOURCE / REGISTRY).read_bytes()
    old_specs = json.loads(registry_bytes)
    old_by_id = {s["id"]: s for s in old_specs}
    require(len(old_specs) == len(old_by_id) == 34 and not old_by_id.keys() & NEW.keys(),
            "Unexpected M9 map registry")

    scope_doc = read_json(WORK / "region5-scope.json")
    scope = {s["id"]: s for s in scope_doc["maps"]}
    requests = {s["id"]: s for s in read_json(ART / "batch-manifest.json")}
    require(scope_doc["artStatus"] == "GENERATED_ACCEPTED", "Missing plate acceptance")
    require(set(scope) == set(NEW) | set(REUSED) and set(requests) == set(NEW), "Unexpected scope")
    review = ART / "REGION5_PLATE_SHEET.md"
    review_text = review.read_text(encoding="utf-8")
    m9_scope = {r["id"]: r for r in read_json(m9 / "region4-scope.json")["maps"]}
    records, reused, specs = [], [], []
    with tempfile.TemporaryDirectory(prefix=".m10-runtime-", dir=WORK) as temp:
        stage = Path(temp) / "runtime"
        shutil.copytree(SOURCE, stage)
        verify_runtime(stage, original)
        (stage / REGION).mkdir()
        for map_id, scoped in scope.items():
            row = rom_map(rom, scoped)
            spec = native_spec(rom, row, scoped)
            native = prepare.render_map(rom, row)
            with Image.open(ROOT / spec["native"]) as reference:
                require(reference.size == native.size and reference.tobytes() == native.tobytes(),
                        f"{map_id}: native reference differs from ROM")
            if map_id in REUSED:
                old = old_by_id[map_id]
                require(scoped["artStatus"] == "REUSED_M9", f"{map_id}: expected M9 reuse")
                for key in ("name", "width", "height", "widthTiles", "heightTiles",
                            "geometrySHA256", "cellKeys", "tiles", "attrs", "palettes"):
                    require(old[key] == spec[key], f"{map_id}: M9 registry {key} mismatch")
                for key in ("geometrySHA256", "nativeSize"):
                    require(scoped[key] == m9_scope[map_id][key], f"{map_id}: M9 scope {key} mismatch")
                require(old["artReady"] and old["image"] == f"assets/region4/{map_id}_hd.png",
                        f"{map_id}: unexpected reused asset")
                reused.append(dict(id=map_id, runtimeAsset=old["image"], runtimeSHA256=original[old["image"]],
                                   nativeSize=scoped["nativeSize"], geometrySHA256=spec["geometrySHA256"]))
                continue

            require(scoped["artStatus"] == "GENERATED_ACCEPTED"
                    and scoped["plate"] == spec["gptSource"]
                    and f"| {map_id} |" in review_text, f"{map_id}: missing supervisor acceptance")
            request = requests[map_id]
            source = ROOT / scoped["plate"]
            meta = source.with_suffix(".png.meta.json")
            request_meta = read_json(meta)
            require(request["output"] == source.name and request_meta["ok"] and
                    Path(request_meta["out"]).name == source.name and
                    request_meta["model"] == request["model"] == "gpt-image-2" and
                    request_meta["quality"] == request["quality"] == "medium" and
                    request_meta["size"] == request["size"] and
                    request_meta["attempts"][-1]["status"] == 200, f"{map_id}: CLI metadata")
            require(request["nativeSize"] == scoped["nativeSize"], f"{map_id}: request native size")
            with Image.open(source) as image:
                actual = list(image.size)
                require(image.format == "PNG" and actual == NEW[map_id], f"{map_id}: unexpected PNG")
                image.verify()
            with Image.open(source) as image:
                image.load()
            width, height = scoped["nativeSize"]
            require(abs(actual[0] * height - actual[1] * width) <= (width + height) / 2,
                    f"{map_id}: actual dimensions break native aspect ratio")
            target = stage / spec["image"]
            shutil.copyfile(source, target)
            digest = sha(source.read_bytes())
            require(sha(target.read_bytes()) == digest, f"{map_id}: copied PNG differs")
            specs.append(spec)
            records.append(dict(id=map_id, name=spec["name"], source=spec["gptSource"],
                                sourceSHA256=digest, nativeSize=scoped["nativeSize"],
                                geometrySHA256=spec["geometrySHA256"],
                                originalCLIMetadata=str(meta.relative_to(ROOT)),
                                metadataSHA256=sha(meta.read_bytes()), actualDimensions=actual,
                                requestedDimensions=request["requestedSize"],
                                model=request_meta["model"], requestedQuality=request_meta["quality"],
                                runtimeAsset=spec["image"], runtimeSHA256=digest))

        write_json(stage / REGION / "maps.json", specs)
        append_registry(stage / REGISTRY, registry_bytes, old_specs, specs)
        final = files(stage)
        changed = {p for p, digest in original.items() if final.get(p) != digest}
        added = set(final) - set(original)
        require(changed == {str(REGISTRY)}, f"Unexpected existing file changes: {changed}")
        require(added == {str(REGION / "maps.json"), *(s["image"] for s in specs)},
                f"Unexpected additions: {added}")
        verify_runtime(SOURCE, original)
        if DEST.exists():
            verify_runtime(DEST, final)
        else:
            stage.rename(DEST)

    INTEGRATION.mkdir(exist_ok=True)
    manifest_path = INTEGRATION / "provenance.json"
    manifest = dict(
        adoptedBase=str(SOURCE.relative_to(ROOT)), originalFileCount=len(original),
        runtimeFileCount=len(final), mapRegistryCount=len(old_specs) + len(specs),
        modifiedExistingFiles=sorted(changed), addedFiles=sorted(added),
        originalCodeROMCoreUnchanged=True, coverage="PENDING_OUTER_QA",
        review=str(review.relative_to(ROOT)), newMaps=records, reusedMaps=reused,
        m9RuntimeSHA256=original, m10RuntimeSHA256=final)
    if manifest_path.exists():
        require(read_json(manifest_path) == manifest, "Existing integration provenance differs")
    else:
        write_json(manifest_path, manifest)
    print(f"Verified {len(original)} M9 files, registered {manifest['mapRegistryCount']} maps, "
          f"copied {len(records)} PNGs verbatim and reused {len(reused)} M9 PNGs.")


if __name__ == "__main__":
    main()
