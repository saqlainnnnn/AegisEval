from __future__ import annotations

from types import TracebackType

from app.adapters.dummy import DummyAdapter
from app.benchmark.runner import BenchmarkRunner
from app.domain.dataset import (
    Dataset,
    DatasetMetadata,
    Question,
)
from app.domain.enums import MetricType, ModelType
from app.domain.evaluation import (
    EvaluationResult,
    ModelConfig,
)
from app.domain.metrics import MetricSummary
from app.metrics.accuracy import AccuracyMetric
from app.metrics.engine import MetricsEngine
from app.metrics.failure_rate import FailureRateMetric
from app.metrics.latency import LatencyMetric
from app.services.evaluation import EvaluationService
from app.tracking.base import (
    BaseExperimentTracker,
    TrackingRun,
)


class FakeTrackingRun(TrackingRun):
    """
    In-memory tracking run used to test service orchestration.
    """

    def __init__(self) -> None:
        self.metrics: MetricSummary | None = None
        self.evaluation_logged = False
        self.entered = False
        self.exited = False

    def __enter__(self) -> FakeTrackingRun:
        self.entered = True
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self.exited = True

    def log_metrics(
        self,
        summary: MetricSummary,
    ) -> None:
        self.metrics = summary

    def log_evaluation(self) -> None:
        self.evaluation_logged = True

    @property
    def run_id(self) -> str:
        return "fake-run-123"


class FakeExperimentTracker(BaseExperimentTracker):
    """
    In-memory experiment tracker used to verify that the
    evaluation service interacts with the tracking contract.
    """

    def __init__(self) -> None:
        self.evaluation: EvaluationResult | None = None
        self.run = FakeTrackingRun()

    def start_run(
        self,
        evaluation: EvaluationResult,
    ) -> TrackingRun:
        self.evaluation = evaluation
        return self.run


def _build_dataset() -> Dataset:
    return Dataset(
        metadata=DatasetMetadata(
            name="Service Test",
            description="Evaluation service test dataset",
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


def _build_service(
    tracker: BaseExperimentTracker | None = None,
) -> EvaluationService:
    config = ModelConfig(
        name="Dummy",
        version="1.0",
        model_type=ModelType.CUSTOM,
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
        tracker=tracker,
    )


def test_evaluation_service_runs_complete_workflow() -> None:
    service = _build_service()
    dataset = _build_dataset()

    result = service.evaluate(dataset)

    assert len(
        result.evaluation.sample_results
    ) == 2

    assert (
        result.metrics.metrics[
            MetricType.ACCURACY
        ].value
        == 1.0
    )

    assert (
        result.metrics.metrics[
            MetricType.FAILURE_RATE
        ].value
        == 0.0
    )

    assert (
        result.metrics.metrics[
            MetricType.LATENCY
        ].value
        >= 0
    )


def test_evaluation_service_returns_model_config() -> None:
    service = _build_service()
    dataset = _build_dataset()

    result = service.evaluate(dataset)

    assert result.evaluation.model.name == "Dummy"
    assert result.evaluation.model.version == "1.0"


def test_evaluation_service_tracks_evaluation() -> None:
    tracker = FakeExperimentTracker()

    service = _build_service(
        tracker=tracker,
    )

    dataset = _build_dataset()

    result = service.evaluate(dataset)

    assert tracker.evaluation == result.evaluation

    assert tracker.run.entered is True
    assert tracker.run.exited is True

    assert tracker.run.metrics == result.metrics

    assert tracker.run.evaluation_logged is True
    assert result.tracking_run_id == "fake-run-123"