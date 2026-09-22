from collections.abc import Sequence

import numpy as np
from matplotlib import colormaps
from PIL import Image


def render_overlays(
    images: Sequence[Image.Image], anomaly_maps: np.ndarray, *, opacity: float = 0.45
) -> list[Image.Image]:
    """Shared-scale heatmap overlay."""
    maps = np.asarray(anomaly_maps, dtype=np.float32)
    if maps.ndim != 3 or maps.shape[0] != len(images) or maps.size == 0:
        raise ValueError("need one non-empty (H, W) anomaly map per image")
    if not np.isfinite(maps).all():
        raise ValueError("anomaly maps contain non-finite values")
    if not 0 <= opacity <= 1:
        raise ValueError("opacity must be between 0 and 1")

    low, high = float(maps.min()), float(maps.max())
    scaled = (maps - low) / (high - low) if high > low else np.zeros_like(maps)
    colours = colormaps["inferno"](scaled, bytes=True)[..., :3]

    overlays = []
    for image, colour in zip(images, colours):
        heatmap = Image.fromarray(colour)
        background = image.convert("RGB").resize(heatmap.size, Image.Resampling.BILINEAR)
        overlays.append(Image.blend(background, heatmap, opacity))
    return overlays
