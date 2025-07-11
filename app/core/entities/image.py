"""
Image domain entities
"""

from datetime import datetime

from pydantic import BaseModel, Field


class Image(BaseModel):
    """Image domain entity"""

    filename: str = Field(
        ...,
        description="Unique filename generated for the uploaded image",
        max_length=255,
    )
    original_filename: str = Field(
        ..., description="Original filename as uploaded by the user", max_length=255
    )
    username: str = Field(..., description="Username of the image owner", max_length=50)
    file_path: str = Field(
        ..., description="File system path where the image is stored", max_length=500
    )
    file_size: int = Field(..., description="File size in bytes")
    content_type: str = Field(
        ..., description="MIME type of the image file", max_length=100
    )
    upload_date: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when the image was uploaded",
    )

    class Config:
        schema_extra = {
            "example": {
                "filename": "abc123_vacation.jpg",
                "original_filename": "vacation.jpg",
                "username": "john_doe",
                "file_path": "/uploads/abc123_vacation.jpg",
                "file_size": 1024000,
                "content_type": "image/jpeg",
                "upload_date": "2024-01-15T10:30:00Z",
            }
        }


class ImageInfo(BaseModel):
    """Image information DTO"""

    filename: str = Field(description="Unique filename of the image")
    original_filename: str = Field(
        description="Original filename as uploaded by the user"
    )
    upload_date: datetime = Field(description="Timestamp when the image was uploaded")
    file_size: int = Field(description="File size in bytes")
    content_type: str = Field(description="MIME type of the image file")

    class Config:
        schema_extra = {
            "example": {
                "filename": "abc123_vacation.jpg",
                "original_filename": "vacation.jpg",
                "upload_date": "2024-01-15T10:30:00Z",
                "file_size": 1024000,
                "content_type": "image/jpeg",
            }
        }
