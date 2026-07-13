from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.datasets.base import BaseDatasetLoader
from app.domain.dataset import DatasetMetadata, Question


class JSONDatasetLoader(BaseDatasetLoader):
    """
    Loads evaluation datasets from JSON files.
    """

    def _read(
        self,
        path: Path,
    ) -> Any:
        with path.open(
            "r",
            encoding="utf-8",
        ) as file:
            return json.load(file)

    def _build_metadata(
        self,
        path: Path,
        raw_data: Any,
    ) -> DatasetMetadata:
        return DatasetMetadata(**raw_data["metadata"])

    def _build_questions(
        self,
        raw_data: Any,
    ) -> list[Question]:
        return [
            Question(**question)
            for question in raw_data["questions"]
        ]