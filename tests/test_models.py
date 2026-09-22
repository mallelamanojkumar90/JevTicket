from __future__ import annotations

import unittest

from models import Category, CategoryDecision


class CategoryDecisionTests(unittest.TestCase):
    def test_marks_urgent_when_probability_is_at_least_half(self) -> None:
        decision = CategoryDecision(
            category=Category.BILLING,
            urgent_probability=0.5,
            severity=1.0,
            model="test-model",
        )

        self.assertTrue(decision.is_urgent)

    def test_marks_not_urgent_when_probability_is_below_half(self) -> None:
        decision = CategoryDecision(
            category=Category.BILLING,
            urgent_probability=0.49,
            severity=1.0,
            model="test-model",
        )

        self.assertFalse(decision.is_urgent)

    def test_displays_severity_as_nearest_integer(self) -> None:
        decision = CategoryDecision(
            category=Category.BILLING,
            urgent_probability=0.0,
            severity=3.6,
            model="test-model",
        )

        self.assertEqual(decision.severity_display, 4)

    def test_escalates_when_displayed_severity_is_four_or_higher(self) -> None:
        decision = CategoryDecision(
            category=Category.BILLING,
            urgent_probability=0.0,
            severity=3.5,
            model="test-model",
        )

        self.assertTrue(decision.should_escalate)

    def test_does_not_escalate_when_displayed_severity_is_below_four(self) -> None:
        decision = CategoryDecision(
            category=Category.BILLING,
            urgent_probability=0.0,
            severity=3.49,
            model="test-model",
        )

        self.assertFalse(decision.should_escalate)


if __name__ == "__main__":
    unittest.main()
