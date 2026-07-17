from app.domain.common import IdentifiableModel


def test_identifiable_model_has_id() -> None:
    model = IdentifiableModel()

    assert model.id is not None


def test_identifiable_model_has_timestamps() -> None:
    model = IdentifiableModel()

    assert model.created_at is not None
    assert model.updated_at is not None
