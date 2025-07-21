"""
Authentication admin routes
Handles admin approval and user management
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException

from ....core.entities import AdminApprovalRequest, PendingUserInfo, User
from ....core.services import AuthService
from ...dependencies import get_auth_service, get_current_admin_user

router = APIRouter()


@router.post(
    "/admin/approve-user",
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
    """
    try:
        return await auth_service.approve_user(request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/admin/pending-users",
    response_model=List[PendingUserInfo],
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
    return await auth_service.get_pending_users()
