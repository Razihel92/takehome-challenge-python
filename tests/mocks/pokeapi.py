from collections.abc import Callable

import httpx

MOCK_POKEMON: dict[int, dict[str, int | str]] = {
    1: {"id": 1, "name": "bulbasaur"},
    25: {"id": 25, "name": "pikachu"},
}

MOCK_ITEMS: dict[int, dict[str, int | str]] = {
    1: {"id": 1, "name": "master-ball"},
}

MOCK_DATA: dict[str, dict[int, dict[str, int | str]]] = {
    "pokemon": MOCK_POKEMON,
    "item": MOCK_ITEMS,
}


def pokeapi_handler(
    request: httpx.Request, requested_paths: list[str]
) -> httpx.Response:
    requested_paths.append(request.url.path)
    *_, resource, element_id = request.url.path.split("/")
    data = MOCK_DATA.get(resource, {}).get(int(element_id))

    if data is None:
        return httpx.Response(404)

    return httpx.Response(200, json=data)


def create_pokeapi_handler(
    requested_paths: list[str],
) -> Callable[[httpx.Request], httpx.Response]:
    return lambda request: pokeapi_handler(request, requested_paths)
