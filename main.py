"""
Main application entry point using Clean Architecture with PostgreSQL
"""

import os

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

import app.bootstrap  # noqa
from app.api.routes import router
from app.config import settings
from app.exceptions import setup_exception_handlers
from app.infrastructure.database import close_db, init_db
from app.infrastructure.notifier import post_notifier
from app.utils.logging import get_logger, setup_logging

print("DEBUG: DATABASE_URL =", os.getenv("DATABASE_URL"))
print("DEBUG: DATABASE_URL on setting =", settings.DATABASE_URL)
# Setup logging
setup_logging(
    level=os.getenv("LOG_LEVEL", "INFO"), log_file=os.getenv("LOG_FILE", "logs/app.log")
)
logger = get_logger(__name__)

# Create FastAPI app with enhanced metadata
app = FastAPI(
    title=settings.PROJECT_NAME,
    version="2.1.0",
    description="""
# 🚀 Image Upload Server API

A modern, scalable image upload server built with **FastAPI**, **PostgreSQL**, and **Clean Architecture**.

## ✨ Features

- 🔐 **JWT Authentication** with refresh tokens
- 📸 **Secure Image Upload** with file validation
- 🗄️ **PostgreSQL Database** with persistent storage
- 🏗️ **Clean Architecture** for maintainability
- 📚 **Auto-generated API Documentation**
- 🔒 **Security Best Practices** implemented

## 🔐 Authentication

This API uses JWT (JSON Web Tokens) for authentication. To access protected endpoints:

1. **Register** a new user or **Login** with existing credentials
2. Use the returned `access_token` in the Authorization header: `Bearer <token>`
3. When the access token expires, use the `refresh_token` to get a new one

## 📸 Image Upload

- **Supported formats**: JPEG, PNG, GIF, WebP
- **Maximum file size**: 10MB
- **Storage**: Images are stored securely with unique filenames
- **Access**: Users can only access their own uploaded images

## 🏗️ Architecture

This project follows **Clean Architecture** principles:
- **Domain Layer**: Business entities and rules
- **Application Layer**: Use cases and services
- **Infrastructure Layer**: Database and external services
- **Presentation Layer**: API endpoints and controllers

## 🔗 Quick Links

- **Interactive API Docs**: `/docs` (Swagger UI)
- **Alternative Docs**: `/redoc` (ReDoc)
- **Health Check**: `/health`
- **OpenAPI Schema**: `/openapi.json`

## 🛠️ Development

```bash
# Start the server
python main.py

# Access the API
curl http://localhost:8000/health

# View documentation
open http://localhost:8000/docs
```

## 📚 Additional Resources

- [Frontend Integration Guide](../docs/API_GUIDE_FRONTEND.md)
- [Authentication Testing](../docs/AUTHENTICATION_TESTING.md)
- [Docker Setup](../docs/README_DOCKER.md)
- [Code Explanation](../docs/CODE_EXPLANATION.md)
    """,
    summary="Modern image upload server with JWT authentication and PostgreSQL",
    contact={
        "name": "Image Upload Server Support",
        "url": "https://github.com/yourusername/image-upload-server",
        "email": "support@yourapp.com",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    servers=[
        {"url": "http://localhost:8000", "description": "Development server"},
        {"url": "https://api.yourapp.com", "description": "Production server"},
    ],
    tags_metadata=[
        {
            "name": "Authentication",
            "description": "User registration, login, and token management operations.",
            "externalDocs": {
                "description": "Authentication Guide",
                "url": "../docs/AUTHENTICATION_TESTING.md",
            },
        },
        {
            "name": "Images",
            "description": "Image upload, retrieval, and management operations.",
            "externalDocs": {
                "description": "Frontend Integration Guide",
                "url": "../docs/API_GUIDE_FRONTEND.md",
            },
        },
        {
            "name": "Health",
            "description": "Server health and status endpoints.",
        },
    ],
)

# Setup exception handlers
setup_exception_handlers(app)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

import time

# Log all requests
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        logger.info(f"Request: {request.method} {request.url}")
        start_time = time.time()
        try:
            response = await call_next(request)
        except Exception:
            logger.exception(f"Error handling request: {request.method} {request.url}")
            raise
        process_time = (time.time() - start_time) * 1000
        logger.info(
            f"Response: {request.method} {request.url} - Status: {response.status_code} - {process_time:.2f}ms"
        )
        return response


app.add_middleware(LoggingMiddleware)

# Include API routes
app.include_router(router, prefix=settings.API_V1_STR)

# Serve the admin directory at /admin
app.mount("/admin", StaticFiles(directory="admin"), name="admin")

# Serve uploaded images at /uploads
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

frontend_dist = os.path.join(os.path.dirname(__file__), "frontend", "dist")
app.mount("/static", StaticFiles(directory=frontend_dist, html=True), name="static")


@app.get("/{full_path:path}", response_class=FileResponse)
async def spa_catch_all(full_path: str):
    # Không intercept các route API, uploads, admin
    if (
        full_path.startswith("api/")
        or full_path.startswith("uploads/")
        or full_path.startswith("admin/")
    ):
        return HTMLResponse(content="Not found", status_code=404)
    static_file = os.path.join(frontend_dist, full_path)
    if os.path.isfile(static_file):
        return FileResponse(static_file)
    index_path = os.path.join(frontend_dist, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return HTMLResponse(content="index.html not found", status_code=404)


def custom_openapi():
    """Custom OpenAPI schema with enhanced documentation"""
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    # Add security schemes
    openapi_schema["components"]["securitySchemes"] = {
        "HTTPBearer": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Enter your JWT token in the format: Bearer <token>",
        }
    }

    # Add response examples
    openapi_schema["components"]["examples"] = {
        "LoginSuccess": {
            "summary": "Successful login response",
            "value": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "username": "john_doe",
            },
        },
        "ImageUploadSuccess": {
            "summary": "Successful image upload response",
            "value": {
                "message": "Image uploaded successfully",
                "filename": "abc123_image.jpg",
                "file_size": 1024000,
                "original_filename": "vacation.jpg",
                "content_type": "image/jpeg",
                "upload_date": "2024-01-15T10:30:00Z",
            },
        },
        "ErrorResponse": {
            "summary": "Error response example",
            "value": {"detail": "Invalid credentials"},
        },
    }

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    logger.info("🚀 Starting Image Upload Server with PostgreSQL...")
    await init_db()
    logger.info("✅ Database initialized successfully")


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up database connections on shutdown"""
    logger.info("🛑 Shutting down server...")
    await close_db()
    logger.info("✅ Database connections closed")


@app.get("/api-root", tags=["Health"])
async def root():
    """
    # 🏠 API Root
    Welcome to the Image Upload Server API! This endpoint provides basic information about the API.
    """
    return {
        "message": "🖼️ Image Upload Server API (Clean Architecture + PostgreSQL)",
        "version": "2.1.0",
        "database": "PostgreSQL",
        "architecture": "Clean Architecture",
        "features": [
            "JWT Authentication",
            "Image Upload",
            "PostgreSQL Storage",
            "Auto-generated Docs",
        ],
        "endpoints": {
            "docs": "/docs",
            "redoc": "/redoc",
            "openapi": "/openapi.json",
            "health": "/health",
        },
        "authentication": {
            "type": "JWT Bearer Token",
            "register": "/api/v1/register",
            "login": "/api/v1/login",
        },
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """
    # 🏥 Health Check

    Check the health status of the API server and database connection.

    ## Response

    - `status`: Overall health status
    - `architecture`: Software architecture used
    - `database`: Database type and status
    - `timestamp`: Current server time

    ## Usage

    This endpoint is useful for:
    - Load balancer health checks
    - Monitoring systems
    - DevOps automation
    """
    return {
        "status": "healthy",
        "architecture": "clean",
        "database": "postgresql",
        "version": "2.1.0",
        "timestamp": "2024-01-15T10:30:00Z",
    }


@app.websocket("/ws/posts/notify")
async def websocket_post_notify(websocket: WebSocket):
    # Lấy username từ query param (nếu có)
    username = websocket.query_params.get("username") or ""
    await post_notifier.connect(websocket, username)
    try:
        while True:
            # Keep connection alive, ignore incoming messages
            await websocket.receive_text()
    except WebSocketDisconnect:
        post_notifier.disconnect(websocket)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=settings.HOST, port=settings.PORT)
