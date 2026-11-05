from collections.abc import Awaitable, Callable
from typing import Any

import httpx
import pytest

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
