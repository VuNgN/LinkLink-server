"""
Script to update existing posts to set is_deleted to false and deleted_at to null
"""

import asyncio
import os
import sys

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.infrastructure.database import DATABASE_URL
from app.infrastructure.models import PosterModel


async def update_existing_posts():
    """Update all existing posts to set is_deleted to false and deleted_at to null"""

    # Create engine
    engine = create_async_engine(DATABASE_URL, echo=True)

    # Create session factory
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        try:
            # Update all existing posts
            stmt = update(PosterModel).values(is_deleted=False, deleted_at=None)

            result = await session.execute(stmt)
            await session.commit()

            print("✅ Successfully updated {} posts".format(result.rowcount))
            print("   - Set is_deleted to False")
            print("   - Set deleted_at to None")

        except Exception as e:
            print(f"❌ Error updating posts: {e}")
            await session.rollback()
            raise
        finally:
            await session.close()

    await engine.dispose()


if __name__ == "__main__":
    print("🔄 Updating existing posts...")
    print(
        "   Setting is_deleted to False and deleted_at to None for all existing posts"
    )
    print()

    asyncio.run(update_existing_posts())

    print()
    print("✅ Update completed successfully!")
