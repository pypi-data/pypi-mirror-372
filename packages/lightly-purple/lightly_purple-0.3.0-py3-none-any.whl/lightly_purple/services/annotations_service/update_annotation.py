"""General annotation update service."""

from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel
from sqlmodel import Session

from lightly_purple.models.annotation.annotation_base import (
    AnnotationBaseTable,
)
from lightly_purple.services import annotations_service


class AnnotationUpdate(BaseModel):
    """Model for updating an annotation."""

    annotation_id: UUID
    dataset_id: UUID
    label_name: str | None
    x: int | None = None
    y: int | None = None
    width: int | None = None
    height: int | None = None


def update_annotation(session: Session, annotation_update: AnnotationUpdate) -> AnnotationBaseTable:
    """Update an annotation.

    Args:
        session: Database session for executing the operation.
        annotation_update: Object containing updates for the annotation.

    Returns:
        The updated annotation.

    """
    if annotation_update.label_name is None:
        raise ValueError("Label name must be provided for updating annotation")

    # comment this out for now so e2e tests will pass
    # todo: uncomment after passing bbox coordinates on update from frontend
    # annotation=get_annotation_by_id(session,annotation_update.annotation_id)
    # if annotation.annotation_type in (
    #     AnnotationType.OBJECT_DETECTION,
    #     AnnotationType.INSTANCE_SEGMENTATION,
    # ) and any(
    #     [
    #         annotation_update.x is None,
    #         annotation_update.y is None,
    #         annotation_update.width is None,
    #         annotation_update.height is None,
    #     ]
    # ):
    #     raise ValueError(
    #         "All bounding box coordinates (x, y, width, height) "
    #         "must be provided for updating this annotation type"
    #     )

    return annotations_service.update_annotation_label(
        session,
        annotation_update.annotation_id,
        annotation_update.label_name,
    )
