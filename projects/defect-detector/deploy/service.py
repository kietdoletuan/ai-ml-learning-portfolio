import logging
import threading
from pathlib import Path

from core.engine import Engine, PartUnavailable
from core.preprocess import InputError, load_views
from core.registry import Registry
from core.render import render_overlays

DEPLOY = Path(__file__).resolve().parent
logger = logging.getLogger(__name__)
# one inference at a time
_inference_lock = threading.Lock()


def input_details(registry: Registry, part_id: str) -> str:
    spec = registry.get(part_id)
    width, height = spec.roi_size
    return (
        f"{spec.display_name}: {spec.min_views}–{spec.max_views} cropped ROI images of the same part; "
        f"exactly {width} × {height} pixels each. Different roll states preferred.\n\n"
        f"{spec.limitations}"
    )


def save_uploads(uploads, folder: Path) -> list[Path]:
    """Index folders keep duplicates."""
    paths = []
    for index, upload in enumerate(uploads):
        path = folder / str(index) / (Path(upload.name).name or "upload")
        path.parent.mkdir(parents=True)
        path.write_bytes(upload.getvalue())
        paths.append(path)
    return paths


def predict_uploads(engine: Engine, registry: Registry, part_id: str, paths):
    """No stale verdicts."""
    try:
        paths = paths or []
        with _inference_lock:
            prediction = engine.predict(part_id, paths)
            images, _ = load_views(paths, registry.get(part_id))
            overlays = render_overlays(images, prediction.anomaly_maps)
        result = prediction.result
        rows, gallery = [], []
        for view, (image, name, score) in enumerate(
            zip(overlays, result.view_names, result.view_scores), start=1
        ):
            rows.append([view, name, score])
            gallery.append((image, f"View {view}: {name} | {score:.6f}"))
        verdict = "FLAGGED" if result.flagged else "PASSED"
        summary = (
            f"{verdict} | part score {result.part_score:.6f} | threshold {result.threshold:g}\n"
            f"Highest score: view {result.top_view + 1} ({result.view_names[result.top_view]})"
        )
        return summary, rows, gallery
    except InputError as exc:
        return f"Input error: {exc}", [], []
    except (PartUnavailable, KeyError):
        logger.exception("Part unavailable: %s", part_id)
        return "Part unavailable. Try again or select another part.", [], []
    except Exception:
        logger.exception("Prediction failed for %s", part_id)
        return "Prediction failed. No verdict was produced.", [], []


def bundled_examples(root: Path, parts: list[str]) -> list[list]:
    """Loads approved example groups."""
    rows = []
    for part_id in parts:
        for group in sorted((root / part_id).glob("*")):
            paths = sorted(group.glob("*.png")) if group.is_dir() else []
            if paths:
                rows.append([part_id, [str(path) for path in paths]])
    return rows
