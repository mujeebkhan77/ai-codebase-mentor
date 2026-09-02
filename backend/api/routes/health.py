from fastapi import APIRouter
from api.models import HealthResponse

router = APIRouter(tags=["Health"])


@router.get("/api/health", response_model=HealthResponse)
def get_health():
    """Health check endpoint for the backend API."""
    return HealthResponse(status="ok", version="1.0.0")
