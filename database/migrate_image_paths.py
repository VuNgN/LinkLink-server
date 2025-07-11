import asyncio
import os
from datetime import datetime

from dotenv import load_dotenv
from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

# Load biến môi trường từ .env
load_dotenv()

UPLOAD_DIR = "uploads"

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL is not set. Please check your .env file or environment variables."
    )

engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def migrate_images_and_posters():
    async with AsyncSessionLocal() as session:
        # Xử lý bảng images
        result = await session.execute(
            text("SELECT filename, file_path, username, upload_date FROM images")
        )
        images = result.fetchall()
        for img in images:
            filename = img.filename
            old_path = img.file_path
            username = img.username
            upload_date = img.upload_date or datetime.now()

            year = upload_date.year
            month = f"{upload_date.month:02d}"
            day = f"{upload_date.day:02d}"
            new_dir = os.path.join(UPLOAD_DIR, str(year), month, day, username)
            os.makedirs(new_dir, exist_ok=True)
            new_path = os.path.join(new_dir, filename)

            if os.path.exists(old_path):
                try:
                    os.rename(old_path, new_path)
                    print(f"[images] Moved {old_path} -> {new_path}")
                except Exception as e:
                    print(f"[images] Error moving {old_path} -> {new_path}: {e}")
            else:
                print(f"[images] File not found: {old_path}")

            await session.execute(
                text(
                    "UPDATE images SET file_path = :new_path WHERE filename = :filename"
                ),
                {"new_path": new_path, "filename": filename},
            )

        # Xử lý bảng posters
        result = await session.execute(
            text("SELECT id, image_path, username, created_at FROM posters")
        )
        posters = result.fetchall()
        for poster in posters:
            poster_id = poster.id
            old_path = poster.image_path
            username = poster.username
            created_at = poster.created_at or datetime.now()
            filename = os.path.basename(old_path)

            year = created_at.year
            month = f"{created_at.month:02d}"
            day = f"{created_at.day:02d}"
            new_dir = os.path.join(UPLOAD_DIR, str(year), month, day, username)
            os.makedirs(new_dir, exist_ok=True)
            new_path = os.path.join(new_dir, filename)

            if os.path.exists(old_path):
                try:
                    os.rename(old_path, new_path)
                    print(f"[posters] Moved {old_path} -> {new_path}")
                except Exception as e:
                    print(f"[posters] Error moving {old_path} -> {new_path}: {e}")
            else:
                print(f"[posters] File not found: {old_path}")

            await session.execute(
                text("UPDATE posters SET image_path = :new_path WHERE id = :poster_id"),
                {"new_path": new_path, "poster_id": poster_id},
            )

        await session.commit()
        print("Migration for images and posters completed.")

        # Sau khi migrate: Xóa file không còn trong DB
        print("\n[Cleanup] Checking for orphan files in uploads/ ...")
        # Lấy tất cả file_path trong images và image_path trong posters
        result = await session.execute(text("SELECT file_path FROM images"))
        image_paths = set(row.file_path for row in result.fetchall())
        result = await session.execute(text("SELECT image_path FROM posters"))
        poster_paths = set(row.image_path for row in result.fetchall())
        all_db_paths = image_paths | poster_paths

        # Duyệt toàn bộ file trong uploads/ (đệ quy)
        for root, dirs, files in os.walk(UPLOAD_DIR):
            for file in files:
                abs_path = os.path.join(root, file)
                if abs_path not in all_db_paths:
                    try:
                        os.remove(abs_path)
                        print(f"[cleanup] Deleted orphan file: {abs_path}")
                    except Exception as e:
                        print(f"[cleanup] Error deleting {abs_path}: {e}")
        print("[Cleanup] Done.")


if __name__ == "__main__":
    asyncio.run(migrate_images_and_posters())
