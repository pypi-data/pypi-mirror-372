"""Pydantic models for the Selection configuration."""

from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel

from lightly_purple.resolvers.samples_filter import SampleFilter


class SelectionConfig(BaseModel):
    """Configuration for the selection process."""

    dataset_id: UUID
    sample_filter: SampleFilter | None = None
    n_samples_to_select: int
    selection_result_tag_name: str
    strategies: list[SelectionStrategy]


class SelectionStrategy(BaseModel):
    """Base class for selection strategies."""

    strength: float = 1.0


class EmbeddingDiversityStrategy(SelectionStrategy):
    """Selection strategy based on embedding diversity."""

    embedding_model_name: str | None
