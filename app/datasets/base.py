from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from app.schemas.dataset import Dataset


class BaseDatasetLoader(ABC):
    """
    Base class for loading evaluation datasets.
    """

    @abstractmethod
    def load(
        self,
        path: Path,
    ) -> Dataset:
        """
        Load a dataset from disk.

        Parameters
        ----------
        path
            Path to the dataset.

        Returns
        -------
        Dataset
        """
        raise NotImplementedError