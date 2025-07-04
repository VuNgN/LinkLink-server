"""
Business logic services - Core use cases
"""

from datetime import datetime, timedelta
from typing import List, Optional

import bcrypt
from fastapi import HTTPException, status
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import EmailStr

from .entities import (AdminApprovalRequest, Image, ImageInfo, PendingUserInfo,
                       RefreshTokenRequest, Token, User, UserCreate, UserLogin,
                       UserRegistrationResponse, UserStatus)
from .interfaces import (FileStorage, ImageRepository, RefreshTokenRepository,
                         TokenRepository, UserRepository)


class EmailService:
    """Email service for sending notifications"""

    def __init__(self, mail_config: ConnectionConfig):
        self.fastmail = FastMail(mail_config)

    async def send_registration_notification(
        self, user_email: str, username: str, admin_email: str
    ):
        """Send registration notification to admin"""
        message = MessageSchema(
            subject="New User Registration - LinkLink Server",
            recipients=[admin_email],
            body=f"""
            <html>
                <body>
                    <h2>New User Registration</h2>
                    <p>A new user has registered for an account:</p>
                    <ul>
                        <li><strong>Username:</strong> {username}</li>
                        <li><strong>Email:</strong> {user_email}</li>
                        <li><strong>Registration Date:</strong> {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}</li>
                    </ul>
                    <p>Please review and approve/reject this registration.</p>
                    <p>You can approve or reject this user through the admin interface.</p>
                </body>
            </html>
            """,
            subtype="html",
        )
        await self.fastmail.send_message(message)

    async def send_approval_notification(
        self,
        user_email: str,
        username: str,
        approved: bool,
        reason: Optional[str] = None,
    ):
        """Send approval/rejection notification to user"""
        status = "approved" if approved else "rejected"
        subject = f"Account {status.title()} - LinkLink Server"

        body_content = f"""
        <html>
            <body>
                <h2>Account {status.title()}</h2>
                <p>Dear {username},</p>
                <p>Your account registration has been <strong>{status}</strong>.</p>
        """

        if approved:
            body_content += """
                <p>You can now log in to your account and start using our services.</p>
                <p>Thank you for choosing LinkLink Server!</p>
            """
        else:
            body_content += f"""
                <p>Reason: {reason or 'No specific reason provided'}</p>
                <p>If you believe this was an error, please contact support.</p>
            """

        body_content += """
            </body>
        </html>
        """

        message = MessageSchema(
            subject=subject, recipients=[user_email], body=body_content, subtype="html"
        )
        await self.fastmail.send_message(message)


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

        # Send notification to admin
        await self.email_service.send_registration_notification(
            user_data.email, user_data.username, self.admin_email
        )

        return UserRegistrationResponse(
            message="Registration submitted successfully. Your account will be reviewed by an administrator.",
            status="pending",
            email=user_data.email,
        )

    async def login_user(self, credentials: UserLogin) -> Token:
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
            expires_at=datetime.utcnow()
            + timedelta(days=self.refresh_token_expire_days),
        )

        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_at=datetime.utcnow()
            + timedelta(minutes=self.access_token_expire_minutes),
        )

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
            user.approved_at = datetime.utcnow()
            user.approved_by = request.admin_username
            await self.user_repository.update(user)

            # Send approval notification
            await self.email_service.send_approval_notification(
                user.email, user.username, True, request.reason
            )

            return {"message": f"User {user.username} approved successfully"}

        elif request.action.lower() == "reject":
            user.status = UserStatus.REJECTED
            user.is_active = False
            await self.user_repository.update(user)

            # Send rejection notification
            await self.email_service.send_approval_notification(
                user.email, user.username, False, request.reason
            )

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
            "exp": datetime.utcnow()
            + timedelta(minutes=self.access_token_expire_minutes),
        }
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

    def _create_refresh_token(self, username: str, is_admin: bool = False) -> str:
        """Create JWT refresh token"""
        to_encode = {
            "sub": username,
            "is_admin": is_admin,
            "exp": datetime.utcnow() + timedelta(days=self.refresh_token_expire_days),
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
        except JWTError:
            raise ValueError("Invalid token")

    async def refresh_access_token(self, refresh_token: str) -> Token:
        """Refresh access token using refresh token"""
        # Verify refresh token
        username = self.verify_token(refresh_token)

        # Check if refresh token exists in database
        stored_token = await self.refresh_token_repository.get_by_token(refresh_token)
        if not stored_token:
            raise ValueError("Invalid refresh token")

        # Check if token is expired
        if stored_token.expires_at < datetime.utcnow():
            await self.refresh_token_repository.delete_by_token(refresh_token)
            raise ValueError("Refresh token expired")

        # Get user
        user = await self.user_repository.get_by_username(username)
        if not user or not user.is_active or user.status != UserStatus.APPROVED:
            raise ValueError("User not found or inactive")

        # Create new tokens
        new_access_token = self._create_access_token(username, user.is_admin)
        new_refresh_token = self._create_refresh_token(username, user.is_admin)

        return Token(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
            expires_at=datetime.utcnow()
            + timedelta(minutes=self.access_token_expire_minutes),
        )

    async def logout_user(self, refresh_token: str, username: str):
        """Logout user by invalidating refresh token"""
        await self.refresh_token_repository.delete_by_token(refresh_token)


class ImageService:
    """Image management business logic"""

    def __init__(
        self,
        image_repo: ImageRepository,
        file_storage: FileStorage,
        upload_dir: str = "uploads",
        max_file_size: int = 10 * 1024 * 1024,  # 10MB
        allowed_types: List[str] = None,
    ):
        self.image_repo = image_repo
        self.file_storage = file_storage
        self.upload_dir = upload_dir
        self.max_file_size = max_file_size
        self.allowed_types = allowed_types or [
            "image/jpeg",
            "image/png",
            "image/gif",
            "image/webp",
        ]

    def _validate_file(
        self, file_content: bytes, content_type: str, original_filename: str
    ) -> None:
        """Validate uploaded file"""
        if not content_type.startswith("image/"):
            raise ValueError("File must be an image")

        if content_type not in self.allowed_types:
            raise ValueError(f"File type {content_type} not allowed")

        if len(file_content) > self.max_file_size:
            raise ValueError(f"File size exceeds maximum of {self.max_file_size} bytes")

        if not original_filename:
            raise ValueError("Filename is required")

    def _generate_filename(self, username: str, original_filename: str) -> str:
        """Generate unique filename"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_extension = (
            original_filename.split(".")[-1] if "." in original_filename else "jpg"
        )
        return f"{username}_{timestamp}.{file_extension}"

    async def upload_image(
        self,
        username: str,
        file_content: bytes,
        content_type: str,
        original_filename: str,
    ) -> Image:
        """Upload image for user"""
        # Validate file
        self._validate_file(file_content, content_type, original_filename)

        # Generate unique filename
        filename = self._generate_filename(username, original_filename)

        # Save file
        file_path = await self.file_storage.save_file(file_content, filename)

        # Create image record
        image = Image(
            filename=filename,
            original_filename=original_filename,
            username=username,
            file_path=file_path,
            file_size=len(file_content),
            content_type=content_type,
        )

        return await self.image_repo.create(image)

    async def get_user_images(self, username: str) -> List[ImageInfo]:
        """Get all images for a user"""
        images = await self.image_repo.get_by_username(username)
        return [
            ImageInfo(
                filename=img.filename,
                original_filename=img.original_filename,
                upload_date=img.upload_date,
                file_size=img.file_size,
                content_type=img.content_type,
            )
            for img in sorted(images, key=lambda x: x.upload_date, reverse=True)
        ]

    async def get_image(self, filename: str, username: str) -> Optional[Image]:
        """Get specific image (with ownership check)"""
        image = await self.image_repo.get_by_filename(filename)
        if not image or image.username != username:
            return None
        return image

    async def delete_image(self, filename: str, username: str) -> bool:
        """Delete image (with ownership check)"""
        image = await self.image_repo.get_by_filename(filename)
        if not image or image.username != username:
            return False

        # Delete file from storage
        await self.file_storage.delete_file(image.file_path)

        # Delete from repository
        return await self.image_repo.delete(filename)
