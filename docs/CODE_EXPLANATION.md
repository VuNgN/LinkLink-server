# 📚 Code Explanation & Architecture Guide

Comprehensive guide explaining the Clean Architecture implementation and design patterns.

## 🏗️ Architecture Overview

### Clean Architecture Principles

This project follows **Clean Architecture** principles:

```
┌─────────────────────────────────────┐
│           Presentation Layer        │  ← API Routes, HTTP handling
├─────────────────────────────────────┤
│           Business Logic            │  ← Core services, use cases
├─────────────────────────────────────┤
│           Data Access               │  ← Repositories, database
├─────────────────────────────────────┤
│           External Services         │  ← File system, external APIs
└─────────────────────────────────────┘
```

### Key Benefits

- **Independence**: Business logic is independent of frameworks
- **Testability**: Easy to test business logic in isolation
- **Flexibility**: Easy to swap implementations
- **Maintainability**: Clear separation of concerns

## 📁 Project Structure

```
app/
├── core/                    # Domain Layer (Business Logic)
│   ├── entities.py         # Domain entities (User, Image, Token)
│   ├── interfaces.py       # Repository interfaces (abstractions)
│   └── services.py         # Business logic services
├── infrastructure/         # Data Layer (External Concerns)
│   ├── database.py         # Database configuration
│   ├── models.py           # SQLAlchemy models
│   └── postgresql_repositories.py # PostgreSQL implementations
├── api/                    # Presentation Layer (HTTP Interface)
│   ├── dependencies.py     # Dependency injection setup
│   └── routes.py          # API endpoints
└── __init__.py

main_clean.py              # Application entry point
database_setup.py          # Database initialization script
```

## 🎯 Core Domain Layer

### Entities (`app/core/entities.py`)

Domain entities represent the core business objects:

```python
@dataclass
class User:
    """User domain entity"""
    username: str
    hashed_password: str
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

@dataclass
class Image:
    """Image domain entity"""
    filename: str
    original_filename: str
    username: str
    file_path: str
    file_size: int
    content_type: str
    upload_date: Optional[datetime] = None

@dataclass
class RefreshToken:
    """Refresh token domain entity"""
    token: str
    username: str
    created_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
```

**Key Points:**
- **Pure Python**: No framework dependencies
- **Data Classes**: Clean, immutable data structures
- **Type Hints**: Clear interface definitions

### Interfaces (`app/core/interfaces.py`)

Repository interfaces define contracts for data access:

```python
class UserRepository(ABC):
    """Abstract interface for user data access"""
    
    @abstractmethod
    async def create(self, user: User) -> User:
        pass
    
    @abstractmethod
    async def get_by_username(self, username: str) -> Optional[User]:
        pass

class ImageRepository(ABC):
    """Abstract interface for image data access"""
    
    @abstractmethod
    async def create(self, image: Image) -> Image:
        pass
    
    @abstractmethod
    async def get_by_username(self, username: str) -> List[Image]:
        pass
```

**Benefits:**
- **Dependency Inversion**: High-level modules don't depend on low-level modules
- **Testability**: Easy to mock for testing
- **Flexibility**: Can swap implementations easily

### Services (`app/core/services.py`)

Business logic services implement use cases:

```python
class AuthService:
    """Authentication business logic"""
    
    def __init__(self, user_repo: UserRepository, token_repo: RefreshTokenRepository, secret_key: str):
        self.user_repo = user_repo
        self.token_repo = token_repo
        self.secret_key = secret_key
    
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode(), salt).decode()
    
    async def register_user(self, username: str, password: str) -> User:
        """Register a new user"""
        existing_user = await self.user_repo.get_by_username(username)
        if existing_user:
            raise ValueError("Username already exists")
        
        hashed_password = self.hash_password(password)
        user = User(username=username, hashed_password=hashed_password)
        return await self.user_repo.create(user)

class ImageService:
    """Image management business logic"""
    
    def __init__(self, image_repo: ImageRepository, upload_dir: str):
        self.image_repo = image_repo
        self.upload_dir = upload_dir
    
    def validate_file(self, file_content: bytes, content_type: str) -> bool:
        """Validate uploaded file"""
        if len(file_content) > 10 * 1024 * 1024:  # 10MB limit
            return False
        
        allowed_types = ["image/jpeg", "image/png", "image/gif", "image/webp"]
        return content_type in allowed_types
    
    async def upload_image(self, file_content: bytes, original_filename: str, 
                          content_type: str, username: str) -> Image:
        """Upload and save image"""
        if not self.validate_file(file_content, content_type):
            raise ValueError("Invalid file")
        
        filename = self.generate_filename(original_filename)
        file_path = os.path.join(self.upload_dir, filename)
        
        # Save file to disk
        with open(file_path, "wb") as f:
            f.write(file_content)
        
        # Save metadata to database
        image = Image(
            filename=filename,
            original_filename=original_filename,
            username=username,
            file_path=file_path,
            file_size=len(file_content),
            content_type=content_type
        )
        
        return await self.image_repo.create(image)
```

## 🗄️ Infrastructure Layer

### Database Configuration (`app/infrastructure/database.py`)

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:password@localhost:5432/image_upload_db")

engine = create_async_engine(
    DATABASE_URL,
    echo=os.getenv("DB_ECHO", "false").lower() == "true",
    pool_pre_ping=True
)

AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()

async def get_db_session() -> AsyncSession:
    """Dependency to get database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
```

### SQLAlchemy Models (`app/infrastructure/models.py`)

```python
class UserModel(Base):
    """SQLAlchemy model for users table"""
    __tablename__ = "users"
    
    username = Column(String(50), primary_key=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class ImageModel(Base):
    """SQLAlchemy model for images table"""
    __tablename__ = "images"
    
    filename = Column(String(255), primary_key=True)
    original_filename = Column(String(255), nullable=False)
    username = Column(String(50), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False)
    content_type = Column(String(100), nullable=False)
    upload_date = Column(DateTime(timezone=True), server_default=func.now())
```

### PostgreSQL Repositories (`app/infrastructure/postgresql_repositories.py`)

```python
class PostgreSQLUserRepository(UserRepository):
    """PostgreSQL implementation of UserRepository"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, user: User) -> User:
        """Create a new user"""
        user_model = UserModel(
            username=user.username,
            hashed_password=user.hashed_password,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at
        )
        
        self.session.add(user_model)
        await self.session.commit()
        await self.session.refresh(user_model)
        
        return User(
            username=user_model.username,
            hashed_password=user_model.hashed_password,
            is_active=user_model.is_active,
            created_at=user_model.created_at,
            updated_at=user_model.updated_at
        )
    
    async def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        result = await self.session.execute(
            select(UserModel).where(UserModel.username == username)
        )
        user_model = result.scalar_one_or_none()
        
        if not user_model:
            return None
        
        return User(
            username=user_model.username,
            hashed_password=user_model.hashed_password,
            is_active=user_model.is_active,
            created_at=user_model.created_at,
            updated_at=user_model.updated_at
        )
```

## 🌐 API Layer

### Dependency Injection (`app/api/dependencies.py`)

```python
def get_user_repository(session: AsyncSession = Depends(get_db_session)) -> PostgreSQLUserRepository:
    """Dependency to get user repository"""
    return PostgreSQLUserRepository(session)

def get_auth_service(
    user_repo: PostgreSQLUserRepository = Depends(get_user_repository),
    token_repo: PostgreSQLRefreshTokenRepository = Depends(get_token_repository)
) -> AuthService:
    """Dependency to get authentication service"""
    secret_key = os.getenv("SECRET_KEY", "your-secret-key")
    return AuthService(user_repo, token_repo, secret_key)
```

### API Routes (`app/api/routes.py`)

```python
@router.post("/register", response_model=dict)
async def register(
    user_data: UserRegister,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Register a new user"""
    try:
        user = await auth_service.register_user(user_data.username, user_data.password)
        return {"message": "User registered successfully", "username": user.username}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/upload-image", response_model=ImageResponse)
async def upload_image(
    file: UploadFile = File(...),
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthService = Depends(get_auth_service),
    image_service: ImageService = Depends(get_image_service)
):
    """Upload an image"""
    # Verify token
    username = auth_service.verify_access_token(credentials.credentials)
    if not username:
        raise HTTPException(status_code=401, detail="Invalid access token")
    
    # Read file content
    content = await file.read()
    
    try:
        # Upload image
        image = await image_service.upload_image(
            content, file.filename, file.content_type, username
        )
        
        return ImageResponse(
            filename=image.filename,
            original_filename=image.original_filename,
            file_size=image.file_size,
            content_type=image.content_type,
            upload_date=image.upload_date
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
```

## 🎨 Design Patterns

### 1. Dependency Injection Pattern

```python
# Services receive dependencies through constructor
class AuthService:
    def __init__(self, user_repo: UserRepository, token_repo: RefreshTokenRepository):
        self.user_repo = user_repo
        self.token_repo = token_repo

# FastAPI dependency injection
def get_auth_service(user_repo: UserRepository = Depends(get_user_repository)) -> AuthService:
    return AuthService(user_repo)
```

### 2. Repository Pattern

```python
# Abstract interface
class UserRepository(ABC):
    @abstractmethod
    async def get_by_username(self, username: str) -> Optional[User]:
        pass

# Concrete implementation
class PostgreSQLUserRepository(UserRepository):
    async def get_by_username(self, username: str) -> Optional[User]:
        # PostgreSQL-specific implementation
        pass
```

### 3. Service Layer Pattern

```python
class AuthService:
    async def register_user(self, username: str, password: str) -> User:
        # Business logic here
        # Validation, password hashing, etc.
        pass
```

## 🔒 Security Implementation

### 1. Password Security

```python
def hash_password(self, password: str) -> str:
    """Hash password using bcrypt with salt"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt).decode()

def verify_password(self, password: str, hashed: str) -> bool:
    """Verify password against hash"""
    return bcrypt.checkpw(password.encode(), hashed.encode())
```

### 2. JWT Token Security

```python
def create_tokens(self, username: str) -> Tuple[str, str]:
    # Access token (short-lived)
    access_token = jwt.encode(
        {
            "sub": username,
            "exp": datetime.utcnow() + timedelta(minutes=30),
            "type": "access"
        },
        self.secret_key,
        algorithm="HS256"
    )
    
    # Refresh token (long-lived, stored in DB)
    refresh_token = secrets.token_urlsafe(32)
    return access_token, refresh_token
```

### 3. File Upload Security

```python
def validate_file(self, file_content: bytes, content_type: str) -> bool:
    # Check file size (10MB limit)
    if len(file_content) > 10 * 1024 * 1024:
        return False
    
    # Check content type
    allowed_types = ["image/jpeg", "image/png", "image/gif", "image/webp"]
    if content_type not in allowed_types:
        return False
    
    return True
```

### 4. User Isolation

```python
async def get_image(self, filename: str, username: str) -> Optional[Image]:
    """Get specific image (with user isolation)"""
    image = await self.image_repo.get_by_filename(filename)
    if not image or image.username != username:
        return None
    return image
```

## 🗄️ Database Design

### Schema Design

```sql
-- Users table
CREATE TABLE users (
    username VARCHAR(50) PRIMARY KEY,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Images table
CREATE TABLE images (
    filename VARCHAR(255) PRIMARY KEY,
    original_filename VARCHAR(255) NOT NULL,
    username VARCHAR(50) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size INTEGER NOT NULL,
    content_type VARCHAR(100) NOT NULL,
    upload_date TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Refresh tokens table
CREATE TABLE refresh_tokens (
    token VARCHAR(500) PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL
);
```

## 🧪 Testing Strategy

### 1. Unit Testing

```python
async def test_auth_service_register_user():
    # Arrange
    mock_user_repo = MockUserRepository()
    auth_service = AuthService(mock_user_repo, mock_token_repo, "secret")
    
    # Act
    user = await auth_service.register_user("testuser", "password123")
    
    # Assert
    assert user.username == "testuser"
    assert user.hashed_password != "password123"  # Should be hashed
```

### 2. Integration Testing

```python
async def test_user_registration_integration():
    async with AsyncSessionLocal() as session:
        user_repo = PostgreSQLUserRepository(session)
        auth_service = AuthService(user_repo, token_repo, "secret")
        
        user = await auth_service.register_user("testuser", "password123")
        saved_user = await user_repo.get_by_username("testuser")
        
        assert saved_user is not None
        assert saved_user.username == "testuser"
```

## 🚀 Performance & Scalability

### 1. Database Optimization

```sql
-- Use indexes for frequently queried columns
CREATE INDEX idx_images_username ON images(username);
CREATE INDEX idx_refresh_tokens_username ON refresh_tokens(username);
CREATE INDEX idx_refresh_tokens_expires ON refresh_tokens(expires_at);
```

### 2. Connection Pooling

```python
engine = create_async_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True,
    pool_recycle=300
)
```

### 3. Scalability Considerations

- **Stateless Services**: Easy horizontal scaling
- **External Storage**: Use S3 for file storage
- **Caching**: Redis for session/token caching
- **Microservices**: Split into separate services

---

**This architecture provides a solid foundation for building scalable, maintainable, and secure applications with clear separation of concerns.** 