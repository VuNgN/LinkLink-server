#!/usr/bin/env python3
"""
Minimal Database Setup Script
- Creates tables
- Creates default admin user from environment variables
"""
import asyncio
import os
from datetime import datetime

from dotenv import load_dotenv
from passlib.context import CryptContext

from app.core.entities import User, UserStatus
from app.infrastructure.database import AsyncSessionLocal, init_db
from app.infrastructure.repositories import PostgreSQLUserRepository

load_dotenv()


async def setup_database():
    print("🗄️ Setting up PostgreSQL database...")
    await init_db()
    print("✅ Tables created successfully")
    await create_default_admin()
    print("✅ Default admin user created")
    print("🎉 Database setup completed!")


async def create_default_admin():
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    async with AsyncSessionLocal() as session:
        user_repo = PostgreSQLUserRepository(session)

        # Get admin credentials from environment
        admin_username = os.getenv("ADMIN_USERNAME", "admin")
        admin_email = os.getenv("ADMIN_EMAIL", "admin@example.com")
        admin_password = os.getenv("ADMIN_PASSWORD", "admin123")

        existing_user = await user_repo.get_by_username(admin_username)
        if existing_user:
            print(f"ℹ️ Admin user '{admin_username}' already exists")
            return

        admin_user = User(
            username=admin_username,
            email=admin_email,
            hashed_password=pwd_context.hash(admin_password),
            is_active=True,
            is_admin=True,
            status=UserStatus.APPROVED,
            approved_at=datetime.utcnow(),
            approved_by="system",
        )
        await user_repo.create(admin_user)
        print(f"👤 Created admin user: {admin_username}/{admin_password}")


def main():
    asyncio.run(setup_database())


if __name__ == "__main__":
    main()
