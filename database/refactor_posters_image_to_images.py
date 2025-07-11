"""
Migration script to refactor posters/images relationship:
- Each poster can have many images, each image belongs to one poster
- Move image_path from posters to images (if not already present)
- Add poster_id to images (FK to posters.id)
- Remove image_path and image_id from posters
"""

import asyncio
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

# Load environment variables
load_dotenv()

from app.infrastructure.database import DATABASE_URL


async def migrate_posters_images():
    engine = create_async_engine(DATABASE_URL, echo=True)
    async with engine.begin() as conn:
        try:
            # 1. Add poster_id column to images
            await conn.execute(
                text(
                    """
                ALTER TABLE images
                ADD COLUMN IF NOT EXISTS poster_id INTEGER;
            """
                )
            )
            print("✅ Added poster_id column to images table")

            # 2. For each poster, move image_path to images and set poster_id
            result = await conn.execute(
                text(
                    """
                SELECT id, image_path, username, created_at FROM posters
            """
                )
            )
            posters = result.fetchall()
            for poster in posters:
                poster_id = poster.id
                image_path = poster.image_path
                username = poster.username
                created_at = poster.created_at
                filename = os.path.basename(image_path) if image_path else None
                if not filename:
                    continue
                # Insert image if not exists, and set poster_id
                await conn.execute(
                    text(
                        """
                    INSERT INTO images (filename, original_filename, username, file_path, file_size, content_type, upload_date, poster_id)
                    VALUES (:filename, :original_filename, :username, :file_path, 0, 'image/unknown', :upload_date, :poster_id)
                    ON CONFLICT (filename) DO NOTHING
                """
                    ),
                    {
                        "filename": filename,
                        "original_filename": filename,
                        "username": username,
                        "file_path": image_path,
                        "upload_date": created_at,
                        "poster_id": poster_id,
                    },
                )
                # Update image to set poster_id if already exists
                await conn.execute(
                    text(
                        """
                    UPDATE images SET poster_id = :poster_id WHERE filename = :filename
                """
                    ),
                    {
                        "filename": filename,
                        "poster_id": poster_id,
                    },
                )
            print(
                "✅ Migrated image paths to images table and linked poster_id in images"
            )

            # 3. Remove image_path and image_id columns from posters
            await conn.execute(
                text(
                    """
                ALTER TABLE posters DROP COLUMN IF EXISTS image_path;
            """
                )
            )
            await conn.execute(
                text(
                    """
                ALTER TABLE posters DROP COLUMN IF EXISTS image_id;
            """
                )
            )
            print("✅ Removed image_path and image_id columns from posters table")

            # 4. Add FK constraint for images.poster_id
            await conn.execute(
                text(
                    """
                ALTER TABLE images
                ADD CONSTRAINT fk_images_poster_id FOREIGN KEY (poster_id) REFERENCES posters(id) ON DELETE SET NULL;
            """
                )
            )
            print("✅ Added FK constraint for images.poster_id")

        except Exception as e:
            print(f"❌ Error during migration: {e}")
            raise
    await engine.dispose()


if __name__ == "__main__":
    print("🔄 Refactoring posters/images relationship to 1-n (poster -> images)...")
    asyncio.run(migrate_posters_images())
    print("✅ Migration completed successfully!")
