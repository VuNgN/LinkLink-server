"""
Domain entities - Core business objects
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from enum import Enum

class TokenType(str, Enum):
    ACCESS = "access"
    REFRESH = "refresh"

class User(BaseModel):
    """User domain entity"""
    username: str = Field(
        ..., 
        description="Unique username for the user account",
        min_length=3,
        max_length=50
    )
    hashed_password: str = Field(
        ..., 
        description="Securely hashed password (never stored in plain text)"
    )
    is_active: bool = Field(
        default=True, 
        description="Whether the user account is active"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when the user account was created"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when the user account was last updated"
    )

    class Config:
        schema_extra = {
            "example": {
                "username": "john_doe",
                "hashed_password": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/HS.iQeO",
                "is_active": True,
                "created_at": "2024-01-15T10:30:00Z",
                "updated_at": "2024-01-15T10:30:00Z"
            }
        }

class Image(BaseModel):
    """Image domain entity"""
    filename: str = Field(
        ..., 
        description="Unique filename generated for the uploaded image",
        max_length=255
    )
    original_filename: str = Field(
        ..., 
        description="Original filename as uploaded by the user",
        max_length=255
    )
    username: str = Field(
        ..., 
        description="Username of the image owner",
        max_length=50
    )
    file_path: str = Field(
        ..., 
        description="File system path where the image is stored",
        max_length=500
    )
    file_size: int = Field(
        ..., 
        description="File size in bytes"
    )
    content_type: str = Field(
        ..., 
        description="MIME type of the image file",
        max_length=100
    )
    upload_date: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when the image was uploaded"
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
                "upload_date": "2024-01-15T10:30:00Z"
            }
        }

class Token(BaseModel):
    """Token domain entity"""
    access_token: str = Field(
        ..., 
        description="JWT access token for API authentication"
    )
    refresh_token: str = Field(
        ..., 
        description="JWT refresh token for getting new access tokens"
    )
    token_type: str = Field(
        default="bearer", 
        description="Type of token (always 'bearer' for JWT)"
    )
    expires_at: datetime = Field(
        ..., 
        description="Timestamp when the access token expires"
    )

    class Config:
        schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJqb2huX2RvZSIsImV4cCI6MTcwNTM5NzAwMH0.example_signature",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJqb2huX2RvZSIsImV4cCI6MTcxMjE3NzAwMH0.refresh_signature",
                "token_type": "bearer",
                "expires_at": "2024-01-15T11:00:00Z"
            }
        }

class UserCreate(BaseModel):
    """User creation DTO"""
    username: str = Field(
        ..., 
        min_length=3, 
        max_length=50,
        description="Username for the new account (3-50 characters)"
    )
    password: str = Field(
        ..., 
        min_length=6, 
        max_length=100,
        description="Password for the new account (6-100 characters)"
    )

    class Config:
        schema_extra = {
            "example": {
                "username": "john_doe",
                "password": "securepassword123"
            }
        }

class UserLogin(BaseModel):
    """User login DTO"""
    username: str = Field(
        ..., 
        min_length=1,
        description="Username for authentication"
    )
    password: str = Field(
        ..., 
        min_length=1,
        description="Password for authentication"
    )

    class Config:
        schema_extra = {
            "example": {
                "username": "john_doe",
                "password": "securepassword123"
            }
        }

class ImageInfo(BaseModel):
    """Image information DTO"""
    filename: str = Field(
        description="Unique filename of the image"
    )
    original_filename: str = Field(
        description="Original filename as uploaded by the user"
    )
    upload_date: datetime = Field(
        description="Timestamp when the image was uploaded"
    )
    file_size: int = Field(
        description="File size in bytes"
    )
    content_type: str = Field(
        description="MIME type of the image file"
    )

    class Config:
        schema_extra = {
            "example": {
                "filename": "abc123_vacation.jpg",
                "original_filename": "vacation.jpg",
                "upload_date": "2024-01-15T10:30:00Z",
                "file_size": 1024000,
                "content_type": "image/jpeg"
            }
        }

class RefreshTokenRequest(BaseModel):
    """Refresh token request DTO"""
    refresh_token: str = Field(
        ...,
        description="The refresh token to use for getting a new access token"
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
        ...,
        description="The refresh token to invalidate during logout"
    )

    class Config:
        schema_extra = {
            "example": {
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJqb2huX2RvZSIsImV4cCI6MTcxMjE3NzAwMH0.refresh_signature"
            }
        }

class SuccessResponse(BaseModel):
    """Generic success response"""
    message: str = Field(
        description="Success message"
    )

    class Config:
        schema_extra = {
            "example": {
                "message": "Operation completed successfully"
            }
        }

class ErrorResponse(BaseModel):
    """Generic error response"""
    detail: str = Field(
        description="Error message describing what went wrong"
    )

    class Config:
        schema_extra = {
            "example": {
                "detail": "Invalid credentials"
            }
        } 