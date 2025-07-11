"""
Migration script to add user_id and created_at columns to album_images table
"""

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
import asyncio

from dotenv import load_dotenv
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

# Load environment variables
load_dotenv()

from app.infrastructure.database import DATABASE_URL


def print_success(msg):
    print(msg)


async def add_columns_album_images():
    engine = create_async_engine(DATABASE_URL, echo=True)
    async with engine.begin() as conn:
        try:
            # Add user_id column
            await conn.execute(
                text(
                    (
                        "ALTER TABLE album_images "
                        "ADD COLUMN IF NOT EXISTS user_id VARCHAR(50) REFERENCES users(username);"
                    )
                )
            )
            print_success("✅ Added user_id column to album_images table")

            # Add created_at column
            await conn.execute(
                text(
                    (
                        "ALTER TABLE album_images "
                        "ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE "
                        "DEFAULT NOW();"
                    )
                )
            )
            print_success("✅ Added created_at column to album_images table")

        except Exception as e:
            print(f"❌ Error during migration: {e}")
            raise
    await engine.dispose()


if __name__ == "__main__":
    print("🔄 Adding user_id and created_at columns to album_images table...")
    asyncio.run(add_columns_album_images())
    print("✅ Migration completed successfully!")
