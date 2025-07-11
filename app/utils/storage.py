"""
File storage utilities
"""

import os

from ..core.interfaces import FileStorage


class LocalFileStorage(FileStorage):
    """Local file system storage implementation"""

    def __init__(self, upload_dir: str = "uploads"):
        self.upload_dir = upload_dir
        self._ensure_upload_dir()

    def _ensure_upload_dir(self):
        """Ensure upload directory exists"""
        if not os.path.exists(self.upload_dir):
            os.makedirs(self.upload_dir)

    async def save_file(self, file_content: bytes, filename: str) -> str:
        """Save file and return file path"""
        file_path = os.path.join(self.upload_dir, filename)

        # Ensure directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        # Write file
        with open(file_path, "wb") as f:
            f.write(file_content)

        return file_path

    async def delete_file(self, file_path: str) -> bool:
        """Delete file"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            return False
        except Exception:
            return False

    async def file_exists(self, file_path: str) -> bool:
        """Check if file exists"""
        return os.path.exists(file_path)
