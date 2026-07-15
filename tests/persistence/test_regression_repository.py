from app.adapters.dummy import DummyAdapter
from app.benchmark.runner import BenchmarkRunner
from app.database.base import Base
from app.database.engine import (
    create_database_engine,
)
from app.database.session import (
    create_session_factory,
)
from app.domain.dataset import (
    Dataset,
    DatasetMetadata,
    Question,
)
from app.domain.enums import (
    MetricType,
    ModelType,
    ThresholdType,
)
from app.domain.evaluation import ModelConfig
from app.domain.regression import (
    RegressionThreshold,
)
from app.metrics.accuracy import AccuracyMetric
from app.metrics.engine import MetricsEngine
from app.metrics.failure_rate import (
    FailureRateMetric,
)
from app.metrics.latency import LatencyMetric
from app.persistence.repositories.regression import (
    RegressionRunRepository,
)
from app.regression.engine import RegressionEngine
from app.regression.policy import (
    RegressionThresholdPolicy,
)
from app.services.evaluation import EvaluationService
from app.services.persistence import (
    EvaluationPersistenceService,
)


def _build_dataset(
    name: str,
) -> Dataset:
    return Dataset(
        metadata=DatasetMetadata(
            name=name,
            description=(
                "Regression persistence test dataset"
            ),
            version="1.0",
        ),
        questions=[
            Question(
                question="What is AI?",
                expected_answer=(
                    "Artificial Intelligence"
                ),
            )
        ],
    )


def _build_evaluation_service(
) -> EvaluationService:
    config = ModelConfig(
        name="Dummy",
        version="1.0",
        model_type=ModelType.CUSTOM,
    )

    adapter = DummyAdapter(
        config
    )

    return EvaluationService(
        runner=BenchmarkRunner(
            adapter
        ),
        metrics_engine=MetricsEngine(
            [
                AccuracyMetric(),
                LatencyMetric(),
                FailureRateMetric(),
            ]
        ),
    )


def test_save_and_get_regression_result() -> None:
    engine = create_database_engine(
        "sqlite+pysqlite:///:memory:"
    )

    Base.metadata.create_all(engine)

    session_factory = (
        create_session_factory(
            engine
        )
    )

    evaluation_service = (
        _build_evaluation_service()
    )

    baseline_dataset = _build_dataset(
        "Baseline Dataset"
    )

    candidate_dataset = _build_dataset(
        "Candidate Dataset"
    )

    baseline_result = (
        evaluation_service.evaluate(
            baseline_dataset
        )
    )

    candidate_result = (
        evaluation_service.evaluate(
            candidate_dataset
        )
    )

    with session_factory() as session:
        persistence_service = (
            EvaluationPersistenceService(
                session
            )
        )

        persistence_service.save(
            dataset=baseline_dataset,
            result=baseline_result,
        )

        persistence_service.save(
            dataset=candidate_dataset,
            result=candidate_result,
        )

        regression_result = RegressionEngine(
            RegressionThresholdPolicy()
        ).compare(
            baseline_run_id=str(
                baseline_result.evaluation.id
            ),
            candidate_run_id=str(
                candidate_result.evaluation.id
            ),
            baseline=(
                baseline_result.metrics
            ),
            candidate=(
                candidate_result.metrics
            ),
            thresholds=[
                RegressionThreshold(
                    metric=(
                        MetricType.ACCURACY
                    ),
                    threshold_type=(
                        ThresholdType.ABSOLUTE
                    ),
                    value=0.05,
                ),
                RegressionThreshold(
                    metric=(
                        MetricType.LATENCY
                    ),
                    threshold_type=(
                        ThresholdType.RELATIVE
                    ),
                    value=0.50,
                ),
            ],
        )

        repository = (
            RegressionRunRepository(
                session
            )
        )

        stored = repository.save(
            regression_result
        )

        regression_id = stored.id

        loaded = repository.get(
            regression_id
        )

        assert loaded is not None

        assert (
            loaded.baseline_run_id
            == str(
                baseline_result.evaluation.id
            )
        )

        assert (
            loaded.candidate_run_id
            == str(
                candidate_result.evaluation.id
            )
        )

        assert (
            loaded.status
            == regression_result.status.value
        )

        assert len(
            loaded.comparisons
        ) == 2

        metric_types = {
            comparison.metric_type
            for comparison
            in loaded.comparisons
        }

        assert (
            MetricType.ACCURACY.value
            in metric_types
        )

        assert (
            MetricType.LATENCY.value
            in metric_types
        )