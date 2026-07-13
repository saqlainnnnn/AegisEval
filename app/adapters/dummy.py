from __future__ import annotations

from app.adapters.base import BaseAdapter
from app.schemas.dataset import Question
from app.schemas.evaluation import Prediction


class DummyAdapter(BaseAdapter):
    """
    Simple adapter used for testing the benchmark pipeline.
    """

    def evaluate(
        self,
        question: Question,
    ) -> Prediction:

        return Prediction(
            question_id=question.id,
            answer=question.expected_answer,
            retrieved_sources=question.expected_sources,
            latency_ms=100.0,
        )