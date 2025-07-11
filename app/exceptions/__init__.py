"""
Custom exceptions
"""

from .handlers import setup_exception_handlers
from .models import CustomHTTPException

__all__ = ["setup_exception_handlers", "CustomHTTPException"]
