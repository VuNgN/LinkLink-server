"""
Dependency injection setup with PostgreSQL support
"""

import os
from typing import Optional

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.security.utils import get_authorization_scheme_param
from fastapi_mail import ConnectionConfig

from ..config import settings
from ..core.entities import User
from ..core.services import (AuthService, EmailService, ImageService,
                             PosterService)
from ..infrastructure.database import AsyncSession, get_db_session
from ..infrastructure.repositories import (LocalFileStorage,
                                           PostgreSQLArchivedPosterRepository,
                                           PostgreSQLImageRepository,
                                           PostgreSQLPosterRepository,
                                           PostgreSQLRefreshTokenRepository,
                                           PostgreSQLTokenRepository,
                                           PostgreSQLUserRepository)

# Security
security = HTTPBearer()

# File storage (still local for now)
_file_storage = LocalFileStorage()


# Email configuration
def get_email_config() -> ConnectionConfig:
    """Get email configuration from settings"""
    return ConnectionConfig(
        MAIL_USERNAME=settings.MAIL_USERNAME,
        MAIL_PASSWORD=settings.MAIL_PASSWORD,
        MAIL_FROM=settings.MAIL_FROM,
        MAIL_PORT=settings.MAIL_PORT,
        MAIL_SERVER=settings.MAIL_SERVER,
        MAIL_STARTTLS=settings.MAIL_STARTTLS,
        MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
        USE_CREDENTIALS=settings.USE_CREDENTIALS,
    )


async def get_user_repository(
    session: AsyncSession = Depends(get_db_session),
) -> PostgreSQLUserRepository:
    """Get user repository with database session"""
    return PostgreSQLUserRepository(session)


async def get_image_repository(
    session: AsyncSession = Depends(get_db_session),
) -> PostgreSQLImageRepository:
    """Get image repository with database session"""
    return PostgreSQLImageRepository(session)


async def get_token_repository(
    session: AsyncSession = Depends(get_db_session),
) -> PostgreSQLTokenRepository:
    """Get token repository with database session"""
    return PostgreSQLTokenRepository(session)


async def get_refresh_token_repository(
    session: AsyncSession = Depends(get_db_session),
) -> PostgreSQLRefreshTokenRepository:
    """Get refresh token repository with database session"""
    return PostgreSQLRefreshTokenRepository(session)


async def get_poster_repository(
    session: AsyncSession = Depends(get_db_session),
) -> PostgreSQLPosterRepository:
    """Get poster repository with database session"""
    return PostgreSQLPosterRepository(session)


async def get_archived_poster_repository(
    session: AsyncSession = Depends(get_db_session),
) -> PostgreSQLArchivedPosterRepository:
    """Get archived poster repository with database session"""
    return PostgreSQLArchivedPosterRepository(session)


def get_file_storage() -> LocalFileStorage:
    """Get file storage instance"""
    return _file_storage


async def get_email_service() -> EmailService:
    """Get email service instance"""
    config = get_email_config()

    # Check if email is properly configured
    if (
        config.MAIL_USERNAME == "your-email@gmail.com"
        or config.MAIL_PASSWORD == "your-app-password"
        or config.MAIL_FROM == "your-email@gmail.com"
    ):
        # Return a mock email service that does nothing
        from ..core.services.email_service import MockEmailService

        return MockEmailService()

    return EmailService(config)


async def get_auth_service(
    user_repo: PostgreSQLUserRepository = Depends(get_user_repository),
    refresh_token_repo: PostgreSQLRefreshTokenRepository = Depends(
        get_refresh_token_repository
    ),
    email_service: EmailService = Depends(get_email_service),
) -> AuthService:
    """Get auth service instance with PostgreSQL repositories"""
    return AuthService(
        user_repository=user_repo,
        refresh_token_repository=refresh_token_repo,
        email_service=email_service,
        secret_key=settings.SECRET_KEY,
        admin_email=settings.ADMIN_EMAIL,
    )


async def get_image_service(
    image_repo: PostgreSQLImageRepository = Depends(get_image_repository),
    file_storage: LocalFileStorage = Depends(get_file_storage),
) -> ImageService:
    """Get image service instance with PostgreSQL repositories"""
    return ImageService(
        image_repo=image_repo,
        file_storage=file_storage,
        upload_dir="uploads",
        max_file_size=10 * 1024 * 1024,  # 10MB
        allowed_types=["image/jpeg", "image/png", "image/gif", "image/webp"],
    )


async def get_poster_service(
    poster_repo: PostgreSQLPosterRepository = Depends(get_poster_repository),
    archived_repo: PostgreSQLArchivedPosterRepository = Depends(
        get_archived_poster_repository
    ),
    file_storage: LocalFileStorage = Depends(get_file_storage),
) -> PosterService:
    """Get poster service instance with PostgreSQL repositories"""
    return PosterService(
        poster_repo=poster_repo,
        archived_repo=archived_repo,
        file_storage=file_storage,
        upload_dir="uploads",
    )


# TODO: Implement AlbumService dependency when PostgreSQLAlbumRepository is created
# async def get_album_service(
#     image_repo: PostgreSQLImageRepository = Depends(get_image_repository),
# ) -> AlbumService:
#     """Get album service instance with PostgreSQL repositories"""
#     from ..infrastructure.postgresql_repositories import PostgreSQLAlbumRepository
#     album_repo = PostgreSQLAlbumRepository(Depends(get_db_session))
#     return AlbumService(album_repo=album_repo, image_repo=image_repo)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthService = Depends(get_auth_service),
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


async def get_current_admin_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Get current admin user - raises 401 if user is not admin"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required"
        )
    return current_user


# Dependency cho phép trả về None nếu không có token (dùng cho route public)
async def get_optional_user(
    request: Request, auth_service: AuthService = Depends(get_auth_service)
) -> Optional[User]:
    auth = request.headers.get("Authorization") or ""
    scheme, param = get_authorization_scheme_param(auth)
    if not auth or scheme.lower() != "bearer" or not param:
        return None

    # Check if token is valid (not expired)
    try:
        username = auth_service.verify_token(param)
        user = await auth_service.user_repository.get_by_username(username)
        if not user or not user.is_active or user.status.value != "approved":
            return None
        return user
    except ValueError:
        # Token is invalid or expired - return None to trigger refresh
        return None
    except Exception:
        # Other exceptions - return None
        return None


# Quyền riêng tư:
# - public: ai cũng xem được
# - community: chỉ người có tài khoản mới xem được
# - private: chỉ người đăng mới xem được
