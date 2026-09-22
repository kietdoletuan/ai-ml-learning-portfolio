from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Sequence


@dataclass(frozen=True)
class PartResult:
    part_id: str
    view_names: tuple[str, ...]
    view_scores: tuple[float, ...]
    part_score: float
    top_view: int
    threshold: float
    flagged: bool


def aggregate(part_id: str, view_names: Sequence[str], view_scores: Sequence[float], threshold: float) -> PartResult:
    if not view_scores or len(view_names) != len(view_scores):
        raise ValueError(f"need one score per view, got {len(view_names)} names and {len(view_scores)} scores")
    if not all(math.isfinite(s) for s in view_scores):
        raise ValueError(f"non-finite view score in {list(view_scores)}")

    # max() keeps the first of equal scores, so a tie names the earlier view
    top = max(range(len(view_scores)), key=view_scores.__getitem__)
    part_score = float(view_scores[top])
    return PartResult(
        part_id=part_id,
        view_names=tuple(view_names),
        view_scores=tuple(float(s) for s in view_scores),
        part_score=part_score,
        top_view=top,
        threshold=threshold,
        flagged=part_score > threshold,
    )
