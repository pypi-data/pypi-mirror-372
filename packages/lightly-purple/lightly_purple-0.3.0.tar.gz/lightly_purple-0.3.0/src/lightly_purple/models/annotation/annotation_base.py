"""This module defines the base annotation model."""

from datetime import datetime, timezone
from typing import TYPE_CHECKING, List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel
from pydantic import Field as PydanticField
from sqlalchemy.orm import Mapped
from sqlmodel import Field, Relationship, SQLModel

from lightly_purple.models.annotation.instance_segmentation import (
    InstanceSegmentationAnnotationTable,
    InstanceSegmentationAnnotationView,
)
from lightly_purple.models.annotation.links import AnnotationTagLinkTable
from lightly_purple.models.annotation.object_detection import (
    ObjectDetectionAnnotationTable,
    ObjectDetectionAnnotationView,
)
from lightly_purple.models.annotation.semantic_segmentation import (
    SemanticSegmentationAnnotationTable,
    SemanticSegmentationAnnotationView,
)
from lightly_purple.models.annotation_task import (
    AnnotationTaskTable,
    AnnotationType,
)

if TYPE_CHECKING:
    from lightly_purple.models.annotation_label import (
        AnnotationLabelTable,
    )
    from lightly_purple.models.sample import (
        SampleTable,
    )
    from lightly_purple.models.tag import TagTable
else:
    TagTable = object
    SampleTable = object
    AnnotationLabelTable = object


class AnnotationBaseTable(SQLModel, table=True):
    """Base class for all annotation models."""

    __tablename__ = "annotation_base"

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), index=True)

    annotation_id: UUID = Field(default_factory=uuid4, primary_key=True)
    annotation_type: AnnotationType
    annotation_label_id: UUID = Field(foreign_key="annotation_labels.annotation_label_id")
    annotation_task_id: UUID = Field(
        foreign_key="annotation_tasks.annotation_task_id",
    )
    confidence: Optional[float] = None
    dataset_id: UUID = Field(foreign_key="datasets.dataset_id")
    sample_id: UUID = Field(foreign_key="samples.sample_id")

    annotation_label: Mapped["AnnotationLabelTable"] = Relationship(
        sa_relationship_kwargs={"lazy": "select"},
    )
    annotation_task: Mapped["AnnotationTaskTable"] = Relationship(
        sa_relationship_kwargs={"lazy": "select"},
    )
    sample: Mapped[Optional["SampleTable"]] = Relationship(
        sa_relationship_kwargs={"lazy": "select"},
    )
    tags: Mapped[List["TagTable"]] = Relationship(
        back_populates="annotations",
        link_model=AnnotationTagLinkTable,
    )

    """ Details about object detection. """
    object_detection_details: Mapped[Optional["ObjectDetectionAnnotationTable"]] = Relationship(
        back_populates="annotation_base",
        sa_relationship_kwargs={"lazy": "select"},
    )

    """ Details about instance segmentation. """
    instance_segmentation_details: Mapped[Optional["InstanceSegmentationAnnotationTable"]] = (
        Relationship(
            back_populates="annotation_base",
            sa_relationship_kwargs={"lazy": "select"},
        )
    )

    """ Details about semantic segmentation. """
    semantic_segmentation_details: Mapped[Optional["SemanticSegmentationAnnotationTable"]] = (
        Relationship(
            back_populates="annotation_base",
            sa_relationship_kwargs={"lazy": "select"},
        )
    )


class AnnotationCreate(SQLModel):
    """Input model for creating annotations."""

    """ Required properties for all annotations. """
    annotation_label_id: UUID
    annotation_type: AnnotationType
    annotation_task_id: UUID
    confidence: Optional[float] = None
    dataset_id: UUID
    sample_id: UUID

    """ Optional properties for object detection. """
    x: Optional[float] = None
    y: Optional[float] = None
    width: Optional[float] = None
    height: Optional[float] = None

    """ Optional properties for instance and semantic segmentation. """
    segmentation_mask: Optional[List[int]] = None


class AnnotationSampleView(SQLModel):
    """Sample class for annotation view."""

    file_path_abs: str
    file_name: str
    dataset_id: UUID
    sample_id: UUID
    width: int
    height: int


class AnnotationView(SQLModel):
    """Response model for bounding box annotation."""

    class AnnotationLabel(SQLModel):
        """Model used when retrieving an annotation label."""

        annotation_label_name: str

    sample_id: UUID
    dataset_id: UUID
    annotation_id: UUID
    annotation_type: AnnotationType
    annotation_label: AnnotationLabel
    annotation_task_id: UUID
    confidence: Optional[float] = None

    object_detection_details: Optional[ObjectDetectionAnnotationView] = None
    instance_segmentation_details: Optional[InstanceSegmentationAnnotationView] = None
    semantic_segmentation_details: Optional[SemanticSegmentationAnnotationView] = None


class AnnotationWithSampleView(AnnotationView):
    """Response model for bounding box annotation."""

    sample: AnnotationSampleView


class CountedAnnotationView(BaseModel):
    """Response model for counted annotations."""

    annotations: List[AnnotationWithSampleView] = PydanticField(..., alias="data")
    total_count: int
    next_cursor: Optional[int] = PydanticField(..., alias="nextCursor")

    class Config:  # noqa: D106
        populate_by_name = True


class AnnotationDetailsView(AnnotationView):
    """Representing detailed view of an annotation."""

    sample: AnnotationSampleView
