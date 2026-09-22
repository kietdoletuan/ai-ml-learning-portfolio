"""Private-only smoke test.

Run from deploy/: python tools/smoke_app.py
"""
import sys
from pathlib import Path

DEPLOY = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(DEPLOY))

from gradio_client import Client, handle_file

from app import create_app


def main():
    data = DEPLOY.parent / "data" / "bolt_roi"
    groups = [
        ("heldout", "bolt_normal_heldout_p23", 2, "PASSED"),
        ("defects/surface", "bolt_defect_surface_p12", 3, "FLAGGED"),
        ("defects/thread", "bolt_defect_thread_p03", 3, "FLAGGED"),
    ]
    examples = [
        ["bolt", [str(data / folder / f"{prefix}_r{view}_A.png") for view in range(1, count + 1)]]
        for folder, prefix, count, _ in groups
    ]
    app = create_app(examples=examples)
    try:
        example_files = [path for _, paths in examples for path in paths]
        _, url, _ = app.queue().launch(
            prevent_thread_lock=True, quiet=True, allowed_paths=example_files
        )
        client = Client(url, verbose=False)
        for index, ((_, _, count, expected), (_, paths)) in enumerate(zip(groups, examples)):
            # Load via Examples widget
            loaded = client.predict(index, api_name="/load_example")
            assert loaded[0]["value"] == "bolt" and len(loaded[1]["value"]) == count, loaded
            result = client.predict(
                loaded[0]["value"],
                [handle_file(path) for path in loaded[1]["value"]],
                api_name="/predict",
            )
            assert result[0].startswith(expected), result[0]
            assert len(result[1]["data"]) == count and len(result[2]) == count
            print(result[0])
        result = client.predict("bolt", [], api_name="/predict")
        assert result[0].startswith("Input error:") and not result[1]["data"] and not result[2]
        print("HTTP examples, normal/surface/thread inference, overlays and empty-upload check passed.")
    finally:
        app.close()


if __name__ == "__main__":
    main()
