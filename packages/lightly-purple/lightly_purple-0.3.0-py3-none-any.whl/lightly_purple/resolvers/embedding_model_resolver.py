"""Handler for database operations related to embedding models."""

from __future__ import annotations

from uuid import UUID

from sqlmodel import Session, col, select

from lightly_purple.models.embedding_model import (
    EmbeddingModelCreate,
    EmbeddingModelTable,
)


def create(session: Session, embedding_model: EmbeddingModelCreate) -> EmbeddingModelTable:
    """Create a new EmbeddingModel in the database."""
    db_embedding_model = EmbeddingModelTable.model_validate(embedding_model)
    session.add(db_embedding_model)
    session.commit()
    session.refresh(db_embedding_model)
    return db_embedding_model


def get_all_by_dataset_id(session: Session, dataset_id: UUID) -> list[EmbeddingModelTable]:
    """Retrieve all embedding models."""
    embedding_models = session.exec(
        select(EmbeddingModelTable)
        .where(EmbeddingModelTable.dataset_id == dataset_id)
        .order_by(col(EmbeddingModelTable.created_at).asc())
    ).all()
    return list(embedding_models)


def get_by_id(session: Session, embedding_model_id: UUID) -> EmbeddingModelTable | None:
    """Retrieve a single embedding model by ID."""
    return session.exec(
        select(EmbeddingModelTable).where(
            EmbeddingModelTable.embedding_model_id == embedding_model_id
        )
    ).one_or_none()


def get_by_model_hash(session: Session, embedding_model_hash: str) -> EmbeddingModelTable | None:
    """Retrieve a single embedding model by hash."""
    return session.exec(
        select(EmbeddingModelTable).where(
            EmbeddingModelTable.embedding_model_hash == embedding_model_hash
        )
    ).one_or_none()


def get_by_name(
    session: Session, dataset_id: UUID, embedding_model_name: str | None
) -> EmbeddingModelTable:
    """Helper function to resolve the embedding model name to its ID.

    Args:
        session: The database session.
        dataset_id: The ID of the dataset.
        embedding_model_name: The name of the embedding model.
            If None, expects the dataset to have exactly one embedding model and
            returns it. Otherwise raises a ValueError.
            If set, expects the dataset to have an embedding model with the given name.
            Otherwise raises a ValueError.

    Returns:
        The embedding model with the given name.
    """
    embedding_models = get_all_by_dataset_id(
        session=session,
        dataset_id=dataset_id,
    )

    if embedding_model_name is None:
        if len(embedding_models) != 1:
            raise ValueError(
                f"Expected exactly one embedding model, "
                f"but found {len(embedding_models)} with names "
                f"{[model.name for model in embedding_models]}."
            )
        return embedding_models[0]

    embedding_model_with_name = next(
        (model for model in embedding_models if model.name == embedding_model_name), None
    )
    if embedding_model_with_name is None:
        raise ValueError(f"Embedding model with name `{embedding_model_name}` not found.")

    return embedding_model_with_name


def delete(session: Session, embedding_model_id: UUID) -> bool:
    """Delete an embedding model."""
    embedding_model = get_by_id(session=session, embedding_model_id=embedding_model_id)
    if not embedding_model:
        return False

    session.delete(embedding_model)
    session.commit()
    return True
