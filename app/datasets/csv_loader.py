from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from app.datasets.base import BaseDatasetLoader
from app.domain.dataset import Question


class CSVDatasetLoader(BaseDatasetLoader):
    """
    Loads evaluation datasets from CSV files.
    """

    def _read(
        self,
        path: Path,
    ) -> Any:
        with path.open(
            "r",
            encoding="utf-8",
            newline="",
        ) as file:
            return list(csv.DictReader(file))

    def _build_questions(
        self,
        raw_data: Any,
    ) -> list[Question]:
        questions: list[Question] = []

        for row in raw_data:
            questions.append(
                Question(
                    question=row["question"],
                    expected_answer=row["expected_answer"],
                    expected_documents=self._parse_list(row.get("expected_documents")),
                    difficulty=row.get(
                        "difficulty",
                        "medium",
                    ),
                    category=row.get(
                        "category",
                        "general",
                    ),
                    tags=self._parse_list(row.get("tags")),
                )
            )

        return questions

    def _parse_list(
        self,
        value: str | None,
    ) -> list[str]:
        if not value:
            return []

        return [item.strip() for item in value.split(",") if item.strip()]
