from app.domain.dataset import (
    Dataset,
    DatasetMetadata,
    Question,
)


def test_question_defaults() -> None:
    question = Question(
        question="What is AI?",
        expected_answer="Artificial Intelligence",
    )

    assert question.expected_documents == []
    assert question.tags == []
    assert question.metadata == {}


def test_dataset_metadata() -> None:
    metadata = DatasetMetadata(
        name="Medical QA",
        description="Medical benchmark",
    )

    assert metadata.name == "Medical QA"


def test_dataset_creation() -> None:
    metadata = DatasetMetadata(
        name="Medical QA",
        description="Medical benchmark",
    )

    question = Question(
        question="What is AI?",
        expected_answer="Artificial Intelligence",
    )

    dataset = Dataset(
        metadata=metadata,
        questions=[question],
    )

    assert len(dataset.questions) == 1
