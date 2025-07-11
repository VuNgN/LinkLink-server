#!/usr/bin/env python3
"""
Admin User Management Script
This script allows you to add admin users to the LinkLink Image Upload Server
"""
import asyncio
import os
import sys
from datetime import datetime
from getpass import getpass

from dotenv import load_dotenv

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from passlib.context import CryptContext
from pydantic import validate_email

from app.core.entities import User, UserStatus
from app.infrastructure.database import AsyncSessionLocal
from app.infrastructure.postgresql_repositories import PostgreSQLUserRepository

load_dotenv()


class AdminUserCreator:
    """Class to handle admin user creation"""

    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    async def create_admin_user(self, username: str, email: str, password: str) -> bool:
        """Create an admin user in the database"""
        try:
            async with AsyncSessionLocal() as session:
                user_repo = PostgreSQLUserRepository(session)

                # Check if user already exists
                existing_user = await user_repo.get_by_username(username)
                if existing_user:
                    print(f"❌ User '{username}' already exists!")
                    return False

                # Check if email already exists
                existing_email = await user_repo.get_by_email(email)
                if existing_email:
                    print(f"❌ Email '{email}' is already registered!")
                    return False

                # Create admin user
                admin_user = User(
                    username=username,
                    email=email,
                    hashed_password=self.pwd_context.hash(password),
                    is_active=True,
                    is_admin=True,
                    status=UserStatus.APPROVED,  # Admin users are automatically approved
                    approved_at=datetime.utcnow(),
                    approved_by="system",
                )

                await user_repo.create(admin_user)
                print("✅ Admin user '{}' created successfully!".format(username))
                print("📧 Email: {}".format(email))
                print("🔐 Status: Approved and Active")
                return True

        except Exception as e:
            print(f"❌ Error creating admin user: {str(e)}")
            return False

    async def list_admin_users(self):
        """List all admin users (users with approved status)"""
        try:
            async with AsyncSessionLocal() as session:
                user_repo = PostgreSQLUserRepository(session)

                # Get all approved users
                admin_users = await user_repo.get_by_status(UserStatus.APPROVED)

                if not admin_users:
                    print("📋 No admin users found in the database.")
                    return

                print(f"📋 Found {len(admin_users)} admin user(s):")
                print("-" * 60)
                for user in admin_users:
                    print(f"👤 Username: {user.username}")
                    print(f"📧 Email: {user.email}")
                    print(f"✅ Status: {user.status}")
                    print(f"🟢 Active: {user.is_active}")
                    print(f"👑 Admin: {user.is_admin}")
                    print(f"📅 Created: {user.created_at}")
                    if user.approved_at:
                        print(f"✅ Approved: {user.approved_at}")
                    print("-" * 60)

        except Exception as e:
            print(f"❌ Error listing admin users: {str(e)}")

    async def remove_admin_user(self, username: str) -> bool:
        """Remove an admin user from the database"""
        try:
            async with AsyncSessionLocal() as session:
                user_repo = PostgreSQLUserRepository(session)

                # Check if user exists
                existing_user = await user_repo.get_by_username(username)
                if not existing_user:
                    print(f"❌ User '{username}' not found!")
                    return False

                # Check if user is admin
                if not existing_user.is_admin:
                    print(f"❌ User '{username}' is not an admin!")
                    return False

                # Prevent removing the last admin
                admin_users = await user_repo.get_by_status(UserStatus.APPROVED)
                admin_count = sum(1 for user in admin_users if user.is_admin)

                if admin_count <= 1:
                    print(
                        f"❌ Cannot remove '{username}' - this is the last admin user!"
                    )
                    print(
                        "💡 Create another admin user first before removing this one."
                    )
                    return False

                # Remove the user
                await user_repo.delete(username)
                print(f"✅ Admin user '{username}' removed successfully!")
                return True

        except Exception as e:
            print(f"❌ Error removing admin user: {str(e)}")
            return False


def validate_email_address(email: str) -> bool:
    """Validate email format"""
    try:
        validate_email(email)
        return True
    except Exception:
        return False


def validate_username(username: str) -> bool:
    """Validate username format"""
    if len(username) < 3 or len(username) > 50:
        return False
    if not username.replace("_", "").replace("-", "").isalnum():
        return False
    return True


def validate_password(password: str) -> bool:
    """Validate password strength"""
    if len(password) < 6:
        return False
    return True


async def interactive_create_admin():
    """Interactive admin user creation"""
    print("🛠️  Admin User Creation Tool")
    print("=" * 40)

    creator = AdminUserCreator()

    # Get user input
    while True:
        username = input("👤 Enter username (3-50 characters): ").strip()
        if validate_username(username):
            break
        print("❌ Invalid username. Must be 3-50 characters, alphanumeric with _ or -")

    while True:
        email = input("📧 Enter email address: ").strip()
        if validate_email_address(email):
            break
        print("❌ Invalid email address")

    while True:
        password = getpass("🔐 Enter password (min 6 characters): ")
        if validate_password(password):
            break
        print("❌ Password must be at least 6 characters")

    confirm_password = getpass("🔐 Confirm password: ")
    if password != confirm_password:
        print("❌ Passwords do not match!")
        return

    print("\n📋 Admin User Details:")
    print(f"👤 Username: {username}")
    print(f"📧 Email: {email}")
    print(f"🔐 Password: {'*' * len(password)}")

    confirm = input("\n❓ Create this admin user? (y/N): ").strip().lower()
    if confirm != "y":
        print("❌ Admin user creation cancelled.")
        return

    # Create the admin user
    success = await creator.create_admin_user(username, email, password)
    if success:
        print("\n🎉 Admin user created successfully!")
        print("\n📋 Next steps:")
        print("1. Login with the new admin credentials")
        print("2. Access admin panel: ./admin/open_admin.sh")


async def interactive_remove_admin():
    """Interactive admin user removal"""
    print("🗑️  Admin User Removal Tool")
    print("=" * 35)

    creator = AdminUserCreator()

    # First, show existing admin users
    print("📋 Current admin users:")
    await creator.list_admin_users()
    print()

    # Get username to remove
    username = input("👤 Enter username to remove: ").strip()
    if not username:
        print("❌ Username cannot be empty!")
        return

    # Confirm removal
    print(f"\n⚠️  WARNING: You are about to remove admin user '{username}'")
    print("This action cannot be undone!")

    confirm = input("❓ Are you sure? Type 'YES' to confirm: ").strip()
    if confirm != "YES":
        print("❌ Admin user removal cancelled.")
        return

    # Remove the admin user
    success = await creator.remove_admin_user(username)
    if success:
        print("\n🎉 Admin user removed successfully!")
        print("\n📋 Remaining admin users:")
        await creator.list_admin_users()


async def list_existing_admins():
    """List existing admin users"""
    print("📋 Listing Admin Users")
    print("=" * 30)

    creator = AdminUserCreator()
    await creator.list_admin_users()


def show_usage():
    """Show usage information"""
    print("🛠️  Admin User Management Tool")
    print("=" * 40)
    print()
    print("Usage:")
    print("  python database/add_admin_user.py create  # Interactive admin creation")
    print("  python database/add_admin_user.py list    # List existing admin users")
    print("  python database/add_admin_user.py remove  # Remove admin user")
    print("  python database/add_admin_user.py         # Show this help")
    print()
    print("Examples:")
    print("  python database/add_admin_user.py create")
    print("  python database/add_admin_user.py list")
    print("  python database/add_admin_user.py remove")
    print()
    print("Or use the shell script:")
    print("  ./add_admin.sh create")
    print("  ./add_admin.sh list")
    print("  ./add_admin.sh remove")


async def main():
    """Main function"""
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()

        if command == "create":
            await interactive_create_admin()
        elif command == "list":
            await list_existing_admins()
        elif command == "remove":
            await interactive_remove_admin()
        else:
            show_usage()
    else:
        show_usage()


if __name__ == "__main__":
    asyncio.run(main())
