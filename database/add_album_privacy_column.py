"""
Database migration script to add 'privacy' column to albums table
"""

import asyncio
import os
import sys

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

# Load environment variables
load_dotenv()

from app.infrastructure.database import DATABASE_URL


async def add_privacy_column():
    """Add privacy column to albums table"""
    engine = create_async_engine(DATABASE_URL, echo=True)
    async with engine.begin() as conn:
        try:
            # Create the enum type if it doesn't exist
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
            print("✅ Ensured albumprivacyenum type exists")

            # Add the privacy column if it doesn't exist
            await conn.execute(
                text(
                    """
                ALTER TABLE albums
                ADD COLUMN IF NOT EXISTS privacy albumprivacyenum NOT NULL DEFAULT 'read-only';
            """
                )
            )
            print("✅ Added privacy column to albums table")
        except Exception as e:
            print(f"❌ Error adding privacy column: {e}")
            raise
    await engine.dispose()


if __name__ == "__main__":
    print("🔄 Adding privacy column to albums table...")
    asyncio.run(add_privacy_column())
    print("✅ Migration completed successfully!")
