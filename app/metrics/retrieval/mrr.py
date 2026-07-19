from __future__ import annotations

from app.domain.enums import MetricType
from app.domain.evaluation import EvaluationResult
from app.domain.metrics import MetricResult
from app.metrics.retrieval.base import BaseRetrievalMetric


class MRRMetric(BaseRetrievalMetric):
    """
    Computes Mean Reciprocal Rank (MRR).

    MRR = Average of reciprocal ranks of the first relevant document.
    """

    def compute(
        self,
        result: EvaluationResult,
    ) -> MetricResult:
        reciprocal_ranks: list[float] = []

        for sample in result.sample_results:
            expected = self._expected_ids(sample)
            retrieved = self._retrieved_ids(sample)

            reciprocal_rank = 0.0

            for rank, doc_id in enumerate(retrieved, start=1):
                if doc_id in expected:
                    reciprocal_rank = 1.0 / rank
                    break

            reciprocal_ranks.append(reciprocal_rank)

        score = (
            sum(reciprocal_ranks) / len(reciprocal_ranks)
            if reciprocal_ranks
            else 0.0
        )

        return MetricResult(
            metric=MetricType.MRR,
            value=score,
            metadata={
                "k": self.k,
            },
        )