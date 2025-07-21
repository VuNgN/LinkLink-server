"""
Authentication routes package
"""

# Combine all auth routes
from fastapi import APIRouter

from .admin import router as admin_router
from .login import router as login_router
from .register import router as register_router

router = APIRouter()

router.include_router(login_router, tags=["Authentication"])
router.include_router(register_router, tags=["Authentication"])
router.include_router(admin_router, tags=["Admin"])
