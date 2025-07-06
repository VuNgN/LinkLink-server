"""
SQLAlchemy database models
"""

from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Enum, Integer, String, Text
from sqlalchemy.sql import func

from .database import Base


class UserModel(Base):
    """User database model"""

    __tablename__ = "users"

    username = Column(String(50), primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)  # Admin flag
    status = Column(String(20), default="pending")  # pending, approved, rejected
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    approved_at = Column(DateTime(timezone=True), nullable=True)
    approved_by = Column(String(50), nullable=True)


class ImageModel(Base):
    """Image database model"""

    __tablename__ = "images"

    filename = Column(String(255), primary_key=True, index=True)
    original_filename = Column(String(255), nullable=False)
    username = Column(String(50), nullable=False, index=True)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False)
    content_type = Column(String(100), nullable=False)
    upload_date = Column(DateTime(timezone=True), server_default=func.now())


class RefreshTokenModel(Base):
    """Refresh token database model"""

    __tablename__ = "refresh_tokens"

    token = Column(String(500), primary_key=True, index=True)
    username = Column(String(50), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)


class PosterModel(Base):
    """Poster database model (image + message)"""

    __tablename__ = "posters"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), nullable=False, index=True)
    message = Column(Text, nullable=False)
    image_path = Column(String(500), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    privacy = Column(
        Enum("public", "community", "private", name="privacyenum"), default="private"
    )
    is_deleted = Column(Boolean, default=False, nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)


class ArchivedPosterModel(Base):
    """Archived poster model for permanently deleted posts (metadata only)"""

    __tablename__ = "archived_posters"

    id = Column(Integer, primary_key=True, index=True)
    original_id = Column(Integer, nullable=False, index=True)  # Original poster ID
    username = Column(String(50), nullable=False, index=True)
    message = Column(Text, nullable=False)
    original_image_path = Column(
        String(500), nullable=False
    )  # Original image path (for reference)
    image_filename = Column(String(255), nullable=False)  # Just the filename
    created_at = Column(DateTime(timezone=True), nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=False)  # When soft deleted
    archived_at = Column(
        DateTime(timezone=True), server_default=func.now()
    )  # When hard deleted
    privacy = Column(String(20), nullable=False)  # Original privacy setting
