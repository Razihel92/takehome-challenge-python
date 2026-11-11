from fastapi import Depends

from app.exceptions import AppError
from app.pokeapi import PokeApiClient
from app.pokeapi.schemas import ItemSchema, PokemonSchema
from app.security import hash_password
from app.users.models import User
from app.users.repository import UserRepository
from app.users.schemas import UserCreateSchema, UserResponseSchema, UserUpdateSchema


class UserService:
    def __init__(
        self,
        repository: UserRepository = Depends(UserRepository),
        poke_api: PokeApiClient = Depends(PokeApiClient),
    ):
        self.repository = repository
        self.poke_api = poke_api

    async def create_user(self, user_data: UserCreateSchema) -> UserResponseSchema:
        pokemons_by_id = await self._validate_elements_ids(
            user_data.pokemon_ids, PokemonSchema
        )

        items_by_id = await self._validate_elements_ids(user_data.items_ids, ItemSchema)

        user_with_pass_hashed = user_data.model_copy(
            update={"password": await hash_password(user_data.password)}
        )
        usuario = await self.repository.create_user(user_with_pass_hashed)

        return self._build_response(usuario, pokemons_by_id, items_by_id)

    async def get_user_by_id(self, user_id: int) -> UserResponseSchema:
        usuario = await self.repository.get_user_by_id(user_id)

        if usuario is None:
            raise AppError.not_found("Usuario no encontrado")

        pokemons_by_id = await self._fetch_elements(usuario.pokemon_ids, PokemonSchema)
        items_by_id = await self._fetch_elements(usuario.items_ids, ItemSchema)
        return self._build_response(usuario, pokemons_by_id, items_by_id)

    async def get_all_users(self) -> list[UserResponseSchema]:
        usuarios = await self.repository.get_all_users()

        all_pokemon_ids = [
            pokemon_id for usuario in usuarios for pokemon_id in usuario.pokemon_ids
        ]
        all_items_ids = [
            item_id for usuario in usuarios for item_id in usuario.items_ids
        ]

        pokemons_by_ids = await self._fetch_elements(all_pokemon_ids, PokemonSchema)
        items_by_ids = await self._fetch_elements(all_items_ids, ItemSchema)

        return [
            self._build_response(usuario, pokemons_by_ids, items_by_ids)
            for usuario in usuarios
        ]

    async def update_user(
        self, user_id: int, user_data: UserUpdateSchema
    ) -> UserResponseSchema:
        if await self.repository.get_user_by_id(user_id) is None:
            raise AppError.not_found("Usuario no encontrado")

        pokemons_by_id = None

        items_by_id = None

        user_to_update = user_data

        if user_data.pokemon_ids is not None:
            pokemons_by_id = await self._validate_elements_ids(
                user_data.pokemon_ids, PokemonSchema
            )

        if user_data.items_ids is not None:
            items_by_id = await self._validate_elements_ids(
                user_data.items_ids, ItemSchema
            )

        if user_data.password is not None:
            user_to_update = user_data.model_copy(
                update={"password": await hash_password(user_data.password)}
            )

        usuario = await self.repository.update_user(user_id, user_to_update)

        if usuario is None:
            raise AppError.not_found("Usuario no encontrado")

        if pokemons_by_id is None:
            pokemons_by_id = await self._fetch_elements(
                usuario.pokemon_ids, PokemonSchema
            )

        if items_by_id is None:
            items_by_id = await self._fetch_elements(usuario.items_ids, ItemSchema)

        return self._build_response(usuario, pokemons_by_id, items_by_id)

    async def delete_user(self, user_id: int) -> UserResponseSchema:
        usuario = await self.repository.delete_user(user_id)
        if usuario is None:
            raise AppError.not_found("Usuario no encontrado")

        pokemons_by_id = await self._fetch_elements(usuario.pokemon_ids, PokemonSchema)
        items_by_id = await self._fetch_elements(usuario.items_ids, ItemSchema)

        return self._build_response(usuario, pokemons_by_id, items_by_id)

    async def _validate_elements_ids[T: (PokemonSchema, ItemSchema)](
        self, elements_ids: list[int], schema: type[T]
    ) -> dict[int, T]:

        elements_by_id = await self._fetch_elements(elements_ids, schema)

        invalid_ids = [
            element_id
            for element_id in elements_ids
            if element_id not in elements_by_id
        ]

        if invalid_ids:
            raise AppError.bad_request(
                f"IDs de {schema.DISPLAY_NAME} no encontrados: {invalid_ids}"
            )
        return elements_by_id

    async def _fetch_elements[T: (PokemonSchema, ItemSchema)](
        self, elements_ids: list[int], schema: type[T]
    ) -> dict[int, T]:

        unique_ids = list(set(elements_ids))

        elements = await self.poke_api.get_elements_by_ids(unique_ids, schema)

        return {element.id: element for element in elements if element is not None}

    def _build_response(
        self,
        user: User,
        pokemons_by_id: dict[int, PokemonSchema],
        items_by_id: dict[int, ItemSchema],
    ) -> UserResponseSchema:
        return UserResponseSchema(
            id=user.id,
            username=user.username,
            email=user.email,
            pokemons=[
                pokemons_by_id[pokemon_id]
                for pokemon_id in user.pokemon_ids
                if pokemon_id in pokemons_by_id
            ],
            items=[
                items_by_id[item_id]
                for item_id in user.items_ids
                if item_id in items_by_id
            ],
        )
