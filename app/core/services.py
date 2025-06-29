"""
Business logic services - Core use cases
"""
from datetime import datetime, timedelta
from typing import List, Optional
from passlib.context import CryptContext
from jose import JWTError, jwt

from .entities import User, Image, Token, UserCreate, UserLogin, ImageInfo
from .interfaces import UserRepository, ImageRepository, TokenRepository, FileStorage

class AuthService:
    """Authentication business logic"""
    
    def __init__(
        self,
        user_repo: UserRepository,
        token_repo: TokenRepository,
        secret_key: str,
        algorithm: str = "HS256",
        access_token_expire_minutes: int = 30,
        refresh_token_expire_days: int = 7
    ):
        self.user_repo = user_repo
        self.token_repo = token_repo
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_token_expire_minutes = access_token_expire_minutes
        self.refresh_token_expire_days = refresh_token_expire_days
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def _get_password_hash(self, password: str) -> str:
        """Hash password"""
        return self.pwd_context.hash(password)
    
    def _create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"exp": expire, "type": "access"})
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
    
    def _create_refresh_token(self, data: dict) -> str:
        """Create JWT refresh token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)
        to_encode.update({"exp": expire, "type": "refresh"})
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
    
    async def register_user(self, user_data: UserCreate) -> User:
        """Register a new user"""
        # Check if user already exists
        existing_user = await self.user_repo.get_by_username(user_data.username)
        if existing_user:
            raise ValueError("Username already registered")
        
        # Create new user
        hashed_password = self._get_password_hash(user_data.password)
        user = User(
            username=user_data.username,
            hashed_password=hashed_password,
            is_active=True
        )
        
        return await self.user_repo.create(user)
    
    async def authenticate_user(self, credentials: UserLogin) -> Optional[User]:
        """Authenticate user with username and password"""
        user = await self.user_repo.get_by_username(credentials.username)
        if not user or not user.is_active:
            return None
        
        if not self._verify_password(credentials.password, user.hashed_password):
            return None
        
        return user
    
    async def login_user(self, credentials: UserLogin) -> Token:
        """Login user and return tokens"""
        user = await self.authenticate_user(credentials)
        if not user:
            raise ValueError("Incorrect username or password")
        
        # Create tokens
        access_token_expires = timedelta(minutes=self.access_token_expire_minutes)
        access_token = self._create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        refresh_token = self._create_refresh_token(data={"sub": user.username})
        
        # Store refresh token
        await self.token_repo.store_refresh_token(refresh_token, user.username)
        
        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_at=datetime.utcnow() + access_token_expires
        )
    
    async def refresh_token(self, refresh_token: str) -> Token:
        """Refresh access token using refresh token"""
        try:
            payload = jwt.decode(refresh_token, self.secret_key, algorithms=[self.algorithm])
            username: str = payload.get("sub")
            token_type: str = payload.get("type")
            
            if not username or token_type != "refresh":
                raise ValueError("Invalid refresh token")
            
            # Verify token exists in storage
            stored_username = await self.token_repo.get_username_by_refresh_token(refresh_token)
            if not stored_username or stored_username != username:
                raise ValueError("Refresh token not found")
            
            # Verify user exists
            user = await self.user_repo.get_by_username(username)
            if not user or not user.is_active:
                raise ValueError("User not found")
            
            # Create new tokens
            access_token_expires = timedelta(minutes=self.access_token_expire_minutes)
            new_access_token = self._create_access_token(
                data={"sub": username}, expires_delta=access_token_expires
            )
            new_refresh_token = self._create_refresh_token(data={"sub": username})
            
            # Update token storage
            await self.token_repo.delete_refresh_token(refresh_token)
            await self.token_repo.store_refresh_token(new_refresh_token, username)
            
            return Token(
                access_token=new_access_token,
                refresh_token=new_refresh_token,
                token_type="bearer",
                expires_at=datetime.utcnow() + access_token_expires
            )
            
        except JWTError:
            raise ValueError("Invalid refresh token")
    
    async def logout_user(self, refresh_token: str) -> bool:
        """Logout user by invalidating refresh token"""
        return await self.token_repo.delete_refresh_token(refresh_token)
    
    async def get_current_user(self, token: str) -> Optional[User]:
        """Get current user from access token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            username: str = payload.get("sub")
            token_type: str = payload.get("type")
            
            if not username or token_type != "access":
                return None
            
            user = await self.user_repo.get_by_username(username)
            if not user or not user.is_active:
                return None
            
            return user
            
        except JWTError:
            return None

class ImageService:
    """Image management business logic"""
    
    def __init__(
        self,
        image_repo: ImageRepository,
        file_storage: FileStorage,
        upload_dir: str = "uploads",
        max_file_size: int = 10 * 1024 * 1024,  # 10MB
        allowed_types: List[str] = None
    ):
        self.image_repo = image_repo
        self.file_storage = file_storage
        self.upload_dir = upload_dir
        self.max_file_size = max_file_size
        self.allowed_types = allowed_types or ["image/jpeg", "image/png", "image/gif", "image/webp"]
    
    def _validate_file(self, file_content: bytes, content_type: str, original_filename: str) -> None:
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
        file_extension = original_filename.split(".")[-1] if "." in original_filename else "jpg"
        return f"{username}_{timestamp}.{file_extension}"
    
    async def upload_image(self, username: str, file_content: bytes, content_type: str, original_filename: str) -> Image:
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
            content_type=content_type
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
                content_type=img.content_type
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