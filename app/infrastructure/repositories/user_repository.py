"""
PostgreSQL User Repository implementation
"""

from datetime import datetime
from typing import List, Optional

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.entities import User, UserStatus
from ...core.interfaces import UserRepository
from ..models import UserModel


class PostgreSQLUserRepository(UserRepository):
    """PostgreSQL user repository implementation"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, user: User) -> User:
        """Create a new user"""
        db_user = UserModel(
            username=user.username,
            email=user.email,
            hashed_password=user.hashed_password,
            is_active=user.is_active,
            is_admin=user.is_admin,
            status=user.status.value,
            created_at=user.created_at,
            updated_at=user.updated_at,
            approved_at=user.approved_at,
            approved_by=user.approved_by,
        )
        self.session.add(db_user)
        await self.session.commit()
        await self.session.refresh(db_user)

        return User(
            username=db_user.username,
            email=db_user.email,
            hashed_password=db_user.hashed_password,
            is_active=db_user.is_active,
            is_admin=db_user.is_admin,
            status=UserStatus(db_user.status),
            created_at=db_user.created_at,
            updated_at=db_user.updated_at,
            approved_at=db_user.approved_at,
            approved_by=db_user.approved_by,
        )

    async def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        result = await self.session.execute(
            select(UserModel).where(UserModel.username == username)
        )
        db_user = result.scalar_one_or_none()

        if not db_user:
            return None

        return User(
            username=db_user.username,
            email=db_user.email,
            hashed_password=db_user.hashed_password,
            is_active=db_user.is_active,
            is_admin=db_user.is_admin,
            status=UserStatus(db_user.status),
            created_at=db_user.created_at,
            updated_at=db_user.updated_at,
            approved_at=db_user.approved_at,
            approved_by=db_user.approved_by,
        )

    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        result = await self.session.execute(
            select(UserModel).where(UserModel.email == email)
        )
        db_user = result.scalar_one_or_none()

        if not db_user:
            return None

        return User(
            username=db_user.username,
            email=db_user.email,
            hashed_password=db_user.hashed_password,
            is_active=db_user.is_active,
            is_admin=db_user.is_admin,
            status=UserStatus(db_user.status),
            created_at=db_user.created_at,
            updated_at=db_user.updated_at,
            approved_at=db_user.approved_at,
            approved_by=db_user.approved_by,
        )

    async def get_by_status(self, status: UserStatus) -> List[User]:
        """Get users by status"""
        result = await self.session.execute(
            select(UserModel).where(UserModel.status == status.value)
        )
        db_users = result.scalars().all()

        return [
            User(
                username=user.username,
                email=user.email,
                hashed_password=user.hashed_password,
                is_active=user.is_active,
                is_admin=user.is_admin,
                status=UserStatus(user.status),
                created_at=user.created_at,
                updated_at=user.updated_at,
                approved_at=user.approved_at,
                approved_by=user.approved_by,
            )
            for user in db_users
        ]

    async def update(self, user: User) -> User:
        """Update user"""
        result = await self.session.execute(
            select(UserModel).where(UserModel.username == user.username)
        )
        db_user = result.scalar_one_or_none()

        if not db_user:
            raise ValueError("User not found")

        db_user.email = user.email
        db_user.hashed_password = user.hashed_password
        db_user.is_active = user.is_active
        db_user.is_admin = user.is_admin
        db_user.status = user.status.value
        db_user.updated_at = datetime.utcnow()
        db_user.approved_at = user.approved_at
        db_user.approved_by = user.approved_by

        await self.session.commit()
        await self.session.refresh(db_user)

        return User(
            username=db_user.username,
            email=db_user.email,
            hashed_password=db_user.hashed_password,
            is_active=db_user.is_active,
            is_admin=db_user.is_admin,
            status=UserStatus(db_user.status),
            created_at=db_user.created_at,
            updated_at=db_user.updated_at,
            approved_at=db_user.approved_at,
            approved_by=db_user.approved_by,
        )

    async def delete(self, username: str) -> bool:
        """Delete user"""
        result = await self.session.execute(
            delete(UserModel).where(UserModel.username == username)
        )
        await self.session.commit()
        return result.rowcount > 0
