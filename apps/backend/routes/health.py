"""System health check route."""
from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def health() -> dict[str, str]:
    """Return basic service status."""
    return {"status": "ok"}
