"""
Concrete repository implementations
"""

import os
import shutil
from datetime import datetime
from typing import Dict, List, Optional

from ..core.entities import Image, User
from ..core.interfaces import (FileStorage, ImageRepository, TokenRepository,
                               UserRepository)


class InMemoryUserRepository(UserRepository):
    """In-memory user repository implementation"""

    def __init__(self):
        self.users: Dict[str, User] = {}
        # Create default admin user
        self._create_default_admin()

    def _create_default_admin(self):
        """Create default admin user"""
        from passlib.context import CryptContext

        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

        admin_user = User(
            username="admin",
            hashed_password=pwd_context.hash("admin123"),
            is_active=True,
        )
        self.users["admin"] = admin_user

    async def create(self, user: User) -> User:
        """Create a new user"""
        if user.username in self.users:
            raise ValueError("Username already exists")
        self.users[user.username] = user
        return user

    async def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        return self.users.get(username)

    async def update(self, user: User) -> User:
        """Update user"""
        if user.username not in self.users:
            raise ValueError("User not found")
        user.updated_at = datetime.utcnow()
        self.users[user.username] = user
        return user

    async def delete(self, username: str) -> bool:
        """Delete user"""
        if username in self.users:
            del self.users[username]
            return True
        return False


class InMemoryImageRepository(ImageRepository):
    """In-memory image repository implementation"""

    def __init__(self):
        self.images: Dict[str, Image] = {}

    async def create(self, image: Image) -> Image:
        """Create a new image record"""
        self.images[image.filename] = image
        return image

    async def get_by_filename(self, filename: str) -> Optional[Image]:
        """Get image by filename"""
        return self.images.get(filename)

    async def get_by_username(self, username: str) -> List[Image]:
        """Get all images for a user"""
        return [img for img in self.images.values() if img.username == username]

    async def delete(self, filename: str) -> bool:
        """Delete image"""
        if filename in self.images:
            del self.images[filename]
            return True
        return False


class InMemoryTokenRepository(TokenRepository):
    """In-memory token repository implementation"""

    def __init__(self):
        self.refresh_tokens: Dict[str, str] = {}  # token -> username

    async def store_refresh_token(self, token: str, username: str) -> bool:
        """Store refresh token"""
        self.refresh_tokens[token] = username
        return True

    async def get_username_by_refresh_token(self, token: str) -> Optional[str]:
        """Get username by refresh token"""
        return self.refresh_tokens.get(token)

    async def delete_refresh_token(self, token: str) -> bool:
        """Delete refresh token"""
        if token in self.refresh_tokens:
            del self.refresh_tokens[token]
            return True
        return False


class LocalFileStorage(FileStorage):
    """Local file system storage implementation"""

    def __init__(self, upload_dir: str = "uploads"):
        self.upload_dir = upload_dir
        self._ensure_upload_dir()

    def _ensure_upload_dir(self):
        """Ensure upload directory exists"""
        if not os.path.exists(self.upload_dir):
            os.makedirs(self.upload_dir)

    async def save_file(self, file_content: bytes, filename: str) -> str:
        """Save file and return file path"""
        file_path = os.path.join(self.upload_dir, filename)

        # Ensure directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        # Write file
        with open(file_path, "wb") as f:
            f.write(file_content)

        return file_path

    async def delete_file(self, file_path: str) -> bool:
        """Delete file"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            return False
        except Exception:
            return False

    async def file_exists(self, file_path: str) -> bool:
        """Check if file exists"""
        return os.path.exists(file_path)
