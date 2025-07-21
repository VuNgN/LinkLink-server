"""
PostgreSQL Image Repository implementation
"""

from typing import List, Optional

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.entities import Image
from ...core.interfaces import ImageRepository
from ..models import ImageModel


class PostgreSQLImageRepository(ImageRepository):
    """PostgreSQL image repository implementation"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, image: Image) -> Image:
        """Create a new image record"""
        db_image = ImageModel(
            filename=image.filename,
            original_filename=image.original_filename,
            username=image.username,
            file_path=image.file_path,
            file_size=image.file_size,
            content_type=image.content_type,
            upload_date=image.upload_date,
        )
        self.session.add(db_image)
        await self.session.commit()
        await self.session.refresh(db_image)

        return Image(
            filename=db_image.filename,
            original_filename=db_image.original_filename,
            username=db_image.username,
            file_path=db_image.file_path,
            file_size=db_image.file_size,
            content_type=db_image.content_type,
            upload_date=db_image.upload_date,
        )

    async def get_by_filename(self, filename: str) -> Optional[Image]:
        """Get image by filename"""
        result = await self.session.execute(
            select(ImageModel).where(ImageModel.filename == filename)
        )
        db_image = result.scalar_one_or_none()

        if not db_image:
            return None

        return Image(
            filename=db_image.filename,
            original_filename=db_image.original_filename,
            username=db_image.username,
            file_path=db_image.file_path,
            file_size=db_image.file_size,
            content_type=db_image.content_type,
            upload_date=db_image.upload_date,
        )

    async def get_by_username(self, username: str) -> List[Image]:
        """Get all images for a user"""
        result = await self.session.execute(
            select(ImageModel)
            .where(ImageModel.username == username)
            .order_by(ImageModel.upload_date.desc())
        )
        db_images = result.scalars().all()

        return [
            Image(
                filename=img.filename,
                original_filename=img.original_filename,
                username=img.username,
                file_path=img.file_path,
                file_size=img.file_size,
                content_type=img.content_type,
                upload_date=img.upload_date,
            )
            for img in db_images
        ]

    async def delete(self, filename: str) -> bool:
        """Delete image"""
        result = await self.session.execute(
            delete(ImageModel).where(ImageModel.filename == filename)
        )
        await self.session.commit()
        return result.rowcount > 0
