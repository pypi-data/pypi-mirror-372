"""This module contains the FastAPI app configuration."""

from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import APIRouter, Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.routing import APIRoute
from sqlmodel import Session
from typing_extensions import Annotated

from lightly_purple.api.db import db_manager
from lightly_purple.api.routes import healthz, images, webapp
from lightly_purple.api.routes.api import (
    annotation,
    annotation_label,
    annotation_task,
    classifier,
    dataset,
    dataset_tag,
    features,
    metadata,
    metrics,
    sample,
    settings,
    text_embedding,
)
from lightly_purple.api.routes.api.exceptions import (
    register_exception_handlers,
)
from lightly_purple.dataset.env import PURPLE_DEBUG

SessionDep = Annotated[Session, Depends(db_manager.session)]


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None, None]:
    """Lifespan context for initializing and cleaning up resources.

    Args:
        _: The FastAPI application instance.

    Yields:
        None when the application is ready.
    """
    yield


if PURPLE_DEBUG:
    import logging

    logging.basicConfig()
    logger = logging.getLogger("sqlalchemy.engine")
    logger.setLevel(logging.DEBUG)

"""Create the FastAPI app."""
app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def use_route_names_as_operation_ids(app: FastAPI) -> None:
    """Use API function name for operation IDs.

    Should be called only after all routes have been added.
    """
    for route in app.routes:
        if isinstance(route, APIRoute):
            route.operation_id = route.name  # in this case, 'read_items'


register_exception_handlers(app)

# api routes
api_router = APIRouter(prefix="/api", tags=["api"])

api_router.include_router(dataset.dataset_router)
api_router.include_router(dataset_tag.tag_router)
api_router.include_router(sample.samples_router)
api_router.include_router(annotation_label.annotations_label_router)
api_router.include_router(annotation.annotations_router)
api_router.include_router(text_embedding.text_embedding_router)
api_router.include_router(annotation_task.router)
api_router.include_router(settings.settings_router)
api_router.include_router(classifier.classifier_router)
api_router.include_router(features.features_router)
api_router.include_router(metadata.metadata_router)
api_router.include_router(metrics.metrics_router)


app.include_router(api_router)
# images serving
app.include_router(images.app_router, prefix="/images")


# health status check
app.include_router(healthz.health_router)

# webapp routes
app.include_router(webapp.app_router)

use_route_names_as_operation_ids(app)
