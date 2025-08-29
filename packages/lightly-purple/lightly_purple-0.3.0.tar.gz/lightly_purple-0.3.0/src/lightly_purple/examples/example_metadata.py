"""Example script demonstrating metadata capabilities.

This script shows how to:
1. Load an existing dataset using DatasetLoader
2. Add metadata to all samples using bulk operations
3. Add metadata to individual samples
4. Filter samples using various metadata types
"""

from __future__ import annotations

import random
import time
from uuid import UUID

from environs import Env
from sqlmodel import Session

from lightly_purple import DatasetLoader
from lightly_purple.api.db import db_manager
from lightly_purple.metadata.gps_coordinate import GPSCoordinate
from lightly_purple.models.dataset import DatasetTable
from lightly_purple.resolvers import (
    metadata_resolver,
    sample_resolver,
)
from lightly_purple.resolvers.metadata_resolver.metadata_filter import Metadata
from lightly_purple.resolvers.samples_filter import SampleFilter

# Environment variables
env = Env()
env.read_env()
dataset_path = env.path("DATASET_PATH", "/path/to/your/yolo/dataset/data.yaml")
purple_dataset_split = env.str("PURPLE_DATASET_SPLIT", "test")


def load_existing_dataset() -> tuple[DatasetTable, list[UUID], DatasetLoader]:
    """Load an existing dataset using DatasetLoader.

    Returns:
        Tuple of (dataset, sample_ids, loader).
    """
    print(" Loading existing dataset...")

    loader = DatasetLoader()
    dataset = loader.from_yolo(
        str(dataset_path),
        input_split=purple_dataset_split,
    )
    # Get all sample IDs from the dataset
    samples = dataset.get_samples()
    sample_ids = [s.sample_id for s in samples]

    print(f"✅ Loaded dataset with {len(sample_ids)} samples")
    return dataset, sample_ids, loader


def add_bulk_metadata(session: Session, sample_ids: list[UUID]) -> None:
    """Add metadata to all samples using bulk operations."""
    print("\n Adding bulk metadata to all samples...")

    # Prepare bulk metadata with random values
    sample_metadata = []
    for sample_id in sample_ids:
        # Generate random metadata
        temp = random.randint(10, 40)
        loc = random.choice(["city", "rural", "mountain", "coastal", "desert"])
        lat = random.uniform(-90.0, 90.0)
        lon = random.uniform(-180.0, 180.0)
        gps_coord = GPSCoordinate(lat=lat, lon=lon)
        confidence = random.uniform(0.5, 1.0)
        is_processed = random.choice([True, False])

        sample_metadata.append(
            (
                sample_id,
                {
                    "temperature": temp,
                    "location": loc,
                    "gps_coordinates": gps_coord,
                    "confidence": confidence,
                    "is_processed": is_processed,
                    "batch_id": "bulk_001",  # Mark as bulk-added
                },
            )
        )

    # Bulk insert metadata
    start_time = time.time()
    metadata_resolver.bulk_set_metadata(session, sample_metadata)
    elapsed_time = time.time() - start_time

    print(f"✅ Added metadata to {len(sample_ids)} samples in {elapsed_time:.2f}s")


def add_individual_metadata(session: Session, sample_ids: list[UUID]) -> None:
    """Add metadata to individual samples."""
    print("\n Adding individual metadata to specific samples...")

    # Add metadata to first 5 samples individually
    for i, sample_id in enumerate(sample_ids[:5]):
        # Add some specific metadata
        metadata_resolver.set_value_for_sample(
            session=session,
            sample_id=sample_id,
            key="special_metadata",
            value=f"sample_{i + 1}_special",
        )

        metadata_resolver.set_value_for_sample(
            session=session,
            sample_id=sample_id,
            key="priority",
            value=random.randint(1, 10),
        )

        metadata_resolver.set_value_for_sample(
            session=session,
            sample_id=sample_id,
            key="list",
            value=[1, 2, 3],
        )

        metadata_resolver.set_value_for_sample(
            session=session,
            sample_id=sample_id,
            key="custom_gps",
            value=GPSCoordinate(
                lat=40.7128 + i * 0.1,  # Slightly different coordinates
                lon=-74.0060 + i * 0.1,
            ),
        )

    print(f"✅ Added individual metadata to {min(5, len(sample_ids))} samples")


def demonstrate_bulk_metadata_filters(dataset: DatasetTable) -> None:
    """Demonstrate filtering with bulk-added metadata."""
    print("\n Bulk Metadata Filters:")
    print("=" * 50)

    # Filter by temperature
    print("\n1. Filter by temperature > 25:")
    filter_temp = SampleFilter(metadata_filters=[Metadata("temperature") > 25])  # noqa PLR2004
    samples = dataset.get_samples(filters=filter_temp)
    print(f"   Found {len(samples)} samples with temperature > 25")
    for sample in samples[:3]:  # Show first 3
        print(f" {sample.file_name}: {sample['temperature']}")

    # Filter by location
    print("\n2. Filter by location == 'city':")
    filter_location = SampleFilter(metadata_filters=[Metadata("location") == "city"])
    samples = dataset.get_samples(filters=filter_location)
    print(f"   Found {len(samples)} samples from cities")
    for sample in samples[:3]:  # Show first 3
        print(f" {sample.file_name}: {sample['location']}")

    # Filter by GPS coordinates
    print("\n3. Filter by latitude > 0° (Northern hemisphere):")
    filter_lat = SampleFilter(metadata_filters=[Metadata("gps_coordinates.lat") > 0])
    samples = dataset.get_samples(filters=filter_lat)
    print(f"   Found {len(samples)} samples in Northern hemisphere")
    for sample in samples[:3]:  # Show first 3
        gps = sample["gps_coordinates"]
        print(f" {sample.file_name}: lat={gps.lat:.4f}, lon={gps.lon:.4f}")

    # Filter by confidence
    print("\n4. Filter by high confidence (> 0.9):")
    filter_confidence = SampleFilter(
        metadata_filters=[Metadata("confidence") > 0.9]  # noqa PLR2004
    )
    samples = dataset.get_samples(filters=filter_confidence)
    print(f"   Found {len(samples)} samples with confidence > 0.9")
    for sample in samples[:3]:  # Show first 3
        print(f"   📸 {sample.file_name}: confidence={sample['confidence']:.3f}")


def demonstrate_individual_metadata_filters(dataset: DatasetTable) -> None:
    """Demonstrate filtering with individually-added metadata."""
    print("\n Individual Metadata Filters:")
    print("=" * 50)

    # Filter by special metadata
    print("\n1. Filter by special metadata (individually added):")
    filter_special = SampleFilter(
        metadata_filters=[Metadata("special_metadata") == "sample_1_special"]
    )
    samples = dataset.get_samples(filters=filter_special)
    print(f"   Found {len(samples)} samples with special metadata")
    for sample in samples:
        print(f" {sample.file_name}: {sample['special_metadata']}")

    # Filter by priority
    print("\n2. Filter by high priority (> 7):")
    filter_priority = SampleFilter(metadata_filters=[Metadata("priority") > 7])  # noqa PLR2004
    samples = dataset.get_samples(filters=filter_priority)
    print(f"   Found {len(samples)} samples with priority > 7")
    for sample in samples:
        print(f" {sample.file_name}: priority={sample['priority']}")

    # Filter by custom GPS
    print("\n3. Filter by custom GPS coordinates:")
    filter_custom_gps = SampleFilter(
        metadata_filters=[Metadata("custom_gps.lat") > 40.8]  # noqa PLR2004
    )
    samples = dataset.get_samples(filters=filter_custom_gps)
    print(f"   Found {len(samples)} samples with custom GPS lat > 40.8")
    for sample in samples:
        gps = sample["custom_gps"]
        print(f" {sample.file_name}: lat={gps.lat:.4f}, lon={gps.lon:.4f}")


def demonstrate_combined_filters(dataset: DatasetTable) -> None:
    """Demonstrate combining multiple filters."""
    print("\n Combined Filters:")
    print("=" * 50)

    # Multiple conditions
    print("\n1. Find high-confidence, processed, warm images:")
    filter_combined = SampleFilter(
        metadata_filters=[
            Metadata("confidence") > 0.8,  # noqa PLR2004
            Metadata("is_processed") == True,  # noqa E712
            Metadata("temperature") > 25,  # noqa PLR2004
        ]
    )
    samples = dataset.get_samples(filters=filter_combined)
    print(f"   Found {len(samples)} samples matching all criteria")
    for sample in samples[:3]:
        print(
            f" {sample.file_name}: conf={sample['confidence']:.2f}, "
            f"temp={sample['temperature']}, processed={sample['is_processed']}"
        )

    # Complex GPS + other filters
    print("\n2. Find northern hemisphere, high-confidence images:")
    filter_gps_combined = SampleFilter(
        metadata_filters=[
            Metadata("gps_coordinates.lat") > 0,  # Northern hemisphere
            Metadata("confidence") > 0.85,  # noqa PLR2004
            Metadata("location") == "city",
        ]
    )
    samples = dataset.get_samples(filters=filter_gps_combined)
    print(f"   Found {len(samples)} samples in northern hemisphere cities with high confidence")
    for sample in samples[:3]:
        gps = sample["gps_coordinates"]
        print(f" {sample.file_name}: lat={gps.lat:.4f}, conf={sample['confidence']:.2f}")


def demonstrate_dictionary_like_access(session: Session, sample_ids: list[UUID]) -> None:
    """Demonstrate adding metadata using dictionary-like access."""
    print("\n Dictionary-like Metadata Access:")
    print("=" * 50)

    # Get the first few samples to demonstrate
    samples = sample_resolver.get_many_by_id(session, sample_ids[:2])

    print("\n1. Adding metadata using sample['key'] = value syntax:")

    # Add different types of metadata to different samples
    samples[0]["temperature"] = 25
    samples[0]["location"] = "city"
    samples[0]["is_processed"] = True
    samples[0]["confidence"] = 0.95
    print(
        f" {samples[0].file_name}: temp={samples[0]['temperature']}°C, "
        f"location={samples[0]['location']},"
        f" processed={samples[0]['is_processed']}"
    )

    samples[1]["temperature"] = 15
    samples[1]["location"] = "mountain"
    samples[1]["gps_coordinates"] = GPSCoordinate(lat=40.7128, lon=-74.0060)
    samples[1]["tags"] = ["outdoor", "nature", "landscape"]
    print(
        f" {samples[1].file_name}: temp={samples[1]['temperature']}°C, "
        f"location={samples[1]['location']}, tags={samples[1]['tags']}"
    )

    # Demonstrate reading metadata
    print("\n2. Reading metadata using sample['key'] syntax:")
    for sample in samples:
        print(f" {sample.file_name}:")
        print(f"      Temperature: {sample['temperature']}°C")
        print(f"      Location: {sample['location']}")
        gps = sample["gps_coordinates"]
        print(f"      GPS: lat={gps.lat:.4f}, lon={gps.lon:.4f}")
        print(f"      Tags: {sample['tags']}")

    # Demonstrate None return for missing keys
    print("  Note: sample['key'] returns None for missing keys")
    missing_value = samples[0]["nonexistent_key"]
    if missing_value is None:
        print(f" sample['nonexistent_key']: {missing_value}")

    print(f"✅ Added metadata to {len(samples)} samples using dictionary-like access")

    # Demonstrate schema presentation
    try:
        samples[0]["temperature"] = "string_value"  # Invalid type for demonstration
        print(f" ❌ This should not print: {missing_value}")
    except ValueError:
        print(" ✅ Correctly raised ValueError for invalid type")


def main() -> None:
    """Main function to demonstrate  metadata functionality."""
    try:
        # Load existing dataset
        dataset, sample_ids, loader = load_existing_dataset()

        with db_manager.session() as session:
            # Add bulk metadata
            add_bulk_metadata(session, sample_ids)

            # Add individual metadata
            add_individual_metadata(session, sample_ids)

            # Demonstrate different types of filtering
            demonstrate_bulk_metadata_filters(dataset)
            demonstrate_individual_metadata_filters(dataset)
            demonstrate_combined_filters(dataset)
            demonstrate_dictionary_like_access(session, sample_ids)

            loader.start_gui()

    except ValueError as e:
        print(f"❌ Error: {e}")
        print("\n💡 Make sure to set the DATASET_PATH environment variable:")
        print("   export DATASET_PATH=/path/to/your/yolo/dataset/data.yaml")
        print("   export PURPLE_DATASET_SPLIT=test")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")


if __name__ == "__main__":
    main()
