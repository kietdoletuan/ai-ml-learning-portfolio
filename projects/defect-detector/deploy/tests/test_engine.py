import tempfile
import unittest
from pathlib import Path

import yaml

from core.artifacts import DEV_ROOT
from core.engine import Engine, PartUnavailable, score_batch
from core.preprocess import InputError, load_views, to_batch
from core.registry import load_registry

DEPLOY = Path(__file__).resolve().parents[1]
DATA = DEV_ROOT / "data" / "bolt_roi"
GOOD = yaml.safe_load((DEPLOY / "parts" / "bolt.yaml").read_text(encoding="utf-8"))
CHECKPOINT = DEV_ROOT / GOOD["local_checkpoint"]

NORMAL = [DATA / "heldout" / f"bolt_normal_heldout_p23_r{i}_A.png" for i in (1, 2)]
SURFACE = [DATA / "defects" / "surface" / f"bolt_defect_surface_p12_r{i}_A.png" for i in (1, 2)]
THREAD = [DATA / "defects" / "thread" / f"bolt_defect_thread_p03_r{i}_A.png" for i in (1, 2)]

NOTEBOOK_SCORE = 10.957717895507812  # bolt_normal_heldout_p23_r1_A in 04_patchcore_bolt.ipynb


@unittest.skipUnless(CHECKPOINT.is_file() and DATA.is_dir(), "needs the local checkpoint and data/bolt_roi")
class EngineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = load_registry(DEPLOY / "parts")
        cls.engine = Engine(cls.registry, prefer_local=True)
        cls.spec = cls.registry.get("bolt")

    def test_parity_with_notebook(self):
        pred = self.engine.predict("bolt", NORMAL)
        self.assertAlmostEqual(pred.result.view_scores[0], NOTEBOOK_SCORE, delta=0.01)

    def test_verdicts(self):
        self.assertFalse(self.engine.predict("bolt", NORMAL).result.flagged)
        self.assertTrue(self.engine.predict("bolt", SURFACE).result.flagged)
        self.assertTrue(self.engine.predict("bolt", THREAD).result.flagged)

    def test_part_score_is_max_of_views(self):
        r = self.engine.predict("bolt", SURFACE + THREAD[:1]).result
        self.assertEqual(r.part_score, max(r.view_scores))
        self.assertEqual(r.view_scores[r.top_view], r.part_score)

    def test_order_follows_upload_order(self):
        forward = self.engine.predict("bolt", NORMAL + SURFACE[:1]).result
        backward = self.engine.predict("bolt", (NORMAL + SURFACE[:1])[::-1]).result
        for a, b in zip(forward.view_scores, backward.view_scores[::-1]):
            self.assertAlmostEqual(a, b, delta=1e-4)
        self.assertEqual(forward.view_names, tuple(p.name for p in NORMAL + SURFACE[:1]))
        self.assertAlmostEqual(forward.part_score, backward.part_score, delta=1e-4)

    def test_repeat_is_stable(self):
        a = self.engine.predict("bolt", NORMAL).result.view_scores
        b = self.engine.predict("bolt", NORMAL).result.view_scores
        for x, y in zip(a, b):
            self.assertAlmostEqual(x, y, delta=1e-5)

    def test_batch_does_not_change_a_score(self):
        model = self.engine._get_model(self.spec)
        images, _ = load_views(NORMAL + SURFACE[:1], self.spec)
        batch = to_batch(images, self.spec)
        together, _ = score_batch(model, batch)
        for i in range(len(images)):
            alone, _ = score_batch(model, batch[i:i + 1])
            self.assertAlmostEqual(together[i], alone[0], delta=1e-4)

    def test_maps_shape(self):
        pred = self.engine.predict("bolt", NORMAL)
        self.assertEqual(pred.anomaly_maps.shape, (2, 256, 720))

    def test_bad_input_never_loads_a_model(self):
        engine = Engine(self.registry, prefer_local=True)
        with self.assertRaises(InputError):
            engine.predict("bolt", NORMAL[:1])
        self.assertEqual(engine._models, {})

    def test_unknown_part(self):
        with self.assertRaises(KeyError):
            self.engine.predict("nut", NORMAL)


@unittest.skipUnless(CHECKPOINT.is_file() and DATA.is_dir(), "needs the local checkpoint and data/bolt_roi")
class FailureIsolationTests(unittest.TestCase):
    def test_bad_part_does_not_stop_good_part(self):
        local = {**GOOD, "model_repo_id": None, "model_revision": None}
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            (folder / "bolt.yaml").write_text(yaml.safe_dump(local), encoding="utf-8")
            (folder / "wrong_hash.yaml").write_text(yaml.safe_dump({**local, "model_sha256": "0" * 64}), encoding="utf-8")
            (folder / "wrong_model.yaml").write_text(yaml.safe_dump({**local, "backbone": "resnet50"}), encoding="utf-8")
            engine = Engine(load_registry(folder), prefer_local=True)

            with self.assertRaisesRegex(PartUnavailable, "sha256"):
                engine.predict("wrong_hash", NORMAL)
            with self.assertRaisesRegex(PartUnavailable, "backbone"):
                engine.predict("wrong_model", NORMAL)
            self.assertFalse(engine.predict("bolt", NORMAL).result.flagged)


if __name__ == "__main__":
    unittest.main()
