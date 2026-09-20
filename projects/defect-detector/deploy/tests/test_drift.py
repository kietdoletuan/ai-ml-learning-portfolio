import unittest
from pathlib import Path

import yaml

from core.registry import load_registry

DEPLOY = Path(__file__).resolve().parents[1]
TRAIN = yaml.safe_load((DEPLOY.parent / "parts" / "bolt.yaml").read_text(encoding="utf-8"))


class DriftTests(unittest.TestCase):
    def setUp(self):
        self.spec = load_registry(DEPLOY / "parts").get("bolt")

    def test_matches_training_config(self):
        x, y, w, h = TRAIN["roi"]
        self.assertEqual(self.spec.roi_size, (w, h))
        self.assertEqual(self.spec.image_size, tuple(TRAIN["image_size"]))
        self.assertEqual(self.spec.threshold, TRAIN["threshold"])
        self.assertEqual(self.spec.backbone, TRAIN["backbone"])

    def test_matches_frozen_plan_constants(self):
        self.assertEqual(self.spec.roi_size, (2563, 909))
        self.assertEqual(self.spec.image_size, (256, 720))
        self.assertEqual(self.spec.threshold, 12.38)
        self.assertEqual((self.spec.min_views, self.spec.max_views), (2, 3))
        self.assertEqual(self.spec.layers, ("layer2", "layer3"))
        self.assertEqual(self.spec.coreset_ratio, 0.02)
        self.assertEqual(self.spec.num_neighbors, 9)
        self.assertEqual(
            self.spec.model_sha256,
            "865197a0782a2e258b202bec7b03622b00dfff674a408b281a59ceb15fca3c83",
        )

    def test_local_checkpoint_matches_training_config(self):
        self.assertEqual(self.spec.local_checkpoint, TRAIN["checkpoint"])


if __name__ == "__main__":
    unittest.main()
