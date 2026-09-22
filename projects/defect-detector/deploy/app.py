import logging
from pathlib import Path

import gradio as gr

from core.engine import Engine, PartUnavailable
from core.preprocess import InputError, load_views
from core.registry import Registry, load_registry
from core.render import render_overlays

DEPLOY = Path(__file__).resolve().parent
logger = logging.getLogger(__name__)


def input_details(registry: Registry, part_id: str) -> str:
    spec = registry.get(part_id)
    width, height = spec.roi_size
    return (
        f"{spec.display_name}: {spec.min_views}–{spec.max_views} cropped ROI images of the same part; "
        f"exactly {width} × {height} pixels each. Different roll states preferred.\n\n"
        f"{spec.limitations}"
    )


def predict_uploads(engine: Engine, registry: Registry, part_id: str, paths):
    """No stale verdicts."""
    try:
        paths = paths or []
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


def create_app(
    registry: Registry | None = None, *, engine: Engine | None = None, examples=None
) -> gr.Blocks:
    registry = registry if registry is not None else load_registry(DEPLOY / "parts")
    engine = engine if engine is not None else Engine(registry)
    if not engine.parts:
        raise RuntimeError(f"No valid part configurations: {registry.errors}")
    for part_id, error in registry.errors.items():
        logger.warning("Skipped part %s: %s", part_id, error)
    if examples is None:
        examples = bundled_examples(DEPLOY / "examples", engine.parts)

    with gr.Blocks(title="Defect Detector") as app:
        part = gr.Dropdown(choices=engine.parts, value=engine.parts[0], label="Part")
        details = gr.Markdown(input_details(registry, engine.parts[0]))
        uploads = gr.File(
            file_count="multiple", file_types=["image"], type="filepath", label="ROI views"
        )
        run = gr.Button("Inspect", variant="primary")
        summary = gr.Textbox(label="Part result", interactive=False)
        scores = gr.Dataframe(
            headers=["View", "File", "Raw score"],
            datatype=["number", "str", "number"],
            interactive=False,
        )
        gallery = gr.Gallery(
            label="Comparative heatmaps — not calibrated probabilities", columns=3, format="png"
        )

        def predict(part_id, paths):
            return predict_uploads(engine, registry, part_id, paths)

        run.click(
            predict, [part, uploads], [summary, scores, gallery],
            api_name="predict", concurrency_limit=1,
        )
        part.change(lambda part_id: input_details(registry, part_id), part, details)
        # Clear stale result
        for component in (part, uploads):
            component.change(lambda: ("", [], []), outputs=[summary, scores, gallery], queue=False)
        if examples:
            gr.Examples(
                examples=examples, inputs=[part, uploads],
                cache_examples=False, label="Example view groups",
            )
    return app


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    create_app().queue().launch()
