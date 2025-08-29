"""Common type definitions for the lightly_purple package."""

from typing import TypeVar

from sqlmodel.sql.expression import SelectOfScalar

from lightly_purple.models.annotation.annotation_base import AnnotationBaseTable
from lightly_purple.models.sample import SampleTable

# Generic query type for filters that work with both data queries and count queries
QueryType = TypeVar(
    "QueryType",
    SelectOfScalar[AnnotationBaseTable],
    SelectOfScalar[SampleTable],
    SelectOfScalar[int],
)
