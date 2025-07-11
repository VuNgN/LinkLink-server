"""
PostgreSQL Poster Repository implementations
"""

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.entities import ArchivedPoster, Poster
from ...core.interfaces import ArchivedPosterRepository, PosterRepository
from ..models import ArchivedPosterModel, ImageModel, PosterModel


class PostgreSQLArchivedPosterRepository(ArchivedPosterRepository):
    """PostgreSQL archived poster repository implementation"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, archived_poster: ArchivedPoster) -> ArchivedPoster:
        db_archived = ArchivedPosterModel(
            original_id=archived_poster.original_id,
            username=archived_poster.username,
            message=archived_poster.message,
            original_image_path=archived_poster.original_image_path,
            image_filename=archived_poster.image_filename,
            created_at=archived_poster.created_at,
            deleted_at=archived_poster.deleted_at,
            archived_at=archived_poster.archived_at,
            privacy=archived_poster.privacy,
        )
        self.session.add(db_archived)
        await self.session.commit()
        await self.session.refresh(db_archived)
        return ArchivedPoster.from_orm(db_archived)

    async def get_by_username(self, username: str) -> list:
        result = await self.session.execute(
            select(ArchivedPosterModel).where(ArchivedPosterModel.username == username)
        )
        archived = result.scalars().all()
        return [ArchivedPoster.from_orm(a) for a in archived]

    async def get_by_original_id(self, original_id: int) -> ArchivedPoster:
        result = await self.session.execute(
            select(ArchivedPosterModel).where(
                ArchivedPosterModel.original_id == original_id
            )
        )
        archived = result.scalar_one_or_none()
        if not archived:
            return None
        return ArchivedPoster.from_orm(archived)


class PostgreSQLPosterRepository(PosterRepository):
    """PostgreSQL poster repository implementation"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, poster: Poster) -> Poster:
        db_poster = PosterModel(
            username=poster.username,
            message=poster.message,
            privacy=poster.privacy,
            is_deleted=poster.is_deleted,
            deleted_at=poster.deleted_at,
        )
        self.session.add(db_poster)
        await self.session.commit()
        await self.session.refresh(db_poster)
        return Poster.from_orm(db_poster)

    async def get_by_id(self, poster_id: int) -> Poster:
        db_poster = await self.session.get(PosterModel, poster_id)
        if not db_poster:
            return None
        return Poster.from_orm(db_poster)

    async def get_by_username(self, username: str) -> list:
        result = await self.session.execute(
            select(PosterModel).where(
                PosterModel.username == username, PosterModel.is_deleted.is_(False)
            )
        )
        posters = result.scalars().all()
        return [Poster.from_orm(p) for p in posters]

    async def update(self, poster: Poster) -> Poster:
        db_poster = await self.session.get(PosterModel, poster.id)
        if not db_poster:
            raise ValueError("Poster not found")
        db_poster.message = poster.message
        db_poster.privacy = poster.privacy
        db_poster.is_deleted = poster.is_deleted
        db_poster.deleted_at = poster.deleted_at
        await self.session.commit()
        await self.session.refresh(db_poster)
        return Poster.from_orm(db_poster)

    async def delete(self, poster_id: int) -> bool:
        # Soft delete: set is_deleted and deleted_at
        db_poster = await self.session.get(PosterModel, poster_id)
        if not db_poster:
            return False
        db_poster.is_deleted = True
        db_poster.deleted_at = datetime.now(timezone.utc)
        await self.session.commit()
        return True

    async def get_deleted(self, username: str) -> list:
        result = await self.session.execute(
            select(PosterModel).where(
                PosterModel.username == username, PosterModel.is_deleted.is_(True)
            )
        )
        posters = result.scalars().all()
        return [Poster.from_orm(p) for p in posters]

    async def hard_delete(self, poster_id: int) -> bool:
        db_poster = await self.session.get(PosterModel, poster_id)
        if not db_poster:
            return False
        await self.session.delete(db_poster)
        await self.session.commit()
        return True

    async def hard_delete_all_deleted(self, username: str) -> int:
        result = await self.session.execute(
            select(PosterModel).where(
                PosterModel.username == username, PosterModel.is_deleted.is_(True)
            )
        )
        posters = result.scalars().all()
        count = 0
        for p in posters:
            await self.session.delete(p)
            count += 1
        await self.session.commit()
        return count

    async def archive_and_hard_delete(
        self, poster_id: int, archived_repo: ArchivedPosterRepository
    ) -> ArchivedPoster:
        """Archive poster metadata then hard delete"""
        db_poster = await self.session.get(PosterModel, poster_id)
        if not db_poster:
            return None

        # Create archived record
        # Get the first image associated with this poster for archival
        image_result = await self.session.execute(
            select(ImageModel).where(ImageModel.poster_id == poster_id).limit(1)
        )
        first_image = image_result.scalar_one_or_none()

        original_image_path = first_image.file_path if first_image else ""
        image_filename = first_image.filename if first_image else ""

        archived_poster = ArchivedPoster(
            original_id=db_poster.id,
            username=db_poster.username,
            message=db_poster.message,
            original_image_path=original_image_path,
            image_filename=image_filename,
            created_at=db_poster.created_at,
            deleted_at=db_poster.deleted_at,
            archived_at=datetime.now(timezone.utc),
            privacy=db_poster.privacy,
        )
        archived_result = await archived_repo.create(archived_poster)

        # Hard delete
        await self.session.delete(db_poster)
        await self.session.commit()
        return archived_result

    async def archive_and_hard_delete_all_deleted(
        self, username: str, archived_repo: ArchivedPosterRepository
    ) -> int:
        """Archive all deleted posters metadata then hard delete"""
        result = await self.session.execute(
            select(PosterModel).where(
                PosterModel.username == username, PosterModel.is_deleted.is_(True)
            )
        )
        posters = result.scalars().all()
        count = 0

        for p in posters:
            # Get the first image associated with this poster for archival
            image_result = await self.session.execute(
                select(ImageModel).where(ImageModel.poster_id == p.id).limit(1)
            )
            first_image = image_result.scalar_one_or_none()

            original_image_path = first_image.file_path if first_image else ""
            image_filename = first_image.filename if first_image else ""

            # Create archived record
            archived_poster = ArchivedPoster(
                original_id=p.id,
                username=p.username,
                message=p.message,
                original_image_path=original_image_path,
                image_filename=image_filename,
                created_at=p.created_at,
                deleted_at=p.deleted_at,
                archived_at=datetime.now(timezone.utc),
                privacy=p.privacy,
            )
            await archived_repo.create(archived_poster)

            # Hard delete
            await self.session.delete(p)
            count += 1

        await self.session.commit()
        return count

    async def restore(self, poster_id: int, username: str) -> bool:
        db_poster = await self.session.get(PosterModel, poster_id)
        if not db_poster or db_poster.username != username or not db_poster.is_deleted:
            return False
        db_poster.is_deleted = False
        db_poster.deleted_at = None
        await self.session.commit()
        return True
