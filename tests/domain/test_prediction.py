from app.domain.prediction import Prediction


def test_prediction_defaults() -> None:
    prediction = Prediction(
        answer="Artificial Intelligence",
    )

    assert prediction.retrieved_sources == []
    assert prediction.metadata == {}
    assert prediction.token_usage is None
    assert prediction.estimated_cost is None


def test_prediction_with_sources() -> None:
    prediction = Prediction(
        answer="Artificial Intelligence",
        retrieved_sources=[
            "paper_1",
            "paper_2",
        ],
    )

    assert len(prediction.retrieved_sources) == 2