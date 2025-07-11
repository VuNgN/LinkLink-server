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

__all__ = ["router", "auth_router", "images_router", "posters_router"]
