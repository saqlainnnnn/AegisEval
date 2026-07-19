from __future__ import annotations

from collections import Counter

from app.domain.enums import MetricType
from app.domain.evaluation import EvaluationResult
from app.domain.metrics import MetricResult
from app.metrics.generation.base import BaseGenerationMetric


class F1Metric(BaseGenerationMetric):
    """
    Computes token-level F1 score.
    """

    def compute(
        self,
        result: EvaluationResult,
    ) -> MetricResult:
        scores: list[float] = []

        for sample in result.sample_results:
            prediction = self._prediction_tokens(sample)
            reference = self._reference_tokens(sample)

            prediction_counter = Counter(prediction)
            reference_counter = Counter(reference)

            common = prediction_counter & reference_counter
            overlap = sum(common.values())

            if overlap == 0:
                scores.append(0.0)
                continue

            precision = overlap / len(prediction)
            recall = overlap / len(reference)

            f1 = (
                2 * precision * recall
                / (precision + recall)
            )

            scores.append(f1)

        score = (
            sum(scores) / len(scores)
            if scores
            else 0.0
        )

        return MetricResult(
            metric=MetricType.F1,
            value=score,
        )