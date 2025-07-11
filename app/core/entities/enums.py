"""
Domain enums
"""

from enum import Enum


class TokenType(str, Enum):
    ACCESS = "access"
    REFRESH = "refresh"


class UserStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class AlbumPrivacy(str, Enum):
    WRITABLE = "writable"
    READ_ONLY = "read-only"
