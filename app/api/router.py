from __future__ import annotations

from fastapi import APIRouter

from app.api.routes.evaluations import (
    router as evaluations_router,
)
from app.api.routes.health import (
    router as health_router,
)


api_router = APIRouter()

api_router.include_router(
    health_router
)

api_router.include_router(
    evaluations_router
)