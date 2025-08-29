"""Handler for database operations related to annotations."""

from __future__ import annotations

from sqlmodel import Session

from lightly_purple.models.annotation.annotation_base import (
    AnnotationBaseTable,
    AnnotationCreate,
)


def create(session: Session, annotation: AnnotationCreate) -> AnnotationBaseTable:
    """Create a new annotation in the database."""
    db_annotation = AnnotationBaseTable.model_validate(annotation)
    session.add(db_annotation)
    session.commit()
    session.refresh(db_annotation)
    return db_annotation
