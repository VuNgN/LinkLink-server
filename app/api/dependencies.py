"""
Dependency injection setup with PostgreSQL support
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional

from ..core.services import AuthService, ImageService
from ..core.entities import User
from ..infrastructure.database import get_db_session, AsyncSession
from ..infrastructure.postgresql_repositories import (
    PostgreSQLUserRepository,
    PostgreSQLImageRepository,
    PostgreSQLTokenRepository
)
from ..infrastructure.repositories import LocalFileStorage

# Security
security = HTTPBearer()

# File storage (still local for now)
_file_storage = LocalFileStorage()

async def get_user_repository(session: AsyncSession = Depends(get_db_session)) -> PostgreSQLUserRepository:
    """Get user repository with database session"""
    return PostgreSQLUserRepository(session)

async def get_image_repository(session: AsyncSession = Depends(get_db_session)) -> PostgreSQLImageRepository:
    """Get image repository with database session"""
    return PostgreSQLImageRepository(session)

async def get_token_repository(session: AsyncSession = Depends(get_db_session)) -> PostgreSQLTokenRepository:
    """Get token repository with database session"""
    return PostgreSQLTokenRepository(session)

def get_file_storage() -> LocalFileStorage:
    """Get file storage instance"""
    return _file_storage

async def get_auth_service(
    user_repo: PostgreSQLUserRepository = Depends(get_user_repository),
    token_repo: PostgreSQLTokenRepository = Depends(get_token_repository)
) -> AuthService:
    """Get auth service instance with PostgreSQL repositories"""
    return AuthService(
        user_repo=user_repo,
        token_repo=token_repo,
        secret_key="your-secret-key-change-this-in-production",
        algorithm="HS256",
        access_token_expire_minutes=30,
        refresh_token_expire_days=7
    )

async def get_image_service(
    image_repo: PostgreSQLImageRepository = Depends(get_image_repository),
    file_storage: LocalFileStorage = Depends(get_file_storage)
) -> ImageService:
    """Get image service instance with PostgreSQL repositories"""
    return ImageService(
        image_repo=image_repo,
        file_storage=file_storage,
        upload_dir="uploads",
        max_file_size=10 * 1024 * 1024,  # 10MB
        allowed_types=["image/jpeg", "image/png", "image/gif", "image/webp"]
    )

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthService = Depends(get_auth_service)
) -> User:
    """Get current authenticated user"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    user = await auth_service.get_current_user(credentials.credentials)
    if not user:
        raise credentials_exception
    
    return user 