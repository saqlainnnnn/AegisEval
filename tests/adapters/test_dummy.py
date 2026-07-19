from app.adapters.dummy import DummyAdapter
from app.domain.dataset import Question
from app.domain.enums import ModelType
from app.domain.evaluation import ModelConfig
from app.domain.dataset import RelevantDocument


def test_dummy_adapter_returns_expected_answer() -> None:
    config = ModelConfig(
        name="Dummy",
        version="1.0",
        model_type=ModelType.CUSTOM,
    )

    adapter = DummyAdapter(config)

    question = question = Question(
    question="What is AI?",
    expected_answer="Artificial Intelligence",
    expected_documents=[
        RelevantDocument(
            id="paper1",
            content="paper1",
        ),
        RelevantDocument(
            id="paper2",
            content="paper2",
        ),
    ],
)

    prediction = adapter.evaluate(question)

    assert prediction.answer == "Artificial Intelligence"


def test_dummy_adapter_returns_sources() -> None:
    config = ModelConfig(
        name="Dummy",
        version="1.0",
        model_type=ModelType.CUSTOM,
    )

    adapter = DummyAdapter(config)

    question = Question(
        question="Q",
        expected_answer="A",
        expected_documents=[
        RelevantDocument(id="paper1", content="paper1"),
        RelevantDocument(id="paper2", content="paper2"),
    ]
    )

    prediction = adapter.evaluate(question)

    assert [doc.id for doc in prediction.retrieved_documents] == [
        "paper1",
        "paper2",
    ]