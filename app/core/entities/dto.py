"""
Data Transfer Objects (DTOs) for API responses
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

from .image import ImageInfo


class SuccessResponse(BaseModel):
    """Generic success response"""

    model_config = ConfigDict(
        json_schema_extra={"example": {"message": "Operation completed successfully"}}
    )

    message: str = Field(description="Success message")


class ErrorResponse(BaseModel):
    """Generic error response"""

    model_config = ConfigDict(
        json_schema_extra={"example": {"detail": "Invalid credentials"}}
    )

    detail: str = Field(description="Error message describing what went wrong")


class PosterResponse(BaseModel):
    """Poster response DTO"""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": 1,
                "username": "john_doe",
                "message": "Check out my new poster!",
                "created_at": "2024-06-29T10:30:00Z",
                "privacy": "public",
                "images": [],
            }
        }
    )

    id: int = Field(..., description="Poster ID")
    username: str = Field(..., description="Username of poster creator")
    message: str = Field(..., description="Poster message content")
    created_at: datetime = Field(..., description="Creation timestamp")
    privacy: str = Field(..., description="Privacy setting")
    images: Optional[List[ImageInfo]] = Field(
        default=None, description="List of associated images"
    )


class PosterCreate(BaseModel):
    """Poster creation DTO"""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "message": "Check out my new poster!",
                "privacy": "public",
            }
        }
    )

    message: str = Field(..., description="Poster message content")
    privacy: str = Field(..., description="Privacy setting")
