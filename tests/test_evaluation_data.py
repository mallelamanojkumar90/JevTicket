from __future__ import annotations

import unittest
from collections import Counter

from evaluation_data import load_labeled_tickets
from models import Category


class LabeledTicketsTests(unittest.TestCase):
    def test_dataset_contains_50_tickets(self) -> None:
        tickets = load_labeled_tickets()

        self.assertEqual(len(tickets), 50)

    def test_ticket_ids_are_unique(self) -> None:
        tickets = load_labeled_tickets()
        ticket_ids = [ticket.ticket_id for ticket in tickets]

        self.assertEqual(len(ticket_ids), len(set(ticket_ids)))

    def test_dataset_covers_every_category(self) -> None:
        tickets = load_labeled_tickets()
        categories = {ticket.category for ticket in tickets}

        self.assertEqual(categories, set(Category))

    def test_dataset_has_urgent_and_non_urgent_examples(self) -> None:
        tickets = load_labeled_tickets()
        urgent_values = {ticket.urgent for ticket in tickets}

        self.assertEqual(urgent_values, {False, True})

    def test_dataset_has_all_severity_levels(self) -> None:
        tickets = load_labeled_tickets()
        severity_values = {ticket.severity for ticket in tickets}

        self.assertEqual(severity_values, {1, 2, 3, 4, 5})

    def test_category_distribution_is_reasonably_balanced(self) -> None:
        tickets = load_labeled_tickets()
        counts = Counter(ticket.category for ticket in tickets)

        self.assertGreaterEqual(min(counts.values()), 12)
        self.assertLessEqual(max(counts.values()), 13)


if __name__ == "__main__":
    unittest.main()
