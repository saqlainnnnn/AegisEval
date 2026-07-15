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


def test_metrics_engine_runs_all_metrics() -> None:
    dataset = Dataset(
        metadata=DatasetMetadata(
            name="Test",
            description="Test dataset",
        ),
        questions=[
            Question(
                question="Q1",
                expected_answer="A1",
            )
        ],
    )

    adapter = DummyAdapter(
        ModelConfig(
            name="Dummy",
            version="1.0",
            model_type=ModelType.CUSTOM,
        )
    )

    evaluation = BenchmarkRunner(adapter).run(dataset)

    engine = MetricsEngine(
        [
            AccuracyMetric(),
            LatencyMetric(),
            FailureRateMetric(),
        ]
    )

    summary = engine.compute(evaluation)

    assert len(summary.metrics) == 3

    assert MetricType.ACCURACY in summary.metrics
    assert MetricType.LATENCY in summary.metrics
    assert MetricType.FAILURE_RATE in summary.metrics


def test_metrics_engine_empty_metrics() -> None:
    dataset = Dataset(
        metadata=DatasetMetadata(
            name="Test",
            description="Test dataset",
        ),
        questions=[],
    )

    adapter = DummyAdapter(
        ModelConfig(
            name="Dummy",
            version="1.0",
            model_type=ModelType.CUSTOM,
        )
    )

    evaluation = BenchmarkRunner(adapter).run(dataset)

    engine = MetricsEngine([])

    summary = engine.compute(evaluation)

    assert summary.metrics == {}