"""
Image management business logic
"""

import os
from datetime import datetime, timezone
from typing import List, Optional

from ..entities import Image, ImageInfo
from ..interfaces import FileStorage, ImageRepository


class ImageService:
    """Image management business logic"""

    def __init__(
        self,
        image_repo: ImageRepository,
        file_storage: FileStorage,
        upload_dir: str = "uploads",
        max_file_size: int = 10 * 1024 * 1024,  # 10MB
        allowed_types: Optional[List[str]] = None,
    ):
        self.image_repo = image_repo
        self.file_storage = file_storage
        self.upload_dir = upload_dir
        self.max_file_size = max_file_size
        self.allowed_types = allowed_types or [
            "image/jpeg",
            "image/png",
            "image/gif",
            "image/webp",
        ]

    def _validate_file(
        self, file_content: bytes, content_type: str, original_filename: str
    ) -> None:
        """Validate uploaded file"""
        if not content_type.startswith("image/"):
            raise ValueError("File must be an image")

        if content_type not in self.allowed_types:
            raise ValueError(f"File type {content_type} not allowed")

        if len(file_content) > self.max_file_size:
            raise ValueError(f"File size exceeds maximum of {self.max_file_size} bytes")

        if not original_filename:
            raise ValueError("Filename is required")

    def _generate_filename(self, username: str, original_filename: str) -> str:
        """Generate unique filename"""
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        file_extension = (
            original_filename.split(".")[-1] if "." in original_filename else "jpg"
        )
        return f"{username}_{timestamp}.{file_extension}"

    async def upload_image(
        self,
        username: str,
        file_content: bytes,
        content_type: str,
        original_filename: str,
    ) -> Image:
        """Upload image for user"""
        # Validate file
        self._validate_file(file_content, content_type, original_filename)

        # Generate unique filename
        filename = self._generate_filename(username, original_filename)

        # Tạo đường dẫn thư mục theo ngày + user
        now = datetime.now(timezone.utc)
        subdir = os.path.join(
            self.upload_dir,
            str(now.year),
            f"{now.month:02d}",
            f"{now.day:02d}",
            username,
        )
        os.makedirs(subdir, exist_ok=True)
        file_path = os.path.join(subdir, filename)

        # Save file
        async def _save():
            with open(file_path, "wb") as f:
                f.write(file_content)

        await _save()

        # Create image record
        image = Image(
            filename=filename,
            original_filename=original_filename,
            username=username,
            file_path=file_path,
            file_size=len(file_content),
            content_type=content_type,
        )

        return await self.image_repo.create(image)

    async def get_user_images(self, username: str) -> List[ImageInfo]:
        """Get all images for a user"""
        images = await self.image_repo.get_by_username(username)

        def to_public_path(fp):
            # Always return a public path starting with /uploads/
            if not fp:
                return ""
            fp = fp.replace("\\", "/")  # Windows compatibility
            if fp.startswith("/uploads/"):
                return fp
            if fp.startswith("uploads/"):
                return "/" + fp
            # fallback: just return filename under uploads
            return "/uploads/" + os.path.basename(fp)

        return [
            {
                "filename": img.filename,
                "original_filename": img.original_filename,
                "upload_date": img.upload_date,
                "file_size": img.file_size,
                "content_type": img.content_type,
                "file_path": to_public_path(img.file_path),
            }
            for img in sorted(images, key=lambda x: x.upload_date, reverse=True)
        ]

    async def get_image(self, filename: str, username: str) -> Optional[Image]:
        """Get specific image (with ownership check)"""
        image = await self.image_repo.get_by_filename(filename)
        if not image or image.username != username:
            return None
        return image

    async def delete_image(self, filename: str, username: str) -> bool:
        """Delete image (with ownership check)"""
        image = await self.image_repo.get_by_filename(filename)
        if not image or image.username != username:
            return False

        # Delete file from storage
        await self.file_storage.delete_file(image.file_path)

        # Delete from repository
        return await self.image_repo.delete(filename)
