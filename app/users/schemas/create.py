from pydantic import BaseModel


class UserCreateSchema(BaseModel):
    username: str
    email: str
    password: str
    pokemon_ids: list[int]
    items_ids: list[int]
