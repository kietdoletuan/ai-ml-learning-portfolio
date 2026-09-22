import unittest

import numpy as np
from PIL import Image

from core.render import render_overlays


class RenderTests(unittest.TestCase):
    def setUp(self):
        self.images = [Image.new("RGB", (8, 4), "black") for _ in range(2)]

    def test_scale_is_shared_between_views(self):
        maps = np.array([[[0, 1]], [[1, 2]]], dtype=np.float32)
        first, second = [np.asarray(image) for image in render_overlays(self.images, maps, opacity=1)]
        np.testing.assert_array_equal(first[0, 1], second[0, 0])
        self.assertFalse(np.array_equal(first[0, 0], second[0, 0]))

    def test_constant_maps_are_finite_and_equal(self):
        overlays = render_overlays(self.images, np.full((2, 2, 4), 7.0))
        self.assertEqual(overlays[0].size, (4, 2))
        np.testing.assert_array_equal(np.asarray(overlays[0]), np.asarray(overlays[1]))

    def test_order_keeps_the_corresponding_background(self):
        images = [Image.new("RGB", (4, 2), colour) for colour in ("red", "blue")]
        overlays = render_overlays(images, np.zeros((2, 2, 4)), opacity=0)
        self.assertEqual(overlays[0].getpixel((0, 0)), (255, 0, 0))
        self.assertEqual(overlays[1].getpixel((0, 0)), (0, 0, 255))

    def test_invalid_maps_and_opacity_raise(self):
        for maps in (np.zeros((1, 2, 4)), np.zeros((2, 0, 4)), np.zeros((2, 4)), np.full((2, 2, 4), np.nan)):
            with self.assertRaises(ValueError):
                render_overlays(self.images, maps)
        with self.assertRaises(ValueError):
            render_overlays(self.images, np.zeros((2, 2, 4)), opacity=1.1)
