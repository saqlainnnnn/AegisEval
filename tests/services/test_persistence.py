from app.adapters.dummy import DummyAdapter
from app.benchmark.runner import BenchmarkRunner
from app.database.base import Base
from app.database.engine import create_database_engine
from app.database.models import (
    DatasetRecord,
    EvaluationRunRecord,
    ModelRecord,
)
from app.database.session import create_session_factory
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
from app.services.evaluation import EvaluationService
from app.services.persistence import (
    EvaluationPersistenceService,
)


def _build_dataset() -> Dataset:
    return Dataset(
        metadata=DatasetMetadata(
            name="Persistence Test",
            description="Persistence service test dataset",
            version="1.0",
        ),
        questions=[
            Question(
                question="What is AI?",
                expected_answer="Artificial Intelligence",
            ),
            Question(
                question="What is ML?",
                expected_answer="Machine Learning",
            ),
        ],
    )


def _build_evaluation_service() -> EvaluationService:
    config = ModelConfig(
        name="Dummy",
        version="1.0",
        model_type=ModelType.CUSTOM,
        prompt_version="v1",
        top_k=5,
    )

    adapter = DummyAdapter(config)

    runner = BenchmarkRunner(adapter)

    metrics_engine = MetricsEngine(
        [
            AccuracyMetric(),
            LatencyMetric(),
            FailureRateMetric(),
        ]
    )

    return EvaluationService(
        runner=runner,
        metrics_engine=metrics_engine,
    )


def test_persist_complete_evaluation() -> None:
    engine = create_database_engine(
        "sqlite+pysqlite:///:memory:"
    )

    Base.metadata.create_all(engine)

    session_factory = create_session_factory(
        engine
    )

    dataset = _build_dataset()

    evaluation_service = (
        _build_evaluation_service()
    )

    result = evaluation_service.evaluate(
        dataset
    )

    with session_factory() as session:
        persistence_service = (
            EvaluationPersistenceService(
                session
            )
        )

        stored_run = persistence_service.save(
            dataset=dataset,
            result=result,
        )

        assert stored_run.id == str(
            result.evaluation.id
        )

        assert stored_run.mlflow_run_id is None

        assert stored_run.model.name == "Dummy"

        assert (
            stored_run.dataset.name
            == "Persistence Test"
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


def test_persistence_creates_model_and_dataset() -> None:
    engine = create_database_engine(
        "sqlite+pysqlite:///:memory:"
    )

    Base.metadata.create_all(engine)

    session_factory = create_session_factory(
        engine
    )

    dataset = _build_dataset()

    result = (
        _build_evaluation_service()
        .evaluate(dataset)
    )

    with session_factory() as session:
        service = EvaluationPersistenceService(
            session
        )

        service.save(
            dataset=dataset,
            result=result,
        )

        stored_models = session.query(
            ModelRecord
        ).all()

        stored_dataset = session.get(
            DatasetRecord,
            str(dataset.id),
        )

        stored_run = session.get(
            EvaluationRunRecord,
            str(result.evaluation.id),
        )

        assert len(stored_models) == 1
        assert stored_models[0].name == "Dummy"

        assert stored_dataset is not None
        assert stored_dataset.name == "Persistence Test"

        assert stored_run is not None


def test_persistence_reuses_existing_model_and_dataset() -> None:
    engine = create_database_engine(
        "sqlite+pysqlite:///:memory:"
    )

    Base.metadata.create_all(engine)

    session_factory = create_session_factory(
        engine
    )

    dataset = _build_dataset()

    evaluation_service = (
        _build_evaluation_service()
    )

    first_result = evaluation_service.evaluate(
        dataset
    )

    second_result = evaluation_service.evaluate(
        dataset
    )

    with session_factory() as session:
        service = EvaluationPersistenceService(
            session
        )

        service.save(
            dataset=dataset,
            result=first_result,
        )

        service.save(
            dataset=dataset,
            result=second_result,
        )

        models = session.query(
            ModelRecord
        ).all()

        datasets = session.query(
            DatasetRecord
        ).all()

        runs = session.query(
            EvaluationRunRecord
        ).all()

        assert len(models) == 1
        assert len(datasets) == 1
        assert len(runs) == 2