import pytest

from app.datasets.base import BaseDatasetLoader


def test_base_dataset_loader_is_abstract() -> None:
    with pytest.raises(TypeError):
        BaseDatasetLoader()
