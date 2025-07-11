"""
Application settings and configuration
"""

import os
from typing import List

from pydantic import BaseModel, Field


class Settings(BaseModel):
    """Application settings"""

    # Database
    DATABASE_URL: str = Field(
        default=os.getenv(
            "DATABASE_URL", "postgresql+asyncpg://a:password@localhost/linklink"
        ),
        description="Database connection URL",
    )

    # Security
    SECRET_KEY: str = Field(
        default=os.getenv("SECRET_KEY", "your-secret-key-change-this-in-production"),
        description="JWT secret key",
    )
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")),
        description="Access token expiration time in minutes",
    )
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(
        default=int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7")),
        description="Refresh token expiration time in days",
    )

    # Email
    MAIL_USERNAME: str = Field(
        default=os.getenv("MAIL_USERNAME", "your-email@gmail.com"),
        description="Email username",
    )
    MAIL_PASSWORD: str = Field(
        default=os.getenv("MAIL_PASSWORD", "your-app-password"),
        description="Email password",
    )
    MAIL_FROM: str = Field(
        default=os.getenv("MAIL_FROM", "your-email@gmail.com"),
        description="Email from address",
    )
    MAIL_PORT: int = Field(
        default=int(os.getenv("MAIL_PORT", "587")), description="Email port"
    )
    MAIL_SERVER: str = Field(
        default=os.getenv("MAIL_SERVER", "smtp.gmail.com"), description="Email server"
    )
    MAIL_STARTTLS: bool = Field(
        default=os.getenv("MAIL_STARTTLS", "true").lower() == "true",
        description="Use STARTTLS",
    )
    MAIL_SSL_TLS: bool = Field(
        default=os.getenv("MAIL_SSL_TLS", "false").lower() == "true",
        description="Use SSL/TLS",
    )
    USE_CREDENTIALS: bool = Field(
        default=os.getenv("USE_CREDENTIALS", "true").lower() == "true",
        description="Use credentials",
    )

    # Admin
    ADMIN_EMAIL: str = Field(
        default=os.getenv("ADMIN_EMAIL", "admin@example.com"),
        description="Admin email address",
    )

    # File Upload
    UPLOAD_DIR: str = Field(
        default=os.getenv("UPLOAD_DIR", "uploads"), description="Upload directory"
    )
    MAX_FILE_SIZE: int = Field(
        default=int(os.getenv("MAX_FILE_SIZE", str(10 * 1024 * 1024))),  # 10MB
        description="Maximum file size in bytes",
    )
    ALLOWED_TYPES: List[str] = Field(
        default=os.getenv(
            "ALLOWED_TYPES", "image/jpeg,image/png,image/gif,image/webp"
        ).split(","),
        description="Allowed file types",
    )

    # API
    API_V1_STR: str = Field(
        default=os.getenv("API_V1_STR", "/api/v1"), description="API version 1 string"
    )
    PROJECT_NAME: str = Field(
        default=os.getenv("PROJECT_NAME", "LinkLink Image Upload Server"),
        description="Project name",
    )

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = Field(
        default=os.getenv(
            "BACKEND_CORS_ORIGINS", "http://localhost:3000,http://localhost:8080"
        ).split(","),
        description="CORS origins",
    )

    # Logging
    LOG_LEVEL: str = Field(
        default=os.getenv("LOG_LEVEL", "INFO"), description="Logging level"
    )
    LOG_FILE: str = Field(
        default=os.getenv("LOG_FILE", "logs/app.log"), description="Log file path"
    )

    # Development
    DEBUG: bool = Field(
        default=os.getenv("DEBUG", "false").lower() == "true", description="Debug mode"
    )

    # Port
    PORT: int = Field(default=int(os.getenv("PORT", "8000")), description="Port")
    HOST: str = Field(default=os.getenv("HOST", "0.0.0.0"), description="Host")


# Create global settings instance
settings = Settings()
