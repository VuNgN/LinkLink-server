"""
Poster domain entities
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class Poster(BaseModel):
    """Poster domain entity"""

    id: int
    username: str
    message: str
    created_at: datetime
    privacy: str  # 'public', 'community', or 'private'
    is_deleted: bool = False
    deleted_at: Optional[datetime] = None
    images: Optional[list] = None  # List of linked images

    class Config:
        from_attributes = True
        schema_extra = {
            "example": {
                "id": 1,
                "username": "john_doe",
                "message": "Check out my new poster!",
                "created_at": "2024-06-29T10:30:00Z",
                "privacy": "public",
                "is_deleted": False,
                "deleted_at": None,
                "images": [],
            }
        }


class ArchivedPoster(BaseModel):
    """Archived poster entity for permanently deleted posts (metadata only)"""

    id: Optional[int] = None
    original_id: int
    username: str
    message: str
    original_image_path: str
    image_filename: str
    created_at: datetime
    deleted_at: datetime
    archived_at: datetime
    privacy: str

    class Config:
        from_attributes = True
        schema_extra = {
            "example": {
                "id": 1,
                "original_id": 123,
                "username": "john_doe",
                "message": "Check out my new poster!",
                "original_image_path": "/uploads/poster1.jpg",
                "image_filename": "poster1.jpg",
                "created_at": "2024-06-29T10:30:00Z",
                "deleted_at": "2024-07-01T15:45:00Z",
                "archived_at": "2024-07-15T09:20:00Z",
                "privacy": "public",
            }
        }
