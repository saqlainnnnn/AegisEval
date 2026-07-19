from app.domain.prediction import Prediction
from app.domain.prediction import RetrievedDocument



def test_prediction_defaults() -> None:
    prediction = Prediction(
    answer="Artificial Intelligence",
    retrieved_documents=[
        RetrievedDocument(
            id="paper_1",
            content="paper_1",
        ),
        RetrievedDocument(
            id="paper_2",
            content="paper_2",
        ),
    ],
)

    assert prediction.retrieved_documents == []
    assert prediction.metadata == {}
    assert prediction.token_usage is None
    assert prediction.estimated_cost is None


def test_prediction_with_sources() -> None:
    prediction = Prediction(
        answer="Artificial Intelligence",
        retrieved_documents=[
            "paper_1",
            "paper_2",
        ],
    )

    assert len(prediction.retrieved_documents) == 2
