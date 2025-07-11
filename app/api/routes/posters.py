"""
Poster management routes
Handles poster CRUD operations, trash, and archive functionality
"""

import os
import shutil
from typing import List

from fastapi import (APIRouter, Depends, File, Form, HTTPException, Path,
                     Request, Security, UploadFile)
from fastapi.security.utils import get_authorization_scheme_param
from sqlalchemy import desc, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.entities import ArchivedPoster, Poster, User
from ...core.services import AuthService
from ...infrastructure.database import get_db_session
from ...infrastructure.models import ImageModel, PosterModel
from ...infrastructure.notifier import post_notifier
from ..dependencies import (get_auth_service, get_current_user,
                            get_poster_service)
from .utils import to_public_path

router = APIRouter()


@router.post(
    "/posters/",
    response_model=Poster,
    tags=["Posters"],
    summary="Create a poster (image + message)",
    dependencies=[Security(get_current_user)],
)
async def create_poster(
    message: str = Form(..., description="Message for the poster"),
    image: UploadFile = File(..., description="Image file for the poster"),
    privacy: str = Form(
        "private", description="Privacy of the post: public or private"
    ),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Create a new poster with image and message."""
    # Save the image
    upload_dir = "uploads"
    os.makedirs(upload_dir, exist_ok=True)
    image_filename = f"{current_user.username}_{image.filename}"
    image_path = os.path.join(upload_dir, image_filename)
    with open(image_path, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)

    # Create PosterModel
    poster = PosterModel(
        username=current_user.username,
        message=message,
        privacy=privacy,
    )
    db.add(poster)
    await db.commit()
    await db.refresh(poster)

    # Create ImageModel and link to poster
    image_model = ImageModel(
        filename=image_filename,
        original_filename=image.filename,
        username=current_user.username,
        file_path=image_path,
        file_size=image.size,
        content_type=image.content_type or "application/octet-stream",
        poster_id=poster.id,
    )
    db.add(image_model)
    await db.commit()

    poster_obj = Poster.from_orm(poster)
    poster_obj.images = [
        {
            "filename": image_model.filename,
            "file_path": to_public_path(image_model.file_path),
        }
    ]

    # Notify all clients except the poster, only for public/community
    if privacy in ("public", "community"):
        try:
            await post_notifier.broadcast_new_post(current_user.username)
        except Exception:
            pass

    return poster_obj.dict()


@router.get(
    "/posters/",
    response_model=List[Poster],
    tags=["Posters"],
    summary="Get all posters (paginated)",
)
async def get_posters(
    request: Request,
    limit: int = 20,
    offset: int = 0,
    db: AsyncSession = Depends(get_db_session),
    auth_service: AuthService = Depends(get_auth_service),
):
    """Get all posters with pagination and privacy filtering."""
    # Check if user is authenticated with valid token
    current_user = None
    auth = request.headers.get("Authorization")
    if auth:
        scheme, param = get_authorization_scheme_param(auth)
        if scheme.lower() == "bearer" and param:
            try:
                username = auth_service.verify_token(param)
                user = await auth_service.user_repository.get_by_username(username)
                if user and user.is_active and user.status.value == "approved":
                    current_user = user
                else:
                    raise Exception("Inactive or unapproved user")
            except Exception:
                raise HTTPException(
                    status_code=401,
                    detail="Token expired or invalid",
                    headers={"WWW-Authenticate": "Bearer"},
                )
        else:
            raise HTTPException(
                status_code=401,
                detail="Invalid authorization header",
                headers={"WWW-Authenticate": "Bearer"},
            )

    # Build query based on authentication status
    username = getattr(current_user, "username", None)
    if username is not None:
        # Authenticated: get public + community + own private posts
        stmt = (
            select(PosterModel)
            .where(
                or_(
                    (PosterModel.privacy == "public"),
                    (PosterModel.privacy == "community"),
                    (PosterModel.username == username),
                ),
                PosterModel.is_deleted.is_(False),
            )
            .order_by(desc(PosterModel.created_at))
            .limit(limit)
            .offset(offset)
        )
    else:
        # Not authenticated: only public posts
        stmt = (
            select(PosterModel)
            .where((PosterModel.privacy == "public"), PosterModel.is_deleted.is_(False))
            .order_by(desc(PosterModel.created_at))
            .limit(limit)
            .offset(offset)
        )

    result = await db.execute(stmt)
    posters = result.scalars().all()

    poster_objs = []
    for p in posters:
        # Get associated images
        images_result = await db.execute(
            select(ImageModel).where(ImageModel.poster_id == p.id)
        )
        images = images_result.scalars().all()
        poster_obj = Poster.from_orm(p)
        poster_obj.images = [
            {"filename": img.filename, "file_path": to_public_path(img.file_path)}
            for img in images
        ]
        poster_objs.append(poster_obj)

    return [po.dict() for po in poster_objs]


@router.patch(
    "/posters/{poster_id}",
    response_model=Poster,
    tags=["Posters"],
    summary="Edit a poster (message and/or image and/or privacy)",
    dependencies=[Security(get_current_user)],
)
async def edit_poster(
    poster_id: int,
    message: str = Form(None, description="New message for the poster"),
    image: UploadFile = File(
        None, description="New image file for the poster (optional)"
    ),
    privacy: str = Form(
        None, description="New privacy setting: public, community, or private"
    ),
    current_user: User = Depends(get_current_user),
    poster_service=Depends(get_poster_service),
    db: AsyncSession = Depends(get_db_session),
):
    """Edit an existing poster."""
    image_content = None
    image_filename = None
    if image is not None:
        image_content = await image.read()
        image_filename = image.filename

    try:
        poster = await poster_service.edit_poster(
            poster_id=poster_id,
            username=current_user.username,
            message=message,
            image_content=image_content,
            image_filename=image_filename,
            privacy=privacy,
        )

        # Handle image update if provided
        if image_content is not None and image_filename is not None:
            # Delete old images for this poster
            old_images_result = await db.execute(
                select(ImageModel).where(ImageModel.poster_id == poster_id)
            )
            old_images = old_images_result.scalars().all()
            for old_img in old_images:
                # Delete file from storage
                if os.path.exists(old_img.file_path):
                    os.remove(old_img.file_path)
                # Delete from database
                await db.delete(old_img)

            # Create new image
            upload_dir = "uploads"
            os.makedirs(upload_dir, exist_ok=True)
            new_image_filename = f"{current_user.username}_{image_filename}"
            new_image_path = os.path.join(upload_dir, new_image_filename)
            with open(new_image_path, "wb") as buffer:
                buffer.write(image_content)

            # Create new ImageModel
            new_image_model = ImageModel(
                filename=new_image_filename,
                original_filename=image_filename,
                username=current_user.username,
                file_path=new_image_path,
                file_size=len(image_content),
                content_type=image.content_type or "application/octet-stream",
                poster_id=poster_id,
            )
            db.add(new_image_model)
            await db.commit()

        # Get updated poster with images
        poster_obj = Poster.from_orm(poster)
        images_result = await db.execute(
            select(ImageModel).where(ImageModel.poster_id == poster.id)
        )
        images = images_result.scalars().all()
        poster_obj.images = [
            {"filename": img.filename, "file_path": to_public_path(img.file_path)}
            for img in images
        ]
        return poster_obj.dict()
    except ValueError as e:
        raise HTTPException(
            status_code=403 if "not allowed" in str(e).lower() else 404, detail=str(e)
        )


@router.delete(
    "/posters/{poster_id}",
    tags=["Posters"],
    summary="Delete a poster",
    dependencies=[Security(get_current_user)],
)
async def delete_poster(
    poster_id: int,
    current_user: User = Depends(get_current_user),
    poster_service=Depends(get_poster_service),
    db: AsyncSession = Depends(get_db_session),
):
    """Delete a poster (soft delete)."""
    try:
        # Delete associated images first
        images_result = await db.execute(
            select(ImageModel).where(ImageModel.poster_id == poster_id)
        )
        images = images_result.scalars().all()
        for img in images:
            # Delete file from storage
            if os.path.exists(img.file_path):
                os.remove(img.file_path)
            # Delete from database
            await db.delete(img)

        await poster_service.delete_poster(poster_id, current_user.username)
        return {"message": "Poster deleted successfully"}
    except ValueError as e:
        raise HTTPException(
            status_code=403 if "not allowed" in str(e).lower() else 404, detail=str(e)
        )


@router.get(
    "/posters/deleted",
    response_model=List[Poster],
    tags=["Posters", "Trash"],
    summary="Get all deleted (trashed) posters for current user",
    description="""
    Retrieve all posts that have been soft deleted (moved to trash) by the current user.
    These posts can be restored or permanently deleted (hard delete).
    """,
    dependencies=[Security(get_current_user)],
)
async def get_deleted_posters(
    current_user: User = Depends(get_current_user),
    poster_service=Depends(get_poster_service),
    db: AsyncSession = Depends(get_db_session),
):
    """Get all deleted (trashed) posters for the current user."""
    deleted = await poster_service.get_deleted_posts(current_user.username)

    # Add images to each poster
    result = []
    for poster in deleted:
        poster_obj = Poster.from_orm(poster)
        images_result = await db.execute(
            select(ImageModel).where(ImageModel.poster_id == poster.id)
        )
        images = images_result.scalars().all()
        poster_obj.images = [
            {"filename": img.filename, "file_path": to_public_path(img.file_path)}
            for img in images
        ]
        result.append(poster_obj.dict())

    return result


@router.delete(
    "/posters/deleted/hard",
    tags=["Posters", "Trash"],
    summary="Permanently delete all deleted posters (empty trash)",
    description="""
    Permanently delete all posts in the trash for the current user.
    This will archive the metadata for all deleted posts and remove their image files.
    """,
    dependencies=[Security(get_current_user)],
)
async def hard_delete_all_deleted_posters(
    current_user: User = Depends(get_current_user),
    poster_service=Depends(get_poster_service),
    db: AsyncSession = Depends(get_db_session),
):
    """Permanently delete all posts from the trash (hard delete)."""
    # Get all deleted posters for this user
    deleted_posters = await poster_service.get_deleted_posts(current_user.username)

    # Delete associated images first
    for poster in deleted_posters:
        images_result = await db.execute(
            select(ImageModel).where(ImageModel.poster_id == poster.id)
        )
        images = images_result.scalars().all()
        for img in images:
            # Delete file from storage
            if os.path.exists(img.file_path):
                os.remove(img.file_path)
            # Delete from database
            await db.delete(img)

    count = await poster_service.hard_delete_all_deleted(current_user.username)
    return {"message": f"{count} deleted posters permanently removed"}


@router.get(
    "/posters/archived",
    response_model=List[ArchivedPoster],
    tags=["Posters", "Archive"],
    summary="Get all archived (permanently deleted) posters metadata for current user",
    description="""
    Retrieve all archived posts metadata for the current user.
    These are posts that have been permanently deleted (hard deleted) and only metadata
    is preserved.
    """,
    dependencies=[Security(get_current_user)],
)
async def get_archived_posters(
    current_user: User = Depends(get_current_user),
    poster_service=Depends(get_poster_service),
):
    """Get all archived (permanently deleted) posters metadata for the current user."""
    archived = await poster_service.get_archived_posts(current_user.username)
    return archived


@router.get(
    "/posters/{poster_id}",
    response_model=Poster,
    tags=["Posters"],
    summary="Get poster detail by id",
)
async def get_poster_detail(
    request: Request,
    poster_id: int = Path(..., description="ID of the poster"),
    db: AsyncSession = Depends(get_db_session),
    auth_service: AuthService = Depends(get_auth_service),
):
    """Get detailed information about a specific poster."""
    # Check if user is authenticated with valid token
    current_user = None
    auth = request.headers.get("Authorization")
    if auth:
        scheme, param = get_authorization_scheme_param(auth)
        if scheme.lower() == "bearer" and param:
            try:
                username = auth_service.verify_token(param)
                user = await auth_service.user_repository.get_by_username(username)
                if user and user.is_active and user.status.value == "approved":
                    current_user = user
                else:
                    raise Exception("Inactive or unapproved user")
            except Exception:
                raise HTTPException(
                    status_code=401,
                    detail="Token expired or invalid",
                    headers={"WWW-Authenticate": "Bearer"},
                )
        else:
            raise HTTPException(
                status_code=401,
                detail="Invalid authorization header",
                headers={"WWW-Authenticate": "Bearer"},
            )

    poster = await db.get(PosterModel, poster_id)
    if poster is None:
        raise HTTPException(status_code=404, detail="Poster not found")

    # Check if poster has been deleted
    if poster.is_deleted:
        raise HTTPException(status_code=404, detail="Poster not found")

    privacy = str(poster.privacy) if poster.privacy is not None else None
    if privacy == "public":
        pass  # Anyone can view
    else:
        # community or private require authentication
        if current_user is None:
            raise HTTPException(
                status_code=401, detail="You must be logged in to view this poster"
            )
        if privacy == "community":
            pass  # Just need to be logged in
        elif privacy == "private":
            if current_user.username != poster.username:
                raise HTTPException(
                    status_code=451, detail="Not allowed to view this poster (private)"
                )

    poster_obj = Poster.from_orm(poster)
    # Get associated images
    images_result = await db.execute(
        select(ImageModel).where(ImageModel.poster_id == poster.id)
    )
    images = images_result.scalars().all()
    poster_obj.images = [
        {"filename": img.filename, "file_path": to_public_path(img.file_path)}
        for img in images
    ]
    return poster_obj.dict()


@router.delete(
    "/posters/{poster_id}/hard",
    tags=["Posters", "Trash"],
    summary="Permanently delete a single deleted poster (hard delete)",
    description="""
    Permanently delete a single post from the trash for the current user.
    This will archive the metadata for the deleted post and remove its image file.
    Only the post owner can perform this action, and only if the post is already soft
    deleted.
    """,
    response_model=ArchivedPoster,
    dependencies=[Security(get_current_user)],
)
async def hard_delete_single_deleted_poster(
    poster_id: int,
    current_user: User = Depends(get_current_user),
    poster_service=Depends(get_poster_service),
    db: AsyncSession = Depends(get_db_session),
):
    """Permanently delete a single poster from trash."""
    try:
        # Delete associated images first
        images_result = await db.execute(
            select(ImageModel).where(ImageModel.poster_id == poster_id)
        )
        images = images_result.scalars().all()
        for img in images:
            # Delete file from storage
            if os.path.exists(img.file_path):
                os.remove(img.file_path)
            # Delete from database
            await db.delete(img)

        archived = await poster_service.hard_delete_post(
            poster_id, current_user.username
        )
        return archived
    except ValueError as e:
        raise HTTPException(
            status_code=403 if "not allowed" in str(e).lower() else 404, detail=str(e)
        )


@router.patch(
    "/posters/{poster_id}/restore",
    tags=["Posters", "Trash"],
    summary="Restore a deleted (trashed) poster",
    description="""
    Restore a soft-deleted (trashed) poster for the current user.
    This sets is_deleted to False and removes deleted_at.
    Only the post owner can perform this action, and only if the post is currently
    deleted.
    """,
    dependencies=[Security(get_current_user)],
)
async def restore_deleted_poster(
    poster_id: int,
    current_user: User = Depends(get_current_user),
    poster_service=Depends(get_poster_service),
    db: AsyncSession = Depends(get_db_session),
):
    """Restore a deleted poster from trash."""
    try:
        poster = await poster_service.restore_post(poster_id, current_user.username)
        # Get restored poster with images
        poster_obj = Poster.from_orm(poster)
        images_result = await db.execute(
            select(ImageModel).where(ImageModel.poster_id == poster.id)
        )
        images = images_result.scalars().all()
        poster_obj.images = [
            {"filename": img.filename, "file_path": to_public_path(img.file_path)}
            for img in images
        ]
        return poster_obj.dict()
    except ValueError as e:
        raise HTTPException(
            status_code=403 if "not allowed" in str(e).lower() else 404, detail=str(e)
        )
