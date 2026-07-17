import json
from pathlib import Path

import mlflow

from app.adapters.dummy import DummyAdapter
from app.benchmark.runner import BenchmarkRunner
from app.datasets.factory import DatasetFactory
from app.domain.enums import MetricType, ModelType
from app.domain.evaluation import ModelConfig
from app.metrics.accuracy import AccuracyMetric
from app.metrics.engine import MetricsEngine
from app.metrics.failure_rate import FailureRateMetric
from app.metrics.latency import LatencyMetric
from app.services.evaluation import EvaluationService
from app.tracking.mlflow_tracker import MLflowTracker


def test_complete_tracked_evaluation_pipeline(
    tmp_path: Path,
) -> None:
    # -----------------------------
    # Arrange: create dataset file
    # -----------------------------

    dataset_path = tmp_path / "evaluation_dataset.json"

    dataset_path.write_text(
        json.dumps(
            {
                "metadata": {
                    "name": "Tracked Integration Dataset",
                    "description": (
                        "Tests the complete tracked " "evaluation pipeline"
                    ),
                    "version": "1.0",
                },
                "questions": [
                    {
                        "question": "What is AI?",
                        "expected_answer": ("Artificial Intelligence"),
                    },
                    {
                        "question": "What is ML?",
                        "expected_answer": ("Machine Learning"),
                    },
                ],
            }
        ),
        encoding="utf-8",
    )

    # -----------------------------
    # Arrange: load dataset
    # -----------------------------

    loader = DatasetFactory.create(dataset_path)
    dataset = loader.load(dataset_path)

    # -----------------------------
    # Arrange: configure AI system
    # -----------------------------

    config = ModelConfig(
        name="Dummy",
        version="1.0",
        model_type=ModelType.CUSTOM,
        prompt_version="v1",
        top_k=5,
    )

    adapter = DummyAdapter(config)

    # -----------------------------
    # Arrange: configure pipeline
    # -----------------------------

    runner = BenchmarkRunner(adapter)

    metrics_engine = MetricsEngine(
        [
            AccuracyMetric(),
            LatencyMetric(),
            FailureRateMetric(),
        ]
    )

    database_path = tmp_path / "mlflow.db"

    tracking_uri = f"sqlite:///{database_path.as_posix()}"

    experiment_name = "AegisEval Integration Test"

    tracker = MLflowTracker(
        experiment_name=experiment_name,
        tracking_uri=tracking_uri,
    )

    service = EvaluationService(
        runner=runner,
        metrics_engine=metrics_engine,
        tracker=tracker,
    )

    # -----------------------------
    # Act
    # -----------------------------

    result = service.evaluate(dataset)

    # -----------------------------
    # Assert: application result
    # -----------------------------

    assert len(result.evaluation.sample_results) == 2

    assert result.metrics.metrics[MetricType.ACCURACY].value == 1.0

    assert result.metrics.metrics[MetricType.FAILURE_RATE].value == 0.0

    # -----------------------------
    # Assert: MLflow experiment
    # -----------------------------

    experiment = mlflow.get_experiment_by_name(experiment_name)

    assert experiment is not None

    runs = mlflow.search_runs(experiment_ids=[experiment.experiment_id])

    assert len(runs) == 1

    logged_run = runs.iloc[0]

    # -----------------------------
    # Assert: MLflow parameters
    # -----------------------------

    assert logged_run["params.model_name"] == "Dummy"

    assert logged_run["params.model_version"] == "1.0"

    assert logged_run["params.prompt_version"] == "v1"

    assert logged_run["params.top_k"] == "5"

    assert logged_run["params.dataset_id"] == str(dataset.id)

    # -----------------------------
    # Assert: MLflow metrics
    # -----------------------------

    assert logged_run[f"metrics.{MetricType.ACCURACY.value}"] == 1.0

    assert logged_run[f"metrics.{MetricType.FAILURE_RATE.value}"] == 0.0

    assert logged_run[f"metrics.{MetricType.LATENCY.value}"] >= 0

    assert logged_run["status"] == "FINISHED"

    # -----------------------------
    # Assert: evaluation artifact
    # -----------------------------

    run_id = logged_run["run_id"]

    artifact_path = mlflow.artifacts.download_artifacts(
        run_id=run_id,
        artifact_path=("evaluation/evaluation.json"),
    )

    artifact = Path(artifact_path)

    assert artifact.exists()

    artifact_data = json.loads(artifact.read_text(encoding="utf-8"))

    assert artifact_data["model"]["name"] == "Dummy"

    assert artifact_data["dataset_id"] == str(dataset.id)

    assert len(artifact_data["sample_results"]) == 2
