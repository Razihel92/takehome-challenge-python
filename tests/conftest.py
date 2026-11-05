import os
from collections.abc import AsyncGenerator

import pytest

os.environ["ENV_FILE"] = ".env.test"

import httpx
from alembic import command
from alembic.config import Config
from app.config import settings
from app.database import DATABASE_URL, get_db
from app.main import app
from app.pokeapi.dependencies import BASE_URL, get_http_client
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from tests.mocks import create_pokeapi_handler

test_engine = create_async_engine(DATABASE_URL, poolclass=NullPool)
TestSessionLocal = async_sessionmaker(test_engine, expire_on_commit=False)


async def override_get_db() -> AsyncGenerator[AsyncSession]:
    async with TestSessionLocal() as session:
        yield session


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture(scope="session", autouse=True)
def check_test_db() -> None:
    if settings.app_env != "test":
        pytest.exit("No se está usando la base de datos de testeo")


@pytest.fixture(scope="session", autouse=True)
def apply_migrations(check_test_db: None) -> None:
    command.upgrade(Config("alembic.ini"), "head")


async def truncate_tables() -> None:
    async with test_engine.begin() as conn:
        await conn.execute(text("TRUNCATE users RESTART IDENTITY CASCADE"))


@pytest.fixture(autouse=True)
async def clean_db(apply_migrations: None) -> AsyncGenerator[None]:
    await truncate_tables()
    yield
    await truncate_tables()


@pytest.fixture
def pokeapi_requests() -> list[str]:
    return []


@pytest.fixture
async def client(pokeapi_requests: list[str]) -> AsyncGenerator[httpx.AsyncClient]:
    async def override_get_http_client() -> AsyncGenerator[httpx.AsyncClient]:
        transport = httpx.MockTransport(create_pokeapi_handler(pokeapi_requests))
        async with httpx.AsyncClient(
            base_url=BASE_URL, transport=transport
        ) as http_client:
            yield http_client

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_http_client] = override_get_http_client

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac

    app.dependency_overrides.clear()
