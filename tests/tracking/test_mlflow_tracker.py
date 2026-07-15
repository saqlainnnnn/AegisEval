from pathlib import Path

import mlflow
import pytest

from app.adapters.dummy import DummyAdapter
from app.benchmark.runner import BenchmarkRunner
from app.domain.dataset import (
    Dataset,
    DatasetMetadata,
    Question,
)
from app.domain.enums import MetricType, ModelType
from app.domain.evaluation import ModelConfig
from app.metrics.accuracy import AccuracyMetric
from app.metrics.engine import MetricsEngine
from app.metrics.failure_rate import FailureRateMetric
from app.metrics.latency import LatencyMetric
from app.tracking.mlflow_tracker import MLflowTracker


def _build_evaluation():
    dataset = Dataset(
        metadata=DatasetMetadata(
            name="Tracking Test",
            description="MLflow integration test",
        ),
        questions=[
            Question(
                question="What is AI?",
                expected_answer="Artificial Intelligence",
            )
        ],
    )

    config = ModelConfig(
        name="Dummy",
        version="1.0",
        model_type=ModelType.CUSTOM,
        prompt_version="v1",
        top_k=5,
    )

    adapter = DummyAdapter(config)

    return BenchmarkRunner(adapter).run(dataset)


def test_mlflow_tracker_logs_run(
    tmp_path: Path,
) -> None:
    database_path = tmp_path / "mlflow.db"
    tracking_uri = f"sqlite:///{database_path.as_posix()}"

    evaluation = _build_evaluation()

    summary = MetricsEngine(
        [
            AccuracyMetric(),
            LatencyMetric(),
            FailureRateMetric(),
        ]
    ).compute(evaluation)

    tracker = MLflowTracker(
        experiment_name="AegisEval Test",
        tracking_uri=tracking_uri,
    )

    with tracker.start_run(evaluation) as run:
        run.log_metrics(summary)
        run.log_evaluation()

    experiment = mlflow.get_experiment_by_name(
        "AegisEval Test"
    )

    assert experiment is not None

    runs = mlflow.search_runs(
        experiment_ids=[
            experiment.experiment_id
        ]
    )

    assert len(runs) == 1

    logged_run = runs.iloc[0]

    run_id = logged_run["run_id"]

    artifact_path = mlflow.artifacts.download_artifacts(
        run_id=run_id,
        artifact_path="evaluation/evaluation.json",
    )

    assert Path(artifact_path).exists()

    assert logged_run["params.model_name"] == "Dummy"
    assert logged_run["params.model_version"] == "1.0"
    assert logged_run["params.prompt_version"] == "v1"
    assert logged_run["params.top_k"] == "5"

    assert logged_run[
        f"metrics.{MetricType.ACCURACY.value}"
    ] == 1.0

    assert logged_run[
        f"metrics.{MetricType.FAILURE_RATE.value}"
    ] == 0.0

    assert logged_run["status"] == "FINISHED"


def test_mlflow_tracker_marks_failed_run(
    tmp_path: Path,
) -> None:
    database_path = tmp_path / "failed_mlflow.db"
    tracking_uri = f"sqlite:///{database_path.as_posix()}"

    evaluation = _build_evaluation()

    tracker = MLflowTracker(
        experiment_name="AegisEval Failed Test",
        tracking_uri=tracking_uri,
    )

    with pytest.raises(
        RuntimeError,
        match="simulated tracking failure",
    ):
        with tracker.start_run(evaluation):
            raise RuntimeError(
                "simulated tracking failure"
            )

    experiment = mlflow.get_experiment_by_name(
        "AegisEval Failed Test"
    )

    assert experiment is not None

    runs = mlflow.search_runs(
        experiment_ids=[
            experiment.experiment_id
        ]
    )

    assert len(runs) == 1
    assert runs.iloc[0]["status"] == "FAILED"