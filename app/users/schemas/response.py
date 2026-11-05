from pydantic import BaseModel, ConfigDict

from app.pokeapi.schemas.pokemon import PokemonSchema
from app.pokeapi.schemas.item import ItemSchema


class UserResponseSchema(BaseModel):
    id: int
    username: str
    email: str
    pokemons: list[PokemonSchema]
    items: list[ItemSchema]
    model_config = ConfigDict(from_attributes=True)
