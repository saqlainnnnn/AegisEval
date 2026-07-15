from __future__ import annotations

from app.domain.enums import MetricType
from app.domain.evaluation import EvaluationResult
from app.domain.metrics import MetricResult
from app.metrics.base import BaseMetric


class AccuracyMetric(BaseMetric):
    """
    Computes exact-match accuracy.
    """

    def compute(
        self,
        result: EvaluationResult,
    ) -> MetricResult:

        total = len(result.sample_results)

        if total == 0:
            return MetricResult(
                metric=MetricType.ACCURACY,
                value=0.0,
            )

        correct = 0

        for sample in result.sample_results:

            if sample.prediction is None:
                continue

            prediction = sample.prediction.answer.strip().lower()
            expected = sample.question.expected_answer.strip().lower()

            if prediction == expected:
                correct += 1

        return MetricResult(
            metric=MetricType.ACCURACY,
            value=correct / total,
            metadata={
                "correct": correct,
                "total": total,
            },
        )