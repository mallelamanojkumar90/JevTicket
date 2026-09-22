from __future__ import annotations

import unittest

from calibration import calibration_summary


class CalibrationTests(unittest.TestCase):
    def test_builds_bins_and_ece(self) -> None:
        summary = calibration_summary(
            confidences=[0.1, 0.3, 0.7, 0.9],
            correctness=[False, True, True, True],
            bin_count=2,
        )

        self.assertEqual(len(summary.bins), 2)
        self.assertEqual(summary.bins[0].count, 2)
        self.assertEqual(summary.bins[1].count, 2)
        self.assertAlmostEqual(summary.bins[0].average_confidence, 0.2)
        self.assertAlmostEqual(summary.bins[0].accuracy, 0.5)
        self.assertAlmostEqual(summary.bins[1].average_confidence, 0.8)
        self.assertAlmostEqual(summary.bins[1].accuracy, 1.0)
        self.assertAlmostEqual(summary.expected_calibration_error, 0.25)

    def test_includes_one_in_last_bin(self) -> None:
        summary = calibration_summary(
            confidences=[1.0],
            correctness=[True],
            bin_count=5,
        )

        self.assertEqual(summary.bins[-1].count, 1)

    def test_mismatched_lengths_raise_error(self) -> None:
        with self.assertRaises(ValueError):
            calibration_summary([0.5], [True, False])


if __name__ == "__main__":
    unittest.main()
