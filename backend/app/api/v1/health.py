"""Health check endpoint (v1)."""

from fastapi import APIRouter

router = APIRouter()

@router.get("/health", summary="Health check")
def health_check():
    """Return a basic service liveness payload."""
    return {
        "status": "ok",
        "service": "erp-incident-triage-api"
    }
