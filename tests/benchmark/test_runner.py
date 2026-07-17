from app.adapters.dummy import DummyAdapter
from app.benchmark.runner import BenchmarkRunner
from app.domain.dataset import (
    Dataset,
    DatasetMetadata,
    Question,
)
from app.domain.enums import ModelType
from app.domain.evaluation import ModelConfig


def test_runner_evaluates_entire_dataset() -> None:
    config = ModelConfig(
        name="Dummy",
        version="1.0",
        model_type=ModelType.CUSTOM,
    )

    adapter = DummyAdapter(config)

    dataset = Dataset(
        metadata=DatasetMetadata(
            name="Test",
            description="Benchmark",
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

    runner = BenchmarkRunner(adapter)

    result = runner.run(dataset)

    assert len(result.sample_results) == 2


def test_runner_stores_model_config() -> None:
    config = ModelConfig(
        name="Dummy",
        version="1.0",
        model_type=ModelType.CUSTOM,
    )

    adapter = DummyAdapter(config)

    dataset = Dataset(
        metadata=DatasetMetadata(
            name="Test",
            description="Benchmark",
        ),
        questions=[],
    )

    runner = BenchmarkRunner(adapter)

    result = runner.run(dataset)

    assert result.model.name == "Dummy"


def test_runner_records_duration() -> None:
    config = ModelConfig(
        name="Dummy",
        version="1.0",
        model_type=ModelType.CUSTOM,
    )

    adapter = DummyAdapter(config)

    dataset = Dataset(
        metadata=DatasetMetadata(
            name="Test",
            description="Benchmark",
        ),
        questions=[],
    )

    runner = BenchmarkRunner(adapter)

    result = runner.run(dataset)

    assert result.duration_ms is not None
    assert result.duration_ms >= 0
