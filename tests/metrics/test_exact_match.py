from app.adapters.dummy import DummyAdapter
from app.benchmark.runner import BenchmarkRunner
from app.domain.dataset import (
    Dataset,
    DatasetMetadata,
    Question,
)
from app.domain.enums import MetricType, ModelType
from app.domain.evaluation import ModelConfig
from app.metrics.generation.exact_match import ExactMatchMetric


def test_exact_match_perfect() -> None:
    dataset = Dataset(
        metadata=DatasetMetadata(
            name="Test",
            description="Test",
        ),
        questions=[
            Question(
                question="Capital?",
                expected_answer="Paris",
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

    metric = ExactMatchMetric().compute(evaluation)

    assert metric.metric == MetricType.EXACT_MATCH
    assert metric.value == 1.0


def test_exact_match_case_insensitive() -> None:
    dataset = Dataset(
        metadata=DatasetMetadata(
            name="Test",
            description="Test",
        ),
        questions=[
            Question(
                question="Capital?",
                expected_answer="PARIS",
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

    metric = ExactMatchMetric().compute(evaluation)

    assert metric.value == 1.0


def test_exact_match_punctuation() -> None:
    dataset = Dataset(
        metadata=DatasetMetadata(
            name="Test",
            description="Test",
        ),
        questions=[
            Question(
                question="Capital?",
                expected_answer="Paris.",
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

    metric = ExactMatchMetric().compute(evaluation)

    assert metric.value == 1.0


def test_exact_match_failure() -> None:
    dataset = Dataset(
        metadata=DatasetMetadata(
            name="Test",
            description="Test",
        ),
        questions=[
            Question(
                question="Capital?",
                expected_answer="London",
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

    evaluation.sample_results[0].prediction.answer = "Paris"

    metric = ExactMatchMetric().compute(evaluation)

    assert metric.value == 0.0