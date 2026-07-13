from __future__ import annotations

from pathlib import Path

from app.datasets.base import BaseDatasetLoader
from app.datasets.csv_loader import CSVDatasetLoader
from app.datasets.json_loader import JSONDatasetLoader
from app.datasets.jsonl_loader import JSONLDatasetLoader


class DatasetFactory:
    """
    Factory for creating dataset loaders.
    """

    _LOADERS: dict[str, type[BaseDatasetLoader]] = {
        ".json": JSONDatasetLoader,
        ".jsonl": JSONLDatasetLoader,
        ".csv": CSVDatasetLoader,
    }

    @classmethod
    def create(
        cls,
        path: Path,
    ) -> BaseDatasetLoader:
        suffix = path.suffix.lower()

        loader = cls._LOADERS.get(suffix)

        if loader is None:
            raise ValueError(
                f"Unsupported dataset format: {suffix}"
            )

        return loader()