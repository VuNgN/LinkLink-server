#!/usr/bin/env python3
"""
Database setup script for PostgreSQL
"""
import asyncio
import os
from dotenv import load_dotenv

from app.infrastructure.database import init_db, engine
from app.infrastructure.models import UserModel, ImageModel, RefreshTokenModel
from app.core.entities import User
from passlib.context import CryptContext

load_dotenv()

async def setup_database():
    """Setup database tables and initial data"""
    print("🗄️ Setting up PostgreSQL database...")
    
    try:
        # Create tables
        await init_db()
        print("✅ Database tables created successfully")
        
        # Create default admin user
        await create_default_admin()
        print("✅ Default admin user created")
        
        print("🎉 Database setup completed!")
        
    except Exception as e:
        print(f"❌ Database setup failed: {str(e)}")
        raise

async def create_default_admin():
    """Create default admin user"""
    from sqlalchemy.ext.asyncio import AsyncSession
    from app.infrastructure.database import AsyncSessionLocal
    from app.infrastructure.postgresql_repositories import PostgreSQLUserRepository
    
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    async with AsyncSessionLocal() as session:
        user_repo = PostgreSQLUserRepository(session)
        
        # Check if admin user already exists
        existing_user = await user_repo.get_by_username("admin")
        if existing_user:
            print("ℹ️ Admin user already exists")
            return
        
        # Create admin user
        admin_user = User(
            username="admin",
            hashed_password=pwd_context.hash("admin123"),
            is_active=True
        )
        
        await user_repo.create(admin_user)
        print("👤 Created admin user: admin/admin123")

async def check_database_connection():
    """Check database connection"""
    try:
        async with engine.begin() as conn:
            await conn.execute("SELECT 1")
        print("✅ Database connection successful")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {str(e)}")
        return False

def main():
    """Main setup function"""
    print("🚀 PostgreSQL Database Setup")
    print("=" * 40)
    
    # Check environment
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("⚠️ DATABASE_URL not set. Using default: postgresql+asyncpg://postgres:password@localhost:5432/image_upload_db")
    
    # Check connection
    if not asyncio.run(check_database_connection()):
        print("\n❌ Cannot connect to database. Please check:")
        print("1. PostgreSQL is running")
        print("2. Database exists: image_upload_db")
        print("3. User has permissions")
        print("4. DATABASE_URL is correct")
        return
    
    # Setup database
    asyncio.run(setup_database())

if __name__ == "__main__":
    main() 