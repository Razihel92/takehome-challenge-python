from typing import ClassVar

from pydantic import BaseModel


class PokemonSchema(BaseModel):
    DISPLAY_NAME: ClassVar[str] = "Pokemon"

    id: int
    name: str
