from __future__ import annotations

from types import TracebackType
from typing import Any

import mlflow

from app.domain.evaluation import EvaluationResult
from app.domain.metrics import MetricSummary
from app.tracking.base import BaseExperimentTracker, TrackingRun


class MLflowTrackingRun(TrackingRun):
    """
    Represents an active MLflow experiment run.
    """

    def __init__(
        self,
        evaluation: EvaluationResult,
        experiment_name: str,
    ) -> None:
        self._evaluation = evaluation
        self._experiment_name = experiment_name
        self._active_run: mlflow.ActiveRun | None = None

    def __enter__(self) -> MLflowTrackingRun:
        mlflow.set_experiment(self._experiment_name)

        self._active_run = mlflow.start_run()

        self._log_evaluation_parameters()

        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        if self._active_run is not None:
            mlflow.end_run(
                status=(
                    "FAILED"
                    if exc_type is not None
                    else "FINISHED"
                )
            )

            self._active_run = None

    def log_metrics(
        self,
        summary: MetricSummary,
    ) -> None:
        """
        Log all computed metrics to MLflow.
        """

        self._ensure_active()

        for metric_type, metric_result in summary.metrics.items():
            mlflow.log_metric(
                key=metric_type.value,
                value=metric_result.value,
            )

    def log_evaluation(self) -> None:
        """
        Log the complete evaluation result as a JSON artifact.
        """

        self._ensure_active()

        mlflow.log_dict(
            dictionary=self._evaluation.model_dump(
                mode="json"
            ),
            artifact_file="evaluation/evaluation.json",
        )

    def _log_evaluation_parameters(self) -> None:
        """
        Log evaluation and model configuration parameters.
        """

        model = self._evaluation.model

        parameters: dict[str, Any] = {
            "model_name": model.name,
            "model_version": model.version,
            "model_type": model.model_type.value,
            "dataset_id": self._evaluation.dataset_id,
        }

        optional_parameters = {
            "embedding_model": model.embedding_model,
            "prompt_version": model.prompt_version,
            "retriever": model.retriever,
            "chunk_size": model.chunk_size,
            "top_k": model.top_k,
        }

        parameters.update(
            {
                key: value
                for key, value in optional_parameters.items()
                if value is not None
            }
        )

        mlflow.log_params(parameters)

    def _ensure_active(self) -> None:
        """
        Ensure logging happens inside an active run.
        """

        if self._active_run is None:
            raise RuntimeError(
                "MLflow tracking run is not active. "
                "Use the tracking run as a context manager."
            )


class MLflowTracker(BaseExperimentTracker):
    """
    MLflow implementation of the experiment tracking interface.
    """

    def __init__(
        self,
        experiment_name: str = "AegisEval",
        tracking_uri: str | None = None,
    ) -> None:
        self._experiment_name = experiment_name

        if tracking_uri is not None:
            mlflow.set_tracking_uri(tracking_uri)

    def start_run(
        self,
        evaluation: EvaluationResult,
    ) -> TrackingRun:
        return MLflowTrackingRun(
            evaluation=evaluation,
            experiment_name=self._experiment_name,
        )