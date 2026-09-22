from __future__ import annotations

from pathlib import Path
from typing import Sequence

import torch
from PIL import Image
from torchvision.transforms import v2

from .contract import PartSpec

IMAGENET_MEAN = (0.485, 0.456, 0.406)
IMAGENET_STD = (0.229, 0.224, 0.225)


class InputError(ValueError):
    """The submitted images cannot be scored; the message is safe to show the user."""


def load_views(paths: Sequence[str | Path], spec: PartSpec) -> tuple[list[Image.Image], list[str]]:
    paths = [Path(p) for p in paths]
    if not spec.min_views <= len(paths) <= spec.max_views:
        raise InputError(
            f"{spec.display_name}: submit {spec.min_views} to {spec.max_views} images "
            f"of the same part, got {len(paths)}"
        )

    images = []
    for path in paths:
        try:
            with Image.open(path) as im:
                # cheap reject before decode
                if im.size != spec.roi_size:
                    raise InputError(
                        f"{path.name} is {im.size[0]}x{im.size[1]} pixels, but {spec.display_name} "
                        f"needs exactly {spec.roi_size[0]}x{spec.roi_size[1]} (a cropped ROI, not a raw frame)"
                    )
                im.load()
                images.append(im.convert("RGB"))
        except (OSError, Image.DecompressionBombError) as exc:
            raise InputError(f"{path.name} could not be read as an image") from exc
    return images, [p.name for p in paths]


def build_transform(spec: PartSpec) -> v2.Compose:
    return v2.Compose([
        v2.ToImage(),
        v2.ToDtype(torch.float32, scale=True),
        v2.Resize(spec.image_size, antialias=True),
        v2.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
    ])


def to_batch(images: Sequence[Image.Image], spec: PartSpec) -> torch.Tensor:
    transform = build_transform(spec)
    batch = torch.stack([transform(im) for im in images])
    expected = (len(images), 3, *spec.image_size)
    if tuple(batch.shape) != expected:
        raise RuntimeError(f"batch shape {tuple(batch.shape)}, expected {expected}")
    return batch
