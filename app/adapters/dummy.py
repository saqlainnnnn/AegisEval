from __future__ import annotations

from app.adapters.base import BaseAdapter
from app.domain.dataset import Question
from app.domain.prediction import Prediction, RetrievedDocument


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
        retrieved_documents=[
            RetrievedDocument(
                id=doc.id,
                content=doc.content,
                metadata=doc.metadata,
            )
            for doc in question.expected_documents
        ],
    )
