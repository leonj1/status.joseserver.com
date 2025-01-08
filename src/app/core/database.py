import os
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./incidents.db")

# Ensure database directory exists
db_path = DATABASE_URL.split("///")[-1]
db_dir = os.path.dirname(db_path)
if db_dir:
    Path(db_dir).mkdir(parents=True, exist_ok=True)
    # Touch the database file to ensure it exists
    Path(db_path).touch(exist_ok=True)

engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)