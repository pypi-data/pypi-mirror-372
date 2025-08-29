"""This module defines the AnnotationTask model."""

from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class AnnotationType(str, Enum):
    """The type of annotation task."""

    BBOX = "bbox"
    CLASSIFICATION = "classification"
    SEMANTIC_SEGMENTATION = "semantic_segmentation"
    INSTANCE_SEGMENTATION = "instance_segmentation"
    OBJECT_DETECTION = "object_detection"


class AnnotationTaskTable(SQLModel, table=True):
    """The annotation task model."""

    __tablename__ = "annotation_tasks"
    annotation_task_id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    annotation_type: AnnotationType
    is_prediction: bool
