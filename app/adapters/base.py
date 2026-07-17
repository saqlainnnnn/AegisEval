from __future__ import annotations

from abc import ABC, abstractmethod

from app.domain.dataset import Question
from app.domain.evaluation import ModelConfig
from app.domain.prediction import Prediction


class BaseAdapter(ABC):
    """
    Base interface for all AI system adapters.
    """

    def __init__(
        self,
        config: ModelConfig,
    ) -> None:
        self._config = config

    @property
    def config(
        self,
    ) -> ModelConfig:
        return self._config

    @abstractmethod
    def evaluate(
        self,
        question: Question,
    ) -> Prediction:
        """
        Generate a prediction for a question.
        """
        raise NotImplementedError
