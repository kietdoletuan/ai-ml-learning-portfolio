import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock

import numpy as np
from PIL import Image

from app import DEPLOY, create_app, predict_uploads
from core.aggregate import aggregate
from core.engine import Engine, PartUnavailable, Prediction
from core.registry import load_registry


class AppTests(unittest.TestCase):
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
            with self.assertLogs("app", level="ERROR"):
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

    def test_interface_builds_without_loading_a_model(self):
        engine = Engine(self.registry)
        app = create_app(self.registry, engine=engine, examples=[])
        self.assertEqual(engine._models, {})
        self.assertTrue(any(item.get("api_name") == "predict" for item in app.config["dependencies"]))
