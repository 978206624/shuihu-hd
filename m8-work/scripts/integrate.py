"""Ingest only the eight supervisor-reviewed original CLI outputs. Offline/idempotent."""
from pathlib import Path
from PIL import Image
import hashlib, json, shutil

R = Path(__file__).resolve().parents[2]
W = R / 'm8-work'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
def write(p, data):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')
def immutable(p, data):
    if p.exists():
        assert p.read_bytes() == data, f'Existing evidence differs: {p}'
    else:
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(data)

batch = W / 'art/cli-generation/20261111T112050Z'
for line in (batch / 'output-sha256.txt').read_text().splitlines():
    digest, rel = line.split(maxsplit=1)
    assert sha(R / rel.strip()) == digest, rel
for rel, digest in json.loads((W / 'art/input-freeze-sha256.json').read_text()).items():
    assert sha(R / rel) == digest, rel
base = R / 'm7-work/stage-a/v3/runtime'
adopted = json.loads((W / 'integrity/adopted-runtime-sha256.json').read_text())
for rel, digest in adopted.items():
    assert sha(base / rel) == digest, rel
    if rel != 'assets/region1/maps.json':
        assert sha(W / 'runtime' / rel) == digest, rel
specs = json.loads((W / 'art/native-map-metadata.json').read_text())
requests = {x['id']: x for x in json.loads((W / 'art/batch-manifest.json').read_text())}
records = []
for s in specs:
    code = s['id']; src = W / f'art/{code}_gpt.png'
    meta = src.with_suffix('.png.meta.json')
    m = json.loads(meta.read_text()); req = requests[code]
    assert m['ok'] and m['model'] == 'gpt-image-2' and m['quality'] == 'medium'
    assert m['size'] == req['size']
    with Image.open(src) as im:
        im.verify()
    with Image.open(src) as im:
        dims = list(im.size)
    # Permit only pixel-rounding aspect error, never crop/stretch to new geometry.
    assert abs(dims[0] * s['height'] - dims[1] * s['width']) <= (s['width'] + s['height']) / 2
    dest = W / 'runtime' / s['image']
    immutable(dest, src.read_bytes())  # Exact PNG bytes, no new art/filter/conversion.
    s['artReady'] = True
    records.append(dict(id=code, source=str(src.relative_to(R)), sourceSHA256=sha(src),
        originalCLIMetadata=str(meta.relative_to(R)), metadataSHA256=sha(meta),
        actualDimensions=dims, requestedDimensions=req['requestedSize'],
        requestedModel=m['model'], requestedQuality=m['quality'], serverReturnedQuality=None,
        runtimeAsset=str(dest.relative_to(R)), runtimeSHA256=sha(dest),
        ingestion='Byte-identical original PNG; unchanged adopted-v3 prepareBase rasterizes authored painting to native dimensions x4.',
        review='m8-work/art/SUPERVISOR_VISUAL_REVIEW.md; provisional integration review, formal QA pending'))
base_specs = json.loads((base / 'assets/region1/maps.json').read_text())
assert not ({s['id'] for s in base_specs} & {s['id'] for s in specs})
write(W / 'runtime/assets/region3/maps.json', specs)
write(W / 'runtime/assets/region1/maps.json', base_specs + specs)
write(W / 'integration/provenance.json', dict(adoptedBase=str(base.relative_to(R)),
    originalRuntimeFiles=len(adopted), originalCodeROMCoreUnchanged=True,
    modifiedExistingFiles=['assets/region1/maps.json'], newMaps=records,
    coverage='NOT_MEASURED; no count inferred from art readiness'))
print(json.dumps(dict(integrated=len(records), existingCodeROMCoreChanges=0,
    exactPNGCopies=True, mapRegistry=len(base_specs + specs))))
