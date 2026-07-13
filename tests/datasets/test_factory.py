from pathlib import Path

import pytest

from app.datasets.csv_loader import CSVDatasetLoader
from app.datasets.factory import DatasetFactory
from app.datasets.json_loader import JSONDatasetLoader
from app.datasets.jsonl_loader import JSONLDatasetLoader


def test_json_loader_selected() -> None:
    loader = DatasetFactory.create(Path("test.json"))

    assert isinstance(loader, JSONDatasetLoader)


def test_jsonl_loader_selected() -> None:
    loader = DatasetFactory.create(Path("test.jsonl"))

    assert isinstance(loader, JSONLDatasetLoader)


def test_csv_loader_selected() -> None:
    loader = DatasetFactory.create(Path("test.csv"))

    assert isinstance(loader, CSVDatasetLoader)


def test_unknown_extension() -> None:
    with pytest.raises(ValueError):
        DatasetFactory.create(Path("test.pdf"))