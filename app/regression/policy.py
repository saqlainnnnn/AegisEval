from __future__ import annotations

import math

from app.domain.enums import (
    RegressionStatus,
    ThresholdType,
)
from app.domain.regression import RegressionThreshold


class RegressionThresholdPolicy:
    """
    Evaluates whether a metric has degraded beyond
    an allowed threshold.
    """

    def evaluate(
        self,
        *,
        baseline_value: float,
        candidate_value: float,
        higher_is_better: bool,
        threshold: RegressionThreshold,
    ) -> RegressionStatus:
        """
        Evaluate a candidate metric against its baseline.
        """

        degradation = self._calculate_degradation(
            baseline_value=baseline_value,
            candidate_value=candidate_value,
            higher_is_better=higher_is_better,
        )

        if threshold.threshold_type == ThresholdType.ABSOLUTE:
            allowed_degradation = threshold.value

        elif threshold.threshold_type == ThresholdType.RELATIVE:
            allowed_degradation = abs(baseline_value) * threshold.value

        else:
            raise ValueError(
                "Unsupported threshold type: " f"{threshold.threshold_type}"
            )

        exceeds_threshold = degradation > allowed_degradation and not math.isclose(
            degradation,
            allowed_degradation,
            rel_tol=1e-9,
            abs_tol=1e-12,
        )

        if exceeds_threshold:
            return RegressionStatus.REGRESSION

        return RegressionStatus.PASSED

    @staticmethod
    def _calculate_degradation(
        *,
        baseline_value: float,
        candidate_value: float,
        higher_is_better: bool,
    ) -> float:
        """
        Return degradation as a positive number.

        Improvement produces a negative number.
        """

        if higher_is_better:
            return baseline_value - candidate_value

        return candidate_value - baseline_value
