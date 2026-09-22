"""Per-part deployment contract: everything the engine needs to know about one part.
"""
from __future__ import annotations

import math
import re
from dataclasses import dataclass

_REPO_ID = re.compile(r"^[A-Za-z0-9][\w.-]*/[\w.-]+$")
_HEX40 = re.compile(r"^[0-9a-f]{40}$")
_HEX64 = re.compile(r"^[0-9a-f]{64}$")
_PART_ID = re.compile(r"^[a-z][a-z0-9_]*$")

_REQUIRED = (
    "display_name", "roi_size", "image_size", "min_views", "max_views", "threshold",
    "backbone", "layers", "coreset_ratio", "num_neighbors", "model_filename",
    "model_sha256", "limitations",
)


class ContractError(ValueError):
    """A parts/*.yaml entry does not satisfy the deployment contract."""


@dataclass(frozen=True)
class PartSpec:
    part_id: str
    display_name: str
    roi_size: tuple[int, int]          # (width, height) of the accepted cropped upload
    image_size: tuple[int, int]        # (height, width) fed to the model
    min_views: int
    max_views: int
    threshold: float                   # part-level; flagged only when part_score > threshold
    backbone: str
    layers: tuple[str, ...]
    coreset_ratio: float
    num_neighbors: int
    model_filename: str
    model_sha256: str
    limitations: str
    model_repo_id: str | None = None     # None until the HF model repo exists
    model_revision: str | None = None    # full 40-char commit, never a branch name
    local_checkpoint: str | None = None  # dev-only source, relative to projects/defect-detector/

    @property
    def has_remote_source(self) -> bool:
        return self.model_repo_id is not None and self.model_revision is not None

    @classmethod
    def from_dict(cls, part_id: str, d: dict) -> "PartSpec":
        if not _PART_ID.match(part_id):
            raise ContractError(f"part_id {part_id!r} must be lowercase letters, digits, underscore")
        missing = [k for k in _REQUIRED if k not in d]
        if missing:
            raise ContractError(f"{part_id}: missing keys {missing}")

        roi_w, roi_h = _int_pair(part_id, "roi_size", d["roi_size"])
        img_h, img_w = _int_pair(part_id, "image_size", d["image_size"])
        min_v, max_v = int(d["min_views"]), int(d["max_views"])
        if not 1 <= min_v <= max_v:
            raise ContractError(f"{part_id}: need 1 <= min_views <= max_views, got {min_v}, {max_v}")
        threshold = float(d["threshold"])
        if not math.isfinite(threshold) or threshold <= 0:
            raise ContractError(f"{part_id}: threshold must be a positive number, got {d['threshold']!r}")
        layers = d["layers"]
        if not isinstance(layers, (list, tuple)) or not layers or not all(isinstance(x, str) for x in layers):
            raise ContractError(f"{part_id}: layers must be a non-empty list of layer names, got {layers!r}")
        if not _HEX64.match(str(d["model_sha256"])):
            raise ContractError(f"{part_id}: model_sha256 must be 64 lowercase hex chars")

        repo, rev = d.get("model_repo_id"), d.get("model_revision")
        if repo is not None and not _REPO_ID.match(str(repo)):
            raise ContractError(f"{part_id}: model_repo_id must look like 'user/name', got {repo!r}")
        if (repo is None) != (rev is None):
            raise ContractError(f"{part_id}: model_repo_id and model_revision must be set together")
        if rev is not None and not _HEX40.match(str(rev)):
            raise ContractError(f"{part_id}: model_revision must be a full 40-char commit hash, not {rev!r}")
        local = d.get("local_checkpoint")
        if repo is None and local is None:
            raise ContractError(f"{part_id}: needs model_repo_id+model_revision or local_checkpoint")

        return cls(
            part_id=part_id,
            display_name=str(d["display_name"]),
            roi_size=(roi_w, roi_h),
            image_size=(img_h, img_w),
            min_views=min_v,
            max_views=max_v,
            threshold=threshold,
            backbone=str(d["backbone"]),
            layers=tuple(layers),
            coreset_ratio=float(d["coreset_ratio"]),
            num_neighbors=int(d["num_neighbors"]),
            model_filename=str(d["model_filename"]),
            model_sha256=str(d["model_sha256"]),
            limitations=str(d["limitations"]),
            model_repo_id=repo,
            model_revision=rev,
            local_checkpoint=local,
        )


def _int_pair(part_id: str, key: str, value) -> tuple[int, int]:
    if not isinstance(value, (list, tuple)) or len(value) != 2:
        raise ContractError(f"{part_id}: {key} must be a 2-item list, got {value!r}")
    a, b = int(value[0]), int(value[1])
    if a <= 0 or b <= 0:
        raise ContractError(f"{part_id}: {key} values must be positive, got {value!r}")
    return a, b
