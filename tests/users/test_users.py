from collections.abc import Awaitable, Callable
from typing import Any

import httpx
import pytest
from app.security import password_hash

from .factories import user_payload

BULBASAUR: dict[str, int | str] = {"id": 1, "name": "bulbasaur"}
PIKACHU: dict[str, int | str] = {"id": 25, "name": "pikachu"}
MASTER_BALL: dict[str, int | str] = {"id": 1, "name": "master-ball"}


# --- POST /users/ ---


@pytest.mark.anyio
async def test_create_user_returns_201(
    client: httpx.AsyncClient,
) -> None:
    created_response = await client.post(
        "/users/",
        json=user_payload(pokemon_ids=[1], items_ids=[1]),
    )
    user_body = created_response.json()

    assert created_response.status_code == 201
    assert "id" in user_body
    assert "password" not in user_body
    assert user_body["username"] == "ash"
    assert user_body["email"] == "ash@pokemon.com"
    assert user_body["pokemons"] == [BULBASAUR]
    assert user_body["items"] == [MASTER_BALL]


@pytest.mark.anyio
async def test_create_user_with_duplicate_username_returns_409(
    client: httpx.AsyncClient,
) -> None:
    await client.post("/users/", json=user_payload())

    response = await client.post(
        "/users/",
        json=user_payload(email="otro@pokemon.com"),
    )

    assert response.status_code == 409
    assert response.json() == {"detail": "El username o email ya está en uso"}


@pytest.mark.anyio
async def test_create_user_with_duplicate_email_returns_409(
    client: httpx.AsyncClient,
) -> None:
    await client.post("/users/", json=user_payload())

    response = await client.post(
        "/users/",
        json=user_payload(username="gary"),
    )

    assert response.status_code == 409
    assert response.json() == {"detail": "El username o email ya está en uso"}


@pytest.mark.anyio
async def test_create_user_with_invalid_pokemon_returns_400(
    client: httpx.AsyncClient,
) -> None:
    response = await client.post(
        "/users/",
        json=user_payload(pokemon_ids=[25, 9999], items_ids=[]),
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "IDs de Pokemon no encontrados: [9999]"

    users = await client.get("/users/")
    assert users.json() == []


@pytest.mark.anyio
async def test_create_user_with_invalid_item_returns_400(
    client: httpx.AsyncClient,
) -> None:
    response = await client.post(
        "/users/",
        json=user_payload(pokemon_ids=[25], items_ids=[1, 9999]),
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "IDs de Item no encontrados: [9999]"}

    users = await client.get("/users/")
    assert users.json() == []


@pytest.mark.anyio
async def test_create_user_stores_hashed_password(
    create_user: Callable[..., Awaitable[dict[str, Any]]],
    get_stored_password: Callable[..., Awaitable[str]],
) -> None:
    user = await create_user()

    stored_password = await get_stored_password(user["id"])

    assert stored_password != "pikachu123"
    assert password_hash.verify("pikachu123", stored_password)


# --- GET /users/ ---


@pytest.mark.anyio
async def test_list_users_empty(client: httpx.AsyncClient) -> None:
    response = await client.get("/users/")

    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.anyio
async def test_list_users_returns_created_users(client: httpx.AsyncClient) -> None:
    user_ash = await client.post(
        "/users/",
        json=user_payload(),
    )
    user_misty = await client.post(
        "/users/",
        json=user_payload(
            username="misty",
            email="misty@pokemon.com",
        ),
    )

    response = await client.get("/users/")
    created_users = response.json()

    assert response.status_code == 200
    assert len(created_users) == 2
    assert [u["username"] for u in created_users] == ["ash", "misty"]
    assert [u["email"] for u in created_users] == [
        "ash@pokemon.com",
        "misty@pokemon.com",
    ]
    assert created_users == [user_ash.json(), user_misty.json()]


# --- GET /users/{user_id} ---


@pytest.mark.anyio
async def test_get_user_returns_pokeapi_details(client: httpx.AsyncClient) -> None:
    created = await client.post(
        "/users/",
        json=user_payload(),
    )
    user_id = created.json()["id"]

    response = await client.get(f"/users/{user_id}")

    assert response.status_code == 200
    body = response.json()
    assert body["pokemons"] == [BULBASAUR, PIKACHU]
    assert body["items"] == [MASTER_BALL]


@pytest.mark.anyio
async def test_get_user_dedupes_pokeapi_requests(
    client: httpx.AsyncClient, pokeapi_requests: list[str]
) -> None:
    created = await client.post(
        "/users/",
        json=user_payload(pokemon_ids=[25, 25], items_ids=[]),
    )
    user_id = created.json()["id"]
    pokeapi_requests.clear()

    response = await client.get(f"/users/{user_id}")

    assert response.status_code == 200
    assert pokeapi_requests == ["/api/v2/pokemon/25"]
    assert response.json()["pokemons"] == [PIKACHU, PIKACHU]


@pytest.mark.anyio
async def test_get_missing_user_returns_404(client: httpx.AsyncClient) -> None:
    response = await client.get("/users/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Usuario no encontrado"}


# --- PATCH /users/{user_id} ---


@pytest.mark.anyio
async def test_update_user_returns_200(client: httpx.AsyncClient) -> None:
    user_created = await client.post(
        "/users/",
        json=user_payload(),
    )
    user_body = user_created.json()

    response = await client.patch(
        f"/users/{user_body['id']}",
        json={"username": "red"},
    )

    updated_user = response.json()
    assert response.status_code == 200
    assert updated_user == {
        **user_body,
        "username": "red",
    }  # Esta linea resume las de abajo
    # assert updated_user["username"] == "red"
    # assert updated_user["email"] == user_body["email"]
    # assert updated_user["pokemons"] == user_body["pokemons"]
    # assert updated_user["items"] == user_body["items"]


@pytest.mark.anyio
async def test_update_user_hashes_new_password(
    client: httpx.AsyncClient,
    create_user: Callable[..., Awaitable[dict[str, Any]]],
    get_stored_password: Callable[..., Awaitable[str]],
) -> None:
    user_body = await create_user()
    response = await client.patch(
        f"/users/{user_body['id']}",
        json={"password": "nueva123"},
    )

    stored_password = await get_stored_password(user_body["id"])

    assert response.status_code == 200
    assert not password_hash.verify("pikachu123", stored_password)
    assert stored_password != "nueva123"
    assert password_hash.verify("nueva123", stored_password)


@pytest.mark.anyio
async def test_update_user_without_password_keeps_stored_password(
    client: httpx.AsyncClient,
    create_user: Callable[..., Awaitable[dict[str, Any]]],
    get_stored_password: Callable[..., Awaitable[str]],
) -> None:
    user_body = await create_user()
    pass_before_change = await get_stored_password(user_body["id"])
    response = await client.patch(
        f"/users/{user_body['id']}",
        json={"username": "red"},
    )
    pass_after_change = await get_stored_password(user_body["id"])

    assert response.status_code == 200
    assert pass_before_change == pass_after_change


@pytest.mark.anyio
async def test_update_missing_user_returns_404(client: httpx.AsyncClient) -> None:
    response = await client.patch(
        "/users/999",
        json={"username": "red"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Usuario no encontrado"}


@pytest.mark.anyio
async def test_update_user_with_invalid_pokemon_returns_400(
    client: httpx.AsyncClient,
) -> None:
    user_created = await client.post(
        "/users/",
        json=user_payload(),
    )
    user_body = user_created.json()

    response = await client.patch(
        f"/users/{user_body['id']}",
        json={"pokemon_ids": [9999]},
    )

    user_after_patch = (await client.get(f"/users/{user_body['id']}")).json()

    assert response.status_code == 400
    assert response.json() == {"detail": "IDs de Pokemon no encontrados: [9999]"}
    assert user_body == user_after_patch


@pytest.mark.anyio
async def test_update_missing_user_with_invalid_pokemon_returns_404(
    client: httpx.AsyncClient,
) -> None:
    response = await client.patch(
        "/users/999",
        json={"pokemon_ids": [9999]},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Usuario no encontrado"}


@pytest.mark.anyio
async def test_update_user_with_duplicate_username_returns_409(
    client: httpx.AsyncClient,
) -> None:
    await client.post("/users/", json=user_payload())
    misty = (
        await client.post(
            "/users/",
            json=user_payload(username="misty", email="misty@pokemon.com"),
        )
    ).json()

    response = await client.patch(f"/users/{misty['id']}", json={"username": "ash"})

    misty_after_patch = (await client.get(f"/users/{misty['id']}")).json()

    assert response.status_code == 409
    assert response.json() == {"detail": "El username o email ya está en uso"}
    assert misty_after_patch == misty


@pytest.mark.anyio
async def test_update_user_with_duplicate_email_returns_409(
    client: httpx.AsyncClient,
) -> None:
    await client.post("/users/", json=user_payload())
    misty = (
        await client.post(
            "/users/",
            json=user_payload(username="misty", email="misty@pokemon.com"),
        )
    ).json()

    response = await client.patch(
        f"/users/{misty['id']}", json={"email": "ash@pokemon.com"}
    )

    misty_after_patch = (await client.get(f"/users/{misty['id']}")).json()

    assert response.status_code == 409
    assert response.json() == {"detail": "El username o email ya está en uso"}
    assert misty_after_patch == misty


# --- DELETE /users/{user_id} ---


@pytest.mark.anyio
async def test_delete_user_returns_200(client: httpx.AsyncClient) -> None:
    user_created = (await client.post("/users/", json=user_payload())).json()
    delete_response = await client.delete(f"/users/{user_created['id']}")
    user_after_delete = await client.get(f"/users/{user_created['id']}")

    assert delete_response.status_code == 200
    assert user_created == delete_response.json()
    assert user_after_delete.status_code == 404


@pytest.mark.anyio
async def test_delete_missing_user_returns_404(client: httpx.AsyncClient) -> None:
    delete_response = await client.delete("/users/999")

    assert delete_response.status_code == 404
    assert delete_response.json() == {"detail": "Usuario no encontrado"}
