from __future__ import annotations

from app.domain.enums import MetricType
from app.domain.evaluation import EvaluationResult
from app.domain.metrics import MetricResult
from app.metrics.retrieval.base import BaseRetrievalMetric


class MAPMetric(BaseRetrievalMetric):
    """
    Mean Average Precision (MAP).
    """

    def compute(
        self,
        result: EvaluationResult,
    ) -> MetricResult:
        average_precisions: list[float] = []

        for sample in result.sample_results:
            expected = self._expected_ids(sample)
            retrieved = self._retrieved_ids(sample)

            if not expected:
                average_precisions.append(1.0)
                continue

            hits = 0
            precision_sum = 0.0

            for rank, doc_id in enumerate(retrieved, start=1):
                if doc_id in expected:
                    hits += 1
                    precision_sum += hits / rank

            average_precisions.append(
                precision_sum / len(expected)
            )

        score = (
            sum(average_precisions) / len(average_precisions)
            if average_precisions
            else 0.0
        )

        return MetricResult(
            metric=MetricType.MAP,
            value=score,
            metadata={
                "k": self.k,
            },
        )