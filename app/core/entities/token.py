"""
Token domain entities
"""

from datetime import datetime

from pydantic import BaseModel, Field


class Token(BaseModel):
    """Token domain entity"""

    access_token: str = Field(
        ..., description="JWT access token for API authentication"
    )
    refresh_token: str = Field(
        ..., description="JWT refresh token for getting new access tokens"
    )
    token_type: str = Field(
        default="bearer", description="Type of token (always 'bearer' for JWT)"
    )
    expires_at: datetime = Field(
        ..., description="Timestamp when the access token expires"
    )

    class Config:
        schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_at": "2024-01-15T11:00:00Z",
            }
        }


class RefreshTokenRequest(BaseModel):
    """Refresh token request DTO"""

    refresh_token: str = Field(
        ..., description="The refresh token to use for getting a new access token"
    )

    class Config:
        schema_extra = {
            "example": {"refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."}
        }


class LogoutRequest(BaseModel):
    """Logout request DTO"""

    refresh_token: str = Field(
        ..., description="The refresh token to invalidate during logout"
    )

    class Config:
        schema_extra = {
            "example": {"refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."}
        }
