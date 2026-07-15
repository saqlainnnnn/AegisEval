from __future__ import annotations

from app.domain.enums import EvaluationStatus, MetricType
from app.domain.evaluation import EvaluationResult
from app.domain.metrics import MetricResult
from app.metrics.base import BaseMetric


class FailureRateMetric(BaseMetric):
    """
    Computes the percentage of failed evaluations.
    """

    def compute(
        self,
        result: EvaluationResult,
    ) -> MetricResult:

        total = len(result.sample_results)

        if total == 0:
            return MetricResult(
                metric=MetricType.FAILURE_RATE,
                value=0.0,
                higher_is_better=False,
            )

        failures = sum(
            1
            for sample in result.sample_results
            if sample.status == EvaluationStatus.FAILED
        )

        return MetricResult(
            metric=MetricType.FAILURE_RATE,
            value=failures / total,
            higher_is_better=False,
            metadata={
                "failures": failures,
                "total": total,
            },
        )