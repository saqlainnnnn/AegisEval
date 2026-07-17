from app.adapters.dummy import DummyAdapter
from app.benchmark.runner import BenchmarkRunner
from app.domain.dataset import (
    Dataset,
    DatasetMetadata,
    Question,
)
from app.domain.enums import MetricType, ModelType
from app.domain.evaluation import ModelConfig
from app.metrics.failure_rate import FailureRateMetric


def test_failure_rate_metric_returns_zero() -> None:
    dataset = Dataset(
        metadata=DatasetMetadata(
            name="Test",
            description="Test dataset",
        ),
        questions=[
            Question(
                question="Q1",
                expected_answer="A1",
            ),
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

    metric = FailureRateMetric().compute(evaluation)

    assert metric.metric == MetricType.FAILURE_RATE
    assert metric.value == 0.0
    assert metric.higher_is_better is False
