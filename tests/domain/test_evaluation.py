from app.domain.dataset import Question
from app.domain.enums import EvaluationStatus, ModelType
from app.domain.evaluation import (
    EvaluationResult,
    EvaluationSampleResult,
    ModelConfig,
)
from app.domain.prediction import Prediction


def test_model_config_creation() -> None:
    config = ModelConfig(
        name="Dummy",
        version="1.0",
        model_type=ModelType.LLM,
    )

    assert config.name == "Dummy"
    assert config.model_type == ModelType.LLM


def test_sample_result_defaults() -> None:
    question = Question(
        question="What is AI?",
        expected_answer="Artificial Intelligence",
    )

    result = EvaluationSampleResult(
        question=question,
    )

    assert result.status == EvaluationStatus.SUCCESS
    assert result.prediction is None
    assert result.error is None


def test_evaluation_result_creation() -> None:
    config = ModelConfig(
        name="Dummy",
        version="1.0",
        model_type=ModelType.LLM,
    )

    result = EvaluationResult(
        model=config,
        dataset_id="dataset-1",
    )

    assert result.sample_results == []