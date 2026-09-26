import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock

import numpy as np
from PIL import Image
from streamlit.testing.v1 import AppTest

from core.aggregate import aggregate
from core.engine import Engine, PartUnavailable, Prediction
from core.registry import load_registry
from service import DEPLOY, predict_uploads, save_uploads


class ServiceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = load_registry(DEPLOY / "parts")

    def test_no_upload_uses_the_input_error_and_clears_outputs(self):
        engine = Engine(self.registry)
        message, rows, gallery = predict_uploads(engine, self.registry, "bolt", None)
        self.assertIn("got 0", message)
        self.assertEqual((rows, gallery), ([], []))
        self.assertEqual(engine._models, {})

    def test_failed_request_returns_no_previous_result(self):
        for error in (PartUnavailable("broken checkpoint"), RuntimeError("bad map")):
            engine = Mock()
            engine.predict.side_effect = error
            with self.assertLogs("service", level="ERROR"):
                message, rows, gallery = predict_uploads(engine, self.registry, "bolt", [])
            self.assertNotIn("PASSED", message)
            self.assertEqual((rows, gallery), ([], []))

    def test_success_uses_engine_verdict_and_preserves_order(self):
        with tempfile.TemporaryDirectory() as folder:
            paths = [Path(folder) / name for name in ("second.png", "first.png")]
            for path in paths:
                Image.new("RGB", self.registry.get("bolt").roi_size).save(path)
            result = aggregate("bolt", [path.name for path in paths], [10.0, 13.5], 12.38)
            engine = Mock()
            engine.predict.return_value = Prediction(result, np.zeros((2, 256, 720)))
            message, rows, gallery = predict_uploads(engine, self.registry, "bolt", paths)
        self.assertIn("FLAGGED", message)
        self.assertIn("view 2", message)
        self.assertEqual([row[1] for row in rows], ["second.png", "first.png"])
        self.assertIn("second.png", gallery[0][1])
        self.assertIn("first.png", gallery[1][1])

    def test_duplicate_upload_names_are_kept_in_order(self):
        uploads = [Mock(), Mock()]
        for upload, data in zip(uploads, (b"a", b"b")):
            upload.name = "view.png"
            upload.getvalue.return_value = data
        with tempfile.TemporaryDirectory() as folder:
            paths = save_uploads(uploads, Path(folder))
            self.assertEqual([p.name for p in paths], ["view.png", "view.png"])
            self.assertEqual([p.read_bytes() for p in paths], [b"a", b"b"])


class AppTests(unittest.TestCase):
    def test_page_renders_without_error(self):
        # file_uploader not scriptable here
        app = AppTest.from_file(str(DEPLOY / "app.py"), default_timeout=120).run()
        self.assertFalse(app.exception)
        self.assertEqual(app.selectbox[0].value, "bolt")
        self.assertIn("Inspect", [button.label for button in app.button])
