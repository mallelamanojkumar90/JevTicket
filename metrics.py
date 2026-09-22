from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass


@dataclass(frozen=True)
class ClassificationMetrics:
    accuracy: float
    precision: float
    recall: float
    f1: float


def accuracy_score(expected: Sequence[object], predicted: Sequence[object]) -> float:
    _validate_lengths(expected, predicted)

    if not expected:
        return 0.0

    correct = sum(1 for actual, guess in zip(expected, predicted) if actual == guess)
    return correct / len(expected)


def binary_metrics(expected: Sequence[bool], predicted: Sequence[bool]) -> ClassificationMetrics:
    _validate_lengths(expected, predicted)

    true_positive = sum(1 for actual, guess in zip(expected, predicted) if actual and guess)
    false_positive = sum(1 for actual, guess in zip(expected, predicted) if not actual and guess)
    false_negative = sum(1 for actual, guess in zip(expected, predicted) if actual and not guess)

    precision = _safe_divide(true_positive, true_positive + false_positive)
    recall = _safe_divide(true_positive, true_positive + false_negative)

    return ClassificationMetrics(
        accuracy=accuracy_score(expected, predicted),
        precision=precision,
        recall=recall,
        f1=_f1(precision, recall),
    )


def macro_metrics(
    expected: Sequence[object],
    predicted: Sequence[object],
    labels: Iterable[object],
) -> ClassificationMetrics:
    _validate_lengths(expected, predicted)

    per_label: list[tuple[float, float, float]] = []
    for label in labels:
        true_positive = sum(1 for actual, guess in zip(expected, predicted) if actual == label and guess == label)
        false_positive = sum(1 for actual, guess in zip(expected, predicted) if actual != label and guess == label)
        false_negative = sum(1 for actual, guess in zip(expected, predicted) if actual == label and guess != label)

        precision = _safe_divide(true_positive, true_positive + false_positive)
        recall = _safe_divide(true_positive, true_positive + false_negative)
        per_label.append((precision, recall, _f1(precision, recall)))

    if not per_label:
        return ClassificationMetrics(accuracy=accuracy_score(expected, predicted), precision=0.0, recall=0.0, f1=0.0)

    return ClassificationMetrics(
        accuracy=accuracy_score(expected, predicted),
        precision=sum(metric[0] for metric in per_label) / len(per_label),
        recall=sum(metric[1] for metric in per_label) / len(per_label),
        f1=sum(metric[2] for metric in per_label) / len(per_label),
    )


def _validate_lengths(expected: Sequence[object], predicted: Sequence[object]) -> None:
    if len(expected) != len(predicted):
        raise ValueError("Expected and predicted values must have the same length.")


def _safe_divide(numerator: int | float, denominator: int | float) -> float:
    if denominator == 0:
        return 0.0
    return numerator / denominator


def _f1(precision: float, recall: float) -> float:
    if precision + recall == 0:
        return 0.0
    return 2 * precision * recall / (precision + recall)
