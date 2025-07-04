#!/usr/bin/env python3
"""
Minimal Database Setup Script
- Creates tables
- Creates default admin user (admin/admin123)
"""
import asyncio
import os
from datetime import datetime

from dotenv import load_dotenv
from passlib.context import CryptContext

from app.core.entities import User, UserStatus
from app.infrastructure.database import AsyncSessionLocal, init_db
from app.infrastructure.postgresql_repositories import PostgreSQLUserRepository

load_dotenv()


async def setup_database():
    print("🗄️ Setting up PostgreSQL database...")
    await init_db()
    print("✅ Tables created successfully")
    await create_default_admin()
    print("✅ Default admin user created (admin/admin123)")
    print("🎉 Database setup completed!")


async def create_default_admin():
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    async with AsyncSessionLocal() as session:
        user_repo = PostgreSQLUserRepository(session)
        existing_user = await user_repo.get_by_username("admin")
        if existing_user:
            print("ℹ️ Admin user already exists")
            return
        admin_user = User(
            username="admin",
            email="admin@example.com",
            hashed_password=pwd_context.hash("admin123"),
            is_active=True,
            is_admin=True,
            status=UserStatus.APPROVED,
            approved_at=datetime.utcnow(),
            approved_by="system",
        )
        await user_repo.create(admin_user)
        print("👤 Created admin user: admin/admin123")


def main():
    asyncio.run(setup_database())


if __name__ == "__main__":
    main()
