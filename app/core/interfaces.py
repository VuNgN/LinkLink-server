"""
Repository interfaces - Abstract base classes for data access
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional

from .entities import ArchivedPoster, Image, Token, User, UserStatus


class UserRepository(ABC):
    """Abstract user repository interface"""

    @abstractmethod
    async def create(self, user: User) -> User:
        """Create a new user"""
        pass

    @abstractmethod
    async def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        pass

    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        pass

    @abstractmethod
    async def get_by_status(self, status: UserStatus) -> List[User]:
        """Get users by status (pending, approved, rejected)"""
        pass

    @abstractmethod
    async def update(self, user: User) -> User:
        """Update user"""
        pass

    @abstractmethod
    async def delete(self, username: str) -> bool:
        """Delete user"""
        pass


class ImageRepository(ABC):
    """Abstract image repository interface"""

    @abstractmethod
    async def create(self, image: Image) -> Image:
        """Create a new image record"""
        pass

    @abstractmethod
    async def get_by_filename(self, filename: str) -> Optional[Image]:
        """Get image by filename"""
        pass

    @abstractmethod
    async def get_by_username(self, username: str) -> List[Image]:
        """Get all images for a user"""
        pass

    @abstractmethod
    async def delete(self, filename: str) -> bool:
        """Delete image"""
        pass


class TokenRepository(ABC):
    """Abstract token repository interface"""

    @abstractmethod
    async def store_refresh_token(self, token: str, username: str) -> bool:
        """Store refresh token"""
        pass

    @abstractmethod
    async def get_username_by_refresh_token(self, token: str) -> Optional[str]:
        """Get username by refresh token"""
        pass

    @abstractmethod
    async def delete_refresh_token(self, token: str) -> bool:
        """Delete refresh token"""
        pass


class FileStorage(ABC):
    """Abstract file storage interface"""

    @abstractmethod
    async def save_file(self, file_content: bytes, filename: str) -> str:
        """Save file and return file path"""
        pass

    @abstractmethod
    async def delete_file(self, file_path: str) -> bool:
        """Delete file"""
        pass

    @abstractmethod
    async def file_exists(self, file_path: str) -> bool:
        """Check if file exists"""
        pass


class RefreshTokenRepository(ABC):
    """Abstract refresh token repository interface"""

    @abstractmethod
    async def create(self, token: str, username: str, expires_at: datetime) -> bool:
        """Create a new refresh token"""
        pass

    @abstractmethod
    async def get_by_token(self, token: str):
        """Get refresh token by token string"""
        pass

    @abstractmethod
    async def delete_by_token(self, token: str) -> bool:
        """Delete refresh token by token string"""
        pass


class PosterRepository(ABC):
    """Abstract poster repository interface"""

    @abstractmethod
    async def create(self, poster):
        """Create a new poster"""
        pass

    @abstractmethod
    async def get_by_id(self, poster_id: int):
        """Get poster by id"""
        pass

    @abstractmethod
    async def get_by_username(self, username: str) -> list:
        """Get all posters for a user (not deleted)"""
        pass

    @abstractmethod
    async def update(self, poster):
        """Update poster"""
        pass

    @abstractmethod
    async def delete(self, poster_id: int) -> bool:
        """Soft delete poster by id (set is_deleted)"""
        pass

    @abstractmethod
    async def restore(self, poster_id: int, username: str) -> bool:
        """Restore a soft-deleted poster (set is_deleted to False)"""
        pass

    @abstractmethod
    async def get_deleted(self, username: str) -> list:
        """Get all deleted posters for a user"""
        pass

    @abstractmethod
    async def hard_delete(self, poster_id: int) -> bool:
        """Permanently delete poster by id"""
        pass

    @abstractmethod
    async def hard_delete_all_deleted(self, username: str) -> int:
        """Permanently delete all deleted posters for a user, return count"""
        pass

    @abstractmethod
    async def archive_and_hard_delete(
        self, poster_id: int, archived_repo
    ) -> ArchivedPoster:
        """Archive poster metadata then hard delete"""
        pass

    @abstractmethod
    async def archive_and_hard_delete_all_deleted(
        self, username: str, archived_repo
    ) -> int:
        """Archive all deleted posters metadata then hard delete, return count"""
        pass


class ArchivedPosterRepository(ABC):
    """Abstract archived poster repository interface"""

    @abstractmethod
    async def create(self, archived_poster):
        """Create a new archived poster record"""
        pass

    @abstractmethod
    async def get_by_username(self, username: str) -> list:
        """Get all archived posters for a user"""
        pass

    @abstractmethod
    async def get_by_original_id(self, original_id: int):
        """Get archived poster by original ID"""
        pass
