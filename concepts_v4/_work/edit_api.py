#!/usr/bin/env python3
"""Call the image edits API. Never print the API key."""
import json, time, base64, uuid, sys
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from concurrent.futures import ThreadPoolExecutor, as_completed

ROOT = Path("/workspace/shawu")
ENV = {}
for line in (ROOT / ".image_api.env").read_text().splitlines():
    if "=" in line and not line.strip().startswith("#"):
        k, v = line.split("=", 1)
        ENV[k] = v
BASE = ENV["IMAGE_API_BASE"].rstrip("/")
KEY = ENV["IMAGE_API_KEY"]
OUT = ROOT / "concepts_v4"
WORK = OUT / "_work"
WORK.mkdir(parents=True, exist_ok=True)

PROMPTS = {
    "title": """Redraw this Game Boy Color title screenshot as a refined, premium, hand-painted HD 2D JRPG illustration with rich cinematic lighting and fine textures.

The FIRST image is the composition authority (original screenshot, nearest-neighbor upscaled). Keep the exact same camera, layout, and UI positions. The SECOND image is only a style/material/lighting reference from a previous HD concept — copy its painterly quality, not any species mistakes from older versions.

CRITICAL CONTENT RULES:
- ZERO humans. No people, faces, hands, or human figures anywhere in the image.
- EXACTLY ONE creature: a golden-yellow, short-bodied, compact winged divine beast (its formal name is unknown — do not label it). Short plump/round body, golden-yellow fur, small dark nose and mouth, slanted closed/squinting happy eyes, brown-gold wings, small ear or horn-like tufts on the head, a short tail. It may have a tiny gold spark or orb near it as in the original. NOT a long Chinese dragon, no long whiskers, no serpentine body, no large jewels. Not a qilin. Follow the original pixel beast silhouette.

UI and typography — keep the same positions as the original:
- Top: a decorative horizontal scroll/banner with the exact Chinese title 水浒神獸 in bold calligraphy.
- Below the beast: two menu items in the same place — a small triangular cursor pointing to the top item 重新开始, and 继续游戏 underneath. Use this exact simplified Chinese wording; do not change it.
- Bottom: ©2001, a small VF diamond logo, then 廣譽科技, same layout as the original.

Background: bright blue sky, distant misty Chinese mountains, a row of pine/evergreen trees along the bottom, same layout as the original.

Style: refined premium hand-painted HD 2D JRPG art, rich lighting, fine fur/wood/silk textures. Not pixel art, not photorealistic 3D, not chibi, not a comparison diptych. Output a single finished title illustration only.
""",
    "cliff": """Redraw this Game Boy Color landscape screenshot as a refined, premium, hand-painted HD 2D JRPG illustration with rich atmospheric lighting and fine textures.

The FIRST image is the composition and SCALE authority (original screenshot, nearest-neighbor upscaled). Keep the same camera, landscape layout, and relative sizes as the original. The SECOND image is only a style/material/lighting reference. Do NOT copy the second image's character scale — a previous HD version drew the woman too large.

CRITICAL CHARACTER RULES:
- EXACTLY ONE person in the entire image. No other humans, no children, no animals, no extra travelers, no text boxes.
- She is an ADULT pregnant woman: the wife of an honest official persecuted by Gao Qiu. She has no confirmed personal name — do not invent or write a name.
- Appearance: black hair with deep-red hair ornaments, red upper garment, light-colored inner collar, light/cream skirt or lower robe, adult face (not a child, not a cute little girl). Somber, grieving expression. A protective hand near her belly is appropriate. She is unarmed.
- SCALE IS THE MOST IMPORTANT FIX: in the original she is a tiny map sprite at the far bottom-right of the pale stone platform — only about 16 pixels tall on a 160×144 screen, roughly one-tenth of the frame height, and much smaller than the cliff itself. She must remain a small distant figure relative to the huge plateau and mountains. She should occupy only a small corner of the lower-right platform, like a game character standing on a vast landscape, NOT a large foreground portrait. If she were measured, her height should be about 8–12% of the full image height.

Landscape — follow the original layout exactly:
- Bright blue sky with large white clouds.
- A blue snow-capped mountain range in the background, main peaks toward the upper-right.
- A pale beige stone cliff/platform occupying the lower-right, with a jagged rocky edge and darker rock plus greenery on the left/underside of the platform.
- A circular dark carved or inlaid swirl/ritual symbol on the flat top of the platform, in the same place as the original (upper area of the platform).
- Sparse small green plants on the platform.
- The woman stands at the far bottom-right of the platform, just inside the frame, as in the original.

Style: refined premium hand-painted HD 2D JRPG art, rich lighting, fine rock, cloud, and fabric textures. Not photorealistic 3D, not pixel art, not a comparison diptych. Output a single finished scene only.
""",
    "palace": """Redraw this Game Boy Color heavenly-palace screenshot as a refined, premium, hand-painted HD 2D JRPG illustration with rich lighting and fine textures.

The FIRST image is the composition authority (original screenshot, nearest-neighbor upscaled). Keep the exact same high-angle/top-down camera, architecture, and character positions. The SECOND image is a style and identity guide from a previous HD concept — use its painterly materials and the two correct identities, but lock counts and positions to the FIRST image.

CRITICAL CHARACTER RULES:
- EXACTLY TWO people in the entire image. No one else — no disciples, no children, no extra guards, no Beidou Xingjun, no Yanlong, no Chenhu, no text boxes.
- Person 1 — the Jade Emperor (玉帝): an elderly man with white eyebrows and a full white beard, golden-yellow imperial robes, and a dark/black-and-gold ceremonial crown (a ritual crown, NOT a military helmet). He stands on the upper terrace, slightly left, immediately in front of the golden throne (almost overlapping the left side of the throne, as in the original). No weapon.
- Person 2 — one adult heavenly soldier (天兵): an adult man (not a child or boy) on the right side of the same upper terrace. Pointed grey-olive helmet with cheek guards, grey-olive armor and shoulder plates, dark waist. Adult male face. Do NOT invent a specific weapon; the original pixels do not clearly show one. Empty-handed or hands at his sides.
- Both figures should stay small, like map sprites relative to the large palace courtyard, matching the original scale.

Architecture — follow the original:
- A white/pale stone floating heavenly palace with two terrace levels and cracked stone floor tiles.
- Blue-and-white decorative corner pillars with floral/medallion tiles and Greek-key (meander) patterns.
- A golden throne at the top center of the upper terrace, with two red/pink square back panels behind it, and a small blue vessel on the throne furniture.
- Gold lamp or railing fixtures along the mid-level left and right walls.
- Bright blue sky and white clouds visible around the palace, especially on the left.

Style: refined premium hand-painted HD 2D JRPG art, rich lighting, fine stone, metal, and silk textures. Slightly more painterly and premium than chibi sprites, still clearly a game scene, not photorealistic live-action, not a comparison diptych. Output a single finished scene only.
""",
}

FILES = {
    "title": (WORK / "title_original_8x.png", ROOT / "concepts_v3/title_hd.jpg"),
    "cliff": (WORK / "cliff_original_8x.png", ROOT / "concepts_v3/cliff_hd.jpg"),
    "palace": (WORK / "palace_original_8x.png", ROOT / "concepts_v3/palace_hd.jpg"),
}


def multipart(fields, files):
    boundary = "----ProbeBoundary" + uuid.uuid4().hex
    chunks = []
    for name, value in fields:
        chunks.append(f"--{boundary}\r\n".encode())
        chunks.append(f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode())
        chunks.append(str(value).encode() + b"\r\n")
    for name, filename, ctype, data in files:
        chunks.append(f"--{boundary}\r\n".encode())
        chunks.append(
            f'Content-Disposition: form-data; name="{name}"; filename="{filename}"\r\n'.encode()
        )
        chunks.append(f"Content-Type: {ctype}\r\n\r\n".encode())
        chunks.append(data + b"\r\n")
    chunks.append(f"--{boundary}--\r\n".encode())
    return b"".join(chunks), f"multipart/form-data; boundary={boundary}"


def post_edit(fields, files, timeout=420):
    body, ctype = multipart(fields, files)
    req = Request(
        BASE + "/v1/images/edits",
        data=body,
        method="POST",
        headers={
            "Authorization": f"Bearer {KEY}",
            "Content-Type": ctype,
            "Accept": "application/json",
            "Content-Length": str(len(body)),
        },
    )
    t0 = time.time()
    try:
        with urlopen(req, timeout=timeout) as r:
            raw = r.read()
            status = r.status
    except HTTPError as e:
        raw = e.read()
        status = e.code
        elapsed = time.time() - t0
        try:
            parsed = json.loads(raw.decode("utf-8", "replace"))
        except Exception:
            parsed = {"_raw": raw.decode("utf-8", "replace")[:4000]}
        return {"ok": False, "status": status, "elapsed": elapsed, "body": parsed, "nbytes": len(raw)}
    except Exception as e:
        return {
            "ok": False,
            "status": 0,
            "elapsed": time.time() - t0,
            "error": f"{type(e).__name__}: {e}",
            "body": None,
            "nbytes": 0,
        }
    elapsed = time.time() - t0
    try:
        parsed = json.loads(raw.decode("utf-8", "replace"))
    except Exception:
        parsed = {"_raw": raw.decode("utf-8", "replace")[:4000]}
    return {"ok": 200 <= status < 300, "status": status, "elapsed": elapsed, "body": parsed, "nbytes": len(raw)}


def summarize(res):
    body = res.get("body")
    s = {
        "ok": res["ok"],
        "status": res["status"],
        "elapsed": round(res["elapsed"], 2),
        "nbytes": res["nbytes"],
        "error": res.get("error"),
    }
    if isinstance(body, dict):
        s["body_keys"] = list(body.keys())
        if "error" in body:
            s["error_body"] = body["error"]
        for k in ("background", "output_format", "quality", "size", "usage"):
            if k in body:
                s[k] = body[k]
        if isinstance(body.get("data"), list) and body["data"]:
            item = body["data"][0]
            if isinstance(item, dict):
                s["item_keys"] = list(item.keys())
                s["has_b64"] = bool(item.get("b64_json"))
    return s


def error_text(res):
    body = res.get("body") or {}
    err = body.get("error") if isinstance(body, dict) else None
    if isinstance(err, dict):
        return json.dumps(err, ensure_ascii=False)
    if err:
        return str(err)
    return res.get("error") or f"HTTP {res.get('status')}"


def is_param_error(res):
    t = error_text(res).lower()
    keys = ("quality", "size", "input_fidelity", "unknown", "unsupported", "invalid", "unexpected")
    return any(k in t for k in keys)


def save_image(body, dest: Path):
    items = body.get("data") or []
    item = items[0]
    raw = base64.b64decode(item["b64_json"])
    dest.write_bytes(raw)
    return dest, len(raw)


def attempt(scene, quality="high", use_style=True, use_fidelity=True, use_size_auto=True, tag="r1"):
    orig, style = FILES[scene]
    fields = [
        ("model", "gpt-image-2"),
        ("prompt", PROMPTS[scene]),
        ("n", "1"),
    ]
    if quality:
        fields.append(("quality", quality))
    if use_size_auto:
        fields.append(("size", "auto"))
    if use_fidelity:
        fields.append(("input_fidelity", "high"))

    files = []
    # Prefer image[] for multi-image; also works for a single image
    files.append(("image[]", orig.name, "image/png", orig.read_bytes()))
    if use_style and style.exists():
        ctype = "image/jpeg" if style.suffix.lower() in {".jpg", ".jpeg"} else "image/png"
        files.append(("image[]", style.name, ctype, style.read_bytes()))

    print(f"=== {scene} tag={tag} quality={quality} style={use_style} fidelity={use_fidelity} size_auto={use_size_auto} ===", flush=True)
    res = post_edit(fields, files, timeout=480)
    s = summarize(res)
    print(json.dumps(s, ensure_ascii=False, indent=2), flush=True)

    meta_path = WORK / f"{scene}_{tag}_meta.json"
    to_save = json.loads(json.dumps(res, default=str))
    if isinstance(to_save.get("body"), dict) and isinstance(to_save["body"].get("data"), list):
        for item in to_save["body"]["data"]:
            if isinstance(item, dict) and item.get("b64_json"):
                item["b64_json"] = f"<omitted {len(item['b64_json'])} chars>"
    to_save["params"] = {
        "quality": quality,
        "use_style": use_style,
        "use_fidelity": use_fidelity,
        "use_size_auto": use_size_auto,
        "tag": tag,
        "model": "gpt-image-2",
    }
    meta_path.write_text(json.dumps(to_save, ensure_ascii=False, indent=2)[:200000])

    if res["ok"]:
        dest = OUT / f"{scene}_hd.png"
        # keep a tagged copy too
        tagged = WORK / f"{scene}_{tag}.png"
        path, n = save_image(res["body"], dest)
        tagged.write_bytes(path.read_bytes())
        print(f"SAVED {scene} -> {path} ({n} bytes) and {tagged}", flush=True)
        return {"scene": scene, "ok": True, "path": str(path), "summary": s, "tag": tag}

    return {"scene": scene, "ok": False, "summary": s, "tag": tag, "error": error_text(res)}


def run_with_fallback(scene, tag="r1"):
    """Try high + size auto + fidelity + style; peel off unsupported params; then medium."""
    # 1) preferred
    r = attempt(scene, quality="high", use_style=True, use_fidelity=True, use_size_auto=True, tag=tag)
    if r["ok"]:
        return r
    err = r.get("error", "")
    print(f"{scene} first attempt failed: {err}", flush=True)

    # If multi-image or a parameter is rejected, try stripped variants
    variants = [
        dict(quality="high", use_style=True, use_fidelity=False, use_size_auto=True, tag=f"{tag}b"),
        dict(quality="high", use_style=True, use_fidelity=False, use_size_auto=False, tag=f"{tag}c"),
        dict(quality="medium", use_style=True, use_fidelity=False, use_size_auto=True, tag=f"{tag}d"),
        dict(quality="high", use_style=False, use_fidelity=False, use_size_auto=False, tag=f"{tag}e"),
        dict(quality="medium", use_style=False, use_fidelity=False, use_size_auto=False, tag=f"{tag}f"),
    ]
    # Only auto-fallback on param/request errors, not on long timeouts after a successful-looking start
    if r["summary"].get("status") in (0, 400, 413, 415, 422):
        for kw in variants:
            r2 = attempt(scene, **kw)
            if r2["ok"]:
                return r2
            print(f"{scene} variant {kw['tag']} failed: {r2.get('error')}", flush=True)
    return r


def main():
    scenes = sys.argv[1:] or ["title", "cliff", "palace"]
    tag = "r1"
    if "--retry" in scenes:
        scenes = [s for s in scenes if s != "--retry"]
        tag = "r2"
    results = {}
    with ThreadPoolExecutor(max_workers=3) as ex:
        futs = {ex.submit(run_with_fallback, sc, tag): sc for sc in scenes}
        for fut in as_completed(futs):
            sc = futs[fut]
            try:
                results[sc] = fut.result()
            except Exception as e:
                results[sc] = {"scene": sc, "ok": False, "error": f"{type(e).__name__}: {e}"}
                print(f"{sc} exception: {type(e).__name__}: {e}", flush=True)
    out = WORK / f"run_{tag}_results.json"
    out.write_text(json.dumps(results, ensure_ascii=False, indent=2))
    print("ALL DONE", json.dumps({k: {"ok": v.get("ok"), "path": v.get("path"), "error": v.get("error"), "quality": (v.get("summary") or {}).get("quality"), "size": (v.get("summary") or {}).get("size"), "elapsed": (v.get("summary") or {}).get("elapsed")} for k, v in results.items()}, ensure_ascii=False, indent=2), flush=True)
    # exit 0 even if some failed so we can inspect
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
