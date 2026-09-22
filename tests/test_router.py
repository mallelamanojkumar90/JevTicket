from __future__ import annotations

import unittest

from models import Category, CategoryDecision
from router import route_ticket


def make_decision(category: Category, severity: float = 1.0) -> CategoryDecision:
    return CategoryDecision(
        category=category,
        urgent_probability=0.0,
        severity=severity,
        model="test-model",
    )


class RouteTicketTests(unittest.TestCase):
    def test_routes_billing_ticket_to_billing_support(self) -> None:
        route = route_ticket(make_decision(Category.BILLING))

        self.assertEqual(route.team, "Billing")
        self.assertEqual(route.queue_name, "billing-support")

    def test_routes_technical_ticket_to_technical_support(self) -> None:
        route = route_ticket(make_decision(Category.TECHNICAL))

        self.assertEqual(route.team, "Technical Support")
        self.assertEqual(route.queue_name, "technical-support")

    def test_routes_sales_ticket_to_sales(self) -> None:
        route = route_ticket(make_decision(Category.SALES))

        self.assertEqual(route.team, "Sales")
        self.assertEqual(route.queue_name, "sales")

    def test_routes_general_ticket_to_general_support(self) -> None:
        route = route_ticket(make_decision(Category.GENERAL))

        self.assertEqual(route.team, "General Support")
        self.assertEqual(route.queue_name, "general-support")

    def test_does_not_escalate_when_displayed_severity_is_below_four(self) -> None:
        route = route_ticket(make_decision(Category.BILLING, severity=3.49))

        self.assertFalse(route.escalate)
        self.assertIsNone(route.escalation_reason)

    def test_escalates_when_displayed_severity_is_four_or_higher(self) -> None:
        route = route_ticket(make_decision(Category.BILLING, severity=3.5))

        self.assertTrue(route.escalate)
        self.assertEqual(route.escalation_reason, "Severity is 4 or higher.")


if __name__ == "__main__":
    unittest.main()
