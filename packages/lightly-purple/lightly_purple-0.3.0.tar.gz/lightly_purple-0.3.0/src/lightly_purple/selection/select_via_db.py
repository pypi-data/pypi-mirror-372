"""Database selection functions for the selection process."""

from __future__ import annotations

import datetime

from sqlmodel import Session

from lightly_purple.models.tag import TagCreate
from lightly_purple.resolvers import (
    embedding_model_resolver,
    sample_embedding_resolver,
    sample_resolver,
    tag_resolver,
)
from lightly_purple.selection.mundig import Mundig
from lightly_purple.selection.selection_config import (
    EmbeddingDiversityStrategy,
    SelectionConfig,
)


def select_via_database(session: Session, config: SelectionConfig) -> None:
    """Runs selection and all database interactions of it.

    First resolves the selection config to actual database values.
    Then calls Mundig to run the selection with pure values.
    Last creates a tag for the selected set.
    """
    # Check if the tag name is already used
    existing_tag = tag_resolver.get_by_name(
        session=session,
        tag_name=config.selection_result_tag_name,
        dataset_id=config.dataset_id,
    )
    if existing_tag:
        msg = (
            f"Tag with name {config.selection_result_tag_name} already exists in the "
            f"dataset {config.dataset_id}. Please use a different tag name."
        )
        raise ValueError(msg)

    # TODO(Malte, 08/2025): Use a DatasetQuery instead of SampleFilter once
    # the latter is implemented.
    # See https://linear.app/lightly/issue/LIG-7292/story-python-ui-mvp1-without-datasetquery-and-sample
    samples = sample_resolver.get_all_by_dataset_id(
        session,
        limit=None,
        dataset_id=config.dataset_id,
        filters=config.sample_filter,
    ).samples
    sample_ids = [s.sample_id for s in samples]

    n_samples_to_select = min(config.n_samples_to_select, len(sample_ids))
    if n_samples_to_select == 0:
        print("No samples available for selection.")
        return

    mundig = Mundig()
    for strat in config.strategies:
        if isinstance(strat, EmbeddingDiversityStrategy):
            embedding_model_id = embedding_model_resolver.get_by_name(
                session=session,
                dataset_id=config.dataset_id,
                embedding_model_name=strat.embedding_model_name,
            ).embedding_model_id
            embedding_tables = sample_embedding_resolver.get_by_sample_ids(
                session=session,
                sample_ids=sample_ids,
                embedding_model_id=embedding_model_id,
            )
            embeddings = [e.embedding for e in embedding_tables]
            mundig.add_diversity(embeddings=embeddings, strength=strat.strength)
        else:
            raise ValueError(f"Selection strategy of type {type(strat)} is unknown.")

    selected_indices = mundig.run(n_samples=n_samples_to_select)
    selected_sample_ids = [sample_ids[i] for i in selected_indices]

    datetime_str = datetime.datetime.now(tz=datetime.timezone.utc).isoformat()
    tag_description = f"Selected at {datetime_str} UTC"
    tag = tag_resolver.create(
        session=session,
        tag=TagCreate(
            dataset_id=config.dataset_id,
            name=config.selection_result_tag_name,
            kind="sample",
            description=tag_description,
        ),
    )
    tag_resolver.add_sample_ids_to_tag_id(
        session=session, tag_id=tag.tag_id, sample_ids=selected_sample_ids
    )
