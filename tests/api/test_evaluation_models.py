import pytest
from pydantic import ValidationError

from app.api.models.evaluation import (
    CreateEvaluationRequest,
)
from app.domain.enums import ModelType


def test_create_evaluation_request() -> None:
    request = CreateEvaluationRequest(
        model={
            "name": "Dummy",
            "version": "1.0",
            "model_type": ModelType.CUSTOM,
            "prompt_version": "v1",
            "top_k": 5,
        },
        dataset={
            "name": "API Test Dataset",
            "description": (
                "Evaluation API request test"
            ),
            "version": "1.0",
            "questions": [
                {
                    "question": "What is AI?",
                    "expected_answer": (
                        "Artificial Intelligence"
                    ),
                }
            ],
        },
    )

    assert request.model.name == "Dummy"
    assert request.model.top_k == 5

    assert (
        request.dataset.name
        == "API Test Dataset"
    )

    assert len(
        request.dataset.questions
    ) == 1


def test_evaluation_request_requires_questions() -> None:
    with pytest.raises(ValidationError):
        CreateEvaluationRequest(
            model={
                "name": "Dummy",
                "version": "1.0",
                "model_type": ModelType.CUSTOM,
            },
            dataset={
                "name": "Empty Dataset",
                "questions": [],
            },
        )


def test_evaluation_request_rejects_invalid_top_k() -> None:
    with pytest.raises(ValidationError):
        CreateEvaluationRequest(
            model={
                "name": "Dummy",
                "version": "1.0",
                "model_type": ModelType.CUSTOM,
                "top_k": 0,
            },
            dataset={
                "name": "Test Dataset",
                "questions": [
                    {
                        "question": "What is AI?",
                        "expected_answer": (
                            "Artificial Intelligence"
                        ),
                    }
                ],
            },
        )