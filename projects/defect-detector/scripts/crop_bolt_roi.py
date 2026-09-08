"""Crop bolt captures to the locked ROI (see parts/bolt.yaml) and save as PNG.

Source: data/bolt/{train,heldout,defects/surface,defects/thread}/*.bmp  (untouched)
Output: data/bolt_roi/<same relative path>.png                          (filenames preserved)

Native capture is 2592x1944. ROI is [x, y, w, h] = [23, 570, 2563, 909] -> a 2.82:1 strip.
Do NOT resize to a square here, that's a separate concern handled by the training script's
non-square image_size. This script only crops to the physical ROI and re-encodes to PNG
(BMP -> PNG also drops the captures from ~4.9MB to a few hundred KB each).
"""
import yaml
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "data" / "bolt"
DST = ROOT / "data" / "bolt_roi"

with open(ROOT / "parts" / "bolt.yaml") as f:
    cfg = yaml.safe_load(f)
x, y, w, h = cfg["roi"]
box = (x, y, x + w, y + h)

n = 0
for src_path in SRC.rglob("*.bmp"):
    rel = src_path.relative_to(SRC)
    dst_path = (DST / rel).with_suffix(".png")
    dst_path.parent.mkdir(parents=True, exist_ok=True)

    im = Image.open(src_path)
    assert im.size == (2592, 1944), f"unexpected native size {im.size} for {src_path}"
    im.crop(box).save(dst_path)
    n += 1

print(f"cropped {n} images -> {DST}")
