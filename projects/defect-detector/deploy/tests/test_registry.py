import tempfile
import unittest
from pathlib import Path

import yaml

from core.artifacts import ChecksumMismatch, resolve_checkpoint, sha256_file, verify_sha256
from core.contract import ContractError, PartSpec
from core.registry import load_registry

DEPLOY = Path(__file__).resolve().parents[1]
GOOD = yaml.safe_load((DEPLOY / "parts" / "bolt.yaml").read_text(encoding="utf-8"))
LOCAL_ONLY = {**GOOD, "model_repo_id": None, "model_revision": None}


def write_part(folder: Path, part_id: str, data) -> None:
    text = data if isinstance(data, str) else yaml.safe_dump(data)
    (folder / f"{part_id}.yaml").write_text(text, encoding="utf-8")


class ContractTests(unittest.TestCase):
    def test_bolt_yaml_loads(self):
        spec = PartSpec.from_dict("bolt", GOOD)
        self.assertEqual(spec.roi_size, (2563, 909))
        self.assertEqual(spec.image_size, (256, 720))
        self.assertEqual(spec.threshold, 12.38)

    def test_remote_source_flag(self):
        self.assertFalse(PartSpec.from_dict("bolt", LOCAL_ONLY).has_remote_source)
        remote = {**LOCAL_ONLY, "model_repo_id": "u/bolt", "model_revision": "a" * 40}
        self.assertTrue(PartSpec.from_dict("bolt", remote).has_remote_source)

    def test_missing_key_rejected(self):
        bad = {k: v for k, v in GOOD.items() if k != "threshold"}
        with self.assertRaisesRegex(ContractError, "threshold"):
            PartSpec.from_dict("bolt", bad)

    def test_repo_without_revision_rejected(self):
        with self.assertRaisesRegex(ContractError, "together"):
            PartSpec.from_dict("bolt", {**LOCAL_ONLY, "model_repo_id": "u/bolt"})

    def test_short_or_branch_revision_rejected(self):
        for rev in ("main", "abc1234", "A" * 40):
            with self.assertRaisesRegex(ContractError, "40-char"):
                PartSpec.from_dict("bolt", {**GOOD, "model_repo_id": "u/bolt", "model_revision": rev})

    def test_full_revision_accepted(self):
        spec = PartSpec.from_dict("bolt", {**GOOD, "model_repo_id": "u/bolt", "model_revision": "a" * 40})
        self.assertTrue(spec.has_remote_source)

    def test_no_source_rejected(self):
        with self.assertRaisesRegex(ContractError, "needs model_repo_id"):
            PartSpec.from_dict("bolt", {**LOCAL_ONLY, "local_checkpoint": None})

    def test_bad_view_range_and_hash_rejected(self):
        with self.assertRaises(ContractError):
            PartSpec.from_dict("bolt", {**GOOD, "min_views": 3, "max_views": 2})
        with self.assertRaises(ContractError):
            PartSpec.from_dict("bolt", {**GOOD, "model_sha256": "xyz"})

    def test_layers_threshold_and_repo_id_validated(self):
        for bad_layers in ("layer2", [], [2, 3], None):
            with self.assertRaisesRegex(ContractError, "layers"):
                PartSpec.from_dict("bolt", {**GOOD, "layers": bad_layers})
        for bad_threshold in (float("nan"), float("inf"), 0, -1.0):
            with self.assertRaisesRegex(ContractError, "threshold"):
                PartSpec.from_dict("bolt", {**GOOD, "threshold": bad_threshold})
        for bad_repo in ("", "no-slash", "/name", "user/", "a/b/c"):
            with self.assertRaisesRegex(ContractError, "user/name"):
                PartSpec.from_dict("bolt", {**GOOD, "model_repo_id": bad_repo, "model_revision": "a" * 40})

    def test_bad_part_id_rejected(self):
        with self.assertRaises(ContractError):
            PartSpec.from_dict("Bolt-2", GOOD)


class RegistryTests(unittest.TestCase):
    def test_real_registry_has_bolt(self):
        reg = load_registry(DEPLOY / "parts")
        self.assertIn("bolt", reg.parts)
        self.assertEqual(reg.errors, {})

    def test_broken_part_is_isolated(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            write_part(folder, "bolt", GOOD)
            write_part(folder, "nut", {**GOOD, "threshold": None, "min_views": 5, "max_views": 1})
            write_part(folder, "washer", "key: [unclosed")
            write_part(folder, "gear", "- just\n- a list\n")
            reg = load_registry(folder)
        self.assertEqual(list(reg.parts), ["bolt"])
        self.assertEqual(set(reg.errors), {"nut", "washer", "gear"})

    def test_unknown_part_message(self):
        reg = load_registry(DEPLOY / "parts")
        with self.assertRaisesRegex(KeyError, "available"):
            reg.get("nut")


class ArtifactTests(unittest.TestCase):
    def test_hash_match_and_mismatch(self):
        with tempfile.TemporaryDirectory() as tmp:
            f = Path(tmp) / "model.ckpt"
            f.write_bytes(b"hello")
            digest = sha256_file(f)
            verify_sha256(f, digest)
            with self.assertRaises(ChecksumMismatch):
                verify_sha256(f, "0" * 64)

    def test_resolve_local_verifies_hash(self):
        spec = PartSpec.from_dict("bolt", LOCAL_ONLY)
        try:
            path = resolve_checkpoint(spec)
        except FileNotFoundError:
            self.skipTest("local checkpoint not present on this machine")
        self.assertEqual(sha256_file(path), spec.model_sha256)

    def test_prefer_local_skips_remote(self):
        spec = PartSpec.from_dict("bolt", {**LOCAL_ONLY, "model_repo_id": "u/bolt", "model_revision": "a" * 40})
        try:
            path = resolve_checkpoint(spec, prefer_local=True)
        except FileNotFoundError:
            self.skipTest("local checkpoint not present on this machine")
        self.assertEqual(path.name, "model.ckpt")

    def test_resolve_local_rejects_wrong_hash(self):
        spec = PartSpec.from_dict("bolt", {**LOCAL_ONLY, "model_sha256": "0" * 64})
        try:
            resolve_checkpoint(spec)
        except FileNotFoundError:
            self.skipTest("local checkpoint not present on this machine")
        except ChecksumMismatch:
            return
        self.fail("wrong fingerprint was accepted")


if __name__ == "__main__":
    unittest.main()
