"""
Common DTOs (Data Transfer Objects)
"""

from pydantic import BaseModel, Field


class SuccessResponse(BaseModel):
    """Generic success response"""

    message: str = Field(description="Success message")

    class Config:
        schema_extra = {"example": {"message": "Operation completed successfully"}}


class ErrorResponse(BaseModel):
    """Generic error response"""

    detail: str = Field(description="Error message describing what went wrong")

    class Config:
        schema_extra = {"example": {"detail": "Invalid credentials"}}
