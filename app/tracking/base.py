from __future__ import annotations

from abc import ABC, abstractmethod
from types import TracebackType

from app.domain.evaluation import EvaluationResult
from app.domain.metrics import MetricSummary


class TrackingRun(ABC):
    """
    Represents an active experiment tracking run.
    """

    @property
    @abstractmethod
    def run_id(self) -> str:
        """
        Return the backend identifier for the tracking run.
        """
        raise NotImplementedError

    @abstractmethod
    def log_metrics(
        self,
        summary: MetricSummary,
    ) -> None:
        """
        Log evaluation metrics for the active run.
        """
        raise NotImplementedError

    @abstractmethod
    def log_evaluation(self) -> None:
        """
        Log the complete evaluation result as an artifact.
        """
        raise NotImplementedError

    @abstractmethod
    def __enter__(self) -> TrackingRun:
        """
        Enter the tracking run context.
        """
        raise NotImplementedError

    @abstractmethod
    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        """
        Exit the tracking run context.
        """
        raise NotImplementedError


class BaseExperimentTracker(ABC):
    """
    Base interface for experiment tracking backends.
    """

    @abstractmethod
    def start_run(
        self,
        evaluation: EvaluationResult,
    ) -> TrackingRun:
        """
        Create a new experiment tracking run.
        """
        raise NotImplementedError
