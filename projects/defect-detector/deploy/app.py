import logging
import tempfile
from pathlib import Path

import streamlit as st

from core.engine import Engine
from core.registry import load_registry
from service import DEPLOY, bundled_examples, input_details, predict_uploads, save_uploads

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@st.cache_resource
def get_service():
    """Shared across sessions, reruns."""
    registry = load_registry(DEPLOY / "parts")
    engine = Engine(registry)
    if not engine.parts:
        raise RuntimeError(f"No valid part configurations: {registry.errors}")
    for part_id, error in registry.errors.items():
        logger.warning("Skipped part %s: %s", part_id, error)
    return registry, engine


def show(summary, rows, gallery):
    if not rows:
        st.warning(summary)
        return
    verdict = st.error if summary.startswith("FLAGGED") else st.success
    verdict(summary.replace("\n", "  \n"))
    st.dataframe(
        [{"View": view, "File": name, "Raw score": score} for view, name, score in rows],
        hide_index=True,
    )
    st.caption("Comparative heatmaps — not calibrated probabilities")
    for image, caption in gallery:
        st.image(image, caption=caption)


st.set_page_config(page_title="Defect Detector")
st.title("Defect Detector")
registry, engine = get_service()

part_id = st.selectbox("Part", engine.parts)
st.markdown(input_details(registry, part_id))
# new part clears uploads
uploads = st.file_uploader(
    "ROI views",
    type=["png", "jpg", "jpeg", "bmp", "tif", "tiff"],
    accept_multiple_files=True,
    key=f"uploads-{part_id}",
)

# results only on click
if st.button("Inspect", type="primary"):
    with tempfile.TemporaryDirectory() as folder:
        paths = save_uploads(uploads or [], Path(folder))
        show(*predict_uploads(engine, registry, part_id, paths))

examples = {
    Path(paths[0]).parent.name: paths
    for example_part, paths in bundled_examples(DEPLOY / "examples", engine.parts)
    if example_part == part_id
}
if examples:
    st.divider()
    group = st.selectbox("Example view groups", list(examples))
    if st.button("Inspect example"):
        show(*predict_uploads(engine, registry, part_id, examples[group]))
