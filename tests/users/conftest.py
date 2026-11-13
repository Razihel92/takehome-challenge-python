from collections.abc import AsyncGenerator, Awaitable, Callable
from typing import Any

import httpx
import pytest
from app.config import settings
from app.main import app
from app.pokeapi.dependencies import get_http_client
from app.users.models import User

from tests.conftest import TestSessionLocal

from .factories import user_payload


@pytest.fixture
def create_user(
    client: httpx.AsyncClient,
) -> Callable[..., Awaitable[dict[str, Any]]]:
    async def _create_user(**overrides: Any) -> dict[str, Any]:
        response = await client.post(
            "/users/",
            json=user_payload(**overrides),
        )
        assert response.status_code == 201
        return response.json()

    return _create_user


@pytest.fixture
def get_stored_password() -> Callable[..., Awaitable[str]]:
    async def _get_stored_password(user_id: int) -> str:
        async with TestSessionLocal() as session:
            user = await session.get(User, user_id)

        assert user is not None
        return user.password

    return _get_stored_password


@pytest.fixture
def pokeapi_down(client: httpx.AsyncClient) -> None:
    def failing_handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("PokeAPI caído", request=request)

    async def override_get_http_client() -> AsyncGenerator[httpx.AsyncClient]:
        transport = httpx.MockTransport(failing_handler)
        async with httpx.AsyncClient(
            base_url=settings.pokeapi_url, transport=transport
        ) as http_client:
            yield http_client

    app.dependency_overrides[get_http_client] = override_get_http_client
