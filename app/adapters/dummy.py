from __future__ import annotations

from app.adapters.base import BaseAdapter
from app.domain.dataset import Question
from app.domain.prediction import Prediction


class DummyAdapter(BaseAdapter):
    """
    Simple adapter used for testing the evaluation pipeline.
    """

    def evaluate(
        self,
        question: Question,
    ) -> Prediction:
        return Prediction(
            answer=question.expected_answer,
            retrieved_sources=question.expected_sources,
        )
