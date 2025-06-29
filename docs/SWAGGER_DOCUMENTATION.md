# 📚 Swagger/OpenAPI Documentation Guide

A comprehensive guide to the enhanced Swagger documentation for the Image Upload Server API.

## 🎯 Overview

The Image Upload Server API includes comprehensive **Swagger/OpenAPI documentation** that provides:

- **Interactive API Explorer** - Test endpoints directly in the browser
- **Detailed Endpoint Documentation** - Complete descriptions and examples
- **Request/Response Schemas** - Automatic validation and examples
- **Authentication Integration** - Built-in JWT token support
- **Error Handling** - Comprehensive error responses and codes

## 🚀 Accessing the Documentation

### Interactive Documentation

| URL | Description | Features |
|-----|-------------|----------|
| `/docs` | **Swagger UI** | Interactive testing, request builder, response viewer |
| `/redoc` | **ReDoc** | Clean, responsive documentation |
| `/openapi.json` | **OpenAPI Schema** | Raw JSON schema for tools |

### Quick Start

```bash
# Start the server
python main.py

# Access Swagger UI
open http://localhost:8000/docs

# Access ReDoc
open http://localhost:8000/redoc
```

## 🔐 Authentication in Swagger

### Setting Up Authentication

1. **Login First**: Use the `/api/v1/login` endpoint to get tokens
2. **Authorize**: Click the **"Authorize"** button in Swagger UI
3. **Enter Token**: Use format: `Bearer <your_access_token>`
4. **Test Protected Endpoints**: All authenticated endpoints will work

### Example Authentication Flow

```json
// 1. Register a user
POST /api/v1/register
{
  "username": "testuser",
  "password": "testpass123"
}

// 2. Login to get tokens
POST /api/v1/login
{
  "username": "testuser",
  "password": "testpass123"
}

// Response:
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "username": "testuser"
}

// 3. Use access_token in Authorization header
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## 📋 API Endpoints Overview

### 🔐 Authentication Endpoints

| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/api/v1/register` | `POST` | Register new user | ❌ |
| `/api/v1/login` | `POST` | Login and get tokens | ❌ |
| `/api/v1/refresh` | `POST` | Refresh access token | ❌ |
| `/api/v1/logout` | `POST` | Logout and invalidate tokens | ✅ |

### 📸 Image Management Endpoints

| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/api/v1/upload-image` | `POST` | Upload image file | ✅ |
| `/api/v1/images` | `GET` | Get user's images | ✅ |
| `/api/v1/image/{filename}` | `GET` | Get specific image info | ✅ |
| `/api/v1/image/{filename}` | `DELETE` | Delete image | ✅ |

### 🏥 Health & Status Endpoints

| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/` | `GET` | API root information | ❌ |
| `/health` | `GET` | Health check | ❌ |

## 🎨 Swagger UI Features

### 1. Interactive Testing

**Try It Out** button allows you to:
- Fill in request parameters
- Upload files directly
- Execute requests
- View real responses
- See response headers and status codes

### 2. Request Builder

- **Parameters**: Automatically validates input
- **Request Body**: JSON editor with examples
- **File Upload**: Drag & drop file upload
- **Headers**: Automatic authentication headers

### 3. Response Viewer

- **Formatted JSON**: Pretty-printed responses
- **Response Headers**: View all response headers
- **Status Codes**: Clear success/error indicators
- **Response Time**: Performance metrics

### 4. Schema Documentation

- **Request Models**: Complete input validation
- **Response Models**: Expected response structure
- **Examples**: Real-world usage examples
- **Error Responses**: All possible error cases

## 📝 Using Swagger UI Effectively

### Step-by-Step Testing

1. **Navigate to `/docs`**
2. **Expand an endpoint** (e.g., `/api/v1/register`)
3. **Click "Try it out"**
4. **Fill in the request body**:
   ```json
   {
     "username": "testuser",
     "password": "testpass123"
   }
   ```
5. **Click "Execute"**
6. **Review the response**:
   ```json
   {
     "message": "User registered successfully"
   }
   ```

### Testing Protected Endpoints

1. **First, get an access token** using `/api/v1/login`
2. **Click "Authorize"** at the top of the page
3. **Enter your token**: `Bearer <your_access_token>`
4. **Click "Authorize"**
5. **Test protected endpoints** - they'll automatically include the token

### File Upload Testing

1. **Navigate to `/api/v1/upload-image`**
2. **Click "Try it out"**
3. **Click "Choose File"** and select an image
4. **Click "Execute"**
5. **View the upload response**

## 🔧 Advanced Features

### 1. Custom OpenAPI Schema

The API includes a custom OpenAPI schema with:
- **Security Schemes**: JWT Bearer authentication
- **Response Examples**: Pre-defined example responses
- **Error Handling**: Comprehensive error documentation
- **Server Configuration**: Multiple environment support

### 2. Enhanced Metadata

- **Contact Information**: Support details
- **License Information**: MIT License
- **External Documentation**: Links to guides
- **Tags**: Organized endpoint grouping

### 3. Response Examples

Each endpoint includes:
- **Success Examples**: Expected successful responses
- **Error Examples**: Common error scenarios
- **Validation Examples**: Input validation cases

## 🛠️ Development Features

### 1. Request Logging

In development mode, you can see:
- **Request Details**: Method, URL, headers
- **Response Details**: Status, headers, body
- **Performance Metrics**: Response times

### 2. Schema Validation

- **Automatic Validation**: Request/response validation
- **Type Checking**: Strong typing with Pydantic
- **Error Messages**: Clear validation errors

### 3. Documentation Generation

- **Auto-generated**: From code comments and types
- **Always Up-to-date**: Reflects current code
- **Version Control**: Tracks API changes

## 📱 Mobile-Friendly Documentation

### ReDoc Interface

The `/redoc` endpoint provides:
- **Responsive Design**: Works on mobile devices
- **Clean Layout**: Easy to read documentation
- **Search Functionality**: Find endpoints quickly
- **Dark Mode**: Better for reading

## 🔍 Troubleshooting

### Common Issues

1. **Authentication Not Working**
   - Ensure you're using the correct token format: `Bearer <token>`
   - Check that the token hasn't expired
   - Verify you're using the access token, not refresh token

2. **File Upload Issues**
   - Check file size (max 10MB)
   - Verify file type (JPEG, PNG, GIF, WebP)
   - Ensure you're authenticated

3. **CORS Issues**
   - The API includes CORS middleware
   - Check browser console for CORS errors
   - Verify the correct server URL

### Getting Help

- **Check the logs**: Server logs show detailed error information
- **Review examples**: Each endpoint includes working examples
- **Test with curl**: Use curl commands for debugging
- **Check status codes**: HTTP status codes indicate the issue

## 🎯 Best Practices

### For API Consumers

1. **Always check status codes** before processing responses
2. **Handle errors gracefully** using the documented error responses
3. **Use the examples** as templates for your requests
4. **Test with Swagger UI** before implementing in your code

### For Developers

1. **Keep documentation updated** when changing endpoints
2. **Add meaningful examples** for all request/response models
3. **Document error cases** comprehensively
4. **Use descriptive field names** and descriptions

## 📚 Additional Resources

- [Frontend Integration Guide](API_GUIDE_FRONTEND.md)
- [Authentication Testing Guide](AUTHENTICATION_TESTING.md)
- [Docker Setup Guide](README_DOCKER.md)
- [Code Explanation](CODE_EXPLANATION.md)

## 🚀 Quick Reference

### Essential URLs

```bash
# Interactive API Documentation
http://localhost:8000/docs

# Alternative Documentation
http://localhost:8000/redoc

# OpenAPI Schema
http://localhost:8000/openapi.json

# Health Check
http://localhost:8000/health

# API Root
http://localhost:8000/
```

### Common Headers

```bash
# Authentication
Authorization: Bearer <access_token>

# Content Type (for JSON)
Content-Type: application/json

# File Upload (automatic)
Content-Type: multipart/form-data
```

---

**Happy API Testing! 🚀** 