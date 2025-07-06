"""
Domain entities - Core business objects
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class TokenType(str, Enum):
    ACCESS = "access"
    REFRESH = "refresh"


class UserStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class User(BaseModel):
    """User domain entity"""

    username: str = Field(
        ...,
        description="Unique username for the user account",
        min_length=3,
        max_length=50,
    )
    email: EmailStr = Field(
        ..., description="Unique email address for the user account"
    )
    hashed_password: str = Field(
        ..., description="Securely hashed password (never stored in plain text)"
    )
    is_active: bool = Field(
        default=True, description="Whether the user account is active"
    )
    is_admin: bool = Field(
        default=False, description="Whether the user has admin privileges"
    )
    status: UserStatus = Field(
        default=UserStatus.PENDING,
        description="User approval status (pending/approved/rejected)",
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when the user account was created",
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when the user account was last updated",
    )
    approved_at: Optional[datetime] = Field(
        default=None,
        description="Timestamp when the user account was approved by admin",
    )
    approved_by: Optional[str] = Field(
        default=None, description="Username of the admin who approved the account"
    )

    class Config:
        schema_extra = {
            "example": {
                "username": "john_doe",
                "email": "john.doe@example.com",
                "hashed_password": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/HS.iQeO",
                "is_active": True,
                "is_admin": False,
                "status": "approved",
                "created_at": "2024-01-15T10:30:00Z",
                "updated_at": "2024-01-15T10:30:00Z",
                "approved_at": "2024-01-15T11:00:00Z",
                "approved_by": "admin",
            }
        }


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
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJqb2huX2RvZSIsImV4cCI6MTcwNTM5NzAwMH0.example_signature",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJqb2huX2RvZSIsImV4cCI6MTcxMjE3NzAwMH0.refresh_signature",
                "token_type": "bearer",
                "expires_at": "2024-01-15T11:00:00Z",
            }
        }


class UserCreate(BaseModel):
    """User creation DTO"""

    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="Username for the new account (3-50 characters)",
    )
    email: EmailStr = Field(
        ..., description="Email address for the new account (must be unique)"
    )
    password: str = Field(
        ...,
        min_length=6,
        max_length=100,
        description="Password for the new account (6-100 characters)",
    )

    class Config:
        schema_extra = {
            "example": {
                "username": "john_doe",
                "email": "john.doe@example.com",
                "password": "securepassword123",
            }
        }


class UserLogin(BaseModel):
    """User login DTO"""

    username: str = Field(..., min_length=1, description="Username for authentication")
    password: str = Field(..., min_length=1, description="Password for authentication")

    class Config:
        schema_extra = {
            "example": {"username": "john_doe", "password": "securepassword123"}
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


class RefreshTokenRequest(BaseModel):
    """Refresh token request DTO"""

    refresh_token: str = Field(
        ..., description="The refresh token to use for getting a new access token"
    )

    class Config:
        schema_extra = {
            "example": {
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJqb2huX2RvZSIsImV4cCI6MTcxMjE3NzAwMH0.refresh_signature"
            }
        }


class LogoutRequest(BaseModel):
    """Logout request DTO"""

    refresh_token: str = Field(
        ..., description="The refresh token to invalidate during logout"
    )

    class Config:
        schema_extra = {
            "example": {
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJqb2huX2RvZSIsImV4cCI6MTcxMjE3NzAwMH0.refresh_signature"
            }
        }


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


class UserRegistrationResponse(BaseModel):
    """User registration response DTO"""

    message: str = Field(..., description="Registration status message")
    status: str = Field(default="pending", description="Registration status")
    email: str = Field(..., description="Email address used for registration")

    class Config:
        schema_extra = {
            "example": {
                "message": "Registration submitted successfully. Your account will be reviewed by an administrator.",
                "status": "pending",
                "email": "john.doe@example.com",
            }
        }


class AdminApprovalRequest(BaseModel):
    """Admin approval request DTO"""

    username: str = Field(..., description="Username of the user to approve/reject")
    action: str = Field(..., description="Action to take: 'approve' or 'reject'")
    admin_username: str = Field(
        ..., description="Username of the admin performing the action"
    )
    reason: Optional[str] = Field(
        default=None, description="Reason for approval/rejection (optional)"
    )

    class Config:
        schema_extra = {
            "example": {
                "username": "john_doe",
                "action": "approve",
                "admin_username": "admin",
                "reason": "Account looks legitimate",
            }
        }


class PendingUserInfo(BaseModel):
    """Pending user information DTO"""

    username: str = Field(description="Username of the pending user")
    email: str = Field(description="Email address of the pending user")
    created_at: datetime = Field(description="Timestamp when the user registered")

    class Config:
        schema_extra = {
            "example": {
                "username": "john_doe",
                "email": "john.doe@example.com",
                "created_at": "2024-01-15T10:30:00Z",
            }
        }


class Poster(BaseModel):
    """Poster domain entity"""

    id: int
    username: str
    message: str
    image_path: str
    created_at: datetime
    privacy: str  # 'public' hoặc 'private'
    is_deleted: bool = False
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True
        schema_extra = {
            "example": {
                "id": 1,
                "username": "john_doe",
                "message": "Check out my new poster!",
                "image_path": "/uploads/poster1.jpg",
                "created_at": "2024-06-29T10:30:00Z",
                "privacy": "public",
                "is_deleted": False,
                "deleted_at": None,
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
