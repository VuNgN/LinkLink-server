#!/usr/bin/env python3
"""
Environment Variables Checker
Validates that all required environment variables are set correctly
"""

import os

from dotenv import load_dotenv

load_dotenv()


def check_env_variables():
    """Check all environment variables"""
    print("🔍 Checking Environment Variables...")
    print("=" * 50)

    # Required variables with their default values
    required_vars = {
        "DATABASE_URL": {
            "default": "postgresql+asyncpg://user:password@localhost/linklink",
            "description": "Database connection URL",
        },
        "SECRET_KEY": {
            "default": "your-secret-key-change-this-in-production",
            "description": "JWT secret key",
        },
        "MAIL_USERNAME": {
            "default": "your-email@gmail.com",
            "description": "Email username",
        },
        "MAIL_PASSWORD": {
            "default": "your-app-password",
            "description": "Email password",
        },
        "MAIL_FROM": {
            "default": "your-email@gmail.com",
            "description": "Email from address",
        },
        "ADMIN_EMAIL": {
            "default": "admin@example.com",
            "description": "Admin email address",
        },
        "ADMIN_USERNAME": {"default": "admin", "description": "Admin username"},
        "ADMIN_PASSWORD": {"default": "admin123", "description": "Admin password"},
    }

    # Optional variables
    optional_vars = {
        "ACCESS_TOKEN_EXPIRE_MINUTES": "30",
        "REFRESH_TOKEN_EXPIRE_DAYS": "7",
        "MAIL_PORT": "587",
        "MAIL_SERVER": "smtp.gmail.com",
        "MAIL_STARTTLS": "true",
        "MAIL_SSL_TLS": "false",
        "USE_CREDENTIALS": "true",
        "UPLOAD_DIR": "uploads",
        "MAX_FILE_SIZE": "10485760",
        "ALLOWED_TYPES": "image/jpeg,image/png,image/gif,image/webp",
        "API_V1_STR": "/api/v1",
        "PROJECT_NAME": "LinkLink Image Upload Server",
        "BACKEND_CORS_ORIGINS": "http://localhost:3000,http://localhost:8080",
        "LOG_LEVEL": "INFO",
        "LOG_FILE": "logs/app.log",
        "DEBUG": "false",
        "DB_ECHO": "false",
    }

    issues = []
    warnings = []

    print("📋 Required Variables:")
    print("-" * 30)

    for var, config in required_vars.items():
        value = os.getenv(var, config["default"])
        status = "✅" if value != config["default"] else "❌"
        print(f"{status} {var}: {value}")

        if value == config["default"]:
            issues.append(f"❌ {var} is using default value")
        elif var in ["SECRET_KEY", "MAIL_PASSWORD", "ADMIN_PASSWORD"]:
            if len(value) < 8:
                warnings.append(f"⚠️ {var} might be too weak")

    print("\n📋 Optional Variables:")
    print("-" * 30)

    for var, default in optional_vars.items():
        value = os.getenv(var, default)
        status = "✅" if value != default else "ℹ️"
        print(f"{status} {var}: {value}")

    print("\n🔍 Security Check:")
    print("-" * 30)

    # Check for security issues
    secret_key = os.getenv("SECRET_KEY", "your-secret-key-change-this-in-production")
    if secret_key == "your-secret-key-change-this-in-production":
        issues.append("❌ SECRET_KEY is using default value - CHANGE THIS!")

    mail_password = os.getenv("MAIL_PASSWORD", "your-app-password")
    if mail_password == "your-app-password":
        issues.append("❌ MAIL_PASSWORD is using default value")

    admin_password = os.getenv("ADMIN_PASSWORD", "admin123")
    if admin_password == "admin123":
        warnings.append("⚠️ ADMIN_PASSWORD is using default value")

    # Check email configuration
    mail_username = os.getenv("MAIL_USERNAME", "your-email@gmail.com")
    mail_from = os.getenv("MAIL_FROM", "your-email@gmail.com")

    if mail_username == "your-email@gmail.com" or mail_from == "your-email@gmail.com":
        warnings.append("⚠️ Email configuration is using default values")

    # Summary
    print("\n📊 Summary:")
    print("=" * 50)

    if issues:
        print("🚨 Issues Found:")
        for issue in issues:
            print(f"  {issue}")
    else:
        print("✅ No critical issues found")

    if warnings:
        print("\n⚠️ Warnings:")
        for warning in warnings:
            print(f"  {warning}")

    if not issues and not warnings:
        print("🎉 All environment variables are properly configured!")

    print("\n💡 Recommendations:")
    print("- Copy env.template to .env if you haven't already")
    print("- Change default values for production")
    print("- Use strong passwords and keys")
    print("- Configure email properly for notifications")


if __name__ == "__main__":
    check_env_variables()
