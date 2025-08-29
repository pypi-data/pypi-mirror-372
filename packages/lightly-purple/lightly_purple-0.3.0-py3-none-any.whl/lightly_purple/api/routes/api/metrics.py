"""This module contains the API routes for computing detection metrics."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlmodel import Session
from typing_extensions import Annotated

from lightly_purple.api.db import get_session
from lightly_purple.metrics.detection.map import (
    DetectionMetricsMAP,
    calculate_map_metric,
)
from lightly_purple.resolvers import (
    annotation_label_resolver,
    annotation_resolver,
)
from lightly_purple.resolvers.annotations.annotations_filter import (
    AnnotationsFilter,
)

metrics_router = APIRouter()

SessionDep = Annotated[Session, Depends(get_session)]


class DetectionMetricsMAPRequest(BaseModel):
    """Request for computing the MAP detection metric."""

    dataset_id: UUID
    ground_truth_task_id: UUID
    prediction_task_id: UUID
    tag_id: UUID | None = None


@metrics_router.post("/metrics/compute/detection/map", response_model=DetectionMetricsMAP)
def compute_detection_map(
    request_body: DetectionMetricsMAPRequest,
    session: SessionDep,
) -> DetectionMetricsMAP:
    """Compute the MAP detection metric."""
    ground_truth_annotations = annotation_resolver.get_all(
        session=session,
        filters=AnnotationsFilter(
            dataset_ids=[request_body.dataset_id],
            annotation_task_ids=[request_body.ground_truth_task_id],
            sample_tag_ids=[request_body.tag_id] if request_body.tag_id else None,
        ),
    ).annotations
    prediction_annotations = annotation_resolver.get_all(
        session=session,
        filters=AnnotationsFilter(
            dataset_ids=[request_body.dataset_id],
            annotation_task_ids=[request_body.prediction_task_id],
            sample_tag_ids=[request_body.tag_id] if request_body.tag_id else None,
        ),
    ).annotations

    metrics_result = calculate_map_metric(
        pred_annotations=prediction_annotations,
        gt_annotations=ground_truth_annotations,
    )

    # Rename per-class metrics to use label names
    raw_map_pc = metrics_result.map_per_class
    if raw_map_pc:
        id2name = annotation_label_resolver.names_by_ids(
            session=session, ids=[UUID(k) for k in raw_map_pc]
        )
        metrics_result.map_per_class = {id2name.get(k, k): v for k, v in raw_map_pc.items()}
    raw_mar100_pc = metrics_result.mar_100_per_class
    if raw_mar100_pc:
        id2name = annotation_label_resolver.names_by_ids(
            session=session, ids=[UUID(k) for k in raw_mar100_pc]
        )
        metrics_result.mar_100_per_class = {id2name.get(k, k): v for k, v in raw_mar100_pc.items()}
    return metrics_result
