"""
PostgreSQL Token Repository implementations
"""

from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.interfaces import RefreshTokenRepository, TokenRepository
from ..models import RefreshTokenModel


class PostgreSQLTokenRepository(TokenRepository):
    """PostgreSQL token repository implementation"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def store_refresh_token(self, token: str, username: str) -> bool:
        """Store refresh token"""
        # Set expiration to 7 days from now
        expires_at = datetime.utcnow() + timedelta(days=7)

        db_token = RefreshTokenModel(
            token=token, username=username, expires_at=expires_at
        )
        self.session.add(db_token)
        await self.session.commit()
        return True

    async def get_username_by_refresh_token(self, token: str) -> Optional[str]:
        """Get username by refresh token"""
        result = await self.session.execute(
            select(RefreshTokenModel)
            .where(RefreshTokenModel.token == token)
            .where(RefreshTokenModel.expires_at > datetime.utcnow())
        )
        db_token = result.scalar_one_or_none()

        return db_token.username if db_token else None

    async def delete_refresh_token(self, token: str) -> bool:
        """Delete refresh token"""
        result = await self.session.execute(
            delete(RefreshTokenModel).where(RefreshTokenModel.token == token)
        )
        await self.session.commit()
        return result.rowcount > 0

    async def cleanup_expired_tokens(self) -> int:
        """Clean up expired refresh tokens"""
        result = await self.session.execute(
            delete(RefreshTokenModel).where(
                RefreshTokenModel.expires_at <= datetime.utcnow()
            )
        )
        await self.session.commit()
        return result.rowcount


class PostgreSQLRefreshTokenRepository(RefreshTokenRepository):
    """PostgreSQL refresh token repository implementation"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, token: str, username: str, expires_at: datetime) -> bool:
        """Create a new refresh token"""
        db_token = RefreshTokenModel(
            token=token, username=username, expires_at=expires_at
        )
        self.session.add(db_token)
        await self.session.commit()
        return True

    async def get_by_token(self, token: str):
        """Get refresh token by token string"""
        result = await self.session.execute(
            select(RefreshTokenModel).where(RefreshTokenModel.token == token)
        )
        return result.scalar_one_or_none()

    async def delete_by_token(self, token: str) -> bool:
        """Delete refresh token by token string"""
        result = await self.session.execute(
            delete(RefreshTokenModel).where(RefreshTokenModel.token == token)
        )
        await self.session.commit()
        return result.rowcount > 0
