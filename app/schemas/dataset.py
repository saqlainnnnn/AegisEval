from __future__ import annotations

from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.common import IdentifiableModel


class Question(IdentifiableModel):
    """
    Represents a single evaluation sample.
    """


    question: str
    expected_answer: str

    expected_sources: list[str] = Field(default_factory=list)

    metadata: dict[str, Any] = Field(default_factory=dict)

    difficulty: str = "medium"

    category: str = "general"

    tags: list[str] = Field(default_factory=list)


class DatasetMetadata(BaseModel):
    """
    Metadata describing an evaluation dataset.
    """

    model_config = ConfigDict(from_attributes=True)

    name: str

    description: str

    version: str = "1.0"

    author: str | None = None


class Dataset(IdentifiableModel):
    """
    Collection of evaluation samples.
    """

    metadata: DatasetMetadata

    questions: list[Question] = Field(default_factory=list)