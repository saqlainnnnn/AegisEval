from __future__ import annotations

import csv
import json
from pathlib import Path

from app.datasets.base import BaseDatasetLoader
from app.schemas.dataset import Dataset, DatasetMetadata, Question


class DatasetLoader(BaseDatasetLoader):
    """
    Loads evaluation datasets from disk.
    """

    def load(
        self,
        path: Path,
    ) -> Dataset:

        suffix = path.suffix.lower()

        if suffix == ".json":
            return self._load_json(path)

        if suffix == ".jsonl":
            return self._load_jsonl(path)

        if suffix == ".csv":
            return self._load_csv(path)

        raise ValueError(f"Unsupported dataset format: {suffix}")

    def _load_json(
        self,
        path: Path,
    ) -> Dataset:

        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)

        metadata = DatasetMetadata(**data["metadata"])

        questions = [
            Question(**question)
            for question in data["questions"]
        ]

        return Dataset(
            metadata=metadata,
            questions=questions,
        )

    def _load_jsonl(
        self,
        path: Path,
    ) -> Dataset:

        questions: list[Question] = []

        with path.open("r", encoding="utf-8") as file:

            for line in file:
                questions.append(
                    Question(**json.loads(line))
                )

        metadata = DatasetMetadata(
            name=path.stem,
            description="JSONL Dataset",
        )

        return Dataset(
            metadata=metadata,
            questions=questions,
        )

    def _load_csv(
        self,
        path: Path,
    ) -> Dataset:

        questions: list[Question] = []

        with path.open(
            newline="",
            encoding="utf-8",
        ) as file:

            reader = csv.DictReader(file)

            for row in reader:

                questions.append(
                    Question(
                        question=row["question"],
                        expected_answer=row["expected_answer"],
                    )
                )

        metadata = DatasetMetadata(
            name=path.stem,
            description="CSV Dataset",
        )

        return Dataset(
            metadata=metadata,
            questions=questions,
        )