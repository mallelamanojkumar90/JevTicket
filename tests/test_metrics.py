from __future__ import annotations

import unittest

from metrics import accuracy_score, binary_metrics, macro_metrics


class MetricsTests(unittest.TestCase):
    def test_accuracy_score(self) -> None:
        self.assertEqual(accuracy_score(["a", "b", "c"], ["a", "x", "c"]), 2 / 3)

    def test_binary_metrics(self) -> None:
        metrics = binary_metrics(
            expected=[True, True, False, False],
            predicted=[True, False, True, False],
        )

        self.assertEqual(metrics.accuracy, 0.5)
        self.assertEqual(metrics.precision, 0.5)
        self.assertEqual(metrics.recall, 0.5)
        self.assertEqual(metrics.f1, 0.5)

    def test_macro_metrics(self) -> None:
        metrics = macro_metrics(
            expected=["a", "a", "b", "b"],
            predicted=["a", "b", "b", "b"],
            labels=["a", "b"],
        )

        self.assertEqual(metrics.accuracy, 0.75)
        self.assertAlmostEqual(metrics.precision, (1.0 + 2 / 3) / 2)
        self.assertAlmostEqual(metrics.recall, (0.5 + 1.0) / 2)

    def test_mismatched_lengths_raise_error(self) -> None:
        with self.assertRaises(ValueError):
            accuracy_score(["a"], ["a", "b"])


if __name__ == "__main__":
    unittest.main()
