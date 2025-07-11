"""
User domain entities
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field

from .enums import UserStatus


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
        ..., description=("Securely hashed password (never stored in plain text)")
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
                "hashed_password": (
                    "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/HS.iQeO"
                ),
                "is_active": True,
                "is_admin": False,
                "status": "approved",
                "created_at": "2024-01-15T10:30:00Z",
                "updated_at": "2024-01-15T10:30:00Z",
                "approved_at": "2024-01-15T11:00:00Z",
                "approved_by": "admin",
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


class UserRegistrationResponse(BaseModel):
    """User registration response DTO"""

    message: str = Field(..., description="Registration status message")
    status: str = Field(default="pending", description="Registration status")
    email: str = Field(..., description="Email address used for registration")

    class Config:
        schema_extra = {
            "example": {
                "message": (
                    "Registration submitted successfully. "
                    "Your account will be reviewed by an administrator."
                ),
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
