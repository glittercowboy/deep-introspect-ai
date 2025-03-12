"""
Health check API routes.
"""
import logging
from typing import Any
from fastapi import APIRouter
from app.core.config import settings

router = APIRouter(tags=["Health"])
logger = logging.getLogger(__name__)


@router.get("/health")
async def health_check() -> Any:
    """
    Simple health check endpoint.
    
    Returns:
        Health status
    """
    return {
        "status": "healthy",
        "version": "0.1.0",
        "app_name": settings.PROJECT_NAME
    }
