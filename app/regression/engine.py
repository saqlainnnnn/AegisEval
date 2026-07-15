from __future__ import annotations

from app.domain.enums import (
    MetricType,
    RegressionStatus,
)
from app.domain.metrics import MetricSummary
from app.domain.regression import (
    MetricComparison,
    RegressionResult,
    RegressionThreshold,
)
from app.regression.policy import (
    RegressionThresholdPolicy,
)


class RegressionEngine:
    """
    Compare evaluation metrics against a baseline.
    """

    def __init__(
        self,
        policy: RegressionThresholdPolicy,
    ) -> None:
        self._policy = policy

    def compare(
        self,
        *,
        baseline_run_id: str,
        candidate_run_id: str,
        baseline: MetricSummary,
        candidate: MetricSummary,
        thresholds: list[
            RegressionThreshold
        ],
    ) -> RegressionResult:
        """
        Compare candidate metrics against baseline metrics.
        """

        comparisons = [
            self._compare_metric(
                baseline=baseline,
                candidate=candidate,
                threshold=threshold,
            )
            for threshold in thresholds
        ]

        status = (
            RegressionStatus.REGRESSION
            if any(
                comparison.status
                == RegressionStatus.REGRESSION
                for comparison in comparisons
            )
            else RegressionStatus.PASSED
        )

        return RegressionResult(
            baseline_run_id=baseline_run_id,
            candidate_run_id=candidate_run_id,
            status=status,
            comparisons=comparisons,
        )

    def _compare_metric(
        self,
        *,
        baseline: MetricSummary,
        candidate: MetricSummary,
        threshold: RegressionThreshold,
    ) -> MetricComparison:
        """
        Compare one metric using its configured threshold.
        """

        metric = threshold.metric

        baseline_result = self._get_metric(
            summary=baseline,
            metric=metric,
            summary_name="baseline",
        )

        candidate_result = self._get_metric(
            summary=candidate,
            metric=metric,
            summary_name="candidate",
        )

        if (
            baseline_result.higher_is_better
            != candidate_result.higher_is_better
        ):
            raise ValueError(
                "Metric direction mismatch for "
                f"{metric.value}."
            )

        absolute_change = (
            candidate_result.value
            - baseline_result.value
        )

        relative_change = (
            None
            if baseline_result.value == 0
            else (
                absolute_change
                / abs(baseline_result.value)
            )
        )

        status = self._policy.evaluate(
            baseline_value=baseline_result.value,
            candidate_value=candidate_result.value,
            higher_is_better=(
                baseline_result.higher_is_better
            ),
            threshold=threshold,
        )

        return MetricComparison(
            metric=metric,
            baseline_value=baseline_result.value,
            candidate_value=candidate_result.value,
            absolute_change=absolute_change,
            relative_change=relative_change,
            threshold=threshold,
            status=status,
        )

    @staticmethod
    def _get_metric(
        *,
        summary: MetricSummary,
        metric: MetricType,
        summary_name: str,
    ):
        """
        Return a metric result or fail with a clear error.
        """

        result = summary.metrics.get(
            metric
        )

        if result is None:
            raise ValueError(
                f"Metric {metric.value} is missing "
                f"from {summary_name} summary."
            )

        return result