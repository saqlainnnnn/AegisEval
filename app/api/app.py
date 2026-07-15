from __future__ import annotations

from fastapi import FastAPI

from app.api.router import api_router
from app.core.config import get_settings


def create_app() -> FastAPI:
    """
    Create and configure the AegisEval API application.
    """

    settings = get_settings()

    application = FastAPI(
        title=settings.app_name,
        description=(
            "Evaluation and regression testing platform "
            "for AI and RAG systems."
        ),
        version=settings.app_version,
    )

    application.include_router(
        api_router,
        prefix="/api/v1",
    )

    return application