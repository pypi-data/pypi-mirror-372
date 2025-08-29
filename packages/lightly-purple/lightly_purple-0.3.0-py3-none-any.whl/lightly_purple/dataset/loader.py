"""Dataset functionality module."""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable
from uuid import UUID

import PIL
from labelformat.formats import (
    COCOInstanceSegmentationInput,
    COCOObjectDetectionInput,
    YOLOv8ObjectDetectionInput,
)
from labelformat.model.binary_mask_segmentation import BinaryMaskSegmentation
from labelformat.model.bounding_box import BoundingBoxFormat
from labelformat.model.image import Image
from labelformat.model.instance_segmentation import (
    ImageInstanceSegmentation,
    InstanceSegmentationInput,
)
from labelformat.model.multipolygon import MultiPolygon
from labelformat.model.object_detection import (
    ImageObjectDetection,
    ObjectDetectionInput,
)
from sqlmodel import Session
from tqdm import tqdm

from lightly_purple.api.db import db_manager
from lightly_purple.api.features import purple_active_features
from lightly_purple.api.server import Server
from lightly_purple.dataset import env
from lightly_purple.dataset.embedding_generator import EmbeddingGenerator
from lightly_purple.dataset.embedding_manager import (
    EmbeddingManager,
    EmbeddingManagerProvider,
)
from lightly_purple.models.annotation.annotation_base import AnnotationCreate
from lightly_purple.models.annotation_label import AnnotationLabelCreate
from lightly_purple.models.annotation_task import (
    AnnotationTaskTable,
    AnnotationType,
)
from lightly_purple.models.dataset import DatasetCreate, DatasetTable
from lightly_purple.models.sample import SampleCreate, SampleTable
from lightly_purple.resolvers import (
    annotation_label_resolver,
    annotation_resolver,
    annotation_task_resolver,
    dataset_resolver,
    sample_resolver,
)

# Constants
ANNOTATION_BATCH_SIZE = 64  # Number of annotations to process in a single batch
SAMPLE_BATCH_SIZE = 32  # Number of samples to process in a single batch


@dataclass
class AnnotationProcessingContext:
    """Context for processing annotations for a single sample."""

    dataset_id: UUID
    sample_id: UUID
    label_map: dict[int, UUID]
    annotation_task_id: UUID


class DatasetLoader:
    """Class responsible for loading datasets from various sources."""

    def __init__(self) -> None:
        """Initialize the dataset loader."""
        with db_manager.session() as session:
            self.session = session
            self.embedding_manager = EmbeddingManagerProvider.get_embedding_manager(session=session)

    def _load_into_dataset(
        self,
        dataset: DatasetTable,
        input_labels: ObjectDetectionInput | InstanceSegmentationInput,
        img_dir: Path,
        annotation_task_id: UUID,
    ) -> None:
        """Store a loaded dataset in database."""
        # Create label mapping
        label_map = _create_label_map(session=self.session, input_labels=input_labels)

        annotations_to_create: list[AnnotationCreate] = []
        sample_ids: list[UUID] = []
        samples_to_create: list[SampleCreate] = []
        samples_image_data: list[
            tuple[SampleCreate, ImageInstanceSegmentation | ImageObjectDetection]
        ] = []

        for image_data in tqdm(input_labels.get_labels(), desc="Processing images", unit=" images"):
            image: Image = image_data.image  # type: ignore[attr-defined]

            typed_image_data: ImageInstanceSegmentation | ImageObjectDetection = image_data  # type: ignore[assignment]
            sample = SampleCreate(
                file_name=str(image.filename),
                file_path_abs=str(img_dir / image.filename),
                width=image.width,
                height=image.height,
                dataset_id=dataset.dataset_id,
            )
            samples_to_create.append(sample)
            samples_image_data.append((sample, typed_image_data))

            if len(samples_to_create) >= SAMPLE_BATCH_SIZE:
                stored_samples = sample_resolver.create_many(
                    session=self.session, samples=samples_to_create
                )
                _process_batch_annotations(
                    session=self.session,
                    stored_samples=stored_samples,
                    samples_data=samples_image_data,
                    dataset_id=dataset.dataset_id,
                    label_map=label_map,
                    annotation_task_id=annotation_task_id,
                    annotations_to_create=annotations_to_create,
                    sample_ids=sample_ids,
                )
                samples_to_create.clear()
                samples_image_data.clear()

        if samples_to_create:
            stored_samples = sample_resolver.create_many(
                session=self.session, samples=samples_to_create
            )
            _process_batch_annotations(
                session=self.session,
                stored_samples=stored_samples,
                samples_data=samples_image_data,
                dataset_id=dataset.dataset_id,
                label_map=label_map,
                annotation_task_id=annotation_task_id,
                annotations_to_create=annotations_to_create,
                sample_ids=sample_ids,
            )

        # Insert any remaining annotations
        if annotations_to_create:
            annotation_resolver.create_many(session=self.session, annotations=annotations_to_create)

        # Generate embeddings for the dataset.
        _generate_embeddings(
            embedding_manager=self.embedding_manager,
            dataset_id=dataset.dataset_id,
            sample_ids=sample_ids,
        )

    def from_yolo(
        self,
        data_yaml_path: str,
        input_split: str = "train",
        task_name: str | None = None,
    ) -> DatasetTable:
        """Load a dataset in YOLO format and store in DB.

        Args:
            data_yaml_path: Path to the YOLO data.yaml file.
            input_split: The split to load (e.g., 'train', 'val').
            task_name: Optional name for the annotation task. If None, a
                default name is generated.

        Returns:
            DatasetTable: The created dataset table entry.
        """
        data_yaml = Path(data_yaml_path).absolute()
        dataset_name = data_yaml.parent.name

        if task_name is None:
            task_name = f"Loaded from YOLO: {data_yaml.name} ({input_split} split)"

        # Load the dataset using labelformat.
        label_input = YOLOv8ObjectDetectionInput(
            input_file=data_yaml,
            input_split=input_split,
        )
        img_dir = label_input._images_dir()  # noqa: SLF001

        return self.from_labelformat(
            input_labels=label_input,
            dataset_name=dataset_name,
            img_dir=str(img_dir),
            is_prediction=False,
            task_name=task_name,
        )

    def from_coco_object_detections(
        self,
        annotations_json_path: str,
        img_dir: str,
        task_name: str | None = None,
    ) -> DatasetTable:
        """Load a dataset in COCO Object Detection format and store in DB.

        Args:
            annotations_json_path: Path to the COCO annotations JSON file.
            img_dir: Path to the folder containing the images.
            task_name: Optional name for the annotation task. If None, a
                default name is generated.

        Returns:
            DatasetTable: The created dataset table entry.
        """
        annotations_json = Path(annotations_json_path)
        dataset_name = annotations_json.parent.name

        if task_name is None:
            task_name = f"Loaded from COCO Object Detection: {annotations_json.name}"

        label_input = COCOObjectDetectionInput(
            input_file=annotations_json,
        )
        img_dir_path = Path(img_dir).absolute()

        return self.from_labelformat(
            input_labels=label_input,
            dataset_name=dataset_name,
            img_dir=str(img_dir_path),
            is_prediction=False,
            task_name=task_name,
        )

    def from_coco_instance_segmentations(
        self,
        annotations_json_path: str,
        img_dir: str,
        task_name: str | None = None,
    ) -> DatasetTable:
        """Load a dataset in COCO Instance Segmentation format and store in DB.

        Args:
            annotations_json_path: Path to the COCO annotations JSON file.
            img_dir: Path to the folder containing the images.
            task_name: Optional name for the annotation task. If None, a
                default name is generated.

        Returns:
            DatasetTable: The created dataset table entry.
        """
        annotations_json = Path(annotations_json_path)
        dataset_name = annotations_json.parent.name

        if task_name is None:
            task_name = f"Loaded from COCO Instance Segmentation: {annotations_json.name}"

        label_input = COCOInstanceSegmentationInput(
            input_file=annotations_json,
        )
        img_dir_path = Path(img_dir).absolute()

        return self.from_labelformat(
            input_labels=label_input,
            dataset_name=dataset_name,
            img_dir=str(img_dir_path),
            is_prediction=False,
            task_name=task_name,
        )

    def from_labelformat(
        self,
        input_labels: ObjectDetectionInput | InstanceSegmentationInput,
        dataset_name: str,
        img_dir: str,
        is_prediction: bool = True,
        task_name: str | None = None,
    ) -> DatasetTable:
        """Load a dataset from a labelformat object and store in database.

        Args:
            input_labels: The labelformat input object.
            dataset_name: The name for the new dataset.
            img_dir: Path to the folder containing the images.
            is_prediction: Whether the task is for prediction or labels.
            task_name: Optional name for the annotation task. If None, a
                default name is generated.

        Returns:
            DatasetTable: The created dataset table entry.
        """
        img_dir_path = Path(img_dir).absolute()

        # Determine annotation type based on input.
        # Currently, we always create BBOX tasks, even for segmentation,
        # as segmentation data is stored alongside bounding boxes.
        annotation_type = AnnotationType.BBOX

        # Generate a default task name if none is provided.
        if task_name is None:
            task_name = f"Loaded from labelformat: {dataset_name}"

        # Create dataset and annotation task.
        dataset = dataset_resolver.create(
            session=self.session,
            dataset=DatasetCreate(
                name=dataset_name,
                directory=str(img_dir_path),
            ),
        )
        new_annotation_task = annotation_task_resolver.create(
            session=self.session,
            annotation_task=AnnotationTaskTable(
                name=task_name,
                annotation_type=annotation_type,
                is_prediction=is_prediction,
            ),
        )

        self._load_into_dataset(
            dataset=dataset,
            input_labels=input_labels,
            img_dir=img_dir_path,
            annotation_task_id=new_annotation_task.annotation_task_id,
        )
        return dataset

    def from_directory(
        self,
        dataset_name: str,
        img_dir: str,
        recursive: bool = True,
        allowed_extensions: Iterable[str] = {
            ".png",
            ".jpg",
            ".jpeg",
            ".gif",
            ".webp",
            ".bmp",
            ".tiff",
        },
    ) -> DatasetTable:
        """Load a dataset from a folder of images and store in database.

        Args:
            dataset_name: The name for the new dataset.
            img_dir: Path to the folder containing the images.
            recursive: If True, search for images recursively in subfolders.
            allowed_extensions: An iterable container of allowed image file
                extensions.
        """
        img_dir_path = Path(img_dir).absolute()
        if not img_dir_path.exists() or not img_dir_path.is_dir():
            raise ValueError(f"Input images folder is not a valid directory: {img_dir_path}")

        # Create dataset.
        dataset = dataset_resolver.create(
            session=self.session,
            dataset=DatasetCreate(
                name=dataset_name,
                directory=str(img_dir_path),
            ),
        )

        # Collect image file paths.
        allowed_extensions_set = {ext.lower() for ext in allowed_extensions}
        image_paths = []
        path_iter = img_dir_path.rglob("*") if recursive else img_dir_path.glob("*")
        for path in path_iter:
            if path.is_file() and path.suffix.lower() in allowed_extensions_set:
                image_paths.append(path)
        print(f"Found {len(image_paths)} images in {img_dir_path}.")

        # Process images.
        sample_ids = _create_samples_from_paths(
            session=self.session,
            dataset_id=dataset.dataset_id,
            image_paths=image_paths,
        )

        # Generate embeddings for the dataset.
        _generate_embeddings(
            embedding_manager=self.embedding_manager,
            dataset_id=dataset.dataset_id,
            sample_ids=list(sample_ids),
        )

        return dataset

    def start_gui(self) -> None:
        """Launch the web interface for the loaded dataset."""
        server = Server(host=env.PURPLE_HOST, port=env.PURPLE_PORT)

        print(f"Open the Purple GUI under: {env.APP_URL}")

        server.start()


def _create_samples_from_paths(
    session: Session,
    dataset_id: UUID,
    image_paths: Iterable[Path],
) -> Iterator[UUID]:
    """Create samples from a list of image paths.

    Args:
        session: The database session to use.
        dataset_id: The ID of the dataset to which samples belong.
        image_paths: An iterable of image file paths.

    Yields:
        UUIDs of created sample records.
    """
    samples_to_create: list[SampleCreate] = []

    for image_path in tqdm(
        image_paths,
        desc="Processing images",
        unit=" images",
    ):
        try:
            image = PIL.Image.open(image_path)
            width, height = image.size
            image.close()
        except (FileNotFoundError, PIL.UnidentifiedImageError, OSError):
            continue

        sample = SampleCreate(
            file_name=image_path.name,
            file_path_abs=str(image_path),
            width=width,
            height=height,
            dataset_id=dataset_id,
        )
        samples_to_create.append(sample)

        # Process batch when it reaches SAMPLE_BATCH_SIZE
        if len(samples_to_create) >= SAMPLE_BATCH_SIZE:
            stored_samples = sample_resolver.create_many(session=session, samples=samples_to_create)
            for stored_sample in stored_samples:
                yield stored_sample.sample_id
            samples_to_create = []

    # Handle remaining samples
    if samples_to_create:
        stored_samples = sample_resolver.create_many(session=session, samples=samples_to_create)
        for stored_sample in stored_samples:
            yield stored_sample.sample_id


def _create_label_map(
    session: Session,
    input_labels: ObjectDetectionInput | InstanceSegmentationInput,
) -> dict[int, UUID]:
    """Create a mapping of category IDs to annotation label IDs."""
    label_map = {}
    for category in tqdm(
        input_labels.get_categories(),
        desc="Processing categories",
        unit=" categories",
    ):
        label = AnnotationLabelCreate(annotation_label_name=category.name)
        stored_label = annotation_label_resolver.create(session=session, label=label)
        label_map[category.id] = stored_label.annotation_label_id
    return label_map


def _process_object_detection_annotations(
    context: AnnotationProcessingContext,
    image_data: ImageObjectDetection,
) -> list[AnnotationCreate]:
    """Process object detection annotations for a single image."""
    new_annotations = []
    for obj in image_data.objects:
        box = obj.box.to_format(BoundingBoxFormat.XYWH)
        x, y, width, height = box

        new_annotations.append(
            AnnotationCreate(
                dataset_id=context.dataset_id,
                sample_id=context.sample_id,
                annotation_label_id=context.label_map[obj.category.id],
                annotation_type="object_detection",
                x=x,
                y=y,
                width=width,
                height=height,
                confidence=obj.confidence,
                annotation_task_id=context.annotation_task_id,
            )
        )
    return new_annotations


def _process_instance_segmentation_annotations(
    context: AnnotationProcessingContext,
    image_data: ImageInstanceSegmentation,
) -> list[AnnotationCreate]:
    """Process instance segmentation annotations for a single image."""
    new_annotations = []
    for obj in image_data.objects:
        segmentation_rle: None | list[int] = None
        if isinstance(obj.segmentation, MultiPolygon):
            box = obj.segmentation.bounding_box().to_format(BoundingBoxFormat.XYWH)
        elif isinstance(obj.segmentation, BinaryMaskSegmentation):
            box = obj.segmentation.bounding_box.to_format(BoundingBoxFormat.XYWH)
            segmentation_rle = obj.segmentation._rle_row_wise  # noqa: SLF001
        else:
            raise ValueError(f"Unsupported segmentation type: {type(obj.segmentation)}")

        x, y, width, height = box

        new_annotations.append(
            AnnotationCreate(
                dataset_id=context.dataset_id,
                sample_id=context.sample_id,
                annotation_label_id=context.label_map[obj.category.id],
                annotation_type="instance_segmentation",
                x=x,
                y=y,
                width=width,
                height=height,
                segmentation_mask=segmentation_rle,
                annotation_task_id=context.annotation_task_id,
            )
        )
    return new_annotations


def _process_batch_annotations(  # noqa: PLR0913
    session: Session,
    stored_samples: list[SampleTable],
    samples_data: list[tuple[SampleCreate, ImageInstanceSegmentation | ImageObjectDetection]],
    dataset_id: UUID,
    label_map: dict[int, UUID],
    annotation_task_id: UUID,
    annotations_to_create: list[AnnotationCreate],
    sample_ids: list[UUID],
) -> None:
    """Process annotations for a batch of samples."""
    for stored_sample, (_, img_data) in zip(stored_samples, samples_data):
        sample_ids.append(stored_sample.sample_id)

        context = AnnotationProcessingContext(
            dataset_id=dataset_id,
            sample_id=stored_sample.sample_id,
            label_map=label_map,
            annotation_task_id=annotation_task_id,
        )

        if isinstance(img_data, ImageInstanceSegmentation):
            new_annotations = _process_instance_segmentation_annotations(
                context=context, image_data=img_data
            )
        elif isinstance(img_data, ImageObjectDetection):
            new_annotations = _process_object_detection_annotations(
                context=context, image_data=img_data
            )
        else:
            raise ValueError(f"Unsupported annotation type: {type(img_data)}")

        annotations_to_create.extend(new_annotations)

        if len(annotations_to_create) >= ANNOTATION_BATCH_SIZE:
            annotation_resolver.create_many(session=session, annotations=annotations_to_create)
            annotations_to_create.clear()


def _generate_embeddings(
    embedding_manager: EmbeddingManager,
    dataset_id: UUID,
    sample_ids: list[UUID],
) -> None:
    """Generate embeddings for the dataset."""
    # Load an embedding generator and register the model.
    embedding_generator = _load_embedding_generator()

    if embedding_generator:
        purple_active_features.append("embeddingSearchEnabled")
        embedding_model = embedding_manager.register_embedding_model(
            dataset_id=dataset_id,
            embedding_generator=embedding_generator,
        )
        embedding_manager.embed_images(
            sample_ids=sample_ids,
            embedding_model_id=embedding_model.embedding_model_id,
        )


def _load_embedding_generator() -> EmbeddingGenerator | None:
    """Load the embedding generator.

    Use MobileCLIP if its dependencies have been installed,
    otherwise return None.
    """
    if env.PURPLE_EMBEDDINGS_MODEL_TYPE == "EDGE":
        try:
            from lightly_purple.dataset.edge_embedding_generator import (
                EdgeSDKEmbeddingGenerator,
            )

            print("Using LightlyEdge embedding generator.")
            return EdgeSDKEmbeddingGenerator(model_path=env.PURPLE_EDGE_MODEL_FILE_PATH)
        except ImportError:
            print("Embedding functionality is disabled.")
            return None
    elif env.PURPLE_EMBEDDINGS_MODEL_TYPE == "MOBILE_CLIP":
        try:
            from lightly_purple.dataset.mobileclip_embedding_generator import (
                MobileCLIPEmbeddingGenerator,
            )

            print("Using MobileCLIP embedding generator.")
            return MobileCLIPEmbeddingGenerator()
        except ImportError:
            print("Embedding functionality is disabled.")
            return None
    else:
        print(
            f"Unsupported model type: '{env.PURPLE_EMBEDDINGS_MODEL_TYPE}'",
        )
        print("Embedding functionality is disabled.")
        return None
