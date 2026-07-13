from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from app.domain.dataset import Dataset, DatasetMetadata, Question


class BaseDatasetLoader(ABC):
    """
    Base class for dataset loaders.

    Implements the common dataset loading algorithm while
    allowing subclasses to define format-specific behavior.
    """

    def load(
        self,
        path: Path,
        metadata_override: DatasetMetadata | None = None,
    ) -> Dataset:
        """
        Load a dataset from disk.
        """

        raw_data = self._read(path)

        metadata = (
            metadata_override
            if metadata_override is not None
            else self._build_metadata(path, raw_data)
        )

        questions = self._build_questions(raw_data)

        return Dataset(
            metadata=metadata,
            questions=questions,
        )

    @abstractmethod
    def _read(
        self,
        path: Path,
    ) -> Any:
        """
        Read the dataset from disk.
        """
        raise NotImplementedError

    def _build_metadata(
        self,
        path: Path,
        raw_data: Any,
    ) -> DatasetMetadata:
        """
        Build dataset metadata.
        """

        return DatasetMetadata(
            name=path.stem,
            description=f"{path.suffix.upper()} Dataset",
        )

    @abstractmethod
    def _build_questions(
        self,
        raw_data: Any,
    ) -> list[Question]:
        """
        Convert raw data into Question objects.
        """
        raise NotImplementedError