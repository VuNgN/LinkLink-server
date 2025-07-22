from sqlalchemy import create_engine

from app import bootstrap  # noqa: F401
from app.config import settings
from app.infrastructure import models  # noqa: F401
from app.infrastructure.database import Base


def create_tables():
    print(f"Using database: {settings.DATABASE_URL}")
    db_url = settings.DATABASE_URL.replace("postgresql+asyncpg", "postgresql")
    engine = create_engine(db_url)
    print("Creating tables if not exist...")
    for table in Base.metadata.sorted_tables:
        print(f"Creating table: {table.name}")
    Base.metadata.create_all(bind=engine)
    print("Done.")


if __name__ == "__main__":
    create_tables()
