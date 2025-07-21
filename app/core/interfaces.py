"""
Repository interfaces - Abstract base classes for data access
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional

from .entities import ArchivedPoster, Image, User, UserStatus


class UserRepository(ABC):
    """Abstract user repository interface"""

    @abstractmethod
    async def create(self, user: User) -> User:
        """Create a new user"""

    @abstractmethod
    async def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""

    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""

    @abstractmethod
    async def get_by_status(self, status: UserStatus) -> List[User]:
        """Get users by status (pending, approved, rejected)"""

    @abstractmethod
    async def update(self, user: User) -> User:
        """Update user"""

    @abstractmethod
    async def delete(self, username: str) -> bool:
        """Delete user"""


class ImageRepository(ABC):
    """Abstract image repository interface"""

    @abstractmethod
    async def create(self, image: Image) -> Image:
        """Create a new image record"""

    @abstractmethod
    async def get_by_filename(self, filename: str) -> Optional[Image]:
        """Get image by filename"""

    @abstractmethod
    async def get_by_username(self, username: str) -> List[Image]:
        """Get all images for a user"""

    @abstractmethod
    async def delete(self, filename: str) -> bool:
        """Delete image"""


class TokenRepository(ABC):
    """Abstract token repository interface"""

    @abstractmethod
    async def store_refresh_token(self, token: str, username: str) -> bool:
        """Store refresh token"""

    @abstractmethod
    async def get_username_by_refresh_token(self, token: str) -> Optional[str]:
        """Get username by refresh token"""

    @abstractmethod
    async def delete_refresh_token(self, token: str) -> bool:
        """Delete refresh token"""


class FileStorage(ABC):
    """Abstract file storage interface"""

    @abstractmethod
    async def save_file(self, file_content: bytes, filename: str) -> str:
        """Save file and return file path"""

    @abstractmethod
    async def delete_file(self, file_path: str) -> bool:
        """Delete file"""

    @abstractmethod
    async def file_exists(self, file_path: str) -> bool:
        """Check if file exists"""


class RefreshTokenRepository(ABC):
    """Abstract refresh token repository interface"""

    @abstractmethod
    async def create(self, token: str, username: str, expires_at: datetime) -> bool:
        """Create a new refresh token"""

    @abstractmethod
    async def get_by_token(self, token: str):
        """Get refresh token by token string"""

    @abstractmethod
    async def delete_by_token(self, token: str) -> bool:
        """Delete refresh token by token string"""


class PosterRepository(ABC):
    """Abstract poster repository interface"""

    @abstractmethod
    async def create(self, poster):
        """Create a new poster"""

    @abstractmethod
    async def get_by_id(self, poster_id: int):
        """Get poster by id"""

    @abstractmethod
    async def get_by_username(self, username: str) -> list:
        """Get all posters for a user (not deleted)"""

    @abstractmethod
    async def update(self, poster):
        """Update poster"""

    @abstractmethod
    async def delete(self, poster_id: int) -> bool:
        """Soft delete poster by id (set is_deleted)"""

    @abstractmethod
    async def restore(self, poster_id: int, username: str) -> bool:
        """Restore a soft-deleted poster (set is_deleted to False)"""

    @abstractmethod
    async def get_deleted(self, username: str) -> list:
        """Get all deleted posters for a user"""

    @abstractmethod
    async def hard_delete(self, poster_id: int) -> bool:
        """Permanently delete poster by id"""

    @abstractmethod
    async def hard_delete_all_deleted(self, username: str) -> int:
        """Permanently delete all deleted posters for a user, return count"""

    @abstractmethod
    async def archive_and_hard_delete(
        self, poster_id: int, archived_repo
    ) -> ArchivedPoster:
        """Archive poster metadata then hard delete"""

    @abstractmethod
    async def archive_and_hard_delete_all_deleted(
        self, username: str, archived_repo
    ) -> int:
        """Archive all deleted posters metadata then hard delete, return count"""


class ArchivedPosterRepository(ABC):
    """Abstract archived poster repository interface"""

    @abstractmethod
    async def create(self, archived_poster):
        """Create a new archived poster record"""

    @abstractmethod
    async def get_by_username(self, username: str) -> list:
        """Get all archived posters for a user"""

    @abstractmethod
    async def get_by_original_id(self, original_id: int):
        """Get archived poster by original ID"""


class AlbumRepository(ABC):
    """Abstract album repository interface"""

    @abstractmethod
    async def create(self, album) -> int:
        """
        Create a new album, return album id
        """

    @abstractmethod
    async def get_by_id(self, album_id: int):
        """Get album by id"""

    @abstractmethod
    async def get_by_username(self, username: str) -> list:
        """
        Get all albums for a user
        """

    @abstractmethod
    async def get_all(self) -> list:
        """
        Get all albums (visible to all users)
        """

    @abstractmethod
    async def delete(self, album_id: int, username: str) -> bool:
        """
        Delete album by id (only creator can delete)
        """

    @abstractmethod
    async def add_image(self, album_id: int, image_id: str, username: str) -> bool:
        """
        Add image to album (enforce privacy rules)
        """

    @abstractmethod
    async def remove_image(self, album_id: int, image_id: str, username: str) -> bool:
        """
        Remove image from album (enforce privacy rules)
        """

    @abstractmethod
    async def get_images(self, album_id: int) -> list:
        """
        Get all images in album
        """

    @abstractmethod
    async def can_edit_album(self, album_id: int, username: str) -> bool:
        """
        Check if user can edit (add/remove) images in album based on privacy
        """

    @abstractmethod
    async def is_album_creator(self, album_id: int, username: str) -> bool:
        """
        Check if user is the creator of the album
        """
