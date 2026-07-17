from __future__ import annotations

from typing import Any

from pydantic import Field

from app.domain.common import DomainModel, IdentifiableModel


class Question(IdentifiableModel):
    """
    Represents a single evaluation sample.
    """

    question: str

    expected_answer: str

    expected_sources: list[str] = Field(default_factory=list)

    difficulty: str = "medium"

    category: str = "general"

    tags: list[str] = Field(default_factory=list)

    metadata: dict[str, Any] = Field(default_factory=dict)


class DatasetMetadata(DomainModel):
    """
    Metadata describing an evaluation dataset.
    """

    name: str

    description: str

    version: str = "1.0"

    author: str | None = None


class Dataset(IdentifiableModel):
    """
    Collection of evaluation questions.
    """

    metadata: DatasetMetadata

    questions: list[Question] = Field(default_factory=list)
