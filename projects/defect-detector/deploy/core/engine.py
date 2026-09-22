from __future__ import annotations

import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

import numpy as np
import torch
from anomalib.models import Patchcore

from .aggregate import PartResult, aggregate
from .artifacts import resolve_checkpoint
from .contract import ContractError, PartSpec
from .preprocess import load_views, to_batch
from .registry import Registry


class PartUnavailable(RuntimeError):
    """A part's model could not be loaded; other parts are unaffected."""


@dataclass(frozen=True)
class Prediction:
    result: PartResult
    anomaly_maps: np.ndarray  # (views, H, W)


def _check_hparams(spec: PartSpec, saved: dict) -> None:
    expected = {
        "backbone": spec.backbone,
        "layers": list(spec.layers),
        "coreset_sampling_ratio": spec.coreset_ratio,
        "num_neighbors": spec.num_neighbors,
    }
    for key, value in expected.items():
        if saved.get(key) != value:
            raise ContractError(
                f"{spec.part_id}: {key} is {value!r} in the spec but {saved.get(key)!r} in the checkpoint"
            )


def build_model(spec: PartSpec, checkpoint: Path) -> Patchcore:
    # already hash-checked upstream
    saved = torch.load(checkpoint, map_location="cpu", weights_only=False)
    _check_hparams(spec, saved["hyper_parameters"])
    # keeps startup offline
    model = Patchcore(
        backbone=spec.backbone,
        layers=list(spec.layers),
        pre_trained=False,
        coreset_sampling_ratio=spec.coreset_ratio,
        num_neighbors=spec.num_neighbors,
    )
    model.load_state_dict(saved["state_dict"], strict=True)
    return model.eval()


def score_batch(model: Patchcore, batch: torch.Tensor) -> tuple[list[float], np.ndarray]:
    # ignore library's 0.5 label
    with torch.inference_mode():
        out = model.model(batch)
    scores = [float(s) for s in out["pred_score"]]
    return scores, out["anomaly_map"].squeeze(1).cpu().numpy()


class Engine:
    def __init__(self, registry: Registry, *, prefer_local: bool = False):
        self._registry = registry
        self._prefer_local = prefer_local
        self._models: dict[str, Patchcore] = {}
        self._lock = threading.Lock()

    @property
    def parts(self) -> list[str]:
        return sorted(self._registry.parts)

    def _get_model(self, spec: PartSpec) -> Patchcore:
        with self._lock:
            if spec.part_id not in self._models:
                try:
                    checkpoint = resolve_checkpoint(spec, prefer_local=self._prefer_local)
                    self._models[spec.part_id] = build_model(spec, checkpoint)
                except Exception as exc:
                    raise PartUnavailable(f"{spec.part_id}: {exc}") from exc
            return self._models[spec.part_id]

    def predict(self, part_id: str, paths: Sequence[str | Path]) -> Prediction:
        spec = self._registry.get(part_id)
        # validate before loading model
        images, names = load_views(paths, spec)
        batch = to_batch(images, spec)
        scores, maps = score_batch(self._get_model(spec), batch)
        return Prediction(aggregate(part_id, names, scores, spec.threshold), maps)
