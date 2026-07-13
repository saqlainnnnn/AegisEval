from app.adapters.dummy import DummyAdapter
from app.benchmark.executor import EvaluationExecutor
from app.domain.dataset import Question
from app.domain.enums import EvaluationStatus, ModelType
from app.domain.evaluation import ModelConfig


def test_executor_runs_successfully() -> None:
    adapter = DummyAdapter(
        ModelConfig(
            name="Dummy",
            version="1.0",
            model_type=ModelType.CUSTOM,
        )
    )

    executor = EvaluationExecutor(adapter)

    result = executor.execute(
        Question(
            question="What is AI?",
            expected_answer="Artificial Intelligence",
        )
    )

    assert result.status == EvaluationStatus.SUCCESS
    assert result.prediction is not None
    assert result.latency_ms >= 0