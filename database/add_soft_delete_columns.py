"""
Database migration script to add soft delete columns to posters table
"""

import asyncio
import os
import sys

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from app.infrastructure.database import DATABASE_URL


async def add_soft_delete_columns():
    """Add is_deleted and deleted_at columns to posters table"""

    # Create engine
    engine = create_async_engine(DATABASE_URL, echo=True)

    async with engine.begin() as conn:
        try:
            # Add is_deleted column with default value False
            await conn.execute(
                text(
                    "ALTER TABLE posters ADD COLUMN IF NOT EXISTS is_deleted BOOLEAN DEFAULT FALSE NOT NULL"
                )
            )
            print("✅ Added is_deleted column")

            # Add deleted_at column
            await conn.execute(
                text(
                    "ALTER TABLE posters ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP WITH TIME ZONE"
                )
            )
            print("✅ Added deleted_at column")

            # Update existing posts to have is_deleted = false
            result = await conn.execute(
                text("UPDATE posters SET is_deleted = FALSE WHERE is_deleted IS NULL")
            )
            print(
                f"✅ Updated {result.rowcount} existing posts to have is_deleted = FALSE"
            )

        except Exception as e:
            print(f"❌ Error adding columns: {e}")
            raise

    await engine.dispose()


if __name__ == "__main__":
    print("🔄 Adding soft delete columns to posters table...")
    print("   - Adding is_deleted column (BOOLEAN, default FALSE)")
    print("   - Adding deleted_at column (TIMESTAMP WITH TIME ZONE)")
    print("   - Setting existing posts to is_deleted = FALSE")
    print()

    asyncio.run(add_soft_delete_columns())

    print()
    print("✅ Migration completed successfully!")
