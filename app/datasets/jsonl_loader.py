from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.datasets.base import BaseDatasetLoader
from app.domain.dataset import Question


class JSONLDatasetLoader(BaseDatasetLoader):
    """
    Loads evaluation datasets from JSONL files.
    """

    def _read(
        self,
        path: Path,
    ) -> Any:
        rows = []

        with path.open(
            "r",
            encoding="utf-8",
        ) as file:
            for line in file:
                if line.strip():
                    rows.append(json.loads(line))

        return rows

    def _build_questions(
        self,
        raw_data: Any,
    ) -> list[Question]:
        return [
            Question(**row)
            for row in raw_data
        ]