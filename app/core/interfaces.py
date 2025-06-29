"""
Repository interfaces - Abstract base classes for data access
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from .entities import User, Image, Token

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