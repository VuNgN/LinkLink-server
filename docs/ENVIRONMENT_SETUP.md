# Environment Variables Setup Guide

## Overview
This project uses environment variables for all sensitive configuration. Copy the template below and customize it for your environment.

## Quick Setup

1. **Copy the template**:
```bash
cp env.template .env
```

2. **Edit the .env file** with your actual values
3. **Restart the application**

## Environment Variables Reference

### Database Configuration
```bash
# Database connection URL
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/linklink

# Database debugging (optional)
DB_ECHO=false
```

### Security Configuration
```bash
# JWT Secret Key (CHANGE THIS IN PRODUCTION!)
SECRET_KEY=your-secret-key-change-this-in-production

# Token expiration times
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

### Email Configuration
```bash
# Gmail SMTP Configuration
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_FROM=your-email@gmail.com
MAIL_PORT=587
MAIL_SERVER=smtp.gmail.com
MAIL_STARTTLS=true
MAIL_SSL_TLS=false
USE_CREDENTIALS=true

# Admin email for notifications
ADMIN_EMAIL=admin@example.com
```

### File Upload Configuration
```bash
# Upload settings
UPLOAD_DIR=uploads
MAX_FILE_SIZE=10485760  # 10MB in bytes
ALLOWED_TYPES=image/jpeg,image/png,image/gif,image/webp
```

### API Configuration
```bash
# API settings
API_V1_STR=/api/v1
PROJECT_NAME=LinkLink Image Upload Server
```

### CORS Configuration
```bash
# Allowed origins (comma-separated)
BACKEND_CORS_ORIGINS=http://localhost:3000,http://localhost:8080
```

### Logging Configuration
```bash
# Logging settings
LOG_LEVEL=INFO
LOG_FILE=logs/app.log
```

### Development Configuration
```bash
# Development mode
DEBUG=false
```

### Admin User Configuration
```bash
# Admin user credentials (for database setup)
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123
```

## Gmail App Password Setup

To use Gmail for sending emails:

1. **Enable 2-Factor Authentication** in your Google Account
2. **Generate App Password**:
   - Go to Google Account Settings
   - Security → 2-Step Verification → App passwords
   - Select "Mail" and generate password
3. **Use the generated password** in `MAIL_PASSWORD`

## Production Security Checklist

- [ ] Change `SECRET_KEY` to a strong random string
- [ ] Use strong database passwords
- [ ] Configure proper CORS origins
- [ ] Set `DEBUG=false`
- [ ] Use HTTPS in production
- [ ] Configure proper email credentials
- [ ] Set appropriate file upload limits

## Example .env File

```bash
# Database
DATABASE_URL=postgresql+asyncpg://myuser:mypassword@localhost:5432/linklink
DB_ECHO=false

# Security
SECRET_KEY=my-super-secret-key-123456789
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Email
MAIL_USERNAME=myapp@gmail.com
MAIL_PASSWORD=my-app-password-123
MAIL_FROM=LinkLink <myapp@gmail.com>
MAIL_PORT=587
MAIL_SERVER=smtp.gmail.com
MAIL_STARTTLS=true
MAIL_SSL_TLS=false
USE_CREDENTIALS=true
ADMIN_EMAIL=admin@linklink.world

# File Upload
UPLOAD_DIR=uploads
MAX_FILE_SIZE=10485760
ALLOWED_TYPES=image/jpeg,image/png,image/gif,image/webp

# API
API_V1_STR=/api/v1
PROJECT_NAME=LinkLink Image Upload Server

# CORS
BACKEND_CORS_ORIGINS=https://linklink.world,http://localhost:3000

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/app.log

# Development
DEBUG=false

# Admin
ADMIN_USERNAME=admin
ADMIN_PASSWORD=secure-admin-password-123
```

## Troubleshooting

### Email Not Working
- Check Gmail App Password is correct
- Verify 2-Factor Authentication is enabled
- Check firewall/network settings

### Database Connection Issues
- Verify PostgreSQL is running
- Check database credentials
- Ensure database exists

### CORS Issues
- Add your frontend URL to `BACKEND_CORS_ORIGINS`
- Use comma-separated list for multiple origins

### File Upload Issues
- Check `UPLOAD_DIR` exists and is writable
- Verify `MAX_FILE_SIZE` is appropriate
- Check `ALLOWED_TYPES` includes your file type 