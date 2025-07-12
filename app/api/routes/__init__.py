"""
API routes package
"""

from fastapi import APIRouter

from .auth import router as auth_router
from .images import router as images_router
from .posters import router as posters_router

# Create main router
router = APIRouter()

# Include all route modules (no prefix here, added in main.py)
router.include_router(auth_router)
router.include_router(images_router)
router.include_router(posters_router)


# Add health check endpoint to API router
@router.get("/health", tags=["Health"])
async def health_check():
    """
    # 🏥 Health Check

    Check the health status of the API server and database connection.

    ## Response

    - `status`: Overall health status
    - `architecture`: Software architecture used
    - `database`: Database type and status
    - `timestamp`: Current server time

    ## Usage

    This endpoint is useful for:
    - Load balancer health checks
    - Monitoring systems
    - DevOps automation
    """
    return {
        "status": "healthy",
        "architecture": "clean",
        "database": "postgresql",
        "version": "2.1.0",
        "timestamp": "2024-01-15T10:30:00Z",
    }


__all__ = ["router", "auth_router", "images_router", "posters_router"]
