from __future__ import annotations

import pytest

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
    RegressionStatus,
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
from app.persistence.repositories import (
    EvaluationRunRepository,
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
from app.services.regression import (
    RegressionService,
)


def _build_dataset(
    name: str,
) -> Dataset:
    return Dataset(
        metadata=DatasetMetadata(
            name=name,
            description=(
                "Regression service test dataset"
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


def _build_regression_service(
    session,
) -> RegressionService:
    return RegressionService(
        evaluation_repository=(
            EvaluationRunRepository(
                session
            )
        ),
        regression_repository=(
            RegressionRunRepository(
                session
            )
        ),
        regression_engine=(
            RegressionEngine(
                RegressionThresholdPolicy()
            )
        ),
    )


def test_compare_persisted_evaluation_runs() -> None:
    engine = create_database_engine(
        "sqlite+pysqlite:///:memory:"
    )

    Base.metadata.create_all(
        engine
    )

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

        regression_repository = (
            RegressionRunRepository(
                session
            )
        )

        service = RegressionService(
            evaluation_repository=(
                EvaluationRunRepository(
                    session
                )
            ),
            regression_repository=(
                regression_repository
            ),
            regression_engine=(
                RegressionEngine(
                    RegressionThresholdPolicy()
                )
            ),
        )

        service_result = service.compare(
            baseline_run_id=str(
                baseline_result.evaluation.id
            ),
            candidate_run_id=str(
                candidate_result.evaluation.id
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
                        ThresholdType.ABSOLUTE
                    ),
                    value=1000.0,
                ),
            ],
        )

        result = service_result.result

        assert service_result.regression_id

        assert (
            result.status
            == RegressionStatus.PASSED
        )

        stored_regressions = (
            regression_repository.list_all()
        )

        assert len(
            stored_regressions
        ) == 1

        stored = stored_regressions[0]

        assert (
            stored.id
            == service_result.regression_id
        )

        assert (
            stored.baseline_run_id
            == str(
                baseline_result.evaluation.id
            )
        )

        assert (
            stored.candidate_run_id
            == str(
                candidate_result.evaluation.id
            )
        )

        assert len(
            stored.comparisons
        ) == 2


def test_compare_rejects_missing_baseline() -> None:
    engine = create_database_engine(
        "sqlite+pysqlite:///:memory:"
    )

    Base.metadata.create_all(
        engine
    )

    session_factory = (
        create_session_factory(
            engine
        )
    )

    with session_factory() as session:
        service = (
            _build_regression_service(
                session
            )
        )

        with pytest.raises(
            ValueError,
            match="Baseline evaluation run",
        ):
            service.compare(
                baseline_run_id=(
                    "missing-baseline"
                ),
                candidate_run_id=(
                    "missing-candidate"
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
                    )
                ],
            )


def test_compare_rejects_missing_candidate() -> None:
    engine = create_database_engine(
        "sqlite+pysqlite:///:memory:"
    )

    Base.metadata.create_all(
        engine
    )

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

    baseline_result = (
        evaluation_service.evaluate(
            baseline_dataset
        )
    )

    with session_factory() as session:
        EvaluationPersistenceService(
            session
        ).save(
            dataset=baseline_dataset,
            result=baseline_result,
        )

        service = (
            _build_regression_service(
                session
            )
        )

        with pytest.raises(
            ValueError,
            match="Candidate evaluation run",
        ):
            service.compare(
                baseline_run_id=str(
                    baseline_result.evaluation.id
                ),
                candidate_run_id=(
                    "missing-candidate"
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
                    )
                ],
            )