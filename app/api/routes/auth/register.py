"""
Authentication registration routes
Handles user registration
"""

from fastapi import APIRouter, Depends, HTTPException

from ....core.entities import UserCreate, UserRegistrationResponse
from ....core.services import AuthService
from ...dependencies import get_auth_service

router = APIRouter()


@router.post(
    "/register",  # Backward compatibility
    response_model=UserRegistrationResponse,
    summary="Register a new user (legacy endpoint)",
    include_in_schema=False,  # Hide from docs
)
async def register_legacy(
    user_data: UserCreate, auth_service: AuthService = Depends(get_auth_service)
):
    """Legacy register endpoint - redirects to /auth/register"""
    return await register(user_data, auth_service)


@router.post(
    "/auth/register",
    response_model=UserRegistrationResponse,
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
                        "message": """Registration submitted successfully.
                        Your account will be reviewed by an administrator.""",
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
    """
    try:
        return await auth_service.register_user(user_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
