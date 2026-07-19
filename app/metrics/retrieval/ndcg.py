from __future__ import annotations

import math

from app.domain.enums import MetricType
from app.domain.evaluation import EvaluationResult
from app.domain.metrics import MetricResult
from app.metrics.retrieval.base import BaseRetrievalMetric


class NDCGMetric(BaseRetrievalMetric):
    """
    Normalized Discounted Cumulative Gain.
    """

    def compute(
        self,
        result: EvaluationResult,
    ) -> MetricResult:
        ndcgs: list[float] = []

        for sample in result.sample_results:
            if sample.prediction is None:
                ndcgs.append(0.0)
                continue

            relevance = {
                doc.id: doc.relevance
                for doc in sample.question.expected_documents
            }

            retrieved = sample.prediction.retrieved_documents[: self.k]

            dcg = 0.0

            for rank, doc in enumerate(retrieved, start=1):
                rel = relevance.get(doc.id, 0.0)

                dcg += (
                    (2**rel - 1)
                    / math.log2(rank + 1)
                )

            ideal = sorted(
                relevance.values(),
                reverse=True,
            )[: self.k]

            idcg = 0.0

            for rank, rel in enumerate(ideal, start=1):
                idcg += (
                    (2**rel - 1)
                    / math.log2(rank + 1)
                )

            if idcg == 0:
                ndcgs.append(0.0)
            else:
                ndcgs.append(dcg / idcg)

        score = (
            sum(ndcgs) / len(ndcgs)
            if ndcgs
            else 0.0
        )

        return MetricResult(
            metric=MetricType.NDCG,
            value=score,
            metadata={
                "k": self.k,
            },
        )