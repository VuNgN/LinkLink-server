#!/usr/bin/env python3
"""
Setup all environments (production & development) for LinkLink Image Upload Server
- Tạo database, bảng, các cột cần thiết, enum, ...
- Dựa trên models trong app/core/entities/*
- Ignore nếu database đã tồn tại để tránh override
- Idempotent: chạy lại không bị lỗi, không override dữ liệu cũ
"""
import asyncio
import os
import sys
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from passlib.context import CryptContext
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.entities.album import Album  # noqa: F401
from app.core.entities.image import Image  # noqa: F401
from app.core.entities.poster import Poster  # noqa: F401
from app.core.entities.user import User, UserStatus  # noqa: F401
from app.infrastructure.database import Base
from app.infrastructure.repositories import PostgreSQLUserRepository

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))


def load_env_file(env_path):
    if Path(env_path).exists():
        load_dotenv(env_path, override=True)
        print(f"Loaded env: {env_path}")
    else:
        print(f"⚠️ Env file not found: {env_path}")


def get_db_url():
    return os.getenv("DATABASE_URL")


def get_admin_info():
    return (
        os.getenv("ADMIN_USERNAME", "admin"),
        os.getenv("ADMIN_EMAIL", "admin@example.com"),
        os.getenv("ADMIN_PASSWORD", "admin123"),
    )


def to_sync_url(db_url):
    # Chuyển asyncpg -> psycopg2 để dùng cho create_engine
    return db_url.replace("postgresql+asyncpg://", "postgresql+psycopg2://")


async def create_tables_and_migrations(async_engine):
    # Tạo bảng dựa trên SQLAlchemy models (Base.metadata)
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        print("✅ Created all tables from SQLAlchemy models (if not exist)")

        # Migration bổ sung (nếu có)
        # 1. Enum cho albums (privacy)
        await conn.execute(
            text(
                """
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'albumprivacyenum') THEN
                CREATE TYPE albumprivacyenum AS ENUM ('writable', 'read-only');
            END IF;
        END$$;
        """
            )
        )
        await conn.execute(
            text(
                """
        ALTER TABLE IF EXISTS albums
        ADD COLUMN IF NOT EXISTS privacy albumprivacyenum NOT NULL DEFAULT 'read-only';
        """
            )
        )
        print("✅ Ensured privacy column on albums table")

        # 2. Các migration bổ sung khác nếu cần (ví dụ: soft delete, FK, ...)
        # ...


async def create_admin_user(async_engine):
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    async_session = sessionmaker(
        async_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        user_repo = PostgreSQLUserRepository(session)
        admin_username, admin_email, admin_password = get_admin_info()
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


async def setup_env(env_name, env_path):
    print(f"\n===== Setting up {env_name} environment =====")
    load_env_file(env_path)
    db_url = get_db_url()
    if not db_url:
        print(f"❌ DATABASE_URL not found in {env_path}, skipping...")
        return
    db_name = db_url.rsplit("/", 1)[-1]
    db_url_root = db_url.rsplit("/", 1)[0] + "/postgres"
    sync_db_url_root = to_sync_url(db_url_root)
    try:
        # Sử dụng AUTOCOMMIT để tạo database ngoài transaction block
        with create_engine(sync_db_url_root).connect().execution_options(
            isolation_level="AUTOCOMMIT"
        ) as conn:
            result = conn.execute(
                text(f"SELECT 1 FROM pg_database WHERE datname='{db_name}'")
            )
            if not result.fetchone():
                conn.execute(text(f"CREATE DATABASE {db_name}"))
                print(f"✅ Created database: {db_name}")
            else:
                print(f"ℹ️ Database {db_name} already exists")
    except Exception as e:
        print(f"❌ Error checking/creating database {db_name}: {e}")
        return
    # Run migrations and admin user setup
    async_engine = create_async_engine(db_url, echo=False)
    await create_tables_and_migrations(async_engine)
    await create_admin_user(async_engine)
    await async_engine.dispose()


async def main():
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    await setup_env("Development", os.path.join(project_root, ".env.development"))
    print("\n🎉 Dev environment setup completed!")


if __name__ == "__main__":
    asyncio.run(main())
