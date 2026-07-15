import json
from pathlib import Path

import mlflow

from app.adapters.dummy import DummyAdapter
from app.benchmark.runner import BenchmarkRunner
from app.database.base import Base
from app.database.engine import create_database_engine
from app.database.models import (
    DatasetRecord,
    EvaluationRunRecord,
    MetricRecord,
    ModelRecord,
)
from app.database.session import create_session_factory
from app.datasets.factory import DatasetFactory
from app.domain.enums import MetricType, ModelType
from app.domain.evaluation import ModelConfig
from app.metrics.accuracy import AccuracyMetric
from app.metrics.engine import MetricsEngine
from app.metrics.failure_rate import FailureRateMetric
from app.metrics.latency import LatencyMetric
from app.services.evaluation import EvaluationService
from app.services.persistence import EvaluationPersistenceService
from app.tracking.mlflow_tracker import MLflowTracker


def test_complete_persisted_evaluation_pipeline(
    tmp_path: Path,
) -> None:
    # Create the evaluation dataset.

    dataset_path = tmp_path / "dataset.json"

    dataset_path.write_text(
        json.dumps(
            {
                "metadata": {
                    "name": "Persisted Integration Dataset",
                    "description": (
                        "Tests evaluation, tracking, "
                        "and persistence together"
                    ),
                    "version": "1.0",
                },
                "questions": [
                    {
                        "question": "What is AI?",
                        "expected_answer": (
                            "Artificial Intelligence"
                        ),
                    },
                    {
                        "question": "What is ML?",
                        "expected_answer": (
                            "Machine Learning"
                        ),
                    },
                ],
            }
        ),
        encoding="utf-8",
    )

    loader = DatasetFactory.create(
        dataset_path
    )

    dataset = loader.load(
        dataset_path
    )

    # Configure the evaluated system.

    config = ModelConfig(
        name="Dummy",
        version="1.0",
        model_type=ModelType.CUSTOM,
        prompt_version="v1",
        top_k=5,
    )

    adapter = DummyAdapter(config)

    runner = BenchmarkRunner(
        adapter
    )

    metrics_engine = MetricsEngine(
        [
            AccuracyMetric(),
            LatencyMetric(),
            FailureRateMetric(),
        ]
    )

    # Configure MLflow tracking.

    mlflow_database_path = (
        tmp_path / "mlflow.db"
    )

    tracking_uri = (
        f"sqlite:///"
        f"{mlflow_database_path.as_posix()}"
    )

    experiment_name = (
        "AegisEval Persistence Integration Test"
    )

    tracker = MLflowTracker(
        experiment_name=experiment_name,
        tracking_uri=tracking_uri,
    )

    # Configure the evaluation workflow.

    evaluation_service = EvaluationService(
        runner=runner,
        metrics_engine=metrics_engine,
        tracker=tracker,
    )

    # Execute evaluation and tracking.

    result = evaluation_service.evaluate(
        dataset
    )

    # Configure the application database.

    application_engine = (
        create_database_engine(
            "sqlite+pysqlite:///:memory:"
        )
    )

    Base.metadata.create_all(
        application_engine
    )

    session_factory = (
        create_session_factory(
            application_engine
        )
    )

    # Persist the completed evaluation.

    with session_factory() as session:
        persistence_service = (
            EvaluationPersistenceService(
                session
            )
        )

        stored_run = (
            persistence_service.save(
                dataset=dataset,
                result=result,
            )
        )

        # Verify application database.

        assert stored_run.id == str(
            result.evaluation.id
        )

        assert result.tracking_run_id is not None

        assert (
            stored_run.mlflow_run_id
            == result.tracking_run_id
        )

        assert stored_run.model.name == "Dummy"

        assert (
            stored_run.dataset.name
            == "Persisted Integration Dataset"
        )

        assert len(stored_run.metrics) == 3

        metric_types = {
            metric.metric_type
            for metric in stored_run.metrics
        }

        assert (
            MetricType.ACCURACY.value
            in metric_types
        )

        assert (
            MetricType.LATENCY.value
            in metric_types
        )

        assert (
            MetricType.FAILURE_RATE.value
            in metric_types
        )

        assert (
            session.query(ModelRecord).count()
            == 1
        )

        assert (
            session.query(DatasetRecord).count()
            == 1
        )

        assert (
            session.query(
                EvaluationRunRecord
            ).count()
            == 1
        )

        assert (
            session.query(MetricRecord).count()
            == 3
        )

    # Verify MLflow independently.

    experiment = (
        mlflow.get_experiment_by_name(
            experiment_name
        )
    )

    assert experiment is not None

    runs = mlflow.search_runs(
        experiment_ids=[
            experiment.experiment_id
        ]
    )

    assert len(runs) == 1

    logged_run = runs.iloc[0]

    assert (
    logged_run["run_id"]
    == result.tracking_run_id
    )

    assert (
        stored_run.mlflow_run_id
        == logged_run["run_id"]
    )
    assert logged_run["status"] == "FINISHED"

    assert (
        logged_run["params.model_name"]
        == "Dummy"
    )

    assert (
        logged_run[
            f"metrics.{MetricType.ACCURACY.value}"
        ]
        == 1.0
    )

    assert (
        logged_run[
            f"metrics.{MetricType.FAILURE_RATE.value}"
        ]
        == 0.0
    )

    artifact_path = (
        mlflow.artifacts.download_artifacts(
            run_id=logged_run["run_id"],
            artifact_path=(
                "evaluation/evaluation.json"
            ),
        )
    )

    assert Path(
        artifact_path
    ).exists()