from __future__ import annotations

from abc import ABC, abstractmethod

from app.domain.dataset import Question
from app.domain.evaluation import ModelConfig
from app.domain.prediction import Prediction


class BaseAdapter(ABC):
    """
    Abstract interface for AI systems evaluated by AegisEval.

    Every AI application (RAG, Agent, LLM, Vision, etc.)
    should implement this interface.
    """

    def __init__(self, config: ModelConfig) -> None:
        self.config = config

    @abstractmethod
    def evaluate(
        self,
        question: Question,
    ) -> Prediction:
        """
        Evaluate a single question.

        Parameters
        ----------
        question
            Evaluation sample.

        Returns
        -------
        Prediction
            Model prediction.
        """
        raise NotImplementedError