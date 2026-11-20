"""Copy the accepted M10 runtime and append the reviewed Region 6 PNGs offline."""

import importlib.util
import json
from math import gcd
import shutil
import struct
import tempfile
from pathlib import Path

from PIL import Image
# Reuse the offline ROM decoder that produced the Region 6 scope and references.
module = importlib.util.spec_from_file_location("prepare_art", Path(__file__).with_name("prepare-art.py"))
prepare = importlib.util.module_from_spec(module)
module.loader.exec_module(prepare)
ROOT, WORK, ART = prepare.ROOT, prepare.WORK, prepare.ART
SOURCE = ROOT / "m10-work/runtime"
DEST = WORK / "runtime"
REGISTRY = Path("assets/region1/maps.json")
NEW = {"00-25": [1122, 1402], "00-26": [1254, 1254], "00-27": [1254, 1254],
       "00-28": [1254, 1254], "00-29": [1374, 1145], "00-2e": [1254, 1254]}
REUSED = ("00-2a", "00-0b", "00-09", "00-00", "00-06")
REGION = Path("assets/region6")
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
                widthTiles=width * 4, heightTiles=height * 4, image=f"assets/region6/{map_id}_hd.png",
                imageNativeSize=width * 32, imageNativeHeight=height * 32,
                cellKeys=[keys_by_tile[tile] for tile in tiles], tiles=tiles,
                attrs=[attributes[tile] for tile in tiles], palettes=palettes,
                geometrySHA256=geometry, native=f"m11-work/art/{map_id}_native.png",
                gptSource=f"m11-work/art/{map_id}_gpt.png", artReady=True)


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


def install_plate(source, target, map_id, native_size):
    with Image.open(source) as image:
        require(image.format == "PNG" and list(image.size) == NEW[map_id],
                f"{map_id}: unexpected source PNG")
        image.verify()

    crop = {}
    width, height = native_size
    with Image.open(source) as image:
        image.load()
        if map_id == "00-25":
            require(image.mode == "RGB", "00-25: unexpected color model")
            # Decoded black padding has RGB noise up to 7. Its edge is visible
            # at full resolution and x=857 still exceeds the pad noise floor.
            box = image.point(lambda value: 255 if value > 7 else 0).getbbox()
            require(box == (0, 0, 858, 1402), f"00-25: unexpected painted bounds {box}")
            painted = image.crop(box)
            divisor = gcd(width, height)
            unit_w, unit_h = width // divisor, height // divisor
            scale = min(painted.width // unit_w, painted.height // unit_h)
            fitted_w, fitted_h = unit_w * scale, unit_h * scale
            left, top = (painted.width - fitted_w) // 2, (painted.height - fitted_h) // 2
            fit_box = (left, top, left + fitted_w, top + fitted_h)
            require(fitted_w >= 4 * width and fitted_h >= 4 * height,
                    "00-25: aspect fit would require upsampling")
            painted.crop(fit_box).save(target, format="PNG")
            crop = dict(cropBox=list(box), paintedDimensions=list(painted.size),
                        padChannelMaximum=7, fitCropBox=list(fit_box),
                        fitMethod="Centered exact native-aspect crop of the painted box, without resampling")
        else:
            require(image.width * height == image.height * width,
                    f"{map_id}: source dimensions break native aspect ratio")
            shutil.copyfile(source, target)

    with Image.open(target) as installed:
        installed_dims = list(installed.size)
        installed.verify()
    source_digest, target_digest = sha(source.read_bytes()), sha(target.read_bytes())
    require(crop or source_digest == target_digest, f"{map_id}: copied PNG differs")
    return dict(sourceSHA256=source_digest, installedSHA256=target_digest,
                runtimeSHA256=target_digest, actualDimensions=NEW[map_id],
                installedDimensions=installed_dims, **crop)


def main():
    m10 = SOURCE.parent
    prefix = str(SOURCE.relative_to(ROOT)) + "/"
    original = {file.removeprefix(prefix): digest
                for file, digest in read_json(m10 / "integration/outer-freeze.json").items()
                if file.startswith(prefix)}
    verify_runtime(SOURCE, original)
    rom = (SOURCE / "assets/game.gbc").read_bytes()
    require(sha(rom) == prepare.ROM_SHA256, "Accepted ROM mismatch")
    require("start.bat" in original, "Accepted runtime is missing start.bat")
    registry_bytes = (SOURCE / REGISTRY).read_bytes()
    old_specs = json.loads(registry_bytes)
    old_by_id = {spec["id"]: spec for spec in old_specs}
    require(len(old_specs) == len(old_by_id) == 38 and not old_by_id.keys() & NEW.keys(),
            "Unexpected M10 map registry")

    scope_doc = read_json(WORK / "region6-scope.json")
    scope = {row["id"]: row for row in scope_doc["maps"]}
    require(set(scope) == set(NEW) | set(REUSED), "Unexpected scope")
    requests = {row["id"]: row for row in read_json(ART / "batch-manifest.json")}
    # The supervisor approved the full cave plate after the strip plan was written.
    requests["00-2e"] = dict(output="00-2e_gpt.png", size="1920x1920", nativeSize=[480, 480],
                             requestedSize=[1920, 1920], model="gpt-image-2", quality="medium")
    records, reused, specs = [], [], []
    with tempfile.TemporaryDirectory(prefix=".m11-runtime-", dir=WORK) as temp:
        stage = Path(temp) / "runtime"
        shutil.copytree(SOURCE, stage)
        verify_runtime(stage, original)
        (stage / REGION).mkdir()
        for map_id, scoped in scope.items():
            row = rom_map(rom, scoped)
            spec = native_spec(rom, row, scoped)
            native = prepare.render_map(rom, row)
            require(scoped["nativePNG"] == spec["native"], f"{map_id}: native reference path")
            with Image.open(ROOT / spec["native"]) as reference:
                require(reference.size == native.size and reference.tobytes() == native.tobytes(),
                        f"{map_id}: native reference differs from ROM")
            if map_id in REUSED:
                old = old_by_id[map_id]
                width, height = scoped["nativeSize"]
                require(old["artReady"] and [old["imageNativeSize"], old["imageNativeHeight"]] == [width, height],
                        f"{map_id}: unexpected reused asset dimensions")
                for key in ("width", "height", "widthTiles", "heightTiles", "geometrySHA256",
                            "cellKeys", "tiles", "attrs", "palettes"):
                    require(old[key] == spec[key], f"{map_id}: M10 registry {key} mismatch")
                digest = original[old["image"]]
                accepted = ROOT / scoped["reusePlate"]
                require(digest == scoped["reusePlateSHA256"] == sha(accepted.read_bytes()),
                        f"{map_id}: accepted reused plate SHA differs")
                reused.append(dict(id=map_id, name=spec["name"], adoptedFrom=scoped["artStatus"],
                                   source=scoped["reusePlate"], runtimeAsset=old["image"],
                                   runtimeSHA256=digest, nativeSize=scoped["nativeSize"],
                                   geometrySHA256=spec["geometrySHA256"]))
                continue

            request = requests[map_id]
            source = ROOT / spec["gptSource"]
            meta = source.with_suffix(".png.meta.json")
            receipt = read_json(meta)
            require(request["output"] == source.name and receipt["ok"] and
                    Path(receipt["out"]).name == source.name and
                    receipt["model"] == request["model"] == "gpt-image-2" and
                    receipt["quality"] == request["quality"] == "medium" and
                    receipt["size"] == request["size"] and receipt["attempts"][-1]["status"] == 200,
                    f"{map_id}: generation metadata")
            require(request["nativeSize"] == scoped["nativeSize"], f"{map_id}: request native size")
            installation = install_plate(source, stage / spec["image"], map_id, scoped["nativeSize"])
            specs.append(spec)
            records.append(dict(id=map_id, name=spec["name"], source=spec["gptSource"],
                                nativeSize=scoped["nativeSize"], geometrySHA256=spec["geometrySHA256"],
                                originalCLIMetadata=str(meta.relative_to(ROOT)),
                                metadataSHA256=sha(meta.read_bytes()), requestedDimensions=request["requestedSize"],
                                model=receipt["model"], requestedQuality=receipt["quality"],
                                runtimeAsset=spec["image"], **installation))

        write_json(stage / REGION / "maps.json", specs)
        append_registry(stage / REGISTRY, registry_bytes, old_specs, specs)
        final = files(stage)
        changed = {p for p, digest in original.items() if final.get(p) != digest}
        added = set(final) - set(original)
        require(changed == {str(REGISTRY)}, f"Unexpected existing file changes: {changed}")
        require(added == {str(REGION / "maps.json"), *(spec["image"] for spec in specs)},
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
        review="Supervisor visually accepted the six full plates",
        coverageScope="Full native rectangle per route map. Uncertified pixels remain native and are counted by QA.",
        newMaps=records, reusedMaps=reused, m10RuntimeSHA256=original, m11RuntimeSHA256=final)
    if manifest_path.exists():
        require(read_json(manifest_path) == manifest, "Existing integration provenance differs")
    else:
        write_json(manifest_path, manifest)
    print(f"Verified {len(original)} M10 files and registered {manifest['mapRegistryCount']} maps. "
          f"Installed {len(records)} plates (five verbatim and one aspect crop) and retained {len(reused)} reuses.")


if __name__ == "__main__":
    main()
