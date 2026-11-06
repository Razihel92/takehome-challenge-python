from urllib.parse import quote_plus

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import settings

password_segura = quote_plus(settings.db_password)

# Neon (producción) exige conexión cifrada; local/Docker/CI no usan SSL
ssl_param = "?ssl=require" if settings.db_ssl else ""

DATABASE_URL = (
    f"postgresql+asyncpg://{settings.db_username}:{password_segura}"
    f"@{settings.db_host}:{settings.db_port}/{settings.db_name}{ssl_param}"
)

engine = create_async_engine(DATABASE_URL)

AsyncSessionLocal = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


class Base(DeclarativeBase):
    pass


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
