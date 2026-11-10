import httpx
import pytest
from app.users.schemas import UserCreateSchema

SEED_USERS_MOCK: list[UserCreateSchema] = [
    UserCreateSchema(
        username="ash",
        email="ash@pokemon.com",
        password="pikachu123",
        pokemon_ids=[25, 1],
        items_ids=[1],
    ),
    UserCreateSchema(
        username="misty",
        email="misty@pokemon.com",
        password="starmie123",
        pokemon_ids=[1],
        items_ids=[1],
    ),
    UserCreateSchema(
        username="brock",
        email="brock@pokemon.com",
        password="onix1234",
        pokemon_ids=[25],
        items_ids=[1],
    ),
]


@pytest.mark.anyio
async def test_seed_returns_201_with_seed_users(
    client: httpx.AsyncClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr("app.seed.service.SEED_USERS", SEED_USERS_MOCK)

    response = await client.post("/seed/")
    created_users = response.json()

    assert response.status_code == 201
    assert len(created_users) == len(SEED_USERS_MOCK)


@pytest.mark.anyio
async def test_seed_twice_does_not_duplicate_users(
    client: httpx.AsyncClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr("app.seed.service.SEED_USERS", SEED_USERS_MOCK)

    await client.post("/seed/")
    second_seed = await client.post("/seed/")

    users_response = await client.get("/users/")

    assert second_seed.status_code == 201
    assert users_response.status_code == 200
    assert len(users_response.json()) == len(SEED_USERS_MOCK)
