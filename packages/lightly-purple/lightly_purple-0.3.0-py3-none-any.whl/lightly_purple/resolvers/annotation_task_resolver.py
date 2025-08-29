"""Resolver for annotation tasks."""

from typing import List, Optional, Sequence
from uuid import UUID

from sqlmodel import Session, col, select

from lightly_purple.models.annotation_task import AnnotationTaskTable


def create(session: Session, annotation_task: AnnotationTaskTable) -> AnnotationTaskTable:
    """Create a new annotation task."""
    session.add(annotation_task)
    session.commit()
    session.refresh(annotation_task)
    return annotation_task


def get_by_id(session: Session, annotation_task_id: UUID) -> Optional[AnnotationTaskTable]:
    """Get an annotation task by ID."""
    statement = select(AnnotationTaskTable).where(
        AnnotationTaskTable.annotation_task_id == annotation_task_id
    )
    return session.exec(statement).first()


def get_all(session: Session) -> List[AnnotationTaskTable]:
    """Get all annotation tasks."""
    statement = select(AnnotationTaskTable).order_by(col(AnnotationTaskTable.created_at).asc())
    results: Sequence[AnnotationTaskTable] = session.exec(statement).all()
    return list(results)
