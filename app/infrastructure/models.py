"""
SQLAlchemy database models
"""
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Integer, Text
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
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
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