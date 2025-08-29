"""Handler for database operations related to annotations."""

from __future__ import annotations

from uuid import UUID

from sqlmodel import Session, select

from lightly_purple.models.annotation.annotation_base import (
    AnnotationBaseTable,
)


def get_by_id(session: Session, annotation_id: UUID) -> AnnotationBaseTable | None:
    """Retrieve a single annotation by ID."""
    return session.exec(
        select(AnnotationBaseTable).where(AnnotationBaseTable.annotation_id == annotation_id)
    ).one_or_none()
