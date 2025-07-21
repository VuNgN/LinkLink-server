"""
Utility functions for API routes
"""

import os


def public_image_path(image_path):
    """Convert internal image path to public URL"""
    filename = os.path.basename(image_path)
    return f"/uploads/{filename}" if filename else ""


def to_public_path(fp):
    """Convert file path to public URL format"""
    if not fp:
        return ""
    fp = fp.replace("\\", "/")
    if fp.startswith("/uploads/"):
        return fp
    if fp.startswith("uploads/"):
        return "/" + fp
    return "/uploads/" + os.path.basename(fp)
