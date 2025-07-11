"""
Album management business logic
"""

from datetime import datetime, timezone
from typing import Optional

from ..interfaces import AlbumRepository, ImageRepository


class AlbumService:
    """Album management business logic"""

    def __init__(self, album_repo: AlbumRepository, image_repo: ImageRepository):
        self.album_repo = album_repo
        self.image_repo = image_repo

    async def create_album(
        self, name: str, username: str, privacy: str = "read-only"
    ) -> int:
        album = {
            "name": name,
            "username": username,
            "created_at": datetime.now(timezone.utc),
            "privacy": privacy,
        }
        return await self.album_repo.create(album)

    async def get_albums(self, username: Optional[str] = None):
        # If username is provided, get user's albums, else get all albums
        if username:
            return await self.album_repo.get_by_username(username)
        return await self.album_repo.get_all()

    async def add_image_to_album(
        self, album_id: int, image_id: str, username: str
    ) -> bool:
        # Enforce privacy: only creator can add if read-only, anyone if writable
        can_edit = await self.album_repo.can_edit_album(album_id, username)
        if not can_edit:
            raise ValueError("You do not have permission to add images to this album")
        image = await self.image_repo.get_by_filename(image_id)
        if not image:
            raise ValueError("Image not found")
        return await self.album_repo.add_image(album_id, image_id, username)

    async def remove_image_from_album(
        self, album_id: int, image_id: str, username: str
    ) -> bool:
        # Enforce privacy: only creator can remove if read-only, anyone if writable
        can_edit = await self.album_repo.can_edit_album(album_id, username)
        if not can_edit:
            raise ValueError(
                "You do not have permission to remove images from this album"
            )
        return await self.album_repo.remove_image(album_id, image_id, username)

    async def get_album_images(self, album_id: int):
        image_ids = await self.album_repo.get_images(album_id)
        images = []
        for image_id in image_ids:
            img = await self.image_repo.get_by_filename(image_id)
            if img:
                images.append(img)
        return images

    async def delete_album(self, album_id: int, username: str) -> bool:
        # Only creator can delete
        is_creator = await self.album_repo.is_album_creator(album_id, username)
        if not is_creator:
            raise ValueError("You do not have permission to delete this album")
        return await self.album_repo.delete(album_id, username)
