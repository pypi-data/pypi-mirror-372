"""API endpoints for annotation tasks."""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from lightly_purple.api.db import get_session
from lightly_purple.models.annotation_task import AnnotationTaskTable
from lightly_purple.resolvers import annotation_task_resolver

router = APIRouter(prefix="/annotationtasks", tags=["annotationtasks"])


@router.get("/", response_model=List[AnnotationTaskTable])
def get_annotation_tasks(
    session: Session = Depends(get_session),  # noqa: B008
) -> List[AnnotationTaskTable]:
    """Get all annotation tasks."""
    return annotation_task_resolver.get_all(session=session)


@router.get("/{annotation_task_id}", response_model=AnnotationTaskTable)
def get_annotation_task(
    annotation_task_id: UUID,
    session: Session = Depends(get_session),  # noqa: B008
) -> AnnotationTaskTable:
    """Get an annotation task by ID."""
    task = annotation_task_resolver.get_by_id(
        session=session, annotation_task_id=annotation_task_id
    )
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Annotation task with ID {annotation_task_id} not found",
        )
    return task
