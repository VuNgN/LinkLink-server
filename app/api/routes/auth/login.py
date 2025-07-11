"""
Authentication login routes
Handles login, refresh token, and logout
"""

from typing import Optional

from fastapi import (APIRouter, Depends, HTTPException, Request, Response,
                     status)
from fastapi.security.utils import get_authorization_scheme_param

from ....core.entities import Token, User, UserLogin
from ....core.services import AuthService
from ...dependencies import get_auth_service, get_current_user


class TokenWithUsername(Token):
    refresh_token: Optional[str] = None
    username: str


router = APIRouter()


@router.post(
    "/login",  # Backward compatibility
    response_model=TokenWithUsername,
    summary="Login user and get access tokens (legacy endpoint)",
    include_in_schema=False,  # Hide from docs
)
async def login_legacy(
    credentials: UserLogin,
    response: Response,
    auth_service: AuthService = Depends(get_auth_service),
):
    """Legacy login endpoint - redirects to /auth/login"""
    return await login(credentials, response, auth_service)


@router.post(
    "/auth/login",
    response_model=TokenWithUsername,
    summary="Login user and get access tokens",
    description="""
    Authenticate a user and return JWT access and refresh tokens.
    ## Authentication Flow
    1. Send username and password
    2. Receive access and refresh tokens
    3. Use access token for API requests
    4. Refresh token when access token expires
    ## Token Usage
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
    Login user and return JWT tokens.
    """
    try:
        token_data = await auth_service.login_user(credentials)
        return TokenWithUsername(
            access_token=token_data["access_token"],
            refresh_token=token_data["refresh_token"],
            token_type=token_data["token_type"],
            expires_at=token_data["expires_at"],
            username=token_data["username"],
        )
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.post(
    "/refresh",  # Backward compatibility
    response_model=TokenWithUsername,
    summary="Refresh access token (legacy endpoint)",
    include_in_schema=False,  # Hide from docs
)
async def refresh_token_legacy(
    request: Request,
    response: Response,
    auth_service: AuthService = Depends(get_auth_service),
):
    """Legacy refresh endpoint - redirects to /auth/refresh"""
    return await refresh_token(request, response, auth_service)


@router.post(
    "/auth/refresh",
    response_model=TokenWithUsername,
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
    """
    Refresh access token using refresh token.
    """
    auth = request.headers.get("Authorization") or ""
    scheme, param = get_authorization_scheme_param(auth)

    if not auth or scheme.lower() != "bearer" or not param:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header",
        )

    try:
        token_data = await auth_service.refresh_access_token(param)
        return TokenWithUsername(
            access_token=token_data["access_token"],
            refresh_token=token_data["refresh_token"],
            token_type=token_data["token_type"],
            expires_at=token_data["expires_at"],
            username=token_data["username"],
        )
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.post(
    "/logout",  # Backward compatibility
    summary="Logout user and invalidate tokens (legacy endpoint)",
    include_in_schema=False,  # Hide from docs
)
async def logout_legacy(
    request: Request,
    response: Response,
    current_user: User = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service),
):
    """Legacy logout endpoint - redirects to /auth/logout"""
    return await logout(request, response, current_user, auth_service)


@router.post(
    "/auth/logout",
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
    """
    Logout user and invalidate tokens.
    """
    auth = request.headers.get("Authorization") or ""
    scheme, param = get_authorization_scheme_param(auth)

    if auth and scheme.lower() == "bearer" and param:
        await auth_service.logout_user(param, current_user.username)

    return {"message": "Logged out successfully"}
