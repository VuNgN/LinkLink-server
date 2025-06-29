"""
Dependency injection setup with PostgreSQL support
"""
import os
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi_mail import ConnectionConfig
from typing import Optional

from ..core.services import AuthService, ImageService, EmailService
from ..core.entities import User
from ..infrastructure.database import get_db_session, AsyncSession
from ..infrastructure.postgresql_repositories import (
    PostgreSQLUserRepository,
    PostgreSQLImageRepository,
    PostgreSQLTokenRepository,
    PostgreSQLRefreshTokenRepository
)
from ..infrastructure.repositories import LocalFileStorage

# Security
security = HTTPBearer()

# File storage (still local for now)
_file_storage = LocalFileStorage()

# Email configuration
def get_email_config() -> ConnectionConfig:
    """Get email configuration"""
    return ConnectionConfig(
        MAIL_USERNAME=os.getenv("MAIL_USERNAME", "your-email@gmail.com"),
        MAIL_PASSWORD=os.getenv("MAIL_PASSWORD", "your-app-password"),
        MAIL_FROM=os.getenv("MAIL_FROM", "your-email@gmail.com"),
        MAIL_PORT=int(os.getenv("MAIL_PORT", "587")),
        MAIL_SERVER=os.getenv("MAIL_SERVER", "smtp.gmail.com"),
        MAIL_STARTTLS=True,
        MAIL_SSL_TLS=False,
        USE_CREDENTIALS=True
    )

async def get_user_repository(session: AsyncSession = Depends(get_db_session)) -> PostgreSQLUserRepository:
    """Get user repository with database session"""
    return PostgreSQLUserRepository(session)

async def get_image_repository(session: AsyncSession = Depends(get_db_session)) -> PostgreSQLImageRepository:
    """Get image repository with database session"""
    return PostgreSQLImageRepository(session)

async def get_token_repository(session: AsyncSession = Depends(get_db_session)) -> PostgreSQLTokenRepository:
    """Get token repository with database session"""
    return PostgreSQLTokenRepository(session)

async def get_refresh_token_repository(session: AsyncSession = Depends(get_db_session)) -> PostgreSQLRefreshTokenRepository:
    """Get refresh token repository with database session"""
    return PostgreSQLRefreshTokenRepository(session)

def get_file_storage() -> LocalFileStorage:
    """Get file storage instance"""
    return _file_storage

async def get_email_service() -> EmailService:
    """Get email service instance"""
    config = get_email_config()
    return EmailService(config)

async def get_auth_service(
    user_repo: PostgreSQLUserRepository = Depends(get_user_repository),
    refresh_token_repo: PostgreSQLRefreshTokenRepository = Depends(get_refresh_token_repository),
    email_service: EmailService = Depends(get_email_service)
) -> AuthService:
    """Get auth service instance with PostgreSQL repositories"""
    return AuthService(
        user_repository=user_repo,
        refresh_token_repository=refresh_token_repo,
        email_service=email_service,
        secret_key=os.getenv("SECRET_KEY", "your-secret-key-change-this-in-production"),
        admin_email=os.getenv("ADMIN_EMAIL", "admin@example.com")
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
    
    try:
        username = auth_service.verify_token(credentials.credentials)
        user = await auth_service.user_repository.get_by_username(username)
        if not user or not user.is_active or user.status.value != "approved":
            raise credentials_exception
        return user
    except ValueError:
        raise credentials_exception

async def get_current_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """Get current admin user - raises 401 if user is not admin"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user 