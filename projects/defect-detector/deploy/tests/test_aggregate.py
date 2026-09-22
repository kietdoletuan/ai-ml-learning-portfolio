import unittest

from core.aggregate import aggregate


class AggregateTests(unittest.TestCase):
    def test_part_score_is_max_and_order_kept(self):
        r = aggregate("bolt", ["a", "b", "c"], [10.0, 13.5, 11.0], 12.38)
        self.assertEqual(r.part_score, 13.5)
        self.assertEqual(r.top_view, 1)
        self.assertEqual(r.view_names, ("a", "b", "c"))
        self.assertEqual(r.view_scores, (10.0, 13.5, 11.0))
        self.assertTrue(r.flagged)

    def test_threshold_is_strict(self):
        at = aggregate("bolt", ["a", "b"], [12.38, 5.0], 12.38)
        above = aggregate("bolt", ["a", "b"], [12.380001, 5.0], 12.38)
        self.assertFalse(at.flagged)
        self.assertTrue(above.flagged)

    def test_tie_names_first_view(self):
        self.assertEqual(aggregate("bolt", ["a", "b"], [9.0, 9.0], 12.38).top_view, 0)

    def test_bad_inputs_rejected(self):
        with self.assertRaises(ValueError):
            aggregate("bolt", [], [], 12.38)
        with self.assertRaises(ValueError):
            aggregate("bolt", ["a", "b"], [1.0], 12.38)
        for bad in (float("nan"), float("inf")):
            with self.assertRaises(ValueError):
                aggregate("bolt", ["a", "b"], [1.0, bad], 12.38)


if __name__ == "__main__":
    unittest.main()
