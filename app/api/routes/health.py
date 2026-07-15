from __future__ import annotations

from fastapi import APIRouter


router = APIRouter(
    prefix="/health",
    tags=["health"],
)


@router.get("")
def health_check() -> dict[str, str]:
    """
    Return the current API health status.
    """

    return {
        "status": "healthy",
    }