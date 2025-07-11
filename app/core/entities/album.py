"""
Album domain entities
"""

from datetime import datetime

from pydantic import BaseModel, Field

from .enums import AlbumPrivacy


class Album(BaseModel):
    """Album domain entity"""

    id: int
    name: str
    username: str
    created_at: datetime
    privacy: AlbumPrivacy = Field(
        default=AlbumPrivacy.READ_ONLY,
        description="Album privacy: writable or read-only",
    )

    class Config:
        from_attributes = True
        schema_extra = {
            "example": {
                "id": 1,
                "name": "My Summer Trip",
                "username": "john_doe",
                "created_at": "2024-07-01T10:00:00Z",
                "privacy": "writable",
            }
        }


class AlbumImage(BaseModel):
    """Album-Image link entity"""

    album_id: int
    image_id: str  # image filename
    added_by: str = Field(..., description="Username of the user who added the image")
    added_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when the image was added to the album",
    )

    class Config:
        from_attributes = True
        schema_extra = {
            "example": {
                "album_id": 1,
                "image_id": "abc123_vacation.jpg",
                "added_by": "john_doe",
                "added_at": "2024-07-01T10:05:00Z",
            }
        }
