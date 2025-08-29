"""Module provides functions to initialize and manage the DuckDB."""

from lightly_purple.models.annotation.annotation_base import (
    AnnotationBaseTable,  # noqa: F401, required for SQLModel to work properly
)
from lightly_purple.models.annotation_label import (
    AnnotationLabelTable,  # noqa: F401, required for SQLModel to work properly
)
from lightly_purple.models.annotation_task import (
    AnnotationTaskTable,  # noqa: F401, required for SQLModel to work properly
)
from lightly_purple.models.dataset import (
    DatasetTable,  # noqa: F401, required for SQLModel to work properly
)
from lightly_purple.models.embedding_model import (
    EmbeddingModelTable,  # noqa: F401, required for SQLModel to work properly
)
from lightly_purple.models.metadata import (
    SampleMetadataTable,  # noqa: F401, required for SQLModel to work properly
)
from lightly_purple.models.sample import (
    SampleTable,  # noqa: F401, required for SQLModel to work properly
)
from lightly_purple.models.sample_embedding import (
    SampleEmbeddingTable,  # noqa: F401, required for SQLModel to work properly
)
from lightly_purple.models.settings import (
    SettingTable,  # noqa: F401, required for SQLModel to work properly
)
from lightly_purple.models.tag import (
    TagTable,  # noqa: F401, required for SQLModel to work properly
)
