"""Resolver for operations for setting metadata."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from sqlmodel import Session

from lightly_purple.metadata.complex_metadata import serialize_complex_metadata
from lightly_purple.models.metadata import (
    SampleMetadataTable,
    get_type_name,
)


def bulk_set_metadata(
    session: Session,
    sample_metadata: list[tuple[UUID, dict[str, Any]]],
) -> None:
    """Bulk insert metadata for multiple samples.

    Args:
        session: The database session.
        sample_metadata: List of (sample_id, metadata_dict) tuples.
    """
    now = datetime.now(timezone.utc)
    objects = []
    for sample_id, metadata in sample_metadata:
        metadata_schema = {}
        serialized_data = {}
        for key, value in metadata.items():
            # Serialize complex metadata objects.
            serialized_data[key] = serialize_complex_metadata(value)
            # Get the type name
            metadata_schema[key] = get_type_name(value)

        obj = SampleMetadataTable(
            sample_id=sample_id,
            data=serialized_data,
            metadata_schema=metadata_schema,
            created_at=now,
            updated_at=now,
        )
        objects.append(obj)
    session.bulk_save_objects(objects)
    session.commit()
