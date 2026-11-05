from typing import Any


def user_payload(**overrides: Any) -> dict[str, Any]:
    return {
        "username": "ash",
        "email": "ash@pokemon.com",
        "password": "pikachu123",
        "pokemon_ids": [1, 25],
        "items_ids": [1],
        **overrides,
    }
