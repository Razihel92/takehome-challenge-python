import asyncio

import httpx
from fastapi import Depends

from app.pokeapi.dependencies import get_http_client
from app.pokeapi.schemas import ItemSchema, PokemonSchema

ROUTE_ELEMENTS: dict[type[PokemonSchema | ItemSchema], str] = {
    PokemonSchema: "pokemon",
    ItemSchema: "item",
}


class PokeApiClient:
    def __init__(self, http: httpx.AsyncClient = Depends(get_http_client)):
        self.http = http

    async def get_element_by_id[T: (PokemonSchema, ItemSchema)](
        self,
        id_element: int,
        schema: type[T],
    ) -> T | None:

        response = await self.http.get(f"/{ROUTE_ELEMENTS[schema]}/{id_element}")

        if response.status_code == 404:
            return None

        response.raise_for_status()
        return schema.model_validate(response.json())

    async def get_elements_by_ids[T: (PokemonSchema, ItemSchema)](
        self, elements_ids: list[int], schema: type[T]
    ) -> list[T | None]:
        tasks = [
            self.get_element_by_id(element_id, schema) for element_id in elements_ids
        ]
        return await asyncio.gather(*tasks)
