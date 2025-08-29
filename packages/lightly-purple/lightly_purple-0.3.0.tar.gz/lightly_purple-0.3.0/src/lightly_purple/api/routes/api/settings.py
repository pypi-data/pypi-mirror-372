"""This module contains the API routes for user settings."""

from fastapi import APIRouter, Depends
from sqlmodel import Session
from typing_extensions import Annotated

from lightly_purple.api.db import get_session
from lightly_purple.models.settings import SettingView
from lightly_purple.resolvers import settings_resolver

settings_router = APIRouter(tags=["settings"])

SessionDep = Annotated[Session, Depends(get_session)]


@settings_router.get("/settings")
def get_settings(
    session: SessionDep,
) -> SettingView:
    """Get the current settings.

    Args:
        session: Database session.

    Returns:
        The current settings.
    """
    return settings_resolver.get_settings(session=session)


@settings_router.post("/settings")
def set_settings(
    settings: SettingView,
    session: SessionDep,
) -> SettingView:
    """Update user settings.

    Args:
        settings: New settings to apply.
        session: Database session.

    Returns:
        Updated settings.
    """
    return settings_resolver.set_settings(session=session, settings=settings)
