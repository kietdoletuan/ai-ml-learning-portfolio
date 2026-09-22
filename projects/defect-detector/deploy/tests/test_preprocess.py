import tempfile
import unittest
from pathlib import Path

from PIL import Image

from core.preprocess import InputError, load_views, to_batch
from core.registry import load_registry

DEPLOY = Path(__file__).resolve().parents[1]
SPEC = load_registry(DEPLOY / "parts").get("bolt")


def make_image(folder: Path, name: str, size=None, color=(0, 0, 0), mode="RGB") -> Path:
    path = folder / name
    Image.new(mode, size or SPEC.roi_size, color).save(path)
    return path


class LoadViewsTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def images(self, n):
        return [make_image(self.dir, f"v{i}.png") for i in range(n)]

    def test_view_count_limits(self):
        for n in (0, 1, 4):
            with self.assertRaisesRegex(InputError, "got %d" % n):
                load_views(self.images(n), SPEC)
        for n in (2, 3):
            images, names = load_views(self.images(n), SPEC)
            self.assertEqual(len(images), n)
            self.assertEqual(names, [f"v{i}.png" for i in range(n)])

    def test_wrong_size_names_file_and_sizes(self):
        good = make_image(self.dir, "good.png")
        bad = make_image(self.dir, "raw.png", size=(2592, 1944))
        with self.assertRaises(InputError) as ctx:
            load_views([good, bad], SPEC)
        msg = str(ctx.exception)
        self.assertIn("raw.png", msg)
        self.assertIn("2592x1944", msg)
        self.assertIn("2563x909", msg)

    def test_downscaled_same_ratio_rejected(self):
        small = make_image(self.dir, "small.png", size=(1281, 454))
        good = make_image(self.dir, "good.png")
        with self.assertRaises(InputError):
            load_views([good, small], SPEC)

    def test_unreadable_and_missing_files_rejected(self):
        good = make_image(self.dir, "good.png")
        junk = self.dir / "junk.png"
        junk.write_bytes(b"not an image")
        with self.assertRaisesRegex(InputError, "junk.png"):
            load_views([good, junk], SPEC)
        with self.assertRaisesRegex(InputError, "gone.png"):
            load_views([good, self.dir / "gone.png"], SPEC)

    def test_other_modes_become_rgb(self):
        rgba = make_image(self.dir, "a.png", mode="RGBA", color=(1, 2, 3, 255))
        gray = make_image(self.dir, "b.png", mode="L", color=10)
        images, _ = load_views([rgba, gray], SPEC)
        self.assertTrue(all(im.mode == "RGB" for im in images))


class BatchTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def test_shape(self):
        paths = [make_image(self.dir, f"v{i}.png") for i in range(3)]
        images, _ = load_views(paths, SPEC)
        self.assertEqual(tuple(to_batch(images, SPEC).shape), (3, 3, 256, 720))

    def test_normalization_and_order(self):
        red = make_image(self.dir, "red.png", color=(255, 0, 0))
        blue = make_image(self.dir, "blue.png", color=(0, 0, 255))
        images, _ = load_views([red, blue], SPEC)
        batch = to_batch(images, SPEC)
        self.assertAlmostEqual(float(batch[0, 0].mean()), (1 - 0.485) / 0.229, places=3)
        self.assertAlmostEqual(float(batch[1, 2].mean()), (1 - 0.406) / 0.225, places=3)
        self.assertLess(float(batch[0, 2].mean()), 0)

    def test_no_center_crop(self):
        path = self.dir / "edge.png"
        img = Image.new("RGB", SPEC.roi_size, (0, 0, 0))
        img.paste((255, 255, 255), (0, 0, 20, SPEC.roi_size[1]))
        img.save(path)
        images, _ = load_views([path, path], SPEC)
        batch = to_batch(images, SPEC)
        # proves no center crop
        self.assertGreater(float(batch[0, 0, :, 0].mean()), 1.0)


if __name__ == "__main__":
    unittest.main()
