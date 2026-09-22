from __future__ import annotations

import argparse
from dataclasses import dataclass

from evaluation_data import LabeledTicket, load_labeled_tickets
from jev_client import JevClient
from calibration import CalibrationSummary, calibration_summary
from metrics import ClassificationMetrics, accuracy_score, binary_metrics, macro_metrics
from models import Category


@dataclass(frozen=True)
class TicketPrediction:
    ticket_id: str
    expected_category: Category
    predicted_category: Category
    expected_urgent: bool
    predicted_urgent: bool
    expected_severity: int
    predicted_severity: int
    category_confidence: float | None
    urgency_confidence: float
    severity_confidence: float | None


def run_evaluation(limit: int | None = None) -> list[TicketPrediction]:
    tickets = load_labeled_tickets()
    if limit is not None:
        tickets = tickets[:limit]

    client = JevClient.from_env()
    predictions: list[TicketPrediction] = []

    for index, ticket in enumerate(tickets, start=1):
        print(f"[{index}/{len(tickets)}] Evaluating {ticket.ticket_id}...")
        decision = client.analyze_ticket(ticket.message)
        predictions.append(
            _prediction_from_decision(
                ticket=ticket,
                predicted_category=decision.category,
                predicted_urgent=decision.is_urgent,
                predicted_severity=decision.severity_display,
                category_confidence=decision.confidence,
                urgency_confidence=max(decision.urgent_probability, 1 - decision.urgent_probability),
                severity_confidence=decision.severity_confidence,
            )
        )

    return predictions


def summarize_predictions(
    predictions: list[TicketPrediction],
) -> dict[str, ClassificationMetrics | CalibrationSummary | float]:
    expected_categories = [prediction.expected_category for prediction in predictions]
    predicted_categories = [prediction.predicted_category for prediction in predictions]
    expected_urgent = [prediction.expected_urgent for prediction in predictions]
    predicted_urgent = [prediction.predicted_urgent for prediction in predictions]
    expected_severity = [prediction.expected_severity for prediction in predictions]
    predicted_severity = [prediction.predicted_severity for prediction in predictions]
    expected_escalation = [severity >= 4 for severity in expected_severity]
    predicted_escalation = [severity >= 4 for severity in predicted_severity]

    return {
        "category": macro_metrics(expected_categories, predicted_categories, labels=list(Category)),
        "urgency": binary_metrics(expected_urgent, predicted_urgent),
        "severity": macro_metrics(expected_severity, predicted_severity, labels=[1, 2, 3, 4, 5]),
        "escalation": binary_metrics(expected_escalation, predicted_escalation),
        "severity_within_one": _within_one_accuracy(expected_severity, predicted_severity),
        "category_calibration": _calibration_from_optional_confidence(
            confidences=[prediction.category_confidence for prediction in predictions],
            correctness=[
                prediction.expected_category == prediction.predicted_category
                for prediction in predictions
            ],
        ),
        "urgency_calibration": calibration_summary(
            confidences=[prediction.urgency_confidence for prediction in predictions],
            correctness=[
                prediction.expected_urgent == prediction.predicted_urgent
                for prediction in predictions
            ],
        ),
        "severity_calibration": _calibration_from_optional_confidence(
            confidences=[prediction.severity_confidence for prediction in predictions],
            correctness=[
                prediction.expected_severity == prediction.predicted_severity
                for prediction in predictions
            ],
        ),
    }


def print_summary(summary: dict[str, ClassificationMetrics | CalibrationSummary | float]) -> None:
    print()
    print("Evaluation Summary")
    print_metric_row("Category", _as_metrics(summary["category"]))
    print_metric_row("Urgency", _as_metrics(summary["urgency"]))
    print_metric_row("Severity", _as_metrics(summary["severity"]))
    print_metric_row("Escalation", _as_metrics(summary["escalation"]))
    print(f"Severity within-one accuracy: {_as_float(summary['severity_within_one']):.3f}")
    print_calibration_summary("Category", _as_calibration(summary["category_calibration"]))
    print_calibration_summary("Urgency", _as_calibration(summary["urgency_calibration"]))
    print_calibration_summary("Severity", _as_calibration(summary["severity_calibration"]))


def print_metric_row(name: str, metrics: ClassificationMetrics) -> None:
    print(
        f"{name:<10} "
        f"accuracy={metrics.accuracy:.3f} "
        f"precision={metrics.precision:.3f} "
        f"recall={metrics.recall:.3f} "
        f"f1={metrics.f1:.3f}"
    )


def print_calibration_summary(name: str, summary: CalibrationSummary) -> None:
    print()
    print(f"{name} Calibration")
    print(f"Expected calibration error: {summary.expected_calibration_error:.3f}")
    print("Bin        Count  Avg conf  Accuracy")
    for calibration_bin in summary.bins:
        print(
            f"{calibration_bin.lower:.1f}-{calibration_bin.upper:.1f}    "
            f"{calibration_bin.count:<5}  "
            f"{calibration_bin.average_confidence:.3f}     "
            f"{calibration_bin.accuracy:.3f}"
        )


def _prediction_from_decision(
    ticket: LabeledTicket,
    predicted_category: Category,
    predicted_urgent: bool,
    predicted_severity: int,
    category_confidence: float | None,
    urgency_confidence: float,
    severity_confidence: float | None,
) -> TicketPrediction:
    return TicketPrediction(
        ticket_id=ticket.ticket_id,
        expected_category=ticket.category,
        predicted_category=predicted_category,
        expected_urgent=ticket.urgent,
        predicted_urgent=predicted_urgent,
        expected_severity=ticket.severity,
        predicted_severity=predicted_severity,
        category_confidence=category_confidence,
        urgency_confidence=urgency_confidence,
        severity_confidence=severity_confidence,
    )


def _within_one_accuracy(expected: list[int], predicted: list[int]) -> float:
    if not expected:
        return 0.0

    correct = sum(1 for actual, guess in zip(expected, predicted) if abs(actual - guess) <= 1)
    return correct / len(expected)


def _calibration_from_optional_confidence(
    confidences: list[float | None],
    correctness: list[bool],
) -> CalibrationSummary:
    filtered_confidences: list[float] = []
    filtered_correctness: list[bool] = []

    for confidence, is_correct in zip(confidences, correctness):
        if confidence is None:
            continue
        filtered_confidences.append(confidence)
        filtered_correctness.append(is_correct)

    return calibration_summary(filtered_confidences, filtered_correctness)


def _as_metrics(value: ClassificationMetrics | CalibrationSummary | float) -> ClassificationMetrics:
    if not isinstance(value, ClassificationMetrics):
        raise TypeError("Expected ClassificationMetrics.")
    return value


def _as_float(value: ClassificationMetrics | CalibrationSummary | float) -> float:
    if not isinstance(value, float):
        raise TypeError("Expected float.")
    return value


def _as_calibration(value: ClassificationMetrics | CalibrationSummary | float) -> CalibrationSummary:
    if not isinstance(value, CalibrationSummary):
        raise TypeError("Expected CalibrationSummary.")
    return value


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate JevTicket predictions against labeled tickets.")
    parser.add_argument("--limit", type=int, default=None, help="Evaluate only the first N labeled tickets.")
    args = parser.parse_args()

    predictions = run_evaluation(limit=args.limit)
    print_summary(summarize_predictions(predictions))


if __name__ == "__main__":
    main()
