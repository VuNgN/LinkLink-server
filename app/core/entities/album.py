"""
Album domain entities
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from .enums import AlbumPrivacy


class Album(BaseModel):
    """Album domain entity"""

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "name": "My Summer Trip",
                "username": "john_doe",
                "created_at": "2024-07-01T10:00:00Z",
                "privacy": "writable",
            }
        },
    )

    id: int
    name: str
    username: str
    created_at: datetime
    privacy: AlbumPrivacy = Field(
        default=AlbumPrivacy.READ_ONLY,
        description="Album privacy: writable or read-only",
    )


class AlbumCreate(BaseModel):
    """Album creation DTO"""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "My Summer Trip",
                "privacy": "writable",
            }
        }
    )

    name: str = Field(..., description="Album name")
    privacy: AlbumPrivacy = Field(
        default=AlbumPrivacy.READ_ONLY,
        description="Album privacy setting",
    )


class AlbumImage(BaseModel):
    """Album image entity"""

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "album_id": 1,
                "image_id": 1,
                "added_at": "2024-07-01T10:00:00Z",
            }
        },
    )

    id: int
    album_id: int
    image_id: int
    added_at: datetime
