"""
Token domain entities
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class Token(BaseModel):
    """Token domain entity"""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 1800,
            }
        }
    )

    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")


class TokenWithUsername(Token):
    """Token with username information"""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 1800,
                "username": "john_doe",
            }
        }
    )

    refresh_token: Optional[str] = Field(default=None, description="JWT refresh token")
    username: str = Field(..., description="Username of the authenticated user")


class RefreshToken(BaseModel):
    """Refresh token domain entity"""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 604800,
            }
        }
    )

    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")


class RefreshTokenRequest(BaseModel):
    """Refresh token request DTO"""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {"refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."}
        }
    )

    refresh_token: str = Field(
        ..., description="The refresh token to use for getting a new access token"
    )


class LogoutRequest(BaseModel):
    """Logout request DTO"""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {"refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."}
        }
    )

    refresh_token: str = Field(
        ..., description="The refresh token to invalidate during logout"
    )


class TokenData(BaseModel):
    """Token data for internal use"""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "username": "john_doe",
                "expires": "2024-01-15T11:00:00Z",
            }
        }
    )

    username: Optional[str] = Field(default=None, description="Username from token")
    expires: Optional[datetime] = Field(
        default=None, description="Token expiration time"
    )
