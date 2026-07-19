from app.adapters.dummy import DummyAdapter
from app.benchmark.runner import BenchmarkRunner
from app.domain.dataset import Dataset, DatasetMetadata, Question
from app.domain.enums import MetricType, ModelType
from app.domain.evaluation import ModelConfig
from app.metrics.generation.f1 import F1Metric


def _evaluation(expected: str):
    dataset = Dataset(
        metadata=DatasetMetadata(
            name="Test",
            description="Test",
        ),
        questions=[
            Question(
                question="Q",
                expected_answer=expected,
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

    return BenchmarkRunner(adapter).run(dataset)


def test_f1_perfect() -> None:
    evaluation = _evaluation("the capital of france")

    metric = F1Metric().compute(evaluation)

    assert metric.metric == MetricType.F1
    assert metric.value == 1.0


def test_f1_partial_overlap() -> None:
    evaluation = _evaluation("capital of france")

    evaluation.sample_results[
        0
    ].prediction.answer = "the capital of france"

    metric = F1Metric().compute(evaluation)

    assert metric.value == 0.8571428571428571


def test_f1_no_overlap() -> None:
    evaluation = _evaluation("paris")

    evaluation.sample_results[
        0
    ].prediction.answer = "london"

    metric = F1Metric().compute(evaluation)

    assert metric.value == 0.0


def test_f1_case_insensitive() -> None:
    evaluation = _evaluation("PARIS")

    evaluation.sample_results[
        0
    ].prediction.answer = "paris"

    metric = F1Metric().compute(evaluation)

    assert metric.value == 1.0