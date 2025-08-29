"""This module contains the API routes for managing annotations."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Body, Depends, HTTPException, Path
from fastapi.params import Query
from pydantic import BaseModel
from sqlmodel import Session
from typing_extensions import Annotated

from lightly_purple.api.db import get_session
from lightly_purple.api.routes.api.dataset import get_and_validate_dataset_id
from lightly_purple.api.routes.api.status import (
    HTTP_STATUS_CREATED,
    HTTP_STATUS_NOT_FOUND,
)
from lightly_purple.api.routes.api.validators import Paginated, PaginatedWithCursor
from lightly_purple.models.annotation.annotation_base import (
    AnnotationBaseTable,
    AnnotationDetailsView,
    CountedAnnotationView,
)
from lightly_purple.models.dataset import DatasetTable
from lightly_purple.resolvers import annotation_resolver, tag_resolver
from lightly_purple.resolvers.annotation_resolver.get_all import (
    GetAllAnnotationsResult,
)
from lightly_purple.resolvers.annotations.annotations_filter import (
    AnnotationsFilter,
)
from lightly_purple.services import annotations_service
from lightly_purple.services.annotations_service.update_annotation import (
    AnnotationUpdate,
)

annotations_router = APIRouter(prefix="/datasets/{dataset_id}", tags=["annotations"])
SessionDep = Annotated[Session, Depends(get_session)]


@annotations_router.get("/annotations/count")
def count_annotations_by_dataset(  # noqa: PLR0913 // FIXME: refactor to use proper pydantic
    dataset: Annotated[
        DatasetTable,
        Path(title="Dataset Id"),
        Depends(get_and_validate_dataset_id),
    ],
    session: SessionDep,
    filtered_labels: Annotated[list[str] | None, Query()] = None,
    min_width: Annotated[int | None, Query(ge=0)] = None,
    max_width: Annotated[int | None, Query(ge=0)] = None,
    min_height: Annotated[int | None, Query(ge=0)] = None,
    max_height: Annotated[int | None, Query(ge=0)] = None,
    tag_ids: list[UUID] | None = None,
) -> list[dict[str, str | int]]:
    """Get annotation counts for a specific dataset.

    Returns a list of dictionaries with label name and count.
    """
    counts = annotation_resolver.count_annotations_by_dataset(
        session=session,
        dataset_id=dataset.dataset_id,
        filtered_labels=filtered_labels,
        min_width=min_width,
        max_width=max_width,
        min_height=min_height,
        max_height=max_height,
        tag_ids=tag_ids,
    )
    return [
        {
            "label_name": label_name,
            "current_count": current_count,
            "total_count": total_count,
        }
        for label_name, current_count, total_count in counts
    ]


@annotations_router.get(
    "/annotations",
    response_model=CountedAnnotationView,
)
def read_annotations(
    dataset_id: Annotated[UUID, Path(title="Dataset Id", description="The ID of the dataset")],
    session: SessionDep,
    pagination: Annotated[PaginatedWithCursor, Depends()],
    annotation_label_ids: Annotated[list[UUID] | None, Query()] = None,
    tag_ids: Annotated[list[UUID] | None, Query()] = None,
) -> GetAllAnnotationsResult:
    """Retrieve a list of annotations from the database."""
    return annotation_resolver.get_all(
        session=session,
        pagination=Paginated(
            offset=pagination.offset,
            limit=pagination.limit,
        ),
        filters=AnnotationsFilter(
            dataset_ids=[dataset_id],
            annotation_label_ids=annotation_label_ids,
            annotation_tag_ids=tag_ids,
        ),
    )


@annotations_router.post(
    "/annotations/{annotation_id}/tag/{tag_id}",
    status_code=HTTP_STATUS_CREATED,
)
def add_tag_to_annotation(
    session: SessionDep,
    annotation_id: UUID,
    tag_id: UUID,
) -> bool:
    """Add annotation to a tag."""
    annotation = annotation_resolver.get_by_id(session=session, annotation_id=annotation_id)
    if not annotation:
        raise HTTPException(
            status_code=HTTP_STATUS_NOT_FOUND,
            detail=f"Annotation {annotation_id} not found",
        )

    if not tag_resolver.add_tag_to_annotation(
        session=session, tag_id=tag_id, annotation=annotation
    ):
        raise HTTPException(status_code=HTTP_STATUS_NOT_FOUND, detail=f"Tag {tag_id} not found")

    return True


class AnnotationUpdateInput(BaseModel):
    """API input model for updating an annotation."""

    annotation_id: UUID
    dataset_id: UUID
    label_name: str | None
    x: int | None = None
    y: int | None = None
    width: int | None = None
    height: int | None = None


@annotations_router.put("/annotations/{annotation_id}")
def update_annotation(
    session: SessionDep,
    dataset_id: Annotated[
        UUID,
        Path(title="Dataset Id"),
    ],
    annotation_id: Annotated[
        UUID,
        Path(title="Annotation ID", description="ID of the annotation to update"),
    ],
    annotation_update_input: Annotated[AnnotationUpdateInput, Body()],
) -> AnnotationBaseTable:
    """Update an existing annotation in the database."""
    return annotations_service.update_annotation(
        session=session,
        annotation_update=AnnotationUpdate(
            annotation_id=annotation_id,
            dataset_id=dataset_id,
            label_name=annotation_update_input.label_name,
            x=annotation_update_input.x,
            y=annotation_update_input.y,
            width=annotation_update_input.width,
            height=annotation_update_input.height,
        ),
    )


@annotations_router.put(
    "/annotations",
)
def update_annotations(
    session: SessionDep,
    dataset_id: Annotated[
        UUID,
        Path(title="Dataset Id"),
    ],
    annotation_update_inputs: Annotated[list[AnnotationUpdateInput], Body()],
) -> list[AnnotationBaseTable]:
    """Update multiple annotations in the database."""
    return annotations_service.update_annotations(
        session=session,
        annotation_updates=[
            AnnotationUpdate(
                annotation_id=annotation_update_input.annotation_id,
                dataset_id=dataset_id,
                label_name=annotation_update_input.label_name,
                x=annotation_update_input.x,
                y=annotation_update_input.y,
                width=annotation_update_input.width,
                height=annotation_update_input.height,
            )
            for annotation_update_input in annotation_update_inputs
        ],
    )


@annotations_router.get("/annotations/{annotation_id}", response_model=AnnotationDetailsView)
def get_annotation(
    session: SessionDep,
    dataset_id: Annotated[  # noqa: ARG001
        UUID,
        Path(title="Dataset Id", description="The ID of the dataset"),
    ],  # We need dataset_id because otherwise the path would not match
    annotation_id: Annotated[UUID, Path(title="Annotation ID")],
) -> AnnotationBaseTable:
    """Retrieve an existing annotation from the database."""
    return annotations_service.get_annotation_by_id(session=session, annotation_id=annotation_id)


@annotations_router.delete("/annotations/{annotation_id}/tag/{tag_id}")
def remove_tag_from_annotation(
    session: SessionDep,
    tag_id: UUID,
    annotation_id: UUID,
) -> bool:
    """Remove annotation from a tag."""
    annotation = annotation_resolver.get_by_id(session=session, annotation_id=annotation_id)
    if not annotation:
        raise HTTPException(
            status_code=HTTP_STATUS_NOT_FOUND,
            detail=f"Annotation {annotation_id} not found",
        )

    if not tag_resolver.remove_tag_from_annotation(
        session=session, tag_id=tag_id, annotation=annotation
    ):
        raise HTTPException(status_code=HTTP_STATUS_NOT_FOUND, detail=f"Tag {tag_id} not found")

    return True
