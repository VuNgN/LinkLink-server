"""
PostgreSQL repository implementations
"""
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload
from datetime import datetime, timedelta

from ..core.interfaces import UserRepository, ImageRepository, TokenRepository, RefreshTokenRepository
from ..core.entities import User, Image, UserStatus
from .models import UserModel, ImageModel, RefreshTokenModel

class PostgreSQLUserRepository(UserRepository):
    """PostgreSQL user repository implementation"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, user: User) -> User:
        """Create a new user"""
        db_user = UserModel(
            username=user.username,
            email=user.email,
            hashed_password=user.hashed_password,
            is_active=user.is_active,
            is_admin=user.is_admin,
            status=user.status.value,
            created_at=user.created_at,
            updated_at=user.updated_at,
            approved_at=user.approved_at,
            approved_by=user.approved_by
        )
        self.session.add(db_user)
        await self.session.commit()
        await self.session.refresh(db_user)
        
        return User(
            username=db_user.username,
            email=db_user.email,
            hashed_password=db_user.hashed_password,
            is_active=db_user.is_active,
            is_admin=db_user.is_admin,
            status=UserStatus(db_user.status),
            created_at=db_user.created_at,
            updated_at=db_user.updated_at,
            approved_at=db_user.approved_at,
            approved_by=db_user.approved_by
        )
    
    async def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        result = await self.session.execute(
            select(UserModel).where(UserModel.username == username)
        )
        db_user = result.scalar_one_or_none()
        
        if not db_user:
            return None
        
        return User(
            username=db_user.username,
            email=db_user.email,
            hashed_password=db_user.hashed_password,
            is_active=db_user.is_active,
            is_admin=db_user.is_admin,
            status=UserStatus(db_user.status),
            created_at=db_user.created_at,
            updated_at=db_user.updated_at,
            approved_at=db_user.approved_at,
            approved_by=db_user.approved_by
        )
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        result = await self.session.execute(
            select(UserModel).where(UserModel.email == email)
        )
        db_user = result.scalar_one_or_none()
        
        if not db_user:
            return None
        
        return User(
            username=db_user.username,
            email=db_user.email,
            hashed_password=db_user.hashed_password,
            is_active=db_user.is_active,
            is_admin=db_user.is_admin,
            status=UserStatus(db_user.status),
            created_at=db_user.created_at,
            updated_at=db_user.updated_at,
            approved_at=db_user.approved_at,
            approved_by=db_user.approved_by
        )
    
    async def get_by_status(self, status: UserStatus) -> List[User]:
        """Get users by status"""
        result = await self.session.execute(
            select(UserModel).where(UserModel.status == status.value)
        )
        db_users = result.scalars().all()
        
        return [
            User(
                username=user.username,
                email=user.email,
                hashed_password=user.hashed_password,
                is_active=user.is_active,
                is_admin=user.is_admin,
                status=UserStatus(user.status),
                created_at=user.created_at,
                updated_at=user.updated_at,
                approved_at=user.approved_at,
                approved_by=user.approved_by
            )
            for user in db_users
        ]
    
    async def update(self, user: User) -> User:
        """Update user"""
        result = await self.session.execute(
            select(UserModel).where(UserModel.username == user.username)
        )
        db_user = result.scalar_one_or_none()
        
        if not db_user:
            raise ValueError("User not found")
        
        db_user.email = user.email
        db_user.hashed_password = user.hashed_password
        db_user.is_active = user.is_active
        db_user.is_admin = user.is_admin
        db_user.status = user.status.value
        db_user.updated_at = datetime.utcnow()
        db_user.approved_at = user.approved_at
        db_user.approved_by = user.approved_by
        
        await self.session.commit()
        await self.session.refresh(db_user)
        
        return User(
            username=db_user.username,
            email=db_user.email,
            hashed_password=db_user.hashed_password,
            is_active=db_user.is_active,
            is_admin=db_user.is_admin,
            status=UserStatus(db_user.status),
            created_at=db_user.created_at,
            updated_at=db_user.updated_at,
            approved_at=db_user.approved_at,
            approved_by=db_user.approved_by
        )
    
    async def delete(self, username: str) -> bool:
        """Delete user"""
        result = await self.session.execute(
            delete(UserModel).where(UserModel.username == username)
        )
        await self.session.commit()
        return result.rowcount > 0

class PostgreSQLImageRepository(ImageRepository):
    """PostgreSQL image repository implementation"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, image: Image) -> Image:
        """Create a new image record"""
        db_image = ImageModel(
            filename=image.filename,
            original_filename=image.original_filename,
            username=image.username,
            file_path=image.file_path,
            file_size=image.file_size,
            content_type=image.content_type,
            upload_date=image.upload_date
        )
        self.session.add(db_image)
        await self.session.commit()
        await self.session.refresh(db_image)
        
        return Image(
            filename=db_image.filename,
            original_filename=db_image.original_filename,
            username=db_image.username,
            file_path=db_image.file_path,
            file_size=db_image.file_size,
            content_type=db_image.content_type,
            upload_date=db_image.upload_date
        )
    
    async def get_by_filename(self, filename: str) -> Optional[Image]:
        """Get image by filename"""
        result = await self.session.execute(
            select(ImageModel).where(ImageModel.filename == filename)
        )
        db_image = result.scalar_one_or_none()
        
        if not db_image:
            return None
        
        return Image(
            filename=db_image.filename,
            original_filename=db_image.original_filename,
            username=db_image.username,
            file_path=db_image.file_path,
            file_size=db_image.file_size,
            content_type=db_image.content_type,
            upload_date=db_image.upload_date
        )
    
    async def get_by_username(self, username: str) -> List[Image]:
        """Get all images for a user"""
        result = await self.session.execute(
            select(ImageModel)
            .where(ImageModel.username == username)
            .order_by(ImageModel.upload_date.desc())
        )
        db_images = result.scalars().all()
        
        return [
            Image(
                filename=img.filename,
                original_filename=img.original_filename,
                username=img.username,
                file_path=img.file_path,
                file_size=img.file_size,
                content_type=img.content_type,
                upload_date=img.upload_date
            )
            for img in db_images
        ]
    
    async def delete(self, filename: str) -> bool:
        """Delete image"""
        result = await self.session.execute(
            delete(ImageModel).where(ImageModel.filename == filename)
        )
        await self.session.commit()
        return result.rowcount > 0

class PostgreSQLTokenRepository(TokenRepository):
    """PostgreSQL token repository implementation"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def store_refresh_token(self, token: str, username: str) -> bool:
        """Store refresh token"""
        # Set expiration to 7 days from now
        expires_at = datetime.utcnow() + timedelta(days=7)
        
        db_token = RefreshTokenModel(
            token=token,
            username=username,
            expires_at=expires_at
        )
        self.session.add(db_token)
        await self.session.commit()
        return True
    
    async def get_username_by_refresh_token(self, token: str) -> Optional[str]:
        """Get username by refresh token"""
        result = await self.session.execute(
            select(RefreshTokenModel)
            .where(RefreshTokenModel.token == token)
            .where(RefreshTokenModel.expires_at > datetime.utcnow())
        )
        db_token = result.scalar_one_or_none()
        
        return db_token.username if db_token else None
    
    async def delete_refresh_token(self, token: str) -> bool:
        """Delete refresh token"""
        result = await self.session.execute(
            delete(RefreshTokenModel).where(RefreshTokenModel.token == token)
        )
        await self.session.commit()
        return result.rowcount > 0
    
    async def cleanup_expired_tokens(self) -> int:
        """Clean up expired refresh tokens"""
        result = await self.session.execute(
            delete(RefreshTokenModel).where(RefreshTokenModel.expires_at <= datetime.utcnow())
        )
        await self.session.commit()
        return result.rowcount

class PostgreSQLRefreshTokenRepository(RefreshTokenRepository):
    """PostgreSQL refresh token repository implementation"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, token: str, username: str, expires_at: datetime) -> bool:
        """Create a new refresh token"""
        db_token = RefreshTokenModel(
            token=token,
            username=username,
            expires_at=expires_at
        )
        self.session.add(db_token)
        await self.session.commit()
        return True
    
    async def get_by_token(self, token: str):
        """Get refresh token by token string"""
        result = await self.session.execute(
            select(RefreshTokenModel).where(RefreshTokenModel.token == token)
        )
        return result.scalar_one_or_none()
    
    async def delete_by_token(self, token: str) -> bool:
        """Delete refresh token by token string"""
        result = await self.session.execute(
            delete(RefreshTokenModel).where(RefreshTokenModel.token == token)
        )
        await self.session.commit()
        return result.rowcount > 0 