# 🖼️ Image Upload Server

A modern, scalable image upload server built with **FastAPI**, **PostgreSQL**, and **Clean Architecture**. Features secure authentication, file management, and a robust API for handling image uploads.

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-blue.svg)](https://postgresql.org)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://docker.com)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## ✨ Features

- 🔐 **JWT Authentication** with refresh tokens
- 📸 **Secure Image Upload** with file validation
- 🗄️ **PostgreSQL Database** with persistent storage
- 🏗️ **Clean Architecture** for maintainability
- 🐳 **Docker Support** for easy deployment
- 📚 **Auto-generated API Documentation**
- 🧪 **Comprehensive Testing** support
- 🔒 **Security Best Practices** implemented

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Docker & Docker Compose
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/image-upload-server.git
   cd image-upload-server
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Setup environment**
   ```bash
   cp env.example .env
   # Edit .env file with your configuration
   ```

4. **Start with Docker (Recommended)**
   ```bash
   chmod +x docker-setup.sh docker-manage.sh
   ./docker-setup.sh
   ```

5. **Run the server**
   ```bash
   python main_clean.py
   ```

6. **Access the API**
   - **API Documentation**: http://localhost:8000/docs
   - **Alternative Docs**: http://localhost:8000/redoc
   - **Health Check**: http://localhost:8000/health

## 📖 API Documentation

### Authentication Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/register` | Register new user |
| `POST` | `/api/v1/login` | Login and get tokens |
| `POST` | `/api/v1/refresh` | Refresh access token |
| `POST` | `/api/v1/logout` | Logout and invalidate tokens |

### Image Management Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/upload-image` | Upload image |
| `GET` | `/api/v1/images` | Get user's images |
| `GET` | `/api/v1/image/{filename}` | Get specific image info |
| `DELETE` | `/api/v1/image/{filename}` | Delete image |

### Example Usage

```bash
# Login
curl -X POST "http://localhost:8000/api/v1/login" \
     -H "Content-Type: application/json" \
     -d '{"username": "admin", "password": "admin123"}'

# Upload image
curl -X POST "http://localhost:8000/api/v1/upload-image" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -F "file=@image.jpg"

# Get images
curl -X GET "http://localhost:8000/api/v1/images" \
     -H "Authorization: Bearer YOUR_TOKEN"
```

## 🏗️ Architecture

This project follows **Clean Architecture** principles with clear separation of concerns:

```
app/
├── core/                    # Domain Layer
│   ├── entities.py         # Business entities
│   ├── interfaces.py       # Repository interfaces
│   └── services.py         # Business logic
├── infrastructure/         # Data Layer
│   ├── database.py         # Database configuration
│   ├── models.py           # SQLAlchemy models
│   └── postgresql_repositories.py # PostgreSQL implementations
└── api/                    # Presentation Layer
    ├── dependencies.py     # Dependency injection
    └── routes.py          # API endpoints
```

### Key Benefits

- **Testability**: Business logic is isolated and easily testable
- **Maintainability**: Clear structure and responsibilities
- **Flexibility**: Easy to swap implementations (in-memory ↔ PostgreSQL)
- **Scalability**: Ready for microservices architecture

## 🐳 Docker Setup

### Quick Docker Setup

```bash
# Automatic setup (recommended)
./docker-setup.sh

# Manual setup
docker-compose up -d
```

### Docker Management

```bash
# Start containers
./docker-manage.sh start

# Stop containers
./docker-manage.sh stop

# View logs
./docker-manage.sh logs

# Create backup
./docker-manage.sh backup

# Access PostgreSQL shell
./docker-manage.sh shell

# Open pgAdmin
./docker-manage.sh pgadmin
```

### Access Information

| Service | URL | Credentials |
|---------|-----|-------------|
| **PostgreSQL** | `localhost:5432` | `postgres/password` |
| **pgAdmin** | `http://localhost:8080` | `admin@example.com/admin123` |

## 🔒 Security

### Default Credentials

⚠️ **Important**: Change these default credentials for production!

- **PostgreSQL**: `postgres/password`
- **pgAdmin**: `admin@example.com/admin123`
- **Admin User**: `admin/admin123`

### Security Features

- **Password Hashing**: bcrypt with salt
- **JWT Tokens**: Secure token-based authentication
- **Token Expiration**: Automatic refresh mechanism
- **User Isolation**: Users can only access their own data
- **File Validation**: Type and size validation
- **SQL Injection Protection**: SQLAlchemy ORM

### Production Security Checklist

- [ ] Change `SECRET_KEY` in `.env`
- [ ] Change PostgreSQL password
- [ ] Change pgAdmin password
- [ ] Use HTTPS in production
- [ ] Disable pgAdmin in production
- [ ] Set up proper firewall rules
- [ ] Use environment variables for secrets

## 🧪 Testing

### Run Tests

```bash
# Run test client
python test_client.py

# Run with pytest (if configured)
pytest

# Manual testing
curl -X GET "http://localhost:8000/health"
```

### Test Coverage

The project includes:
- **Unit tests** for business logic
- **Integration tests** for API endpoints
- **End-to-end tests** for complete workflows

## 📊 Database Schema

### Users Table
```sql
CREATE TABLE users (
    username VARCHAR(50) PRIMARY KEY,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### Images Table
```sql
CREATE TABLE images (
    filename VARCHAR(255) PRIMARY KEY,
    original_filename VARCHAR(255) NOT NULL,
    username VARCHAR(50) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size INTEGER NOT NULL,
    content_type VARCHAR(100) NOT NULL,
    upload_date TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### Refresh Tokens Table
```sql
CREATE TABLE refresh_tokens (
    token VARCHAR(500) PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL
);
```

## 🚀 Deployment

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Setup environment
cp env.example .env

# Run with local PostgreSQL
python main_clean.py
```

### Docker Production

```bash
# Build and run
docker-compose -f docker-compose.prod.yml up -d

# Or use Dockerfile
docker build -t image-upload-server .
docker run -p 8000:8000 image-upload-server
```

### Environment Variables

```bash
# Required
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/db
SECRET_KEY=your-secret-key

# Optional
DB_ECHO=false
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
MAX_FILE_SIZE=10485760
```

## 🔧 Configuration

### File Upload Settings

```python
# Maximum file size (10MB)
MAX_FILE_SIZE = 10 * 1024 * 1024

# Allowed image types
ALLOWED_IMAGE_TYPES = [
    "image/jpeg",
    "image/png", 
    "image/gif",
    "image/webp"
]
```

### Token Settings

```python
# Access token expiration (30 minutes)
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Refresh token expiration (7 days)
REFRESH_TOKEN_EXPIRE_DAYS = 7
```

## 🐛 Troubleshooting

### Common Issues

**Database Connection Failed**
```bash
# Check if PostgreSQL is running
docker-compose ps

# Check logs
docker-compose logs postgres

# Restart containers
docker-compose restart
```

**Permission Denied**
```bash
# Fix directory permissions
chmod +x docker-setup.sh docker-manage.sh
chmod 755 uploads/
```

**Port Already in Use**
```bash
# Check what's using the port
sudo netstat -tlnp | grep :8000

# Kill the process or change port in .env
```

### Getting Help

1. Check the [Issues](../../issues) page
2. Review the [Docker Documentation](docs/README_DOCKER.md)
3. Check the [Code Explanation](docs/CODE_EXPLANATION.md)
4. Read the [Authentication Testing Guide](docs/AUTHENTICATION_TESTING.md)

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Development Setup

```bash
# Clone your fork
git clone https://github.com/yourusername/image-upload-server.git

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements.txt

# Run tests
python test_client.py
```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - Modern web framework
- [PostgreSQL](https://postgresql.org/) - Powerful database
- [SQLAlchemy](https://sqlalchemy.org/) - Database toolkit
- [Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html) - Software design principles

## 📞 Support

- **Documentation**: [docs/README_DOCKER.md](docs/README_DOCKER.md)
- **Code Explanation**: [docs/CODE_EXPLANATION.md](docs/CODE_EXPLANATION.md)
- **Vietnamese Guide**: [docs/HUONG_DAN_VIET_NAM.md](docs/HUONG_DAN_VIET_NAM.md)
- **Authentication Testing**: [docs/AUTHENTICATION_TESTING.md](docs/AUTHENTICATION_TESTING.md)
- **Frontend API Guide**: [docs/API_GUIDE_FRONTEND.md](docs/API_GUIDE_FRONTEND.md)
- **Swagger Documentation**: [docs/SWAGGER_DOCUMENTATION.md](docs/SWAGGER_DOCUMENTATION.md)
- **SSH Security Guide**: [docs/SSH_SECURITY_GUIDE.md](docs/SSH_SECURITY_GUIDE.md)
- **GitHub SSH Setup**: [docs/GITHUB_SSH_SETUP.md](docs/GITHUB_SSH_SETUP.md)
- **Persistent GitHub Auth**: [docs/PERSISTENT_GITHUB_AUTH.md](docs/PERSISTENT_GITHUB_AUTH.md)
- **GitHub Auth Summary**: [docs/GITHUB_AUTH_SUMMARY.md](docs/GITHUB_AUTH_SUMMARY.md)
- **GitHub Push Checklist**: [docs/GITHUB_PUSH_CHECKLIST.md](docs/GITHUB_PUSH_CHECKLIST.md)
- **Issues**: [GitHub Issues](../../issues)
- **Discussions**: [GitHub Discussions](../../discussions)

---

**Built with ❤️ using modern technologies and best practices** 