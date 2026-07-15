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


def test_accuracy_metric_returns_one() -> None:
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
            Question(
                question="Q2",
                expected_answer="A2",
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

    metric = AccuracyMetric().compute(evaluation)

    assert metric.metric == MetricType.ACCURACY
    assert metric.value == 1.0