"""
Poster management business logic
"""

from typing import Optional

from ..interfaces import (ArchivedPosterRepository, FileStorage,
                          PosterRepository)


class PosterService:
    """Poster management business logic"""

    def __init__(
        self,
        poster_repo: PosterRepository,
        archived_repo: ArchivedPosterRepository,
        file_storage: FileStorage,
        upload_dir: str = "uploads",
    ):
        self.poster_repo = poster_repo
        self.archived_repo = archived_repo
        self.file_storage = file_storage
        self.upload_dir = upload_dir

    async def edit_poster(
        self,
        poster_id: int,
        username: str,
        message: Optional[str] = None,
        image_updates: Optional[list] = None,
        privacy: Optional[str] = None,
    ):
        poster = await self.poster_repo.get_by_id(poster_id)
        if not poster:
            raise ValueError("Poster not found")
        if poster.username != username:
            raise ValueError("Not allowed to edit this poster")
        if poster.is_deleted:
            raise ValueError("Cannot edit a deleted poster")

        # Update message
        if message is not None:
            poster.message = message

        # Update privacy
        if privacy is not None:
            poster.privacy = privacy

        # Update image if provided
        if image_updates is not None:
            # Note: Image handling is now done in the route layer
            # since images are stored separately in the database
            pass

        await self.poster_repo.update(poster)
        return poster

    async def delete_poster(self, poster_id: int, username: str):
        poster = await self.poster_repo.get_by_id(poster_id)
        if not poster:
            raise ValueError("Poster not found")
        if poster.username != username:
            raise ValueError("Not allowed to delete this poster")
        if poster.is_deleted:
            raise ValueError("Poster already deleted")
        await self.poster_repo.delete(poster_id)
        return True

    async def get_deleted_posts(self, username: str):
        return await self.poster_repo.get_deleted(username)

    async def hard_delete_post(self, poster_id: int, username: str):
        poster = await self.poster_repo.get_by_id(poster_id)
        if not poster:
            raise ValueError("Poster not found")
        if poster.username != username:
            raise ValueError("Not allowed to hard delete this poster")
        if not poster.is_deleted:
            raise ValueError("Poster must be deleted first (in trash)")

        # Note: Image file deletion is now handled in the route layer
        # since images are stored separately and linked via poster_id

        # Archive and hard delete, and return the archived poster
        archived = await self.poster_repo.archive_and_hard_delete(
            poster_id, self.archived_repo
        )
        if not archived:
            raise ValueError("Failed to archive poster")
        return archived

    async def hard_delete_all_deleted(self, username: str):
        # Note: Image file deletion is now handled in the route layer
        # since images are stored separately and linked via poster_id

        count = await self.poster_repo.archive_and_hard_delete_all_deleted(
            username, self.archived_repo
        )
        return count

    async def get_archived_posts(self, username: str):
        return await self.archived_repo.get_by_username(username)

    async def restore_post(self, poster_id: int, username: str):
        poster = await self.poster_repo.get_by_id(poster_id)
        if not poster:
            raise ValueError("Poster not found")
        if poster.username != username:
            raise ValueError("Not allowed to restore this poster")
        if not poster.is_deleted:
            raise ValueError("Poster is not deleted")
        success = await self.poster_repo.restore(poster_id, username)
        if not success:
            raise ValueError("Failed to restore poster")
        # Return the restored poster
        return await self.poster_repo.get_by_id(poster_id)
