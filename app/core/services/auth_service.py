"""
Authentication and authorization service
"""

from datetime import datetime, timedelta, timezone
from typing import List

import bcrypt
from jose import jwt

from ..entities import (AdminApprovalRequest, PendingUserInfo, User,
                        UserCreate, UserLogin, UserRegistrationResponse,
                        UserStatus)
from ..interfaces import RefreshTokenRepository, UserRepository
from .email_service import EmailService


class AuthService:
    """Authentication and authorization service"""

    def __init__(
        self,
        user_repository: UserRepository,
        refresh_token_repository: RefreshTokenRepository,
        email_service: EmailService,
        secret_key: str,
        admin_email: str,
    ):
        self.user_repository = user_repository
        self.refresh_token_repository = refresh_token_repository
        self.email_service = email_service
        self.secret_key = secret_key
        self.admin_email = admin_email
        self.algorithm = "HS256"
        self.access_token_expire_minutes = 30
        self.refresh_token_expire_days = 7

    async def register_user(self, user_data: UserCreate) -> UserRegistrationResponse:
        """Register a new user (pending admin approval)"""
        # Check if username already exists
        existing_user = await self.user_repository.get_by_username(user_data.username)
        if existing_user:
            raise ValueError("Username already exists")

        # Check if email already exists
        existing_email = await self.user_repository.get_by_email(user_data.email)
        if existing_email:
            raise ValueError("Email already registered")

        # Hash password
        hashed_password = bcrypt.hashpw(
            user_data.password.encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8")

        # Create user with pending status
        user = User(
            username=user_data.username,
            email=user_data.email,
            hashed_password=hashed_password,
            status=UserStatus.PENDING,
            is_active=False,  # Inactive until approved
        )

        await self.user_repository.create(user)

        # Send notification to admin (optional - don't fail registration if email fails)
        try:
            await self.email_service.send_registration_notification(
                user_data.email, user_data.username, self.admin_email
            )
        except Exception as e:
            # Log the error but don't fail the registration
            import logging

            logger = logging.getLogger(__name__)
            logger.warning(f"Failed to send registration notification email: {e}")

        return UserRegistrationResponse(
            message=(
                "Registration submitted successfully. "
                "Your account will be reviewed by an administrator."
            ),
            status="pending",
            email=user_data.email,
        )

    async def login_user(self, credentials: UserLogin) -> dict:
        """Login user and return JWT tokens"""
        user = await self.user_repository.get_by_username(credentials.username)
        if not user:
            raise ValueError("Invalid username or password")

        # Check if user is approved
        if user.status != UserStatus.APPROVED:
            if user.status == UserStatus.PENDING:
                raise ValueError(
                    "Account is pending approval. Please wait for admin review."
                )
            elif user.status == UserStatus.REJECTED:
                raise ValueError("Account has been rejected. Please contact support.")

        # Check if user is active
        if not user.is_active:
            raise ValueError("Account is deactivated")

        # Verify password
        if not bcrypt.checkpw(
            credentials.password.encode("utf-8"), user.hashed_password.encode("utf-8")
        ):
            raise ValueError("Invalid username or password")

        # Create tokens
        access_token = self._create_access_token(user.username, user.is_admin)
        refresh_token = self._create_refresh_token(user.username, user.is_admin)

        # Store refresh token
        await self.refresh_token_repository.create(
            token=refresh_token,
            username=user.username,
            expires_at=datetime.now(timezone.utc)
            + timedelta(days=self.refresh_token_expire_days),
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_at": datetime.now(timezone.utc)
            + timedelta(minutes=self.access_token_expire_minutes),
            "username": user.username,
        }

    async def approve_user(self, request: AdminApprovalRequest) -> dict:
        """Approve or reject a user registration"""
        user = await self.user_repository.get_by_username(request.username)
        if not user:
            raise ValueError("User not found")

        if user.status != UserStatus.PENDING:
            raise ValueError(f"User is already {user.status}")

        if request.action.lower() == "approve":
            user.status = UserStatus.APPROVED
            user.is_active = True
            user.approved_at = datetime.now(timezone.utc)
            user.approved_by = request.admin_username
            await self.user_repository.update(user)

            # Send approval notification (optional - don't fail if email fails)
            try:
                await self.email_service.send_approval_notification(
                    user.email, user.username, True, request.reason
                )
            except Exception as e:
                import logging

                logger = logging.getLogger(__name__)
                logger.warning(f"Failed to send approval notification email: {e}")

            return {"message": f"User {user.username} approved successfully"}

        elif request.action.lower() == "reject":
            user.status = UserStatus.REJECTED
            user.is_active = False
            await self.user_repository.update(user)

            # Send rejection notification (optional - don't fail if email fails)
            try:
                await self.email_service.send_approval_notification(
                    user.email, user.username, False, request.reason
                )
            except Exception as e:
                import logging

                logger = logging.getLogger(__name__)
                logger.warning(f"Failed to send rejection notification email: {e}")

            return {"message": f"User {user.username} rejected"}
        else:
            raise ValueError("Invalid action. Use 'approve' or 'reject'")

    async def get_pending_users(self) -> List[PendingUserInfo]:
        """Get list of pending user registrations"""
        users = await self.user_repository.get_by_status(UserStatus.PENDING)
        return [
            PendingUserInfo(
                username=user.username, email=user.email, created_at=user.created_at
            )
            for user in users
        ]

    def _create_access_token(self, username: str, is_admin: bool = False) -> str:
        """Create JWT access token"""
        to_encode = {
            "sub": username,
            "is_admin": is_admin,
            "exp": datetime.now(timezone.utc)
            + timedelta(minutes=self.access_token_expire_minutes),
        }
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

    def _create_refresh_token(self, username: str, is_admin: bool = False) -> str:
        """Create JWT refresh token"""
        to_encode = {
            "sub": username,
            "is_admin": is_admin,
            "exp": datetime.now(timezone.utc)
            + timedelta(days=self.refresh_token_expire_days),
        }
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

    def verify_token(self, token: str) -> str:
        """Verify JWT token and return username"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            username = payload.get("sub")
            if username is None:
                raise ValueError("Invalid token")
            return username
        except Exception:
            raise ValueError("Invalid token")

    async def refresh_access_token(self, refresh_token: str) -> dict:
        """Refresh access token using refresh token"""
        # Verify refresh token
        username = self.verify_token(refresh_token)

        # Check if refresh token exists in database
        stored_token = await self.refresh_token_repository.get_by_token(refresh_token)
        if not stored_token:
            raise ValueError("Invalid refresh token")

        # Check if token is expired
        if stored_token.expires_at < datetime.now(timezone.utc):
            await self.refresh_token_repository.delete_by_token(refresh_token)
            raise ValueError("Refresh token expired")

        # Get user
        user = await self.user_repository.get_by_username(username)
        if not user or not user.is_active or user.status != UserStatus.APPROVED:
            raise ValueError("User not found or inactive")

        # Create new tokens
        new_access_token = self._create_access_token(username, user.is_admin)
        new_refresh_token = self._create_refresh_token(username, user.is_admin)

        # Store new refresh token and delete old one
        await self.refresh_token_repository.delete_by_token(refresh_token)
        await self.refresh_token_repository.create(
            token=new_refresh_token,
            username=username,
            expires_at=datetime.now(timezone.utc)
            + timedelta(days=self.refresh_token_expire_days),
        )

        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer",
            "expires_at": datetime.now(timezone.utc)
            + timedelta(minutes=self.access_token_expire_minutes),
            "username": user.username,
        }

    async def logout_user(self, refresh_token: str, username: str):
        """Logout user by invalidating refresh token"""
        await self.refresh_token_repository.delete_by_token(refresh_token)
