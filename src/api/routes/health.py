"""Health and status API routes."""

from fastapi import APIRouter
from datetime import datetime
from src import __version__
from src.config import get_config

router = APIRouter(prefix="/api/v1", tags=["health"])
config = get_config()


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": __version__,
        "environment": "production" if not config.DEBUG else "development",
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/status")
async def status():
    """Get application status."""
    return {
        "api_version": __version__,
        "qdrant_url": config.QDRANT_URL,
        "collection_name": config.QDRANT_COLLECTION_NAME,
        "debug": config.DEBUG,
        "timestamp": datetime.utcnow().isoformat()
    }
