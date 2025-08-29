"""Provides the user python interface to selection."""

from __future__ import annotations

from uuid import UUID

from sqlmodel import Session

from lightly_purple.resolvers.samples_filter import SampleFilter
from lightly_purple.selection.select_via_db import select_via_database
from lightly_purple.selection.selection_config import (
    EmbeddingDiversityStrategy,
    SelectionConfig,
    SelectionStrategy,
)


class Selection:
    """User selection interface for the dataset."""

    # TODO(Malte, 08/2025): Create this class within the DatasetView.
    # Then the arguments can be passed directly from the DatasetView.
    # Example:
    # class DatasetView:
    #     def __init__(self, dataset_id: UUID, session: Session):
    #         self.select = Select(dataset_id, session)
    # User interface:
    # dataset_view = ...
    # dataset_view.select.diverse(...)
    #
    # See https://docs.google.com/document/d/1ZRICdFmfJmxUBy3FFoeUWsAgsCNWDHg8CK5MJiGmX74/edit?tab=t.kbfvnrepsuf#bookmark=id.8klhhwr5q4dp

    def __init__(self, dataset_id: UUID, session: Session):
        """Creates the interface to run selection.

        Args:
            dataset_id: The ID of the dataset to select from.
            session: The database session to use for selection.

        """
        self.dataset_id = dataset_id
        self.session = session

    def diverse(
        self,
        n_samples_to_select: int,
        selection_result_tag_name: str,
        embedding_model_name: str | None = None,
        sample_filter: SampleFilter | None = None,
    ) -> None:
        """Selects a diverse subset of the dataset.

        Args:
            n_samples_to_select: The number of samples to select.
            selection_result_tag_name: The tag name to use for the selection result.
            embedding_model_name:
                The name of the embedding model to use.
                If None, assert that there is only one embedding model and uses it.
            sample_filter: An optional filter to apply to the samples.
        """
        strategy = EmbeddingDiversityStrategy(embedding_model_name=embedding_model_name)
        selection_config = SelectionConfig(
            dataset_id=self.dataset_id,
            n_samples_to_select=n_samples_to_select,
            selection_result_tag_name=selection_result_tag_name,
            sample_filter=sample_filter,
            strategies=[strategy],
        )
        select_via_database(session=self.session, config=selection_config)

    def multi_strategies(
        self,
        n_samples_to_select: int,
        selection_result_tag_name: str,
        selection_strategies: list[SelectionStrategy],
        sample_filter: SampleFilter | None = None,
    ) -> None:
        """Select a subset of the dataset based on multiple selection strategies.

        Args:
            n_samples_to_select: The number of samples to select.
            selection_result_tag_name: The tag name to use for the selection result.
            selection_strategies:
                Selection strategies to use for the selection. They can be created after
                importing them from `lightly_purple.selection.selection_config`.
            sample_filter: An optional filter to apply to the samples.

        """
        config = SelectionConfig(
            dataset_id=self.dataset_id,
            n_samples_to_select=n_samples_to_select,
            selection_result_tag_name=selection_result_tag_name,
            sample_filter=sample_filter,
            strategies=selection_strategies,
        )
        select_via_database(session=self.session, config=config)
