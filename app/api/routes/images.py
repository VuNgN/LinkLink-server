"""
Image management routes
Handles image upload, retrieval, and deletion
"""

from typing import List

from fastapi import (APIRouter, Depends, File, HTTPException, Security,
                     UploadFile)

from ...core.entities import ImageInfo, User
from ...core.services import ImageService
from ..dependencies import get_current_user, get_image_service
from .utils import to_public_path

router = APIRouter()


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
                            "file_path": "/uploads/abc123_vacation.jpg",
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
        images = await image_service.get_user_images(current_user.username)
        # Ensure file_path is public
        for img in images:
            img["file_path"] = to_public_path(img.get("file_path", ""))
        return images
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
        "file_path": to_public_path(image.file_path),
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
