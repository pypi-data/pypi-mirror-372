"""Implementation for calculating Mean Average Precision (MAP)."""

from __future__ import annotations

import math
from collections import defaultdict
from collections.abc import Sequence
from uuid import UUID

import torch
from pydantic import BaseModel
from torch import Tensor
from torchmetrics.detection.mean_ap import MeanAveragePrecision

from lightly_purple.models.annotation.annotation_base import AnnotationBaseTable


class DetectionMetricsMAP(BaseModel):
    """Response for computing the MAP detection metric."""

    name: str
    map: float
    map_small: float
    map_medium: float
    map_large: float
    mar_1: float
    mar_10: float
    mar_100: float
    mar_small: float
    mar_medium: float
    mar_large: float
    map_50: float
    map_75: float
    map_per_class: dict[str, float] | None = None
    mar_100_per_class: dict[str, float] | None = None
    classes: list[int]

    @property
    def value(self) -> float:
        """Backwards compatibility alias for map."""
        return self.map

    @property
    def per_class(self) -> dict[str, float] | None:
        """Backwards compatibility alias for map_per_class."""
        return self.map_per_class


def calculate_map_metric(  # noqa: C901
    pred_annotations: Sequence[AnnotationBaseTable],
    gt_annotations: Sequence[AnnotationBaseTable],
) -> DetectionMetricsMAP:
    """Calculate the Mean Average Precision (MAP) metric."""
    if not gt_annotations or not pred_annotations:
        return DetectionMetricsMAP(
            name="mAP@.5:.95",
            map=0.0,
            map_small=0.0,
            map_medium=0.0,
            map_large=0.0,
            mar_1=0.0,
            mar_10=0.0,
            mar_100=0.0,
            mar_small=0.0,
            mar_medium=0.0,
            mar_large=0.0,
            map_50=-1.0,
            map_75=-1.0,
            map_per_class=None,
            mar_100_per_class=None,
            classes=[],
        )
    uuid_to_int_label: dict[UUID, int] = {}

    # Map sample_id to annotations.
    sample_id_to_annotations = _group_by_sample_id(
        pred_annotations=pred_annotations,
        gt_annotations=gt_annotations,
    )

    # Create the MeanAveragePrecision object.
    map_metric = MeanAveragePrecision(
        box_format="xywh",
        iou_thresholds=None,
        class_metrics=True,
        average="macro",
        backend="faster_coco_eval",
    )

    # Compute MAP updating the object sample by sample.
    for _sample_id, (
        sample_pred_annotations,
        sample_gt_annotations,
    ) in sample_id_to_annotations.items():
        # Convert to torchmetrics format.
        prediction_tm = _convert_to_torchmetrics(
            annotations=sample_pred_annotations,
            is_prediction=True,
            uuid_to_int_label_map=uuid_to_int_label,
        )
        ground_truth_tm = _convert_to_torchmetrics(
            annotations=sample_gt_annotations,
            is_prediction=False,
            uuid_to_int_label_map=uuid_to_int_label,
        )

        # Update the metric.
        map_metric.update(preds=[prediction_tm], target=[ground_truth_tm])

    # Compute the final results.
    results = map_metric.compute()
    # Invert label map to recover original UUIDs
    int_to_uuid = {v: k for k, v in uuid_to_int_label.items()}

    # Helper to convert Tensor to Python list
    def to_list(t: Tensor) -> list[float]:
        if t.dim() == 0:
            return [t.item()]
        return t.tolist()

    # Scalar metrics
    map_val = results["map"].item()
    map_small = results["map_small"].item()
    map_medium = results["map_medium"].item()
    map_large = results["map_large"].item()
    mar_1 = results["mar_1"].item()
    mar_10 = results["mar_10"].item()
    mar_100 = results["mar_100"].item()
    mar_small = results["mar_small"].item()
    mar_medium = results["mar_medium"].item()
    mar_large = results["mar_large"].item()

    # IoU-specific metrics
    map_50 = results.get("map_50")
    map_50 = map_50.item() if isinstance(map_50, Tensor) and map_50.dim() == 0 else -1.0
    map_75 = results.get("map_75")
    map_75 = map_75.item() if isinstance(map_75, Tensor) and map_75.dim() == 0 else -1.0

    # Per-class metrics
    raw_map_pc = results.get("map_per_class")
    per_class_dict: dict[str, float] | None = None
    if raw_map_pc is not None:
        pc_list = to_list(raw_map_pc)
        per_class_dict = {}
        for idx, val in enumerate(pc_list):
            if not math.isnan(val):
                per_class_dict[str(int_to_uuid[idx])] = val

    # Per-class recall at 100 detections
    raw_mar100_pc = results.get("mar_100_per_class")
    mar_100_pc_dict: dict[str, float] | None = None
    if raw_mar100_pc is not None:
        m100_list = to_list(raw_mar100_pc)
        mar_100_pc_dict = {}
        for idx, val in enumerate(m100_list):
            if not math.isnan(val):
                mar_100_pc_dict[str(int_to_uuid[idx])] = val

    # Observed classes
    raw_classes = results.get("classes")
    classes_list_output: list[int] = []
    if raw_classes is not None:
        classes_list_output = [int(x) for x in to_list(raw_classes)]

    return DetectionMetricsMAP(
        name="mAP@.5:.95",
        map=map_val,
        map_small=map_small,
        map_medium=map_medium,
        map_large=map_large,
        mar_1=mar_1,
        mar_10=mar_10,
        mar_100=mar_100,
        mar_small=mar_small,
        mar_medium=mar_medium,
        mar_large=mar_large,
        map_50=map_50,
        map_75=map_75,
        map_per_class=per_class_dict,
        mar_100_per_class=mar_100_pc_dict,
        classes=classes_list_output,
    )


def _group_by_sample_id(
    pred_annotations: Sequence[AnnotationBaseTable],
    gt_annotations: Sequence[AnnotationBaseTable],
) -> dict[
    UUID,
    tuple[list[AnnotationBaseTable], list[AnnotationBaseTable]],
]:
    """Group prediction and ground truth annotations by sample_id.

    Returns a dictionary with sample_id as key and a tuple of
    (list of prediction annotations, list of ground truth annotations) as value.
    """
    sample_id_to_annotations: defaultdict[
        UUID,
        tuple[list[AnnotationBaseTable], list[AnnotationBaseTable]],
    ] = defaultdict(lambda: ([], []))
    for ann in pred_annotations:
        sample_id_to_annotations[ann.sample_id][0].append(ann)
    for ann in gt_annotations:
        sample_id_to_annotations[ann.sample_id][1].append(ann)
    return sample_id_to_annotations


def _convert_to_torchmetrics(
    annotations: Sequence[AnnotationBaseTable],
    is_prediction: bool,
    uuid_to_int_label_map: dict[UUID, int],
) -> dict[str, Tensor]:
    """Convert annotations to torchmetrics format.

    Args:
        annotations: List of bounding box annotations.
        is_prediction: Whether the annotations are predictions.
        uuid_to_int_label_map: Map from UUID to integer label.

    Returns:
        Dictionary in torchmetrics format. For predictions the keys are
        `boxes`, `scores`, `labels`. For ground truth they are `boxes`,
        `labels`.

    """
    if not annotations:
        empty_boxes = torch.empty((0, 4), dtype=torch.float32)
        empty_labels = torch.empty((0,), dtype=torch.int64)
        if is_prediction:
            return {
                "boxes": empty_boxes,
                "scores": torch.empty((0,), dtype=torch.float32),
                "labels": empty_labels,
            }
        return {"boxes": empty_boxes, "labels": empty_labels}

    boxes = torch.tensor(
        [
            [
                a.object_detection_details.x,
                a.object_detection_details.y,
                a.object_detection_details.width,
                a.object_detection_details.height,
            ]
            for a in annotations
            if a.object_detection_details is not None
        ],
        dtype=torch.float32,
    )

    mapped_labels = []
    # Use the passed-in map instead of a global one
    for uuid_label in (a.annotation_label_id for a in annotations):
        if uuid_label not in uuid_to_int_label_map:
            # Assign the next available integer ID based on the current map size
            uuid_to_int_label_map[uuid_label] = len(uuid_to_int_label_map)
        mapped_labels.append(uuid_to_int_label_map[uuid_label])

    labels = torch.tensor(mapped_labels, dtype=torch.int64)

    if is_prediction:
        scores = torch.tensor([a.confidence for a in annotations], dtype=torch.float32)
        return {
            "boxes": boxes,
            "scores": scores,
            "labels": labels,
        }
    return {"boxes": boxes, "labels": labels}
