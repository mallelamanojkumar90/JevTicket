from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CalibrationBin:
    lower: float
    upper: float
    count: int
    average_confidence: float
    accuracy: float


@dataclass(frozen=True)
class CalibrationSummary:
    bins: list[CalibrationBin]
    expected_calibration_error: float


def calibration_summary(
    confidences: list[float],
    correctness: list[bool],
    bin_count: int = 5,
) -> CalibrationSummary:
    if len(confidences) != len(correctness):
        raise ValueError("Confidences and correctness values must have the same length.")

    if bin_count <= 0:
        raise ValueError("bin_count must be greater than 0.")

    total = len(confidences)
    bins: list[CalibrationBin] = []
    expected_calibration_error = 0.0

    for index in range(bin_count):
        lower = index / bin_count
        upper = (index + 1) / bin_count
        item_indexes = [
            item_index
            for item_index, confidence in enumerate(confidences)
            if _in_bin(confidence, lower, upper, is_last_bin=index == bin_count - 1)
        ]

        if item_indexes:
            average_confidence = sum(confidences[item_index] for item_index in item_indexes) / len(item_indexes)
            accuracy = sum(1 for item_index in item_indexes if correctness[item_index]) / len(item_indexes)
            expected_calibration_error += len(item_indexes) / total * abs(accuracy - average_confidence)
        else:
            average_confidence = 0.0
            accuracy = 0.0

        bins.append(
            CalibrationBin(
                lower=lower,
                upper=upper,
                count=len(item_indexes),
                average_confidence=average_confidence,
                accuracy=accuracy,
            )
        )

    return CalibrationSummary(
        bins=bins,
        expected_calibration_error=expected_calibration_error,
    )


def _in_bin(confidence: float, lower: float, upper: float, is_last_bin: bool) -> bool:
    if is_last_bin:
        return lower <= confidence <= upper
    return lower <= confidence < upper
