"""Compose verified canvas captures from the completed in-browser M9 QA."""

import hashlib
import json
import os
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
WORK = ROOT / "m9-work"
RUN = Path(os.environ["M9_RESULTS"]).resolve()
DEST = ROOT / "shots/m9_region4_contact.png"
SIZE = (640, 576)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    assert RUN.parent == WORK / "results"
    config = json.loads((WORK / "integration/outer-plan.json").read_text())["official"]
    report = json.loads((RUN / "qa/report.json").read_text())
    assert (RUN / "qa.done").is_file() and report["pass"] is True
    contacts = report["contacts"]
    assert contacts.keys() == config["contacts"].keys()
    source = RUN / "qa" / config["name"]

    margin, gap, header, caption = 20, 12, 58, 32
    row_height = SIZE[1] + caption + gap
    sheet = Image.new("RGB", (2 * SIZE[0] + gap + 2 * margin,
                             header + len(contacts) * row_height + margin), "#151d23")
    draw = ImageDraw.Draw(sheet)
    draw.text((margin, 15), "Region 4   |   Native vs. M9 in-runtime HD",
              font=ImageFont.load_default(size=23), fill="#f3f5f5")
    label_font = ImageFont.load_default(size=16)

    for row, (map_id, action) in enumerate(config["contacts"].items()):
        info = contacts[map_id]
        assert info["action"] == action and 0 < info["samePlate"] <= info["eligible"]
        top = header + row * row_height
        plaque = "   |   Inn plaque visible" if map_id == "00-24" else ""
        for col, (mode, label) in enumerate([("native", "Native"), ("hd", "M9 HD")]):
            file = source / f"{map_id}-{mode}.png"
            assert digest(file) == info[mode + "PNG"], file
            left = margin + col * (SIZE[0] + gap)
            draw.text((left, top + 6), f"{map_id}   |   {label}   |   Action {action}{plaque}",
                      font=label_font, fill="#e8eef1")
            with Image.open(file) as image:
                assert image.size == SIZE and image.format == "PNG", file
                sheet.paste(image.convert("RGB"), (left, top + caption))

    candidate = RUN / "contact-verified.png"
    pending = candidate.with_suffix(".partial.png")
    sheet.save(pending)
    pending.replace(candidate)
    if not DEST.exists():
        os.link(candidate, DEST)
    assert digest(DEST) == digest(candidate), f"Existing contact sheet differs: {DEST}"
    print(DEST, digest(DEST))


if __name__ == "__main__":
    main()
