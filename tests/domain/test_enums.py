from app.domain.enums import (
    EvaluationStatus,
    MetricType,
    ModelType,
)


def test_model_type_values() -> None:
    assert ModelType.RAG.value == "rag"
    assert ModelType.LLM.value == "llm"


def test_evaluation_status_values() -> None:
    assert EvaluationStatus.SUCCESS.value == "success"
    assert EvaluationStatus.FAILED.value == "failed"


def test_metric_type_values() -> None:
    assert MetricType.ACCURACY.value == "accuracy"
    assert MetricType.LATENCY.value == "latency"