"""
API routes - Presentation layer
"""

import os
import shutil
from datetime import datetime
from typing import List, Optional

from fastapi import (APIRouter, Body, Depends, File, Form, HTTPException, Path,
                     Request, Response, Security, UploadFile, status)
from pydantic import BaseModel
from sqlalchemy import delete as sqlalchemy_delete
from sqlalchemy import desc, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database import get_db_session
from app.infrastructure.models import PosterModel
from app.infrastructure.notifier import post_notifier

from ..core.entities import (AdminApprovalRequest, ArchivedPoster, ImageInfo,
                             LogoutRequest, PendingUserInfo, Poster,
                             RefreshTokenRequest, Token, User, UserCreate,
                             UserLogin, UserRegistrationResponse)
from ..core.services import AuthService, ImageService
from .dependencies import (get_auth_service, get_current_admin_user,
                           get_current_user, get_image_service,
                           get_optional_user, get_poster_service)


class TokenWithUsername(Token):
    refresh_token: Optional[str] = None
    username: str


router = APIRouter()


def public_image_path(image_path):
    filename = os.path.basename(image_path)
    return f"/uploads/{filename}" if filename else ""


@router.post(
    "/register",
    response_model=UserRegistrationResponse,
    tags=["Authentication"],
    summary="Register a new user (pending admin approval)",
    description="""
    Register a new user account with username, email, and password.
    The account will be pending admin approval before activation.
    
    ## Requirements
    
    - **Username**: 3-50 characters, unique
    - **Email**: Valid email address, unique
    - **Password**: 6-100 characters
    
    ## Process
    
    1. User submits registration
    2. Admin receives email notification
    3. Admin approves/rejects the account
    4. User receives approval/rejection notification
    
    ## Response
    
    Returns a success message indicating the account is pending approval.
    
    ## Errors
    
    - `400 Bad Request`: Invalid input data, username exists, or email exists
    """,
    responses={
        200: {
            "description": "Registration submitted successfully",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Registration submitted successfully. Your account will be reviewed by an administrator.",
                        "status": "pending",
                        "email": "john.doe@example.com",
                    }
                }
            },
        },
        400: {
            "description": "Bad request - validation error or username/email exists",
            "content": {
                "application/json": {"example": {"detail": "Username already exists"}}
            },
        },
    },
)
async def register(
    user_data: UserCreate, auth_service: AuthService = Depends(get_auth_service)
):
    """
    Register a new user account (pending admin approval).

    This endpoint creates a new user account with pending status.
    The admin will receive an email notification and can approve/reject the account.

    **Example Request:**
    ```json
    {
        "username": "john_doe",
        "email": "john.doe@example.com",
        "password": "securepassword123"
    }
    ```
    """
    try:
        return await auth_service.register_user(user_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post(
    "/admin/approve-user",
    tags=["Admin"],
    summary="Approve or reject a user registration",
    description="""
    Approve or reject a pending user registration.
    Only accessible by admin users.
    
    ## Actions
    
    - **approve**: Activate the user account
    - **reject**: Reject the user registration
    
    ## Notifications
    
    - User receives email notification of approval/rejection
    - Admin can provide optional reason for rejection
    """,
    responses={
        200: {
            "description": "User approved/rejected successfully",
            "content": {
                "application/json": {
                    "example": {"message": "User john_doe approved successfully"}
                }
            },
        },
        400: {
            "description": "Bad request - user not found or invalid action",
            "content": {"application/json": {"example": {"detail": "User not found"}}},
        },
        401: {
            "description": "Unauthorized - admin access required",
            "content": {
                "application/json": {"example": {"detail": "Admin access required"}}
            },
        },
    },
)
async def approve_user(
    request: AdminApprovalRequest,
    current_user: User = Depends(get_current_admin_user),
    auth_service: AuthService = Depends(get_auth_service),
):
    """
    Approve or reject a user registration.

    **Example Request:**
    ```json
    {
        "username": "john_doe",
        "action": "approve",
        "admin_username": "admin",
        "reason": "Account looks legitimate"
    }
    ```
    """
    # TODO: Add admin role check
    # if not current_user.is_admin:
    #     raise HTTPException(status_code=401, detail="Admin access required")

    try:
        return await auth_service.approve_user(request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/admin/pending-users",
    response_model=List[PendingUserInfo],
    tags=["Admin"],
    summary="Get list of pending user registrations",
    description="""
    Get a list of all users with pending registration status.
    Only accessible by admin users.
    
    ## Response
    
    Returns a list of pending users with their registration details.
    """,
    responses={
        200: {
            "description": "List of pending users",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "username": "john_doe",
                            "email": "john.doe@example.com",
                            "created_at": "2024-01-15T10:30:00Z",
                        }
                    ]
                }
            },
        },
        401: {
            "description": "Unauthorized - admin access required",
            "content": {
                "application/json": {"example": {"detail": "Admin access required"}}
            },
        },
    },
)
async def get_pending_users(
    current_user: User = Depends(get_current_admin_user),
    auth_service: AuthService = Depends(get_auth_service),
):
    """
    Get list of pending user registrations.

    Returns all users who have registered but are waiting for admin approval.
    """
    # TODO: Add admin role check
    # if not current_user.is_admin:
    #     raise HTTPException(status_code=401, detail="Admin access required")

    return await auth_service.get_pending_users()


@router.post(
    "/login",
    response_model=TokenWithUsername,
    tags=["Authentication"],
    summary="Login user and get access tokens",
    description="""
    Authenticate a user and return JWT access and refresh tokens.
    
    ## Authentication Flow
    
    1. Send username and password
    2. Receive access and refresh tokens
    3. Use access token for API requests
    4. Refresh token when access token expires
    
    ## Token Usage
    
    Include the access token in the Authorization header:
    ```
    Authorization: Bearer <access_token>
    ```
    """,
    responses={
        200: {
            "description": "Login successful",
            "content": {
                "application/json": {
                    "example": {
                        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        "token_type": "bearer",
                        "username": "john_doe",
                    }
                }
            },
        },
        401: {
            "description": "Invalid credentials",
            "content": {
                "application/json": {
                    "example": {"detail": "Invalid username or password"}
                }
            },
        },
    },
)
async def login(
    credentials: UserLogin,
    response: Response,
    auth_service: AuthService = Depends(get_auth_service),
):
    """
    Login user and receive JWT tokens.

    Authenticates the user with username and password, then returns
    JWT access and refresh tokens for API access.

    **Example Request:**
    ```json
    {
        "username": "john_doe",
        "password": "securepassword123"
    }
    ```
    """
    try:
        result = await auth_service.login_user(credentials)
        # Đặt refresh token vào HttpOnly cookie
        response.set_cookie(
            key="refresh_token",
            value=result["refresh_token"],
            httponly=True,
            secure=True,  # chỉ nên dùng khi chạy HTTPS
            samesite="strict",
            max_age=7 * 24 * 3600,
            path="/api/v1/refresh",
        )
        # Không trả refresh_token trong body nữa
        result.pop("refresh_token", None)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post(
    "/refresh",
    response_model=TokenWithUsername,
    tags=["Authentication"],
    summary="Refresh access token",
    description="""
    Get a new access token using a valid refresh token.
    
    ## When to Use
    
    - Access token has expired
    - Need to continue API access without re-login
    
    ## Token Expiration
    
    - **Access Token**: 30 minutes
    - **Refresh Token**: 7 days
    """,
    responses={
        200: {
            "description": "Token refreshed successfully",
            "content": {
                "application/json": {
                    "example": {
                        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        "token_type": "bearer",
                        "username": "john_doe",
                    }
                }
            },
        },
        401: {
            "description": "Invalid or expired refresh token",
            "content": {
                "application/json": {"example": {"detail": "Invalid refresh token"}}
            },
        },
    },
)
async def refresh_token(
    request: Request,
    response: Response,
    auth_service: AuthService = Depends(get_auth_service),
):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=401, detail="No refresh token in cookie")
    result = await auth_service.refresh_access_token(refresh_token)
    # Đặt lại refresh token mới vào cookie
    response.set_cookie(
        key="refresh_token",
        value=result["refresh_token"],
        httponly=True,
        secure=True,
        samesite="strict",
        max_age=7 * 24 * 3600,
        path="/api/v1/refresh",
    )
    result.pop("refresh_token", None)
    return result


@router.post(
    "/logout",
    tags=["Authentication"],
    summary="Logout user and invalidate tokens",
    description="""
    Logout the current user and invalidate their refresh token.
    
    ## Security
    
    - Invalidates the refresh token on the server
    - Client should also clear stored tokens
    - Forces re-authentication for future requests
    """,
    responses={
        200: {
            "description": "Logout successful",
            "content": {
                "application/json": {"example": {"message": "Logged out successfully"}}
            },
        }
    },
)
async def logout(
    request: Request,
    response: Response,
    current_user: User = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service),
):
    refresh_token = request.cookies.get("refresh_token")
    if refresh_token:
        await auth_service.logout_user(refresh_token, current_user.username)
    # Xóa cookie
    response.delete_cookie(key="refresh_token", path="/api/v1/refresh")
    return {"message": "Logged out successfully"}


@router.post(
    "/upload-image",
    tags=["Images"],
    summary="Upload an image file",
    description="""
    Upload an image file to the server.
    
    ## File Requirements
    
    - **Supported formats**: JPEG, PNG, GIF, WebP
    - **Maximum size**: 10MB
    - **Authentication**: Required (Bearer token)
    
    ## File Processing
    
    - File is validated for type and size
    - Unique filename is generated
    - File is stored securely
    - Metadata is saved to database
    
    ## Security
    
    - Only authenticated users can upload
    - Files are isolated per user
    - Original filename is preserved
    """,
    responses={
        200: {
            "description": "Image uploaded successfully",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Image uploaded successfully",
                        "filename": "abc123_vacation.jpg",
                        "file_size": 1024000,
                        "original_filename": "vacation.jpg",
                        "content_type": "image/jpeg",
                        "upload_date": "2024-01-15T10:30:00Z",
                    }
                }
            },
        },
        400: {
            "description": "Invalid file or upload error",
            "content": {
                "application/json": {
                    "example": {"detail": "File size exceeds 10MB limit"}
                }
            },
        },
        401: {
            "description": "Authentication required",
            "content": {
                "application/json": {"example": {"detail": "Not authenticated"}}
            },
        },
    },
    dependencies=[Security(get_current_user)],
)
async def upload_image(
    file: UploadFile = File(..., description="Image file to upload"),
    current_user: User = Depends(get_current_user),
    image_service: ImageService = Depends(get_image_service),
):
    """
    Upload an image file to the server.

    The file will be validated, processed, and stored securely.
    Only the authenticated user can access their uploaded images.

    **Supported file types**: JPEG, PNG, GIF, WebP
    **Maximum file size**: 10MB
    """
    try:
        # Read file content
        file_content = await file.read()

        # Upload image
        image = await image_service.upload_image(
            username=current_user.username,
            file_content=file_content,
            content_type=file.content_type or "application/octet-stream",
            original_filename=file.filename or "unknown",
        )

        return {
            "message": "Image uploaded successfully",
            "filename": image.filename,
            "file_size": image.file_size,
            "original_filename": image.original_filename,
            "content_type": image.content_type,
            "upload_date": image.upload_date.isoformat(),
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading file: {str(e)}")


@router.get(
    "/images",
    response_model=List[ImageInfo],
    tags=["Images"],
    summary="Get all images for current user",
    description="""
    Retrieve all images uploaded by the authenticated user.
    
    ## Response
    
    Returns a list of image information including:
    - Filename (unique identifier)
    - Original filename
    - File size in bytes
    - Content type (MIME type)
    - Upload date
    
    ## Access Control
    
    - Only returns images owned by the authenticated user
    - No access to other users' images
    - Empty list if no images uploaded
    """,
    responses={
        200: {
            "description": "List of user's images",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "filename": "abc123_vacation.jpg",
                            "original_filename": "vacation.jpg",
                            "upload_date": "2024-01-15T10:30:00Z",
                            "file_size": 1024000,
                            "content_type": "image/jpeg",
                        },
                        {
                            "filename": "def456_profile.png",
                            "original_filename": "profile.png",
                            "upload_date": "2024-01-14T15:20:00Z",
                            "file_size": 512000,
                            "content_type": "image/png",
                        },
                    ]
                }
            },
        },
        401: {
            "description": "Authentication required",
            "content": {
                "application/json": {"example": {"detail": "Not authenticated"}}
            },
        },
    },
    dependencies=[Security(get_current_user)],
)
async def get_images(
    current_user: User = Depends(get_current_user),
    image_service: ImageService = Depends(get_image_service),
):
    """
    Get all images uploaded by the current user.

    Returns a list of image metadata for all images owned by the authenticated user.
    The actual image files can be accessed via the `/uploads/{filename}` endpoint.
    """
    try:
        return await image_service.get_user_images(current_user.username)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error retrieving images: {str(e)}"
        )


@router.get(
    "/image/{filename}",
    tags=["Images"],
    summary="Get specific image information",
    description="""
    Retrieve detailed information about a specific image.
    
    ## Parameters
    
    - `filename`: The unique filename of the image
    
    ## Access Control
    
    - Only the image owner can access image information
    - Returns 404 if image doesn't exist or user doesn't own it
    
    ## Usage
    
    Use this endpoint to get metadata before displaying or downloading an image.
    """,
    responses={
        200: {
            "description": "Image information",
            "content": {
                "application/json": {
                    "example": {
                        "filename": "abc123_vacation.jpg",
                        "original_filename": "vacation.jpg",
                        "file_path": "/uploads/abc123_vacation.jpg",
                        "file_size": 1024000,
                        "content_type": "image/jpeg",
                        "upload_date": "2024-01-15T10:30:00Z",
                    }
                }
            },
        },
        404: {
            "description": "Image not found",
            "content": {"application/json": {"example": {"detail": "Image not found"}}},
        },
        401: {
            "description": "Authentication required",
            "content": {
                "application/json": {"example": {"detail": "Not authenticated"}}
            },
        },
    },
)
async def get_image(
    filename: str,
    current_user: User = Depends(get_current_user),
    image_service: ImageService = Depends(get_image_service),
):
    """
    Get detailed information about a specific image.

    Returns complete metadata for the specified image, including file path,
    size, content type, and upload date.
    """
    image = await image_service.get_image(filename, current_user.username)
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")

    return {
        "filename": image.filename,
        "original_filename": image.original_filename,
        "file_path": image.file_path,
        "file_size": image.file_size,
        "content_type": image.content_type,
        "upload_date": image.upload_date.isoformat(),
    }


@router.delete(
    "/image/{filename}",
    tags=["Images"],
    summary="Delete an image",
    description="""
    Delete a specific image from the server.
    
    ## Parameters
    
    - `filename`: The unique filename of the image to delete
    
    ## Access Control
    
    - Only the image owner can delete the image
    - Returns 404 if image doesn't exist or user doesn't own it
    
    ## Effects
    
    - Removes the image file from storage
    - Deletes the image record from database
    - Action cannot be undone
    """,
    responses={
        200: {
            "description": "Image deleted successfully",
            "content": {
                "application/json": {
                    "example": {"message": "Image deleted successfully"}
                }
            },
        },
        404: {
            "description": "Image not found",
            "content": {"application/json": {"example": {"detail": "Image not found"}}},
        },
        401: {
            "description": "Authentication required",
            "content": {
                "application/json": {"example": {"detail": "Not authenticated"}}
            },
        },
    },
)
async def delete_image(
    filename: str,
    current_user: User = Depends(get_current_user),
    image_service: ImageService = Depends(get_image_service),
):
    """
    Delete a specific image from the server.

    Permanently removes the image file and its database record.
    This action cannot be undone.
    """
    success = await image_service.delete_image(filename, current_user.username)
    if not success:
        raise HTTPException(status_code=404, detail="Image not found")

    return {"message": "Image deleted successfully"}


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
        image_path=image_path,
        privacy=privacy,
    )
    db.add(poster)
    await db.commit()
    await db.refresh(poster)
    poster_obj = Poster.from_orm(poster)
    # Notify all clients except the poster, chỉ khi public/community
    if privacy in ("public", "community"):
        try:
            await post_notifier.broadcast_new_post(current_user.username)
        except Exception:
            pass
    return {**poster_obj.dict(), "image_path": public_image_path(poster_obj.image_path)}


@router.get(
    "/posters/",
    response_model=List[Poster],
    tags=["Posters"],
    summary="Get all posters (paginated)",
)
async def get_posters(
    limit: int = 20,
    offset: int = 0,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_optional_user),
):
    # Nếu user chưa đăng nhập, chỉ trả về post public
    username = getattr(current_user, "username", None)
    if username is not None:
        # Đã đăng nhập: lấy post public + post community + post private của chính user, chỉ lấy post chưa bị xóa
        stmt = (
            select(PosterModel)
            .where(
                or_(
                    (PosterModel.privacy == "public"),
                    (PosterModel.privacy == "community"),
                    (PosterModel.username == username),
                ),
                PosterModel.is_deleted == False,
            )
            .order_by(desc(PosterModel.created_at))
            .limit(limit)
            .offset(offset)
        )
    else:
        # Chưa đăng nhập: chỉ lấy post public, chưa bị xóa
        stmt = (
            select(PosterModel)
            .where((PosterModel.privacy == "public"), PosterModel.is_deleted == False)
            .order_by(desc(PosterModel.created_at))
            .limit(limit)
            .offset(offset)
        )
    result = await db.execute(stmt)
    posters = result.scalars().all()
    poster_objs = [Poster.from_orm(p) for p in posters]
    return [
        {**po.dict(), "image_path": public_image_path(po.image_path)}
        for po in poster_objs
    ]


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
):
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
        return {**poster.dict(), "image_path": public_image_path(poster.image_path)}
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
):
    try:
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
):
    """
    Get all deleted (trashed) posters for the current user.
    Returns a list of posts that are in the trash (soft deleted, not yet permanently removed).
    """
    deleted = await poster_service.get_deleted_posts(current_user.username)
    return [
        {**po.dict(), "image_path": public_image_path(po.image_path)} for po in deleted
    ]


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
):
    """
    Permanently delete all posts from the trash (hard delete).
    All posts' metadata will be archived, and image files will be removed.
    """
    count = await poster_service.hard_delete_all_deleted(current_user.username)
    return {"message": f"{count} deleted posters permanently removed"}


@router.get(
    "/posters/archived",
    response_model=List[ArchivedPoster],
    tags=["Posters", "Archive"],
    summary="Get all archived (permanently deleted) posters metadata for current user",
    description="""
    Retrieve all archived posts metadata for the current user.
    These are posts that have been permanently deleted (hard deleted) and only metadata is preserved.
    """,
    dependencies=[Security(get_current_user)],
)
async def get_archived_posters(
    current_user: User = Depends(get_current_user),
    poster_service=Depends(get_poster_service),
):
    """
    Get all archived (permanently deleted) posters metadata for the current user.
    Returns a list of archived post metadata (no image files).
    """
    archived = await poster_service.get_archived_posts(current_user.username)
    return archived


@router.get(
    "/posters/{poster_id}",
    response_model=Poster,
    tags=["Posters"],
    summary="Get poster detail by id",
)
async def get_poster_detail(
    poster_id: int = Path(..., description="ID of the poster"),
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_optional_user),
):
    poster = await db.get(PosterModel, poster_id)
    if poster is None:
        raise HTTPException(status_code=404, detail="Poster not found")
    privacy = str(poster.privacy) if poster.privacy is not None else None
    if privacy == "public":
        pass  # ai cũng xem được
    else:
        # community hoặc private đều cần đăng nhập
        if current_user is None:
            raise HTTPException(
                status_code=403, detail="You must be logged in to view this poster"
            )
        if privacy == "community":
            pass  # chỉ cần đăng nhập là xem được
        elif privacy == "private":
            if current_user.username != poster.username:
                raise HTTPException(
                    status_code=451, detail="Not allowed to view this poster (private)"
                )
    poster_obj = Poster.from_orm(poster)
    return {**poster_obj.dict(), "image_path": public_image_path(poster_obj.image_path)}


@router.delete(
    "/posters/{poster_id}/hard",
    tags=["Posters", "Trash"],
    summary="Permanently delete a single deleted poster (hard delete)",
    description="""
    Permanently delete a single post from the trash for the current user.
    This will archive the metadata for the deleted post and remove its image file.
    Only the post owner can perform this action, and only if the post is already soft deleted.
    """,
    response_model=ArchivedPoster,
    dependencies=[Security(get_current_user)],
)
async def hard_delete_single_deleted_poster(
    poster_id: int,
    current_user: User = Depends(get_current_user),
    poster_service=Depends(get_poster_service),
):
    try:
        archived = await poster_service.hard_delete_post(
            poster_id, current_user.username
        )
        return archived
    except ValueError as e:
        raise HTTPException(
            status_code=403 if "not allowed" in str(e).lower() else 404, detail=str(e)
        )
