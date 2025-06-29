# 📚 Hướng Dẫn Chi Tiết Dự Án Image Upload Server

## 🎯 Tổng Quan Dự Án

Đây là một **server upload ảnh** được xây dựng bằng **FastAPI** và **PostgreSQL**, sử dụng kiến trúc **Clean Architecture**. Server này cho phép:

- 🔐 **Đăng ký/Đăng nhập** người dùng với JWT tokens
- 📸 **Upload ảnh** an toàn với xác thực
- 📋 **Quản lý ảnh** (xem, xóa ảnh đã upload)
- 🗄️ **Lưu trữ dữ liệu** trong PostgreSQL database

## 🏗️ Kiến Trúc Tổng Thể

### Clean Architecture là gì?

**Clean Architecture** là một cách tổ chức code để:
- **Tách biệt** các lớp chức năng
- **Dễ test** và bảo trì
- **Linh hoạt** khi thay đổi công nghệ
- **Độc lập** với framework

```
┌─────────────────────────────────────┐
│           Lớp Giao Diện            │  ← API Routes, HTTP handling
├─────────────────────────────────────┤
│           Lớp Logic Nghiệp Vụ      │  ← Core services, use cases
├─────────────────────────────────────┤
│           Lớp Truy Cập Dữ Liệu     │  ← Repositories, database
├─────────────────────────────────────┤
│           Lớp Dịch Vụ Bên Ngoài    │  ← File system, external APIs
└─────────────────────────────────────┘
```

## 📁 Cấu Trúc Thư Mục

```
linklink/
├── app/                           # Thư mục chính của ứng dụng
│   ├── core/                      # Lớp Logic Nghiệp Vụ (Domain Layer)
│   │   ├── entities.py           # Các đối tượng nghiệp vụ (User, Image, Token)
│   │   ├── interfaces.py         # Giao diện cho repositories
│   │   └── services.py           # Logic nghiệp vụ (AuthService, ImageService)
│   ├── infrastructure/           # Lớp Truy Cập Dữ Liệu (Data Layer)
│   │   ├── database.py           # Cấu hình database
│   │   ├── models.py             # SQLAlchemy models
│   │   └── postgresql_repositories.py # Triển khai PostgreSQL
│   ├── api/                      # Lớp Giao Diện (Presentation Layer)
│   │   ├── dependencies.py       # Dependency injection
│   │   └── routes.py            # API endpoints
│   └── __init__.py
├── main.py                       # Điểm khởi đầu ứng dụng
├── main_clean.py                 # Phiên bản Clean Architecture
├── database_setup.py             # Script khởi tạo database
├── docker-compose.yml            # Cấu hình Docker
├── docker-setup.sh               # Script setup Docker
├── docker-manage.sh              # Script quản lý Docker
├── requirements.txt              # Các thư viện Python cần thiết
├── test_client.py                # Client test API
├── .env                          # Biến môi trường (không commit lên Git)
├── uploads/                      # Thư mục lưu ảnh upload
└── README.md                     # Hướng dẫn tiếng Anh
```

## 🚀 Giải Thích Chi Tiết main.py

### main.py làm gì?

File `main.py` là **điểm khởi đầu** của ứng dụng. Nó:

1. **Tạo FastAPI app**
2. **Cấu hình CORS** (cho phép frontend gọi API)
3. **Kết nối các routes** (API endpoints)
4. **Khởi tạo database** khi server start
5. **Dọn dẹp** khi server shutdown

### Code chi tiết:

```python
# 1. Import các thư viện cần thiết
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router  # ← Import routes từ app/api/routes.py
from app.infrastructure.database import init_db, close_db

# 2. Tạo FastAPI app
app = FastAPI(
    title="Image Upload Server (Clean Architecture + PostgreSQL)",
    version="2.1.0",
    description="A FastAPI server with Clean Architecture and PostgreSQL for image upload and authentication"
)

# 3. Cấu hình CORS (cho phép frontend gọi API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Cho phép tất cả origins (chỉ dùng cho dev)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 4. Kết nối routes (API endpoints)
app.include_router(router, prefix="/api/v1")  # ← Tất cả API sẽ có prefix /api/v1

# 5. Event khi server khởi động
@app.on_event("startup")
async def startup_event():
    print("🚀 Starting Image Upload Server with PostgreSQL...")
    await init_db()  # ← Khởi tạo database
    print("✅ Database initialized successfully")

# 6. Event khi server tắt
@app.on_event("shutdown")
async def shutdown_event():
    print("🛑 Shutting down server...")
    await close_db()  # ← Đóng kết nối database
    print("✅ Database connections closed")

# 7. API endpoint gốc (/)
@app.get("/")
async def root():
    return {
        "message": "Image Upload Server API (Clean Architecture + PostgreSQL)",
        "version": "2.1.0",
        "database": "PostgreSQL",
        "docs": "/docs",
        "redoc": "/redoc"
    }

# 8. API endpoint kiểm tra sức khỏe (/health)
@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "architecture": "clean",
        "database": "postgresql"
    }

# 9. Chạy server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)  # ← Chạy trên port 8000
```

## 🔗 Các Liên Kết Từ main.py

### 1. `from app.api.routes import router`

**Đường dẫn:** `app/api/routes.py`

**Chức năng:** Chứa tất cả các API endpoints:
- `/api/v1/register` - Đăng ký người dùng
- `/api/v1/login` - Đăng nhập
- `/api/v1/upload-image` - Upload ảnh
- `/api/v1/images` - Lấy danh sách ảnh
- `/api/v1/image/{filename}` - Xem thông tin ảnh
- `/api/v1/delete-image/{filename}` - Xóa ảnh

**Ví dụ code:**
```python
@router.post("/register")
async def register(user_data: UserRegister):
    # Logic đăng ký người dùng
    pass

@router.post("/upload-image")
async def upload_image(file: UploadFile):
    # Logic upload ảnh
    pass
```

### 2. `from app.infrastructure.database import init_db, close_db`

**Đường dẫn:** `app/infrastructure/database.py`

**Chức năng:** Quản lý kết nối database PostgreSQL

**Code chính:**
```python
# Kết nối database
DATABASE_URL = "postgresql+asyncpg://postgres:password@localhost:5432/image_upload_db"
engine = create_async_engine(DATABASE_URL)

# Khởi tạo database
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Đóng kết nối
async def close_db():
    await engine.dispose()
```

## 🎯 Giải Thích Từng Lớp

### 1. Lớp Core (Logic Nghiệp Vụ)

#### `app/core/entities.py`
**Chức năng:** Định nghĩa các đối tượng nghiệp vụ

```python
@dataclass
class User:
    username: str           # Tên đăng nhập
    hashed_password: str    # Mật khẩu đã mã hóa
    is_active: bool = True  # Trạng thái hoạt động

@dataclass
class Image:
    filename: str           # Tên file trên server
    original_filename: str  # Tên file gốc
    username: str          # Người sở hữu
    file_path: str         # Đường dẫn file
    file_size: int         # Kích thước file
```

#### `app/core/interfaces.py`
**Chức năng:** Định nghĩa giao diện cho repositories

```python
class UserRepository(ABC):
    @abstractmethod
    async def create(self, user: User) -> User:
        pass
    
    @abstractmethod
    async def get_by_username(self, username: str) -> Optional[User]:
        pass
```

#### `app/core/services.py`
**Chức năng:** Chứa logic nghiệp vụ

```python
class AuthService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo
    
    async def register_user(self, username: str, password: str) -> User:
        # Kiểm tra user đã tồn tại chưa
        existing_user = await self.user_repo.get_by_username(username)
        if existing_user:
            raise ValueError("Username already exists")
        
        # Mã hóa mật khẩu
        hashed_password = self.hash_password(password)
        
        # Tạo user mới
        user = User(username=username, hashed_password=hashed_password)
        return await self.user_repo.create(user)
```

### 2. Lớp Infrastructure (Truy Cập Dữ Liệu)

#### `app/infrastructure/models.py`
**Chức năng:** Định nghĩa cấu trúc bảng database

```python
class UserModel(Base):
    __tablename__ = "users"
    
    username = Column(String(50), primary_key=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
```

#### `app/infrastructure/postgresql_repositories.py`
**Chức năng:** Triển khai cụ thể cho PostgreSQL

```python
class PostgreSQLUserRepository(UserRepository):
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, user: User) -> User:
        # Chuyển đổi từ domain entity sang database model
        user_model = UserModel(
            username=user.username,
            hashed_password=user.hashed_password
        )
        
        # Lưu vào database
        self.session.add(user_model)
        await self.session.commit()
        
        # Trả về domain entity
        return User(
            username=user_model.username,
            hashed_password=user_model.hashed_password
        )
```

### 3. Lớp API (Giao Diện)

#### `app/api/dependencies.py`
**Chức năng:** Cấu hình dependency injection

```python
def get_user_repository(session: AsyncSession = Depends(get_db_session)):
    return PostgreSQLUserRepository(session)

def get_auth_service(user_repo: UserRepository = Depends(get_user_repository)):
    return AuthService(user_repo)
```

#### `app/api/routes.py`
**Chức năng:** Định nghĩa các API endpoints

```python
@router.post("/register")
async def register(
    user_data: UserRegister,
    auth_service: AuthService = Depends(get_auth_service)  # ← Inject service
):
    try:
        user = await auth_service.register_user(
            user_data.username, 
            user_data.password
        )
        return {"message": "User registered successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
```

## 🔄 Luồng Hoạt Động

### Khi User Đăng Ký:

1. **Client gọi API:** `POST /api/v1/register`
2. **FastAPI nhận request** → `app/api/routes.py`
3. **Routes gọi AuthService** → `app/core/services.py`
4. **AuthService gọi UserRepository** → `app/infrastructure/postgresql_repositories.py`
5. **Repository lưu vào database** → PostgreSQL
6. **Trả về kết quả** → Client

### Khi User Upload Ảnh:

1. **Client gọi API:** `POST /api/v1/upload-image`
2. **FastAPI nhận file** → `app/api/routes.py`
3. **Routes gọi ImageService** → `app/core/services.py`
4. **ImageService lưu file** → `uploads/` folder
5. **ImageService gọi ImageRepository** → Lưu metadata vào database
6. **Trả về thông tin ảnh** → Client

## 🗄️ Database Schema

### Bảng Users:
```sql
CREATE TABLE users (
    username VARCHAR(50) PRIMARY KEY,           -- Tên đăng nhập
    hashed_password VARCHAR(255) NOT NULL,      -- Mật khẩu đã mã hóa
    is_active BOOLEAN DEFAULT TRUE,             -- Trạng thái hoạt động
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),  -- Thời gian tạo
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()   -- Thời gian cập nhật
);
```

### Bảng Images:
```sql
CREATE TABLE images (
    filename VARCHAR(255) PRIMARY KEY,          -- Tên file trên server
    original_filename VARCHAR(255) NOT NULL,    -- Tên file gốc
    username VARCHAR(50) NOT NULL,              -- Người sở hữu
    file_path VARCHAR(500) NOT NULL,            -- Đường dẫn file
    file_size INTEGER NOT NULL,                 -- Kích thước file
    content_type VARCHAR(100) NOT NULL,         -- Loại file
    upload_date TIMESTAMP WITH TIME ZONE DEFAULT NOW()  -- Thời gian upload
);
```

### Bảng Refresh Tokens:
```sql
CREATE TABLE refresh_tokens (
    token VARCHAR(500) PRIMARY KEY,             -- Token refresh
    username VARCHAR(50) NOT NULL,              -- Người sở hữu token
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),  -- Thời gian tạo
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL        -- Thời gian hết hạn
);
```

## 🔒 Bảo Mật

### 1. Mã Hóa Mật Khẩu:
```python
def hash_password(self, password: str) -> str:
    salt = bcrypt.gensalt()  # Tạo salt ngẫu nhiên
    return bcrypt.hashpw(password.encode(), salt).decode()
```

### 2. JWT Tokens:
```python
def create_tokens(self, username: str) -> Tuple[str, str]:
    # Access token (30 phút)
    access_token = jwt.encode(
        {"sub": username, "exp": datetime.utcnow() + timedelta(minutes=30)},
        self.secret_key,
        algorithm="HS256"
    )
    
    # Refresh token (7 ngày)
    refresh_token = secrets.token_urlsafe(32)
    return access_token, refresh_token
```

### 3. Xác Thực File Upload:
```python
def validate_file(self, file_content: bytes, content_type: str) -> bool:
    # Kiểm tra kích thước (10MB)
    if len(file_content) > 10 * 1024 * 1024:
        return False
    
    # Kiểm tra loại file
    allowed_types = ["image/jpeg", "image/png", "image/gif", "image/webp"]
    return content_type in allowed_types
```

## 🐳 Docker Setup

### Các Container:
1. **PostgreSQL** (port 5432) - Database
2. **pgAdmin** (port 8080) - Quản lý database

### Commands:
```bash
# Khởi động
./docker-setup.sh

# Quản lý
./docker-manage.sh start
./docker-manage.sh stop
./docker-manage.sh status

# Backup/Restore
./docker-manage.sh backup
./docker-manage.sh restore <file>
```

## 🧪 Testing

### Test Client:
```bash
python test_client.py
```

**Test các chức năng:**
1. Health check
2. Đăng ký user
3. Đăng nhập
4. Upload ảnh
5. Lấy danh sách ảnh
6. Xóa ảnh

## 🚀 Chạy Dự Án

### 1. Setup Database:
```bash
./docker-setup.sh
```

### 2. Chạy Server:
```bash
python main.py
```

### 3. Truy Cập:
- **API Docs:** http://localhost:8000/docs
- **pgAdmin:** http://localhost:8080
- **Health Check:** http://localhost:8000/health

## 📚 Tài Liệu Tham Khảo

- **FastAPI:** https://fastapi.tiangolo.com/
- **PostgreSQL:** https://www.postgresql.org/
- **Clean Architecture:** https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html
- **Docker:** https://docs.docker.com/

---

**Dự án này sử dụng Clean Architecture để tạo ra một hệ thống upload ảnh an toàn, dễ bảo trì và có thể mở rộng! 🚀** 