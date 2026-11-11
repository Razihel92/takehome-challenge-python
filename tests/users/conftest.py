from collections.abc import Awaitable, Callable
from typing import Any

import httpx
import pytest
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
