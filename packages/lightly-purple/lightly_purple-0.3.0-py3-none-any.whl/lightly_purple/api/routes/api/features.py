"""This module contains the API routes for active features."""

from __future__ import annotations

from fastapi import APIRouter

from lightly_purple.api.features import purple_active_features

__all__ = ["features_router", "purple_active_features"]

features_router = APIRouter()


@features_router.get("/features")
def get_features() -> list[str]:
    """Get the list of active features in the Purple app."""
    return purple_active_features
